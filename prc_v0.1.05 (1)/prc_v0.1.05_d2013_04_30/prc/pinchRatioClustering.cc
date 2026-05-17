// This file is part of PRC, a C++ library for pinch ratio clustering.
//
// Copyright (C) 2012 Doug Heisterkamp <drh@ieee.org>
//
// PRC is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 3 of the License, or (at your option) any later version.
//
// Alternatively, you can redistribute it and/or
// modify it under the terms of the GNU General Public License as
// published by the Free Software Foundation; either version 2 of
// the License, or (at your option) any later version.
//
// PRC is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License or the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License and a copy of the GNU General Public License along with
// PRC. If not, see <http://www.gnu.org/licenses/>.

// The following lines uses subversion's keyword expansion to insert the
// last time the file was modified and by who.

/// \file pinchRatioClustering.cc
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

/// define PINCH_VERIFY_LEX to check that the width is being reduced every iteration
///        it will also back off the epsilon a few times before aborting in case the 
///        problem was just numerical noise and epsilon is too tight
//#define PINCH_VERIFY_LEX
///
/// define HAVE_BENCH to time the execution.  Currently, timing is output to standard output.
//#define HAVE_BENCH

#include<ctime>  // for ms windows
#include<iostream>
#include<iomanip>
#include<fstream>
#include<sstream>
#include<vector>
#include<prc/prcutils.h>
#include<prc/denseEigenStorage.h>
#include<prc/sparseEigenStorage.h>
#include<prc/prcPolicies.h>
#include<prc/runConfigs.h>
#include<prc/pinch.h>
#include<prc/OrderObject.h>
#include<prc/multilevelPinch.h>
#include<prc/knnsim.h>
#include<prc/knnsimSparse.h>
#include<prc/gausssim.h>
#include<prc/gausssimSparse.h>
#include<vector>
#include<iterator>
#include<Eigen/Core>
#include<algorithm>
#include<functional>
#include<prc/internal/purity.h>

using namespace std;
using std::cout;
using std::endl;


// some helper functions defined at end of file
bool cless(PRC::prcReturnStruct &a, PRC::prcReturnStruct &b, std::vector<double> &ab, std::vector<double> &bb); // compare the widths of two separate runs
bool processCmdLine(int argc, const char *argv[], PRC::prcPolicyStruct &policy, PRC::knnAdjPolicyStruct &knnpolicy, PRC::gaussAdjPolicyStruct &gausspolicy, PRC::runConfigStruct &runConfig, PRC::dataConfigStruct &dataConfig);
bool readData( PRC::shared_ptr<PRC::MLSparseMatrixType> &sparseA, PRC::shared_ptr<PRC::MLDenseMatrixType> &denseA, Eigen::MatrixXd &data, Eigen::MatrixXd &vertexWeights, PRC::knnAdjPolicyStruct &knnpolicy, PRC::gaussAdjPolicyStruct &gausspolicy, PRC::runConfigStruct &runConfig, PRC::dataConfigStruct &dataConfig);
void  initOrder( int N, PRC::OrderObject &order);
bool initOrder( int N, PRC::OrderObject &orderObj, PRC::runConfigStruct &runConfig, PRC::dataConfigStruct &);


int main(int argc, const char *argv[])
{

   // should use boost or getopt to process commandline options, but for now
   // just hard code it.
   std::istringstream line;
   PRC::prcPolicyStruct policy;
   PRC::knnAdjPolicyStruct knnpolicy;
   PRC::gaussAdjPolicyStruct gausspolicy;
   PRC::runConfigStruct runConfig;
   PRC::dataConfigStruct dataConfig;

   bool printUsage = processCmdLine(argc,argv, policy,knnpolicy,gausspolicy,runConfig,dataConfig);

   if (dataConfig.inputFileName =="")  // later on, allow using standard input if no filename
      printUsage=true;

   if (printUsage )
   {
      std::cout << "usage: "<<argv[0]<<" [long options]  [filename [numberOfPartitions]]" << std::endl;
      std::cout << "   Possible long options include:\n";
      runConfig.cmdLineUsage(std::cout,"      ");
      dataConfig.cmdLineUsage(std::cout,"      ");
      policy.cmdLineUsage(std::cout,"      ");
      knnpolicy.cmdLineUsage(std::cout,"      ");
      gausspolicy.cmdLineUsage(std::cout,"      ");
      std::cout << std::endl;
      exit(-1);
   }

   if (runConfig.verboseLevel >0)
   {
      std::cout << "Run Configuration:\n"; runConfig.Print(std::cout,"   ");
      std::cout << "Data Configuration:\n"; dataConfig.Print(std::cout,"   ");
      std::cout << "Current Policy:\n"; policy.Print(std::cout,"   ");
      std::cout << "Current KNN Adj Policy:\n"; knnpolicy.Print(std::cout,"   ");
      std::cout << "Current Gaussian Similarity Adj Policy:\n"; gausspolicy.Print(std::cout,"   ");
   }


   PRC::shared_ptr<PRC::MLSparseMatrixType> sparseA(new PRC::MLSparseMatrixType);
   PRC::shared_ptr<PRC::MLDenseMatrixType> denseA(new PRC::MLDenseMatrixType);

   Eigen::MatrixXd data;
   Eigen::MatrixXd vertexWeights; // for future use ... read from adjacency graph
   if (! readData(sparseA,denseA,data,vertexWeights,knnpolicy,gausspolicy,runConfig,dataConfig))
   {
      std::cerr << "Failed to process input data file : " << dataConfig.inputFileName << std::endl;
      exit(-1);
   }

// PRC::DenseEigenStorage<Eigen::Block<PRC::MLDenseMatrixType> > dStorage(denseA->block(0,0,denseA->rows(),denseA->cols()));
// PRC::SparseEigenStorage<PRC::MLSparseMatrixType> sStorage(*sparseA);
   PRC::DenseEigenStorage<PRC::shared_ptr<PRC::MLDenseMatrixType> > dStorage;
   PRC::SparseEigenStorage<PRC::shared_ptr<PRC::MLSparseMatrixType> > sStorage;
   if (!dataConfig.useSparseMatrix)
       dStorage.AdjMatrixPtr() = denseA;
   else
       sStorage.AdjMatrixPtr() = sparseA;

   int &numParts = runConfig.numberOfPartitions;
   std::string &graphFileName = dataConfig.inputFileName;

   if (runConfig.seed == 0)
      srand((unsigned)time(NULL));
   else
      srand(runConfig.seed);

   ostringstream tmpstream;
   tmpstream << graphFileName << runConfig.outputLabelSuffix<<numParts << runConfig.infoSuffix;
   if (runConfig.seedSuffix)
      tmpstream <<"_seed_"<<runConfig.seed;
   std::string clusterOutputFileName = tmpstream.str();

   std::string mrl_clusterOutputFileName =clusterOutputFileName + "_multirun_labels";
   std::string mri_clusterOutputFileName =clusterOutputFileName + "_multirun_info";

   ostringstream tmpstream2;
   tmpstream2 << graphFileName <<  runConfig.outputOrderSuffix<<numParts << runConfig.infoSuffix;
   if (runConfig.seedSuffix)
      tmpstream2 <<"_seed_"<<runConfig.seed;
   std::string clusterOrderFileName = tmpstream2.str();
   Eigen::VectorXi best_labels;

   std::vector<double> best_b;
   std::vector<double> cur_b;
   std::vector<std::pair<double,double> > pr_purity;
   const int N = dataConfig.useSparseMatrix? sparseA->rows() :  denseA->rows();

   PRC::OrderObject myOrder;
   PRC::OrderObject bestOrder;
   int best_orun = 0;
   PRC::prcReturnStruct best_counts;
   bool haveInitialOrder = initOrder(N,myOrder,runConfig,dataConfig);

   ofstream outMRL;
   ofstream outMRI;
   if (runConfig.saveMultipleRuns)
   {
      outMRL.open( mrl_clusterOutputFileName.c_str());
      outMRI.open( mri_clusterOutputFileName.c_str());
   }


   for (int orun=0; orun < runConfig.numberInitOrderings; ++orun)
   {
      if ((orun >0) || !haveInitialOrder)
      {
         initOrder(N,myOrder);
      }
      Eigen::VectorXi labels;
      PRC::prcReturnStruct counts;
      if (runConfig.useMultiLevelPRC)
      {
         if (dataConfig.useSparseMatrix)
         {
// todo: convert multilevel to use storage objects
std::cout << "not Running prc -- multi level sparse is not currently available.\nExiting." << std::endl;
exit(-1);
//            counts = PRC::multilevelPRC(sparseA,myOrder,labels,numParts,policy);
         }
         else
         {
// todo: convert multilevel to use storage objects
std::cout << "not Running prc -- multi level dense is not currently available.\nExiting." << std::endl;
exit(-1);
//            counts = PRC::multilevelPRC(denseA,myOrder,labels,numParts,policy);
         }
      }
      else
      {
         if (dataConfig.useSparseMatrix)
         {
            counts = PRC::pinchRatioClustering(sStorage,myOrder,labels,numParts,policy);
         }
         else
         {
            counts = PRC::pinchRatioClustering(dStorage,myOrder,labels,numParts,policy);
         }
      }
      // update current widths from run
      cur_b.resize(myOrder.boundary().size());
      std::copy(myOrder.boundary().data(),myOrder.boundary().data()+myOrder.boundary().size(),cur_b.begin());
      std::sort(cur_b.begin(), cur_b.end(),std::greater<double>());

      if (runConfig.saveMultipleRuns)
      {
         for(int i=0; i< labels.size();i++)
         {
            outMRL<< " " << labels[i];
         }
         outMRL<<std::endl;
         if ((dataConfig.fileType == PRC::POINT_DATA) && (dataConfig.pointDataConfig.tagLoc != PRC::NO_TAGS))
         {
            Eigen::VectorXi trueTags;
            if(dataConfig.pointDataConfig.tagLoc == PRC::FRONT_TAGS)
               trueTags = data.col(0).cast<int>();
            else if(dataConfig.pointDataConfig.tagLoc == PRC::REAR_TAGS)
               trueTags =  data.col(data.cols()-1).cast<int>();
            else
               assert(false && "unknown tagLoc");
            double accuracy = PRC::calcPurity(labels, trueTags);
            outMRI << "   purity = " << accuracy << std::endl;
            pr_purity.push_back(std::pair<double,double>(counts.averageWeightedClusterQuality, accuracy));
         }
         counts.Print(outMRI," ",",");
         outMRI<<"  vorder = "; myOrder.Print(outMRI);outMRI << std::endl;
         outMRI<<"  boundary = ";
         for (int qqq=0; qqq < myOrder.boundary().size();++qqq)
         {
            if (qqq%10 == 0)
            {
               outMRI << std::endl;
            }
            outMRI << std::setw(10) << std::setprecision(6) <<  myOrder.boundary()(qqq);
         }
         outMRI<<std::endl;
         outMRI <<"marks = ";
         PRC::PrintMarks(outMRI,myOrder.marks());
         outMRI << std::endl<<std::endl;
         outMRI<<"  width = ";
         PRC::printStdVec(outMRI,cur_b);
         outMRI<<std::endl;
      }

      if ((orun == 0) || cless(counts, best_counts,cur_b, best_b))
      {
         best_labels = labels;
         best_counts = counts;
         best_b = cur_b;
         bestOrder = myOrder; 
         best_orun = orun;
      }
   }
          
   if (runConfig.saveMultipleRuns)
   {
      outMRI.close();
      outMRL.close();
   }

   if (runConfig.saveLabels)
   {
      ofstream fout(clusterOutputFileName.c_str());
      for(int i=0; i< best_labels.size();i++)
      {
         fout<< best_labels[i] << std::endl;
      }
      fout.close();
   }

   if (runConfig.saveOrder)
   {
      ofstream fout2(clusterOrderFileName.c_str());
      fout2<<"order = "<< bestOrder.Print() << std::endl;
      fout2 <<"boundary = ";
      bestOrder.boundary().Print(fout2);
      fout2<<std::endl;
      fout2 <<"marks = ";
      PRC::PrintMarks(fout2,bestOrder.marks());
      fout2<<std::endl;
      fout2 << "labels = " << best_labels.transpose() << endl;
      fout2 << "run " << best_orun << " best out of " << runConfig.numberInitOrderings << " runs." << endl;
      fout2.close();
   }
   if (runConfig.verboseLevel > 0)
   {
      cout << "Finished with results:\n";
      cout << "   labels = " << best_labels.transpose() << endl;

      if ((dataConfig.fileType == PRC::POINT_DATA) && (dataConfig.pointDataConfig.tagLoc != PRC::NO_TAGS))
      {
         if (runConfig.verboseLevel>5)
         {
            cout << "pr purity vector = ";
            for(std::vector<std::pair<double,double> >::iterator p=pr_purity.begin(); p != pr_purity.end();++p)
               cout << p->first << " " << p->second << ",";
            cout << endl;
         }

         Eigen::VectorXi trueTags;
         if(dataConfig.pointDataConfig.tagLoc == PRC::FRONT_TAGS)
            trueTags = data.col(0).cast<int>();
         else if(dataConfig.pointDataConfig.tagLoc == PRC::REAR_TAGS)
            trueTags =  data.col(data.cols()-1).cast<int>();
         else
            assert(false && "unknown tagLoc");
         if (runConfig.verboseLevel>1)
         {
            double accuracy = PRC::calcPurity(best_labels, trueTags);
            cout  << accuracy << " | ";best_counts.Print(cout," ",",");cout << " # " << clusterOutputFileName.c_str() << " # ACCACC --- for grep'ing"<<  endl;
            cout << accuracy << " = purity  " << std::endl;
         }
      }
      cout << endl;
   }
   if (haveInitialOrder && (runConfig.useMultiLevelPRC))
      cout << "Warning: multilevel PRC currently ignores provided initial order." << std::endl;
   return 0;
}


/// compare the widths of two separate runs
///
/// todo : cleanup and move to a utility file
bool cless(PRC::prcReturnStruct &a, PRC::prcReturnStruct &b, std::vector<double> &ab, std::vector<double> &bb)
{
      double cureps = 1e-12;
      for(std::vector<double>::size_type i=0;i<ab.size();++i)
      {
         if (( ab[i] - bb[i] ) < -1*cureps*(1+bb[i]))
         {
//std::cout << "cless true at " << i << " | "<< ab[i] << " vs " << bb[i] << ", diff = " << ab[i] -bb[i] << std::endl;
            return true;
         }
         else if (( ab[i] - bb[i] ) > 1*cureps*(1+bb[i]))
         {
//std::cout << "cless false at " << i << " | "<< ab[i] << " vs " << bb[i] << ", diff = " << ab[i] -bb[i] << std::endl;
            return false;
         }
      }
 
      if (fabs(a.averageWeightedClusterQuality - b.averageWeightedClusterQuality) > 1e-10)
      {
         if (a.averageWeightedClusterQuality < b.averageWeightedClusterQuality)
            return true;
         else
            return false;
      }

      if (fabs( a.averageClusterQuality - b.averageClusterQuality  ) > 1e-10)
      {
         if (a.averageClusterQuality  < b.averageClusterQuality  )
            return true;
         else
            return false;
      }

      if (fabs( a.weightedGeometricMean - b.weightedGeometricMean ) > 1e-10)
      {
         if ( a.weightedGeometricMean < b.weightedGeometricMean )
            return true;
         else
            return false;
      }

      if (fabs( a.geometricMean -  b.geometricMean ) > 1e-10)
      {
         if ( a.geometricMean < b.geometricMean )
            return true;
         else
            return false;
      }

      // warning message
//      std::cout << "Warning ################################################# need more comparisons" <<  ab.size() << " " << bb.size() << std::endl;
//      PRC::printStdVec(std::cout,ab);
//      std::cout << std::endl;
//      PRC::printStdVec(std::cout,bb);
//      std::cout << "-------------------------------------------------" << std::endl;
      return false;
}


/// todo : cleanup and move to a utility file
bool processCmdLine(int argc, const char *argv[], 
          PRC::prcPolicyStruct &policy, PRC::knnAdjPolicyStruct &knnpolicy,
          PRC::gaussAdjPolicyStruct &gausspolicy, PRC::runConfigStruct &runConfig,
          PRC::dataConfigStruct &dataConfig)
{

   std::istringstream line;
   bool printUsage = false;
   for(int i=1; i < argc; ++i)
   {
      if (argv[i] == NULL)
         break;
      int consumed = policy.checkCmdLineOption(i,argc,argv);
      if (consumed>0)
      {
         i += consumed -1;
         continue;
      }

      consumed = runConfig.checkCmdLineOption(i,argc,argv);
      if (consumed>0)
      {
         i += consumed -1;
         continue;
      }
      consumed = dataConfig.checkCmdLineOption(i,argc,argv);
      if (consumed>0)
      {
         i += consumed -1;
         continue;
      }

      if (consumed>0)
      {
         i += consumed -1;
         continue;
      }
      consumed = knnpolicy.checkCmdLineOption(i,argc,argv);
      if (consumed>0)
      {
         i += consumed -1;
         continue;
      }
      consumed = gausspolicy.checkCmdLineOption(i,argc,argv);
      if (consumed>0)
      {
         i += consumed -1;
         continue;
      }

      if (argv[i][0] == '-')
      {
         std::cerr << "Unknow option " << argv[i] << std::endl;
         printUsage=true;
         break;
      }
      else
      {
         dataConfig.inputFileName = argv[i];
         if (argv[i+1] != NULL)
         {
            if (argv[i+1][0] != '-')
            {
               line.clear();
               line.str(argv[i+1]);
               if (!(line >> runConfig.numberOfPartitions))
               {
                  std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer number of partitions." << std::endl;
                  printUsage=true;
                  break;
               }
               i++;
            }
         }
      }
   }
   return printUsage;
}



/// todo : cleanup and move to a utility file
bool readData( 
   PRC::shared_ptr<PRC::MLSparseMatrixType> &sparseA,
   PRC::shared_ptr<PRC::MLDenseMatrixType> &denseA,
   Eigen::MatrixXd &data,
   Eigen::MatrixXd &vertexWeights, // for future use ... read from adjacency graph
   PRC::knnAdjPolicyStruct &knnpolicy,
   PRC::gaussAdjPolicyStruct &gausspolicy, PRC::runConfigStruct &runConfig,
   PRC::dataConfigStruct &dataConfig
      )
{
   std::ifstream fin(dataConfig.inputFileName.c_str());
   if (!fin)
   {
      std::cerr << "Failed to open file " << dataConfig.inputFileName << std::endl;
      return false;
   }

   bool flag = false;
   if (dataConfig.fileType == PRC::POINT_DATA)
   {
      flag = PRC::loadtxt(fin,data);
      if (flag)
      {
         internalPRC::BlockXd points = internalPRC::sliceTags(data,dataConfig.pointDataConfig.tagLoc);
         if (dataConfig.useSparseMatrix)
         {
            if (dataConfig.pointDataConfig.simType == PRC::GAUSS_ADJ_SIM)
            {
               double tmpsigma = PRC::gaussSimSparseMatrix(points,*sparseA,gausspolicy.sigma,gausspolicy.mode,gausspolicy.threshold);
               if ((runConfig.verboseLevel > 2)&&(gausspolicy.sigma <=0))
                  std::cout << "using Gaussian similarity sigma of " << tmpsigma << std::endl;
            }
            else if (dataConfig.pointDataConfig.simType == PRC::KNN_ADJ_SIM)
            {
               int tmpk = PRC::knnSimSparseMatrix(points,*sparseA,knnpolicy.k,knnpolicy.mode,knnpolicy.sigma);
               if ((runConfig.verboseLevel > 2)&&(knnpolicy.k <=0))
                  std::cout << "using " << tmpk << " nearest neighbor similarity."  << std::endl;
            }
            else
            {
               std::cout << "Need to specify gaussian or knn point similarity.  Currently not  able to use " << EnumName(dataConfig.pointDataConfig.simType) << std::endl;
               exit(-3);
            }
         }
         else
         {
            if (dataConfig.pointDataConfig.simType == PRC::GAUSS_ADJ_SIM)
            {
               double tmpsigma = PRC::gaussSimMatrix(points,*denseA,gausspolicy.sigma,gausspolicy.mode,gausspolicy.threshold);
               if ((runConfig.verboseLevel > 2)&&(gausspolicy.sigma <=0))
                  std::cout << "using Gaussian similarity sigma of " << tmpsigma << std::endl;
            }
            else if (dataConfig.pointDataConfig.simType == PRC::KNN_ADJ_SIM)
            {
               int tmpk = PRC::knnSimMatrix(points,*denseA,knnpolicy.k,knnpolicy.mode,knnpolicy.sigma);
               if ((runConfig.verboseLevel > 2)&&(knnpolicy.k <=0))
                  std::cout << "using " << tmpk << " nearest neighbor similarity."  << std::endl;
            }
            else
            {
               std::cout << "Need to specify gaussian or knn point similarity.  Currently not  able to use " << EnumName(dataConfig.pointDataConfig.simType) << std::endl;
               exit(-3);
            }
         }
      }
   }
   else if (dataConfig.fileType == PRC::ADJACENCY_DATA)
   {
      if (dataConfig.useSparseMatrix)
         flag = loadSparseGraph(fin,*sparseA,dataConfig.adjDataConfig.nodeOffset,vertexWeights);
      else
         flag = loadGraph(fin,*denseA,dataConfig.adjDataConfig.nodeOffset,vertexWeights);
   }

   if (!flag)
   {
      std::cerr << "Failed to read file " << dataConfig.inputFileName  << " into matrix" <<  std::endl;
      exit(-3);
   }
   if (runConfig.verboseLevel > 0)
   {
      if (dataConfig.useSparseMatrix)
         std::cout << "Sparse Graph size ="<<sparseA->rows() <<"x"<<sparseA->cols() << " with "<<sparseA->nonZeros() << std::endl;
      else
         std::cout << "Dense Graph size= "<<denseA->rows() << "x"<<denseA->cols() << std::endl;
   }
   fin.close();
   return flag;
}

void  initOrder( int N, PRC::OrderObject &order)
{
   std::vector<int> tmp(N);
   for(int i=0; i<N;++i)
   {
     tmp[i] = i;
   }
   std::random_shuffle(tmp.data(),tmp.data()+N);
   order.setFrom(tmp);
}

bool initOrder( int N,
          PRC::OrderObject &orderObj,
          PRC::runConfigStruct &runConfig,
          PRC::dataConfigStruct &)
{
   bool haveInitialOrder = false;
   Eigen::VectorXi tmpV;
   if (runConfig.initOrderFile != "")
   {
      std::ifstream fin2(runConfig.initOrderFile.c_str());
      if (!fin2)
      {
         std::cerr << "Failed to open initial order file " << runConfig.initOrderFile << std::endl;
         exit(-2);
      }
      if ( PRC::loadtxt(fin2,tmpV))
      {
         if (tmpV.size() == N)
         {
            // validate order
            vector<int> v(tmpV.size());
            std::fill(v.begin(),v.end(),0);
            bool validFlag = true;
            for(int zzz=0; zzz<tmpV.size();++zzz)
            {
               if (tmpV(zzz)>=0 && tmpV(zzz) < tmpV.size())
                  v[zzz] += 1;
               else
               {
                  validFlag = false;
                  std::cerr << "ERROR: order indexing out of range."<<std::endl;
                  std::cerr << "order = " << tmpV.transpose() << std::endl;

                  break;
               }
            }
            if (validFlag)
            {
               for(int zzz=0; zzz<tmpV.size();++zzz)
               {
                  if (v[zzz]==0)
                  {
                     validFlag = false;
                     std::cerr << "Error: order missed location " << zzz << std::endl;
                  std::cerr << "order = " << tmpV.transpose() << std::endl;
                     break;
                  }
                  else if (v[zzz] > 1)
                  {
                     validFlag = false;
                     std::cerr << "Error: order duplicated location " << zzz << std::endl;
                  std::cerr << "order = " << tmpV.transpose() << std::endl;
                     break;
                  }
               }
            }

            if(validFlag)
            {
               orderObj.setFrom(tmpV);
               haveInitialOrder = true;
            }
            else
               exit(-2);
         }
         else
         {
            std::cerr << "Initial order file size differs from data file: " << tmpV.size() << " vs " << N << std::endl;;
            exit(-2);
         }
      }
      else
      {
         std::cerr << "Failed to read initial order file " << runConfig.initOrderFile 
            << " in to a vector of integers." << std::endl;
         exit(-2);
      }
      fin2.close();
   }
   else if (runConfig.initLabelsFile != "")
   {
      std::ifstream fin2(runConfig.initLabelsFile.c_str());
      if (!fin2)
      {
         std::cerr << "Failed to open initial label file " << runConfig.initLabelsFile << std::endl;
         exit(-2);
      }
      Eigen::VectorXi labels;
      Eigen::VectorXd dlabels;  // labels may be ints saved as floats 
      if ( PRC::loadtxt(fin2,dlabels))
      {
         labels = dlabels.cast<int>();
         if (labels.size() == N)
         {
            std::map<int,std::vector<int> > r;
            for(int i=0;i<labels.size();i++)
            {
               std::map<int,std::vector<int> >::iterator p = r.find(labels[i]);
               if (p != r.end())
               {
                  p->second.push_back(i);
               }
               else
               {
                  std::vector<int> tmp;
                  tmp.push_back(i);
                  r[labels[i]] = tmp;
               }
            }
            tmpV.resize(labels.size());
            tmpV.fill(-1);
            int curLoc=0;
            for(std::map<int,std::vector<int> >::iterator p = r.begin(); p != r.end(); p++)
            {
               for (std::vector<int>::iterator q = p->second.begin(); q != p->second.end();++q)
               {
                  tmpV[curLoc++] = *q;
               }
            }

            // validate order
            vector<int> v(tmpV.size());
            std::fill(v.begin(),v.end(),0);
            bool validFlag = true;
            for(int zzz=0; zzz<tmpV.size();++zzz)
            {
               if (tmpV(zzz)>=0 && tmpV(zzz) < tmpV.size())
                  v[zzz] += 1;
               else
               {
                  validFlag = false;
                  std::cerr << "ERROR: order indexing out of range."<<std::endl;
                  std::cerr << "order = " << tmpV.transpose() << std::endl;

                  break;
               }
            }
            if (validFlag)
            {
               for(int zzz=0; zzz<tmpV.size();++zzz)
               {
                  if (v[zzz]==0)
                  {
                     validFlag = false;
                     std::cerr << "Error: order missed location " << zzz << std::endl;
                     std::cerr << "order = " << tmpV.transpose() << std::endl;
                     break;
                  }
                  else if (v[zzz] > 1)
                  {
                     validFlag = false;
                     std::cerr << "Error: order duplicated location " << zzz << std::endl;
                     break;
                  }
               }
            }

            if(validFlag)
            {
               orderObj.setFrom(tmpV);
               haveInitialOrder = true;
            }
            else
               exit(-2);
         }
         else
         {
            std::cerr << "Initial label file size differs from data file: " << labels.size() << " vs " << N << std::endl;;
            std::cerr << labels.transpose() << std::endl;
            std::cerr <<"rows = " <<  labels.rows() << std::endl;
            exit(-2);
         }
      }
      else
      {
         std::cerr << "Failed to read initial labels file " << runConfig.initLabelsFile 
            << " in to a vector of integers." << std::endl;
         exit(-2);
      }
      fin2.close();
   }

   return haveInitialOrder;
}


