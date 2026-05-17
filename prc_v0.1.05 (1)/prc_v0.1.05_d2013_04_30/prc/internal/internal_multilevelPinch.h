// This file is part of PRC, a C++ library for thin position clustering.
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

// \file  internal_multilevelPinch.h
//
// Last changed by = $Author: drh $
// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_MULTILEVELPINCH_H__
#define INTERNAL_MULTILEVELPINCH_H__

#ifndef MULTILEVELPINCH_H__
#include<prc/multilevelPinch.h>
#endif


#ifndef ORDEROBJECT_H__
#include<prc/OrderObject.h>
#endif


namespace internalPRC
{
   bool validateMatrix(PRC::MLDenseMatrixType &a,double threshold=1e-12);
   bool validateMatrix(PRC::MLSparseMatrixType &a,double threshold=1e-12);
   template<typename StorageKind> bool isSparse();
   template<> inline bool isSparse<Eigen::Sparse>(){return true;}
   template<> inline bool isSparse<Eigen::Dense>(){return false;}

   typedef Eigen::Block<Eigen::MatrixXd> BlockXd;
   const BlockXd  sliceTags(Eigen::MatrixXd &A,PRC::TagModeEnum mode);

   template<typename StorageKind> struct updateHelper
   {
      template<typename MatType> 
      static
         void generate(PRC::shared_ptr<MatType> &result, int curV,const PRC::shared_ptr<MatType> &prevA, const std::vector<int> omap);
   };

   template<> struct updateHelper<Eigen::Sparse>
   {
      template<typename MatType> 
      static
      void generate(PRC::shared_ptr<MatType> &result,int curV, const PRC::shared_ptr<MatType> &prevA, const std::vector<int> omap)
      {
//         std::cout << "generate sparse : " << curV << ": " << prevA->rows() << std::endl;
         assert(isSparse<typename MatType::StorageKind>() == true);
         std::vector<Eigen::Triplet<double> > tripletList;
         tripletList.reserve(prevA->nonZeros());
         for(int j=0; j < prevA->outerSize(); ++j)
         {
            for (typename MatType::InnerIterator it(*prevA,j); it; ++it)
            {
               if (omap[it.row()]==omap[it.col()])
                  continue; // no edges to self  ... should encode as the weight of the node
               if (it.value()>1e-14)
                  tripletList.push_back(Eigen::Triplet<double>(omap[it.row()],omap[it.col()],it.value()));
            }
         }
         result->resize(curV,curV);
         result->setZero();
         result->setFromTriplets(tripletList.begin(),tripletList.end());
      }
   };

   template<> struct updateHelper<Eigen::Dense>
   {
      template<typename MatType> 
      static
      void generate(PRC::shared_ptr<MatType> &result,int curV,const PRC::shared_ptr<MatType> &prevA, const std::vector<int> omap)
      {
         //std::cout << "generate dense : " << curV << ": " << prevA->rows() << std::endl;
         assert(isSparse<typename MatType::StorageKind>() == false);
         result->resize(curV,curV);
         result->setZero();
         for(int j=0; j < prevA->outerSize(); ++j)
         {
            for (typename MatType::InnerIterator it(*prevA,j); it; ++it)
            {
               if (omap[it.row()]==omap[it.col()])
                  continue; // no edges to self  ... should encode as the weight of the node

               if (it.value()>1e-14)
                  result->coeffRef(omap[it.row()],omap[it.col()]) = it.value();
            }
         }
      }
   };


inline
bool validateMatrix(PRC::MLDenseMatrixType &a,double threshold)
{
   bool flag = true;
   for(int r=0;r<a.rows();++r)
      for(int c=0;c<a.cols();++c)
         if ((fabs(a(r,c) -a(c,r))<threshold*(1+a.coeff(r,c))) || (a.coeff(r,c)<0))
         {
            return false;
         }
   return flag;
}

inline
   bool validateMatrix(PRC::MLSparseMatrixType &a, double threshold)
{
   bool flag = true;
   for(int r=0;r<a.rows();++r)
      for(int c=0;c<a.cols();++c)
         if ((fabs(a.coeff(r,c) - a.coeff(c,r)) > threshold*(1+a.coeff(r,c))) || (a.coeff(r,c)<0))
         {
            std::cout << "Failed at A(" << r <<","<<c<<")  =  " << a.coeff(r,c) <<" != " << a.coeff(c,r) << " || " << a.coeff(r,c) - a.coeff(c,r) << std::endl;
            return false;
         }
   return flag;
}
}


inline
const internalPRC::BlockXd  internalPRC::sliceTags(Eigen::MatrixXd &A,PRC::TagModeEnum mode)
{
   switch(mode)
   {
      case PRC::NO_TAGS: 
         return A.block(0,0,A.rows(),A.cols());
         break;
      case PRC::FRONT_TAGS: 
         return A.block(0,1,A.rows(),A.cols()-1);
      case PRC::REAR_TAGS: 
         return A.block(0,0,A.rows(),A.cols()-1);
      default:
         assert(false && "Slice needs to be specialed for each mode");
   }
   // should not reach here, but if we do just return the matrix.
   return A.block(0,0,A.rows(),A.cols());
}


template<typename MatType>
inline 
PRC::prcReturnStruct PRC::multilevelPRC(const PRC::shared_ptr<MatType> &A, Eigen::VectorXi &labels,int K,const PRC::prcPolicyStruct &policy)
{
   Eigen::VectorXi order;
   return multilevelPRC(A,order,labels,K,policy);
}
template<typename MatType>
inline 
PRC::prcReturnStruct PRC::multilevelPRC(const PRC::shared_ptr<MatType> &A, Eigen::VectorXi &order, Eigen::VectorXi &labels,int K,const PRC::prcPolicyStruct &policy)
{
   if (A == NULL)
   {
      std::cerr << "Non existence matrix A.  Aborting." << std::endl;
      return prcReturnStruct();
   }

   const int N = A->rows();
   if (order.size() == 0)
   {
      order.resize(N);
      for(int i=0; i<N;++i)
      {
        order[i] = i;
      }
      std::random_shuffle(order.data(),order.data()+N);
   }
   OrderObject myOrder;
   myOrder.setFrom(order);
   PRC::prcReturnStruct result = multilevelPRC(A,myOrder,labels,K,policy);
   myOrder.copyTo(order);
   return result;
}

template<typename MatType, typename V>
inline 
PRC::prcReturnStruct PRC::multilevelPRC(
      const PRC::shared_ptr<MatType> &A, 
      PRC::Ordering<V> &vorder, Eigen::VectorXi &labels, int K, const PRC::prcPolicyStruct &policy)
{

   std::cerr << "WARNING: multilevel PRC is undergoing revisions.  Do not use.  Or at least comment this out, recompile, and use at you own risk.\nExiting." <<std::endl;
   exit(-1);

   if (A == NULL)
   {
      std::cerr << "Non existence matrix A.  Aborting." << std::endl;
      return prcReturnStruct();
   }
   assert(A->rows() == A->cols());
   assert(K>1);
   prcCountsStruct countTotals;
   prcCountsStruct tmpCounts;
   prcReturnStruct prcCounts;

   if (A->rows() <= 5*K)
   {  // too small, don't do multilevel
      return PRC::pinchRatioClustering(*A,vorder,labels,K,policy);
   }

#ifdef HAVE_BENCH
   Eigen::BenchTimer timerA;
   Eigen::BenchTimer timerB;
   timerA.start();
#endif
   std::vector<shared_ptr<MatType> > sparseA;
   sparseA.push_back(A);
   std::vector< std::vector<int> > sparse_map;
   std::vector<int> randomorder;
   std::vector<int> omap;
   //bool usingSparse = internalPRC::isSparse<typename MatType::StorageKind>();
   long maxIter=0;
   int level = 0;
   double threshold = policy.tiloPolicy.tiloEpsilon;
//   std::cout << "Oringal A = \n"<< A->toDense() << std::endl;
//std::cout << "Original A dim = " << A->rows() << "x"<< A->cols() << " with "<<A->nonZeros() << std::endl;
   while ((sparseA.back()->outerSize() > 5*K) && (maxIter < 1000))
   {
      maxIter++;
      shared_ptr<MatType> prevA = sparseA.back();
      int N = prevA->outerSize();// dimension of previous
      omap.resize(N);
      std::fill(omap.begin(),omap.end(),-1);
      randomorder.resize(N);
      int curV = 0;
      for(int i=0;i<N;++i) 
         randomorder[i] = i;
      std::random_shuffle(randomorder.begin(),randomorder.end());
      for(int loopV =0; loopV < N; ++loopV)
      {
         int j = randomorder[loopV];
         if (omap[j] >=0)
            continue; // all ready processed

         int k = -1;
         double maxvalue = -1;

         for (typename MatType::InnerIterator it(*prevA,j); it; ++it)
         {
            int v = MatType::IsRowMajor ? it.col(): it.row();
            if ((omap[v] <0) && (it.value() > maxvalue))
            {
               maxvalue = it.value();
               k = v;
            }
         }
         if (k>=0)
         {
           // std::cout << "("<<j<<","<<k<<") ";
            omap[j] = curV;
            omap[k] = curV;
            curV++;
         }
      }
      if (curV > N/10.0)  // fraction should be in policy
      { // merged at least 1/10 of graph, so OK
         for(int j=0; j < N; ++j)
         {
            if (omap[j]<0)
            {
               omap[j] = curV;
               curV++;
            }
         }
      }
      else  // did not merge enough nodes, merge pairs of unassigned nodes
      {
         int x=-1;
         for(int j=0; j < N; ++j)
         {
            if(omap[j]<0)
            {
               if (x>=0)
               {
                  omap[x] = curV;
                  omap[j] = curV;
                  curV++;
                  x = -1;
               }
               else
                  x = j;
            }
         }
         if (x>=0)
         {
            omap[x] = curV;
            curV++;
         }
      }

//     std::cout << "\n   curV = " << curV << std::endl;
//std::cout << "omap = "; printStdVec(std::cout,omap); std::cout <<std::endl;
     shared_ptr<MatType>  Ap(new MatType);
     internalPRC::updateHelper<typename MatType::StorageKind>::generate(Ap,curV,prevA,omap);

     threshold *= 2; // increase threshold for each coarsen level
     if (!internalPRC::validateMatrix(*Ap, threshold))
     {
        std::cout << "Failed to validate Ap " << std::endl;
std::cout << "pushing back new A dim = " << Ap->rows() << "x"<< Ap->cols() << " with "<<Ap->nonZeros() << std::endl;
exit(-1);
     }
           
 //  std::cout << "pushing Ap = \n"<< Ap->toDense() << std::endl;
      sparseA.push_back(Ap);
      level++;
      sparse_map.push_back(omap);
   }
   
#ifdef HAVE_BENCH
   timerA.stop();
   std::cout << "LLLLLL  Coarsing graphs took : "<<timerA.value() <<std::endl;
   timerA.reset();
   timerA.start();
#endif
   std::cout << "\n\nRunning TILO's"<<std::endl;

   // now run TILO

   Eigen::RowVectorXd degrees;
   std::vector<std::vector<int> > invmap;
   std::vector<OrderObject> tmpOrderObjs;
   tmpOrderObjs.resize(level);
   Eigen::VectorXi tmpOrder;
   for(int curLevel =level-1; curLevel>=0;curLevel--)
   {
#ifdef HAVE_BENCH
      timerB.reset();
      timerB.start();
#endif

      shared_ptr<MatType> curA = sparseA[curLevel];
      degrees.resize(curA->cols());
      for(int i=0; i<curA->cols();++i)
         degrees[i] = curA->col(i).sum();
      tmpOrder.resize(curA->cols());
      if (curLevel == level-1)
      { // random initial order
         for(int i=0; i<curA->cols();++i)
              tmpOrder[i] = i;
         std::random_shuffle(tmpOrder.data(),tmpOrder.data()+tmpOrder.size());
      }
      else
      { // build order from lower level
         invmap.clear();
         int prevLevel = curLevel+1;
         invmap.resize(sparseA[prevLevel]->cols());
         assert(long(curLevel) < long(sparse_map.size()));
         for(int i=0; i<curA->cols();++i)
         {
            assert(long(sparse_map[curLevel][i]) < long(invmap.size()));
            assert(sparse_map[curLevel][i] >= 0);
            invmap[sparse_map[curLevel][i]].push_back(i);
         }
         int tmpLoc=0;
         for(int i=0;i<tmpOrderObjs[prevLevel].size();++i)
         {
            for(std::vector<int>::const_iterator p=invmap[i].begin(); p != invmap[i].end();++p)
            {
               tmpOrder[tmpLoc++] = *p;
            }
         }
         assert(tmpLoc == curA->cols());
      }
      tmpOrderObjs[curLevel].setFrom(tmpOrder);
      if (curLevel > 0)
      {
         tmpCounts = TILO(tmpOrderObjs[curLevel],*curA,degrees,policy.tiloPolicy);
         countTotals.numberOfShifts += tmpCounts.numberOfShifts;
         countTotals.numberOfInversions += tmpCounts.numberOfInversions;
         countTotals.numberOfIterations += tmpCounts.numberOfIterations;
      }
      else
      {
         assert(vorder.size() == tmpOrderObjs[0].size() && "Invalid virtual order in multilevel pinch ratio clustering");
         vorder.setFrom(tmpOrderObjs[0].VData());
         prcCounts = pinchRatioClustering(*A,vorder,labels,K,policy);
         prcCounts.counts.numberOfShifts  += countTotals.numberOfShifts; 
         prcCounts.counts.numberOfInversions +=countTotals.numberOfInversions; 
         prcCounts.counts.numberOfIterations += countTotals.numberOfIterations;
      }
#ifdef HAVE_BENCH
      timerB.stop();
      std::cout << "MMMMMM  On level : "<< curLevel<< " : CPU time : " << timerB.value() << " : "; tmpCounts.Print(std::cout," ",",");
      std::cout << " :  on coarse graph size " << curA->rows()<<"x"<<curA->cols() << " with "<<curA->nonZeros() << " nonzeros"<<std::endl;
#endif
   }
#ifdef HAVE_BENCH
   timerA.stop();
   std::cout << "NNNNNN TILO over all levels took : "<<timerA.value() <<std::endl;
#endif
   return prcCounts;
}

#endif
