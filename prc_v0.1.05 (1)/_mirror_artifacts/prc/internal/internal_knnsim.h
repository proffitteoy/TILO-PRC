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

/// \file  internal_knnsim.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_KNNSIM_H__
#define INTERNAL_KNNSIM_H__

#ifndef __KNNSIM_H__
#include<prc/knnsim.h>
#endif


#ifndef INTERNAL_GAUSSSIM_H__
#include<prc/internal/internal_gausssim.h>
#endif


#include<cassert>
#include<cmath>
#include<vector>
#include<utility>
#include<algorithm>
#include<functional>


/// knnSimMatrix creates an adjacency matrix from  X view rows points
///       k is k nearest neighbors, if k <=0 then auto estimate k = log(n)+1
///       mode is adj matrix mode. 
///           mode == 0 : edge if either X[i],X[j] is knn of each other
///           mode == 1 : edge only if both X[i],X[j] are knn of each other
///           mode == 2 : edge if either X[i],X[j] is knn of each other, with
///                      value of 1 if both, otherwise value 1/2.
///
///      return adj matrix  in result.   
///      
/// ToDo : allow option to handle ties by setting more than k-nn.
///      

template<typename T, typename S> 
inline 
int PRC::knnSimMatrix(const T &data, S &result, int k, KNN_ADJ_MODE mode,double sigma)
{
   assert(k+1<data.rows());
   int n = int(data.rows());
   if (k <=0)
      k=int(log(double(n))+1);
   if ((mode == KNN_EITHER_ADJ_GAUSS) && (sigma <=0))
      sigma = findAverageKNNDist(data,-1);
   double gamma =-1.0/(2.0*sigma*sigma);


   result.setZero(n,n);
   std::vector<std::pair<double,int> > vdist;
	typedef std::vector<std::pair<double,int> >::size_type  stdvec_size_type; 
   vdist.resize(stdvec_size_type(n));
   for(int i=0;i<n;++i)
   {
      std::fill(vdist.begin(),vdist.end(),std::make_pair(0.0,0));
      for(int j=0; j<n;++j)
      {
         vdist[stdvec_size_type(j)] = std::make_pair( (data.row(i)-data.row(j)).squaredNorm(), j);
      }
      std::partial_sort(vdist.begin(),vdist.begin()+k+1,vdist.end());
      for(int j=0;j<k+1;++j)
      {
         if (vdist[stdvec_size_type(j)].second == i)
            continue;
         result(i,vdist[stdvec_size_type(j)].second) += 1.0;
         result(vdist[stdvec_size_type(j)].second,i) += 0.25;
      }
   }
   // make a second pass to make W symmetric.  Approach depends on mode
   for(int i = 0; i < n; ++i)
   {
      for(int j = 0; j < n; ++j)
      {
         if (result(i,j)>0)
         {
            switch (mode)
            {
               case KNN_EITHER_ADJ_ONE : // standard approach of edge if either exist
                  result(i,j) = 1.0;
                  result(j,i) = 1.0;
                  break;
               case KNN_BOTH_ADJ_ONE: // mutual k-nn :  edge only if both are k-nn 
                  if ( result(i,j) > 1.1)
                     result(i,j) = 1.0;
                  else
                     result(i,j) = 0.0;
                  break;
               case KNN_BOTH_EITHER_ONE_ONEHALF:  // set to 1/2 if not mutual k-nn
                  if ( result(i,j) > 1.1)
                     result(i,j) = 1.0;
                  else if ( result(i,j) > 0.1)
                     result(i,j) = 0.5;
                  break;
               case KNN_EITHER_ADJ_GAUSS:  
                  {
                     double tmpd = exp((data.row(i)-data.row(j)).squaredNorm()*gamma);
                     result(i,j) = tmpd;
                     result(j,i) = tmpd;
                  }
                  break;
               default:
                  assert("Unknown knn simularity mode:");
            }
         }
      }
   }
   return k;
}
#endif
