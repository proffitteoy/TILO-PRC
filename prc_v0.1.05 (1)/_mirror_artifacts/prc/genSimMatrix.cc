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

// \file genSimMatrix.cc
//
// Last changed by = $Author: drh $
// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
// Lastest revision = $Revision: 149 $

#include<ctime>  // for ms windows

#include<iostream>
#include<fstream>
#include<sstream>
#include<prc/prcutils.h>
#include<prc/multilevelPinch.h>
#include<prc/prcPolicies.h>
#include<prc/runConfigs.h>
#include<prc/knnsim.h>
#include<prc/knnsimSparse.h>
#include<prc/gausssim.h>
#include<prc/gausssimSparse.h>
#include<vector>
#include<iterator>
#include<Eigen/Core>

using namespace std;
using std::cout;
using std::endl;


int main(int argc, const char *argv[])
{
   // should use boost or getopt to process commandline options, but for now
   // just hard code it.
   std::istringstream line;
   PRC::prcPolicyStruct policy;
   PRC::knnAdjPolicyStruct knnpolicy;
   PRC::runConfigStruct runConfig;
   PRC::gaussAdjPolicyStruct gausspolicy;
   PRC::dataConfigStruct dataConfig;
   dataConfig.useSparseMatrix = true;
   runConfig.verboseLevel = 0;

   bool printUsage = false;
   string outputFileName = "simMatrix.txt";
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
               outputFileName =  argv[i+1];
               i++;
            }
         }
      }
   }

   if (dataConfig.inputFileName =="")  // later on, allow using standard input if no filename
      printUsage=true;

   if (printUsage )
   {
      std::cout << "usage: "<<argv[0]<<" [long options]  [filename outputFileName]" << std::endl;
      std::cout << "   Possible long options include ... (NOTE: most are not used in this program):\n";
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

   std::string &graphFileName = dataConfig.inputFileName;

   std::ifstream fin(graphFileName.c_str());
   if (!fin)
   {
      std::cerr << "Failed to open file " << graphFileName << std::endl;
      exit(-2);
   }


   std::ofstream fout(outputFileName.c_str());
   if (!fout)
   {
      std::cerr << "Failed to open file " << outputFileName << std::endl;
      exit(-2);
   }


   if (dataConfig.useSparseMatrix)
   {
      std::cerr << "Outputing sparse similiarity matrix is not implemented yet." << std::endl;
   }

   bool flag = false;
   PRC::shared_ptr<PRC::MLDenseMatrixType> denseA(new PRC::MLDenseMatrixType);
   PRC::shared_ptr<PRC::MLSparseMatrixType> sparseA(new PRC::MLSparseMatrixType);
   Eigen::MatrixXd data;
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
   if (dataConfig.fileType == PRC::ADJACENCY_DATA)
   {
      std::cout << "Only works on point data." << std::endl;
      exit(-2);
   }

   if (!flag)
   {
      std::cerr << "Failed to read file " << graphFileName << " into matrix" <<  std::endl;
      exit(-3);
   }

   if (dataConfig.useSparseMatrix)
      *denseA = sparseA->toDense();

   for(int r=0; r< denseA->rows();++r)
   {
      for(int c=0; c<denseA->cols();++c)
      {
         fout << " " << denseA->coeff(r,c);
         if (denseA->coeff(r,c)>1.0)
         {
            std::cout << "!!!! similarity greater than 1 at A["<<r <<", "<<c<<"] = "<<denseA->coeff(r,c)<<std::endl;
            exit(-1);
         }
      }
      fout << "\n";
   }
   fout.close();

   return 0;
}

