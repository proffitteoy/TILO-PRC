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

/// \file  internal_pinch.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef INTERNAL_PINCH_H__
#define INTERNAL_PINCH_H__
#include<cassert>
#include<iterator>
#include<queue>
#include<list>
#include<algorithm>
#include<functional>

#ifndef PINCH_H__
#include<prc/pinch.h>
#endif


#ifndef VIRTUALORDEROBJECT_H__
#include<prc/VirtualOrderObject.h>
#endif


namespace PRC
{
   struct pqstruct
   {
      double quality;
      int loc;
      VirtualOrderObject v;
      prcMetricValues mvalues;
      bool operator<(const pqstruct & other) const
      { return quality < other.quality;}
      pqstruct():quality(-1),loc(-1),mvalues() {}
      pqstruct(double val, int index, VirtualOrderObject &order, const prcMetricValues &m):quality(val),loc(index),v(order),mvalues(m) {}
   };

   template<typename T> double calcNCut(const SBase<T> &a, Eigen::VectorXi &labels,int NumPart);
   template<typename T, typename F, typename V> std::pair<long,long> doShifts(const BoundaryObject::MarksType &m, Ordering<V> &order, const BoundaryObject &b, const SBase<T> &a, double epsilon);
   template<typename T, typename F, typename V> std::pair<long,long> doRShifts(const BoundaryObject::MarksType &m, Ordering<V> &order, const BoundaryObject &b, const SBase<T> &a, double epsilon);

  template<typename T, typename V1, typename V2>
  prcMetricValues findSplitLocation(Ordering<V1> &curOrder,long &loc,double &value,const SBase<T> &a, Ordering<V2> &vorder, prcMetricEnum metric, bool evalAllMetrics=false );
}


template<typename T> 
inline 
PRC::prcReturnStruct PRC::pinchRatioClustering(const SBase<T> &A, Eigen::VectorXi &labels,int K,const prcPolicyStruct &policy)
{
   Eigen::VectorXi order;
   return pinchRatioClustering(A, order, labels, K, policy);
}

template<typename T> 
inline 
PRC::prcReturnStruct PRC::pinchRatioClustering(const SBase<T> &A, Eigen::VectorXi &order, Eigen::VectorXi &labels, int K, const PRC::prcPolicyStruct &policy)
{
   const int N = A.rows();
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
   PRC::prcReturnStruct result = pinchRatioClustering(A, myOrder, labels, K, policy);
   myOrder.copyTo(order);
   return result;
}

template<typename T, typename V> 
inline 
PRC::prcReturnStruct PRC::pinchRatioClustering(const SBase<T> &A, Ordering<V> &vorder, std::vector<int> &labels, int K, const PRC::prcPolicyStruct &policy)
{
   // for now, just copy to/from eigen vector
   Eigen::VectorXi b;
   PRC::prcReturnStruct res = PRC::pinchRatioClustering(A,vorder,b,K,policy);
   labels.resize(b.size());
   std::copy(b.data(),b.data()+b.size(), 
         //labels.data()
         &(labels[0])
         );
   return res;
}

template<typename T, typename V> 
inline 
PRC::prcReturnStruct PRC::pinchRatioClustering(const SBase<T> &A, Ordering<V> &vorder, Eigen::VectorXi &labels, int K, const PRC::prcPolicyStruct &policy)
{

#ifdef HAVE_BENCH
   Eigen::BenchTimer timerA;
   Eigen::BenchTimer timerB;
   Eigen::BenchTimer timerC;
   timerA.start();
   timerB.start();
#endif


   assert(A.rows() == A.cols());
   assert(K>1);
   const int N = A.rows();
   prcCountsStruct countTotals;
   prcCountsStruct tmpCounts;
   prcReturnStruct return_results;

   if (vorder.size() < N)
   {
      std::cerr << "Invalid Order Object.  Not large enough for matrix A." << std::endl;
      // note: in the k-way splits, virtual order size may not equal matrix size
      exit(-3);
   }

#if VERBOSE_PINCH > 0
   std::cout << "Starting pinch ratio clustiner with initial order = "<< vorder.Print() << std::endl;
#endif

   tmpCounts = TILO(vorder,A,policy.tiloPolicy);
   countTotals.numberOfShifts += tmpCounts.numberOfShifts;
   countTotals.numberOfInversions += tmpCounts.numberOfInversions;
   countTotals.numberOfIterations += tmpCounts.numberOfIterations;
#ifdef HAVE_BENCH
   timerA.stop();
   std::cout << "AAAAAA Initial TILO took :  "<<timerA.value() <<" : cpu seconds with : "; tmpCounts.Print(std::cout," ",",");std::cout<<std::endl;
#endif
   if (policy.prcRefineTILO) 
   {
#ifdef HAVE_BENCH
      timerA.reset();
      timerA.start();
#endif
      tmpCounts = RefineTILO(vorder,A,policy.tiloPolicy);
      countTotals.numberOfShifts += tmpCounts.numberOfShifts;
      countTotals.numberOfInversions += tmpCounts.numberOfInversions;
      countTotals.numberOfIterations += tmpCounts.numberOfIterations;
#ifdef HAVE_BENCH
      timerA.stop();
      std::cout << "BBBBBB Refining TILO took : "<<timerA.value() <<" : cpu seconds with  : ";tmpCounts.Print(std::cout," ",","); std::cout <<std::endl;
#endif
   }

#if VERBOSE_PINCH > 0
   std::cout << "Finished pinch ratio clustering initial TILO run with order "<< vorder.Print()  << std::endl;
   std::cout << "After TILO boundary  " << vorder.boundary().Print()<< std::endl;
   std::cout << "and marks = "<< PrintMarks(vorder.marks()) << std::endl;
#endif

#ifdef HAVE_BENCH
      timerC.start();
#endif


   long loc=-1;
   double value=-1;
   std::priority_queue<pqstruct> pqueue;
   VirtualOrderObject rvorder( & (vorder.derived()) );
   OrderObject tmpOrder;
   prcMetricValues mvalues_accum;
   const bool ReturnRO = policy.prcRecurseTILO && policy.prcReturnRecursiveOrder;
   if (ReturnRO)
   {  // rvorder changes will change order in vorder
      rvorder.boundary() = vorder.boundary();
      rvorder.marks() = vorder.marks();
   }
   else
   {
      tmpOrder = vorder.derived();
      // rvorder changes will change order in tmpOrder ... which will be discarded
      rvorder = VirtualOrderObject(&tmpOrder);
      rvorder.boundary() = vorder.boundary();
      rvorder.marks() = vorder.marks();
   }

   if (policy.prcRecurseTILO)
   {
     prcMetricValues mvals=  findSplitLocation(rvorder,loc,value,A,rvorder,policy.metric,policy.prcEvalAllMetrics);

#if VERBOSE_PINCH > 20
   std::cout << "------------------------------------------------------------\nrvorder First split at loc = " << loc << ", with value =  "<<value <<std::endl;
#endif
      pqstruct tmppq(-1*value,loc,rvorder,mvals);
      pqueue.push(tmppq);
      while(long(pqueue.size()) < long(K))
      {
         const pqstruct &cur = pqueue.top();

#if VERBOSE_PINCH > 20
   std::cout << "VOrder of cur top = " << cur.v.Print() << std::endl;
#endif

         if (cur.quality > 0)
            break;  // no more posible split locations
         if (cur.loc < 0)
            break;  // not posible to split
//         prSplits.push_back(std::pair<double,prcMetricValues>(-1*cur.quality, cur.mvalues ));
#if VERBOSE_PINCH > 20
   std::cout << "SPLITTING at "<<cur.loc << " with quality " << cur.quality << " and metric values "<< cur.mvalues.Print(" ",",")<<std::endl;
#endif
         VirtualOrderObject tmpA;
         VirtualOrderObject tmpB;
         cur.v.split(cur.loc,tmpA,tmpB,policy.reverseOrderOnSplit);

         return_results.mvalues.push_back(cur.mvalues);
         pqueue.pop(); // may want to store in an heirarchy
#ifdef HAVE_BENCH
         timerA.reset();
         timerA.start();
#endif

#if VERBOSE_PINCH > 80
   std::cout << "Branch A, calling TILO on tmpA =  "<<tmpA.Print() <<std::endl;
#endif
         tmpCounts = TILO(tmpA,A,policy.tiloPolicy); // use global degrees?
         countTotals.numberOfShifts += tmpCounts.numberOfShifts;
         countTotals.numberOfInversions += tmpCounts.numberOfInversions;
         countTotals.numberOfIterations += tmpCounts.numberOfIterations;
         if (policy.prcRefineTILO) 
         {
            tmpCounts = RefineTILO(tmpA,A,policy.tiloPolicy); // use global degrees?
            countTotals.numberOfShifts += tmpCounts.numberOfShifts;
            countTotals.numberOfInversions += tmpCounts.numberOfInversions;
            countTotals.numberOfIterations += tmpCounts.numberOfIterations;
         }
#
#ifdef HAVE_BENCH
      timerA.stop();
      std::cout << "CCCCCC rec A on size "<<tmpA.size() << " TILO took : "<<timerA.value() <<" : cpu seconds with : ";tmpCounts.Print(std::cout," ",","); std::cout << std::endl;
#endif
         prcMetricValues mvA = findSplitLocation(tmpA,loc,value,A,tmpA,policy.metric,policy.prcEvalAllMetrics);

#if VERBOSE_PINCH > 20
   std::cout << "Branch A, Found split location " << loc << " with value " << value << " form order "<< tmpA.Print() << std::endl;
#endif

         if (!ReturnRO)
         {  
            tmpA.boundary().resize(0,0);
            tmpA.marks().resize(0);
         }

         pqstruct tmppqA(-1*value,loc,tmpA,mvA);

#if VERBOSE_PINCH > 100
   std::cout << "pushing A :loc,-1*quality ="<< loc << ", "<<-1*value <<std::endl;
   std::cout << "VOrder of A = "<< tmpA.Print() << std::endl;
#endif

         pqueue.push(tmppqA);

#ifdef HAVE_BENCH
         timerA.reset();
         timerA.start();
#endif

#if VERBOSE_PINCH > 80
   std::cout << "Branch B, calling TILO on tmpB =  "<<tmpB.Print() <<std::endl;
#endif
         tmpCounts = TILO(tmpB,A,policy.tiloPolicy); // use global degrees?
         countTotals.numberOfShifts += tmpCounts.numberOfShifts;
         countTotals.numberOfInversions += tmpCounts.numberOfInversions;
         countTotals.numberOfIterations += tmpCounts.numberOfIterations;
         if (policy.prcRefineTILO) 
         {
            tmpCounts = RefineTILO(tmpB,A,policy.tiloPolicy); // use global degrees?
            countTotals.numberOfShifts += tmpCounts.numberOfShifts;
            countTotals.numberOfInversions += tmpCounts.numberOfInversions;
            countTotals.numberOfIterations += tmpCounts.numberOfIterations;
         }

#ifdef HAVE_BENCH
      timerA.stop();
      std::cout << "CCCCCC rec B on size "<<tmpB.size() << " TILO took : "<<timerA.value() <<" :  cpu seconds with :  ";tmpCounts.Print(std::cout," ",","); std::cout << std::endl;
#endif
         prcMetricValues mvB=findSplitLocation(tmpB,loc,value,A,tmpB,policy.metric,policy.prcEvalAllMetrics);

#if VERBOSE_PINCH > 20
   std::cout << "Branch B: Found split location " << loc << " with value " << value << " form order "<< tmpB.Print()<<std::endl;
#endif

         if (!ReturnRO) 
         {
            tmpB.boundary().resize(0,0);
            tmpB.marks().resize(0);
         }
         pqstruct tmppqB(-1*value,loc,tmpB,mvB);
         pqueue.push(tmppqB);

#if VERBOSE_PINCH > 100
   std::cout << "pushing B :loc,-1*quality ="<< loc << ", "<<-1*value <<std::endl;
   std::cout << "VOrder of B = "<< tmpB.Print() << std::endl;
#endif
      }

   }
   else
   { 
      prcMetricValues mvals = findSplitLocation(rvorder,loc,value,A,vorder,policy.metric,policy.prcEvalAllMetrics);

#if VERBOSE_PINCH > 20
      std::cout << "===========================================================\nvorder First split at loc = " << loc << " with value " << value <<  std::endl;
#endif

      pqstruct tmppq(-1*value,loc,rvorder,mvals);
      pqueue.push(tmppq);
      // don't rerun TILO on components
      while(long(pqueue.size()) < long(K))
      {
         const pqstruct &cur = pqueue.top();
         if (cur.quality > 0)
            break;  // no more posible split locations
         if (cur.loc < 0)
            break;  // not posible to split
#if VERBOSE_PINCH > 20
   std::cout << "SPLITTING at "<<cur.loc  << " with quality " << cur.quality << " and metric values "<< cur.mvalues.Print(" ",",")<<std::endl;
#endif
//         prSplits.push_back(std::pair<double,prcMetricValues>(-1*cur.quality, cur.mvalues));
         VirtualOrderObject tmpA;
         VirtualOrderObject tmpB;
         cur.v.split(cur.loc,tmpA,tmpB,false);

         return_results.mvalues.push_back(cur.mvalues);
         pqueue.pop(); // may want to store in an heirarchy
         prcMetricValues mvA = findSplitLocation(tmpA,loc,value,A,vorder,policy.metric,policy.prcEvalAllMetrics);
#if VERBOSE_PINCH > 20
   std::cout << "tmpA First split at loc = " << loc << " with value " << value <<  std::endl;
#endif
         tmpA.boundary().resize(0,0);
         tmpA.marks().resize(0);
         pqstruct tmppqA(-1*value,loc,tmpA,mvA);
         pqueue.push(tmppqA);
         prcMetricValues mvB = findSplitLocation(tmpB,loc,value,A,vorder,policy.metric,policy.prcEvalAllMetrics);
#if VERBOSE_PINCH > 20
   std::cout << "tmpB First split at loc = " << loc << " with value " << value <<  std::endl;
#endif
         tmpB.boundary().resize(0,0);
         tmpB.marks().resize(0);
         pqstruct tmppqB(-1*value,loc,tmpB,mvB);
         pqueue.push(tmppqB);
      }
   }
   labels.resize(N);
   labels.fill(-1);
   int tag = 0;
   while(!pqueue.empty())
   {
      const pqstruct &cur = pqueue.top();
#if VERBOSE_PINCH > 20
   std::cout << "USING from queue (not splitted) "<<cur.loc << " with quality = " << -1* cur.quality <<" from values "<< cur.mvalues.Print(" ",",")<<std::endl;
#endif
      for(int j=0; j< cur.v.size(); ++j)
         labels(cur.v(j))= tag;

      if (ReturnRO)
      {
         int s = cur.v.baseStart();
         std::copy(cur.v.boundary().data(), cur.v.boundary().data()+cur.v.boundary().size(), vorder.boundary().data()+s);
      }

      pqueue.pop();
      tag++;
   }

#ifdef HAVE_BENCH
   timerC.stop();
   timerB.stop();
   std::cout << "DDDDDD K-way splitting took : "<<timerC.value() <<" :  cpu seconds."<<std::endl;
   std::cout << "EEEEEE pinchRatioClustering took :   "<<timerB.value() << " : cpu seconds  with :  "; countTotals.Print(std::cout," ",","); std::cout <<std::endl;
#endif

#if VERBOSE_PINCH > 20
   std::cout << " finished pinch ratio clustering with  counts = "<< countTotals.Print() <<std::endl;
#endif
   return_results.counts = countTotals;
   return return_results;
}


template<typename T, typename V> 
inline void PRC::calcBoundaries(PRC::BoundaryObject &b, const SBase<T> &a, const Ordering<V> &order)
{
   b.resize(order.size(),order.getPrefixDegree(a));
   for(int  i =0; i < b.size(); ++i)
   {
      b(i) = order.slope(i-1,i,a) + b(i-1);
   }
}

template<typename T, typename V> 
inline std::pair<long,long> PRC::doShifts(const BoundaryObject::MarksType &m, Ordering<V> &order, const BoundaryObject &b, const SBase<T> &a, double epsilon)
{

#if VERBOSE_PINCH > 60
   std::cout << "Starting doShifts " << std::endl;
#endif

#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
   Eigen::BenchTimer timerDS1;
   Eigen::BenchTimer timerDS2;
#endif


   long count = 0;
   long inversionCount = 0;
   int prevS = -1;
   for(PRC::BoundaryObject::MarksType::size_type z=0; z < m.size(); ++z)
   {
      if (m[z].type == FlatStruct::LocalMin)
         continue;

#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
      timerDS1.start();
#endif

#if VERBOSE_PINCH > 60
   std::cout << "On Mark "<< m[z].Print() << std::endl;
#endif
      int y = 0;
      int i = m[z].start; // start of max flat
      int upperLimit = order.size()-1; 
      if (i >= upperLimit)
         i = upperLimit-1; // can not shift at location i+1, so try at i
      int j = m[z].stop;  // end of max flat
      int prevMin = -1; 
      int nextMin = b.size()-1; 
      if (z>0)
      {
         prevMin = m[z-1].stop;
         assert(m[z-1].type == FlatStruct::LocalMin && "Error: two adjacent local max in mark vector");
      }
      if (z+1<m.size())
      {
         nextMin = m[z+1].start;
         assert(m[z+1].type == FlatStruct::LocalMin && "Error: two adjacent local max in mark vector");
      }
      double sAi = b(i+1)-b(i);   
      double sBj = b(j)-b(j-1);  // boundary object handles -1 indexing
#if VERBOSE_PINCH > 60
      std::cout << "     sAi ="<<sAi  << std::endl;
      std::cout << "     sBj ="<<sBj  << std::endl;
#endif
      // search for good swap/shift
      double yval = epsilon*(1+fabs(sAi));
      double ytmp = epsilon;
      double eps_sqrt = sqrt(epsilon);
      double orig_yval = yval;
#if VERBOSE_PINCH > 60
      std::cout << "     1st branch : upperLimit = "<< upperLimit << ", i+1 = " << i+1 << ", prevMin+1 = "<< prevMin+1<< ", nextMin = " << nextMin <<std::endl;
#endif
      for (int k = prevMin+1; k <=i;++k)
      {
#if VERBOSE_PINCH > 60
         std::cout << " AAA       at k="<<k<<" , i =  " << i<< ", prevMin =  "<< prevMin << ", upperLimit = " << upperLimit <<std::endl;
#endif


         double tmp = order.slope(i,k,a);
         double tmp2 = tmp - sAi -2 * a.getCoeff(order[k],order[i+1]);
#if VERBOSE_PINCH > 60
         std::cout << "        at k="<<k<<" : " << tmp << " , " << tmp2 <<  "  || " << y << ","<<yval <<std::endl;
#endif

         if (((tmp >ytmp) && (tmp2  >yval)) ||
             ((tmp >ytmp) && (ytmp < eps_sqrt)&& (tmp2  >orig_yval)))
         {
            y = k;
            ytmp = fabs(tmp);
            yval= tmp2;
#if VERBOSE_PINCH > 60
            std::cout << "        1st Branch: setting y = "<<y << " with val = " << yval << std::endl;
            std::cout << "        i="<<i<<", sAi="<<sAi<<" at k="<<k<<" : tmp =  " << tmp << " ,  tmp2 = " << tmp2  <<  "  || " << y << ","<<yval <<std::endl;
#endif
         }
      }

#if VERBOSE_PINCH > 60
      std::cout << "     2nd branch"<<std::endl;
#endif
      for (int k = j+1; k <=std::min(nextMin,upperLimit);++k)
      {
         double tmp = order.slope(j,k,a);
         double tmp2 = -tmp + sBj -2 * a.getCoeff(order[k],order[j]) ;
#if VERBOSE_PINCH > 60
         std::cout << "        at k="<<k<<" : tmp = " << tmp << " , tmp2 =" << tmp2  <<  "  || " << y << ","<<yval <<std::endl;
#endif
         if (((tmp <-ytmp) && (tmp2 >yval)) ||
             ((tmp <-ytmp)&&(ytmp <eps_sqrt) && (tmp2 >orig_yval)))
         {
            y = k;
            ytmp = fabs(tmp);
            yval= tmp2;
#if VERBOSE_PINCH > 60
            std::cout << "        2nd Branch : setting y = "<<y << " with val = " << yval <<   std::endl;
            std::cout << "        j="<<j<<", sBj ="<<sBj<<" at K="<<k<<" : " << tmp << " , " << tmp2 <<  "  || " << y << ","<<yval <<std::endl;
#endif
         }
      }

#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
      timerDS1.stop();
      timerDS2.start();
#endif


      // apply shift
      if (yval >orig_yval)
      {  
#if VERBOSE_PINCH > 60
         std::cout << "     Found possible shift location at " << y << " with value " << yval << ", i = " << i << std::endl;
#endif

         if (y <= i)
         {
            if (y == prevS)
            {
#if VERBOSE_PINCH > 60
               std::cout << "        y== prevS "<<prevS <<".  skipping." << std::endl;
#endif
               continue; // overlap with previous shift
            }

            prevS = i+1;
#if VERBOSE_PINCH > 60
std::cout << "     Shifting  y="<< y << ",o(y)= "<<order[y]<<" and i+1="<< i+1<< " o(i+1)= "<<order[i+1]<<" with val = " << yval << std::endl;
#endif

             order.applyShift(y,i+1,a);
//             int otmp = order[y];
//            for(int x=y; x<i+1;++x)
//               order.setAt(x, order[x+1]);
//            order.setAt(i+1,otmp);
            count++;
            inversionCount += i+1-y;
         }
         else
         {
            if (y> upperLimit)
            {
#if VERBOSE_PINCH > 60
               std::cout << "        y = " << y <<" > upperLimit "<<upperLimit <<".  skipping." << std::endl;
#endif
               continue; 
            }

            if (j == prevS)
            {
#if VERBOSE_PINCH > 60
               std::cout << "        y== prevS "<<prevS <<".  skipping." << std::endl;
#endif
               continue; // overlap with previous shift
            }

            prevS = y;
#if VERBOSE_PINCH > 60
std::cout << "     Shifting  y="<< y << ",o(y)= "<<order[y]<<" and j="<< j<< " o(j)= "<<order[j]<<" with val = " << yval << std::endl;
#endif
            order.applyShift(y,j,a);
//            int otmp = order[y];
//            for(int x=y; x>j;--x)
//            {
//               order.setAt(x,order[x-1]);
//            }
//            order.setAt(j,otmp);
            count++;
            inversionCount += y-j;
         }
      }

#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
      timerDS2.stop();
#endif

   }
#if VERBOSE_PINCH > 60
   std::cout << "Finished doShifts: shift count = " << count << ", inversion count = "<< inversionCount << std::endl;
#endif

#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
   std::cout << "DDDDD doshift search totals = " << timerDS1.total() << ", shift = " << timerDS2.total() << std::endl;
#endif

   return std::make_pair(count,inversionCount);
}

template<typename T, typename V> 
inline 
PRC::prcCountsStruct PRC::RefineTILO( Ordering<V> &order,const SBase<T> &A, const tiloPolicyStruct &policy)
{
#if VERBOSE_PINCH > 50
      std::cout << "Starting Refine TILO " << std::endl;
#endif

   int loopCount=0;
   long flag = 1;
   long shiftCount = 0;
   long inversionCount = 0;
   std::pair<long,long> counts;
   double cureps = policy.tiloEpsilon;


#ifdef PINCH_VERIFY_LEX
   long lexCheckInterval = 1;
   std::vector<double> curW(order.size());
   std::vector<double> prevW(order.size());
   PRC::calcBoundaries(order.boundary(),A,order);
   for(int i=0;i<order.size();++i)
   {
      curW[i] = order.boundary()(i);
      prevW[i] = order.boundary()(i);
   }
   std::sort(curW.begin(),curW.end(),std::greater<double>());
   std::sort(prevW.begin(),prevW.end(),std::greater<double>());
#endif

   while(flag>0 && loopCount<policy.maxIterations)
   {

#if VERBOSE_PINCH > 50
   std::cout << "      On RefineTILO iteration " << loopCount << std::endl;
#endif

      counts = order.refineOrder(A,cureps);
      flag = counts.first;
      shiftCount += counts.first;
      inversionCount += counts.second;

#if VERBOSE_PINCH > 50
   std::cout << "         flag = " << bool(flag > 0) << ", after update, order = "<<order.Print() << std::endl;
#endif
 
#ifdef PINCH_VERIFY_LEX
   if (((loopCount % lexCheckInterval)==0)&& flag)
   {
      std::copy(curW.begin(),curW.end(),prevW.begin());
      PRC::calcBoundaries(order.boundary(),A,order);

      for(int i=0;i<order.size();++i)
         curW[i] = order.boundary()(i);
      std::sort(curW.begin(),curW.end(),std::greater<double>());
      bool vlexFlag = false;
      int badloc = -1;
      for(int i=0;i<order.size();++i)
      {
         if ( (prevW[i] - curW[i]) <= -1*(cureps*(1+prevW[i])))
         {
            std::cout << "PrevW < curW" << std::endl;
            badloc = i;
            break;
         }
         else if (( prevW[i] - curW[i] )>=cureps*(1+prevW[i]))
         {
            vlexFlag = true;
            break;
         }
      }
      if (!vlexFlag )
      {
         std::cout << "\ncureps = " << cureps << std::endl;
            std::cout << "ERROR: current Boundary is not less than previous boundary:\n loopcount = "<< loopCount <<", shfitCount = " << shiftCount <<",  invCount = " << inversionCount<< " at location " << badloc;
            if (badloc>=0)
               std::cout << "\n with diff = " << curW[badloc] -prevW[badloc] << " from " << curW[badloc] << "-"<<prevW[badloc]<<  " || " <<-1*policy.tiloEpsilon*(1+prevW[badloc]) <<std::endl;
            else
               std::cout << " boundary is the same " << std::endl;
            std::cout << std::endl << "Prev W = ";
            std::copy(prevW.begin(),prevW.end(), std::ostream_iterator<double>(std::cout," "));
            std::cout << std::endl << "Cur W  = ";
            std::copy(curW.begin(),curW.end(), std::ostream_iterator<double>(std::cout," "));
            std::cout << std::endl;
   std::cout << "Current order = " << order.Print()<<  std::endl;
   std::cout << "      Local Max Marks = "<< PrintMarks(order.marks()) << std::endl;
            std::cout << "cur  boundary = " << order.boundary().Print(); 
            if (cureps > 1e-5)
            {
               std::cout << "Warning: increase tilo epsilon greater than 1e-5.  Please check validate data matrix.\n exiting." << std::endl;
               exit(-1);
            }
            cureps *= 16;
            std::cout << "\n\nincrease cureps to " << cureps << std::endl;
      }
   }
#endif


      ++loopCount;
   }
assert((loopCount < policy.maxIterations) && "Reached max iteration limit in TILO");

#if VERBOSE_PINCH > 50
   std::cout << "     Finished RefineTILO, shiftCount = "<<shiftCount<<", inversionCount = "<<inversionCount<<", loopCount = "<< loopCount << std::endl;
#endif
   return prcCountsStruct(shiftCount,inversionCount,loopCount);
}


template<typename T, typename V> 
inline 
PRC::prcCountsStruct PRC::TILO( Ordering<V> &order,const SBase<T> &A,  const tiloPolicyStruct &policy)
{

#if VERBOSE_PINCH > 50
      std::cout << "Starting TILO " << std::endl;
#endif

   int loopCount=0;
   long flag = 1;
   long shiftCount = 0;
   long inversionCount = 0;
   std::pair<long,long> counts;
   double cureps = policy.tiloEpsilon;


#ifdef PINCH_VERIFY_LEX
   long lexCheckInterval = 1;
   std::vector<double> curW(order.size());
   std::vector<double> prevW(order.size());
   PRC::calcBoundaries(order.boundary(),A,order);
   for(int i=0;i<order.size();++i)
   {
      curW[i] = order.boundary()(i);
      prevW[i] = order.boundary()(i);
   }
   std::sort(curW.begin(),curW.end(),std::greater<double>());
   std::sort(prevW.begin(),prevW.end(),std::greater<double>());
#endif

   while(flag>0 && loopCount<policy.maxIterations)
   {

#if VERBOSE_PINCH > 50
   std::cout << "      On TILO iteration " << loopCount << std::endl;
#endif


      counts = order.updateOrder(A,cureps);
      flag = counts.first;
      shiftCount += counts.first;
      inversionCount += counts.second;

#if VERBOSE_PINCH > 50
   std::cout << "         flag = " << bool(flag > 0) << ", after update, order = "<<order.Print() << std::endl;
#endif
   
#ifdef PINCH_VERIFY_LEX
   if (((loopCount % lexCheckInterval)==0)&& flag)
   {
      std::copy(curW.begin(),curW.end(),prevW.begin());
      PRC::calcBoundaries(order.boundary(),A,order);

      for(int i=0;i<order.size();++i)
         curW[i] = order.boundary()(i);
      std::sort(curW.begin(),curW.end(),std::greater<double>());
      bool vlexFlag = false;
      int badloc = -1;
      for(int i=0;i<order.size();++i)
      {
         if ( (prevW[i] - curW[i]) <= -1*(cureps*(1+prevW[i])))
         {
            std::cout << "PrevW < curW" << std::endl;
            badloc = i;
            break;
         }
         else if (( prevW[i] - curW[i] )>=cureps*(1+prevW[i]))
         {
            vlexFlag = true;
            break;
         }
      }
      if (!vlexFlag )
      {
         std::cout << "\ncureps = " << cureps << std::endl;
            std::cout << "ERROR: current Boundary is not less than previous boundary:\n loopcount = "<< loopCount <<", shfitCount = " << shiftCount <<",  invCount = " << inversionCount<< " at location " << badloc;
            if (badloc>=0)
               std::cout << "\n with diff = " << curW[badloc] -prevW[badloc] << " from " << curW[badloc] << "-"<<prevW[badloc]<<  " || " <<-1*policy.tiloEpsilon*(1+prevW[badloc]) <<std::endl;
            else
               std::cout << " boundary is the same " << std::endl;
            std::cout << std::endl << "Prev W = ";
            std::copy(prevW.begin(),prevW.end(), std::ostream_iterator<double>(std::cout," "));
            std::cout << std::endl << "Cur W  = ";
            std::copy(curW.begin(),curW.end(), std::ostream_iterator<double>(std::cout," "));
            std::cout << std::endl;
   std::cout << "Current order = " << order.Print() << std::endl;
   std::cout << "      Local Max Marks = "<< PrintMarks(order.marks()) << std::endl;
            std::cout << "cur  boundary = "<< order.boundary().Print(); 
            if (cureps > 1e-5)
            {
               std::cout << "Warning: increase tilo epsilon greater than 1e-5.  Please check validate data matrix.\n exiting." << std::endl;
               exit(-1);
            }
            cureps *= 16;
            std::cout << "\n\nincrease cureps to " << cureps << std::endl;
      }
   }
#endif
      ++loopCount;
   }
assert((loopCount < policy.maxIterations) && "Reached max iteration limit in TILO");


#if VERBOSE_PINCH > 50
   std::cout << "     Finished RefineTILO, shiftCount = "<<shiftCount<<", inversionCount = "<<inversionCount<<", loopCount = "<< loopCount << std::endl;
#endif
   return prcCountsStruct(shiftCount,inversionCount,loopCount);
}

template<typename T, typename V1, typename V2>
inline
PRC::prcMetricValues PRC::findSplitLocation(PRC::Ordering<V1> &curOrder,long &loc,double &value,const SBase<T> &a, PRC::Ordering<V2> &vorder,prcMetricEnum metric, bool evalAllMetrics)
{
   prcMetricValues results;
   //double bestR = -1*std::numeric_limits<double>::max();
   double bestR = std::numeric_limits<double>::max();
   double bestD = -1*std::numeric_limits<double>::max();
   long bestIndex = -1;
   long curStart = curOrder.baseStart() - vorder.baseStart();
   long curStop = curOrder.baseStart()+curOrder.size()-1 - vorder.baseStart();
#if VERBOSE_PINCH > 60
std::cout << "----------------------- Finding Splits : order size() = " << curOrder.size() << ", curStart = " << curStart << ", curStop = " << curStop <<  std::endl;
#endif
   for(BoundaryObject::MarksType::size_type z=0; z<vorder.marks().size(); ++z)
   {
#if VERBOSE_PINCH > 60
      std::cout << "   on z= "<<z<<"  mark "<< vorder.marks()[z].Print() << std::endl;
#endif
      if (vorder.marks()[z].type == FlatStruct::LocalMax)
         continue;
      if (vorder.marks()[z].start >= curStop)
         continue;
       if (vorder.marks()[z].stop  <= curStart)
         continue;
       if (vorder.marks()[z].start  == curStart)
         continue;
            
      double local_min_cut = vorder.boundary()(vorder.marks()[z].start);
#if VERBOSE_PINCH > 60
      std::cout << "   local_min_cut = " << local_min_cut << std::endl;
#endif
      double am = local_min_cut;
      long ax = z;
      for(long x = long(z)-1; x>=0; --x)
      {
//         if ((vorder.marks()[x].type == FlatStruct::LocalMin) && (vorder.boundary()(vorder.marks()[x].start) <= local_min_cut))
//            break;

         if (vorder.marks()[x].start  <= curStart)
            break;

         if ((vorder.marks()[x].type == FlatStruct::LocalMin))
            continue;
         if (vorder.boundary()(vorder.marks()[x].start) > am)
         {
            am =  vorder.boundary()(vorder.marks()[x].start);
            ax = x;
#if VERBOSE_PINCH > 60
std::cout << "   updating am  = " << am << ",  ax = " << ax << ", at loc = " << vorder.marks()[ax].start<<std::endl;
#endif
         }
      }
      double bm = local_min_cut;
      long bx = z;
      for(BoundaryObject::MarksType::size_type x = z+1; x<vorder.marks().size(); ++x)
      {
//         if ((vorder.marks()[x].type == FlatStruct::LocalMin) && (vorder.boundary()(vorder.marks()[x].start) <= local_min_cut))
//            break;

         if (vorder.marks()[x].start  >= curStop)
            break;
         if ((vorder.marks()[x].type == FlatStruct::LocalMin))
            continue;
         if (vorder.boundary()(vorder.marks()[x].start) > bm)
         {
            bm =  vorder.boundary()(vorder.marks()[x].start);
            bx = x;
#if VERBOSE_PINCH > 60
std::cout << "   updating bm  = " << bm << ",  bx = " << bx <<", at loc = " << vorder.marks()[bx].start <<std::endl;
#endif
         }
      }

      double quality = std::numeric_limits<double>::max();
      double thickwidth_both = std::min(am,bm);
      double diff_minmax = thickwidth_both-local_min_cut; 
#if VERBOSE_PINCH > 60
std::cout << "   --- local_min_cut  = " << local_min_cut << ", am, bm = "<< am << "," << bm<< std::endl;
#endif

      double dA = 0;
      double dB = 0;
      double aInt = 0;
      double bInt = 0;
      double a2Ext = 0;
      double b2Ext = 0;
      double relB =  std::numeric_limits<double>::max();
      double relA =  std::numeric_limits<double>::max();

      double pinchR =  (thickwidth_both>0)?fabs(local_min_cut/thickwidth_both): std::numeric_limits<double>::max(); 
      double ncutV =  std::numeric_limits<double>::max();
      double crossR =  std::numeric_limits<double>::max();{
            quality = std::min(relA,relB);
         }

      double rRatio =   std::numeric_limits<double>::max();
      if (evalAllMetrics || (metric==NCut))
      {
         for(int ttt=curStart; ttt<=vorder.marks()[z].start; ++ttt)
            dA += a.degree(vorder(ttt));

         for(int ttt=vorder.marks()[z].start+1; ttt<=curStop; ++ttt)
            dB += a.degree(vorder(ttt));
          
         ncutV = (dA>0 && dB>0)? local_min_cut/dA + local_min_cut/dB : std::numeric_limits<double>::max();
      }
      if (evalAllMetrics || (metric == CrossRatio)||(metric == RelRatio))
      {
         a.calcCuts(curStart, vorder.marks()[ax].start,vorder.marks()[z].start,vorder.marks()[bx].start,curStop, aInt,a2Ext,bInt,b2Ext,vorder);
         relB = (bInt>0)? b2Ext/bInt : std::numeric_limits<double>::max();
         relA = (aInt>0)? a2Ext/aInt : std::numeric_limits<double>::max();
         crossR = (aInt>0 && bInt > 0) ?  relA*relB : std::numeric_limits<double>::max();
         rRatio= std::min(relA,relB);
      }

      if (metric == PinchRatio)
      {
         quality = pinchR; 
      }
      else if (metric == NCut)
      {
         quality = ncutV;
      }
      else if (metric == CrossRatio)
      {
         quality = crossR;
      }
      else if (metric == RelRatio)
      {
         quality = rRatio;
      }
      else
         assert(false && "invalid metric in pinch ratio split");

      if ( (quality < bestR) || ((quality == bestR)&&(diff_minmax > bestD)))
      {
         bestR = quality; bestD=diff_minmax; bestIndex = long(z);
         results.mincut = local_min_cut;
         results.minmaxcutA = am;
         results.minmaxcutB = bm;
         results.intA = aInt;
         results.extA = a2Ext;
         results.intB = bInt;
         results.extB = b2Ext;
         results.dA = dA;
         results.dB = dB;
         results.pinchRatio = pinchR;
         results.ncut = ncutV;
         results.relA = relA;
         results.relB = relB;
         results.relRatio = rRatio;
         results.crossRatio = crossR;

#if VERBOSE_PINCH > 60
   std::cout << "     UPDATING best R value : " << quality << " at z="<<z << " using metric mode " << metric << std::endl;
   std::cout <<"      updated best values : "<< results.Print("     ",",") << std::endl<<std::endl;
#endif
      }
   }
   value =  bestR;
   results.loc = -1;
   if (bestIndex >=0)
   {
      loc = vorder.marks()[bestIndex].start - curStart;
      results.loc = vorder.marks()[bestIndex].start;
   }
   else
      loc = -1;
#if VERBOSE_PINCH > 60
   std::cout << "     -------SELECTED LOCATION: " << loc << " with value results = "<<results.Print("      ",",") << std::endl << "-----------" << std::endl;
#endif
   return results;
}


template<typename T>
inline
double PRC::calcNCut(const SBase<T> &a, Eigen::VectorXi &labels, int NumPart)
{
   // TODO: specialize for sparse matrix 
   const int N = a.cols();
   Eigen::VectorXd degrees(NumPart);
   Eigen::VectorXd cut(NumPart);
   degrees.fill(0.0);
   cut.fill(0.0);

   for(int i=0; i<N;++i)
   {
      int tag = labels[i];
      degrees[tag] += a.col(i).sum();
      for(int j=0; j<N;++j)
      {
         if (labels[j] != tag)
         {
            double tmp = a.getCoeff(j,i);
            cut[tag] += tmp;
         }
      }
   }
   double ncut = 0;
   for(int i=0; i<NumPart;++i)
   {
      if (degrees[i]>0)
         ncut += cut[i]/degrees[i];
      else
         std::cerr <<"Warning: cluster "<<i<< " is empty" << std::endl;
   }
   return ncut;
}


template<typename T, typename V> 
inline std::pair<long,long> PRC::doRShifts(const BoundaryObject::MarksType &m, Ordering<V> &order, const BoundaryObject &b, const SBase<T> &a, double epsilon)
{
#if VERBOSE_PINCH > 60
   std::cout << "Starting doRShifts " << std::endl;
#endif

#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
   Eigen::BenchTimer timerDS1;
   Eigen::BenchTimer timerDS2;
#endif


   long count = 0;
   long inversionCount = 0;
   int prevS = -1;
   for(PRC::BoundaryObject::MarksType::size_type z=0; z < m.size(); ++z)
   {
      if (m[z].type == FlatStruct::LocalMin)
         continue;
      
#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
      timerDS1.start();
#endif

#if VERBOSE_PINCH > 60
   std::cout << "On Mark "<< m[z].Print() << std::endl;
#endif

      int y = 0;
      int mx_i = m[z].start; // start of max flat
      int mx_j = m[z].stop;  // end of max flat
      int prevMin = -1; 
      int nextMin = b.size()-1; 
      if (z>0)
      {
         prevMin = m[z-1].stop;
         assert(m[z-1].type == FlatStruct::LocalMin && "Error: two adjacent local max in mark vector");
      }
      if (z+1<m.size())
      {
         nextMin = m[z+1].start;
         assert(m[z+1].type == FlatStruct::LocalMin && "Error: two adjacent local max in mark vector");
      }
      double mx_sAi = (long(mx_i+1) < long(b.size()))?b(mx_i+1)-b(mx_i) : -b(mx_i);  
      double yval = epsilon*(1+fabs(mx_sAi));
      double ytmp = epsilon;
      double eps_sqrt = sqrt(epsilon);
      double orig_yval = yval;
      int r = mx_i;
      int upperLimit = order.size()-1; // only shifts on first branch

      for(int i = mx_i; i >prevMin; i--)
      {
          if (i+1 > upperLimit)
               continue; 
           
         double sAi = (long(i+1) < long(b.size()))?b(i+1)-b(i) : -b(i);  
         // search for good swap/shift

#if VERBOSE_PINCH > 60
      std::cout << "     1st branch, i = "<< i << ", mx_i = " << mx_i <<std::endl;
      std::cout << "     sAi ="<<sAi  << std::endl;
#endif

         for (int k = prevMin+1; k <=i;++k)
         {
            double tmp = order.slope(i,k,a);
            double tmp2 = tmp - sAi -2 * a.getCoeff(order[k],order[i+1]);
#if VERBOSE_PINCH > 60
         std::cout << "        at k="<<k<<" : tmp = " << tmp << " , tmp2 =" << tmp2  <<  "  || " << y << ","<<yval <<std::endl;
#endif


            if (((tmp >ytmp) && (tmp2 >yval)) ||
                ((tmp >ytmp) && (ytmp < eps_sqrt)&& (tmp2  >orig_yval)))
            {
               y = k;
               r = i;
               ytmp = fabs(tmp);
               yval= tmp2;
#if VERBOSE_PINCH > 60
            std::cout << "        1st Branch: setting y = "<<y << " with val = " << yval << std::endl;
            std::cout << "        i="<<i<<"sAi="<<sAi<<" at k="<<k<<" : tmp = " << tmp << " ,  tmp2 = " << tmp2 <<  "  || " << y << ","<<yval <<std::endl;
#endif
            }
         }

         if (yval >orig_yval)
            break;
      }

 
      for(int j = mx_j; j <= nextMin; j++)
      {
         if (yval >orig_yval)
            break;
         double sBj = b(j)-b(j-1);  // boundary object handles -1 indexing

#if VERBOSE_PINCH > 60
      std::cout << "     2nd branch, j = "<< j << ", mx_j = " << mx_j << std::endl;
      std::cout << "     sBj ="<<sBj <<std::endl;
#endif


         for (int k = j+1; k <=std::min(nextMin,upperLimit);++k)
         {
            double tmp = order.slope(j,k,a);
            double tmp2 = -tmp + sBj -2 * a.getCoeff(order[k],order[j]);
#if VERBOSE_PINCH > 60
         std::cout << "        at k="<<k<<" : tmp= " << tmp << " , tmp2 = " << tmp2  <<  "  || " << y << ","<<yval <<std::endl;
#endif
            if (((tmp <-ytmp) && (tmp2  >yval)) ||
                ((tmp <-ytmp)&&(ytmp <eps_sqrt) && (tmp2  >orig_yval)))
            {
               y = k;
               r = j;
               ytmp = fabs(tmp);
               yval= tmp2;

#if VERBOSE_PINCH > 60
            std::cout << "        2nd Branch: setting y = "<<y << " with val = " << yval << std::endl;
            std::cout << "        j="<<j<<"sBj="<<sBj<<" at k="<<k<<" : tmp = " << tmp << " , tmp2 = " <<  tmp2   <<  "  || " << y << ","<<yval <<std::endl;
#endif
            }
         }
      }

#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
      timerDS1.stop();
      timerDS2.start();
#endif


      // apply shift
      if (yval >orig_yval)
      {  
#if VERBOSE_PINCH > 60
         std::cout << "     Found possible shift location at " << y << " with value " << yval << ", mx_i = " << mx_i << std::endl;
#endif


         if (y <= mx_i)
         {
            if (r+1 > upperLimit)
            {
#if VERBOSE_PINCH > 60
               std::cout << "        r+1, " << r+1<<" > upperLimit "<<upperLimit <<".  skipping." << std::endl;
#endif
               continue; 
            }

            if (y == prevS)
            {
#if VERBOSE_PINCH > 60
               std::cout << "        y== prevS "<<prevS <<".  skipping." << std::endl;
#endif
               continue; 
            }

            prevS = r+1;
#if VERBOSE_PINCH > 60
std::cout << "     Shifting  y="<< y << ",o(y)= "<<order[y]<<" and r+1="<< r+1<< " o(r+1)= "<<order[r+1]<<" with val = " << yval << std::endl;
#endif

            order.applyShift(y,r+1,a); 
            //int otmp = order[y];
            //for(int x=y; x<r+1;++x)
            //   order.setAt(x, order[x+1]);
            //order.setAt(r+1,otmp);
            count++;
            inversionCount += r+1-y;
         }
         else
         {
            if (y> upperLimit)
            {

#if VERBOSE_PINCH > 60
               std::cout << "        y, " << y<<" > upperLimit "<<upperLimit <<".  skipping." << std::endl;
#endif
               continue; 
            }

            if (r == prevS)
            {
#if VERBOSE_PINCH > 60
               std::cout << "        r== prevS "<<prevS <<".  skipping." << std::endl;
#endif
               continue; 
            }

            prevS = y;

#if VERBOSE_PINCH > 60
std::cout << "     Shifting  y="<< y << ",o(y)= "<<order[y]<<" and r="<< r<< " o(r)= "<<order[r]<<" with val = " << yval << std::endl;
#endif

            order.applyShift(y,r,a);
            //int otmp = order[y];
            //for(int x=y; x>r;--x)
            //{
            //   order.setAt(x,order[x-1]);
            //}
            //order.setAt(r,otmp);
            count++;
            inversionCount += y-r;
         }
      }
      
#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
      timerDS2.stop();
#endif

   }

#if VERBOSE_PINCH > 60
   std::cout << "Finished doRShifts: shift count = " << count << ", inversion count = "<< inversionCount << std::endl;
#endif

   
#if defined(TIME_SHIFTS) && defined(HAVE_BENCH)
   std::cout << "RDDDDD doRshift search totals = " << timerDS1.total() << ", shift = " << timerDS2.total() << std::endl;
#endif


   return std::make_pair(count,inversionCount);
}
#endif
