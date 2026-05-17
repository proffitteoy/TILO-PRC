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
// Eigen. If not, see <http://www.gnu.org/licenses/>.

// The following lines uses subversion's keyword expansion to insert the
// last time the file was modified and by who.

/// \file  internal_gausssim.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $



#ifndef INTERNAL_GAUSSSIM_H__
#define INTERNAL_GAUSSSIM_H__

#ifndef GAUSSSIM_H__
#include<gausssim.h>
#endif

#include<cassert>
#include<cmath>
#include<iostream>

#include<vector>
#include<utility>
#include<algorithm>
#include<functional>
#include<prc/prcPolicies.h>


template<typename T> 
inline
double PRC::findAverageKNNDist(const T &data,  int k)
{
   int n = data.rows();
   if ((k <=0)||(k>n-2))
      k=int(log(double(n))+1);
   double avg = 0.0;
   std::vector<double> dist(n);
   for(int i=0;i<n;++i)
   {
      for(int j=0;j<n;++j)
      {
         dist[j] = (data.row(i)-data.row(j)).squaredNorm();
      }
      std::partial_sort(dist.begin(),dist.begin()+k+1,dist.end());
      avg += sqrt(dist[k]);
   }
   avg /= n;
   return avg;
}
   


template<typename T, typename S> 
inline 
double PRC::gaussSimMatrix(const T &data, S &result, double sigma, GAUSSSIM_ADJ_MODE mode, double eps, bool zeroDiagonal)
{
   long n = long(data.rows());
   if ( sigma <=0 )
   {
      sigma = findAverageKNNDist(data,-1);
   }
   result = data * data.transpose();
   double g =-1.0/(2.0*sigma*sigma);
   for(long i=0; i<n;++i)
   {
      for(long j=i+1;j<n;++j)
      {
         double d = exp(g*(result(i,i)-2*result(i,j)+result(j,j)));
         if (! ((mode == GS_ADJ_ALL) || ( (mode == GS_ADJ_THRESHOLD) && (d > eps))))
             d = 0;
         result(i,j) = d;
         result(j,i) = d;
      }
      if (zeroDiagonal)
         result(i,i) = 0;
      else
         result(i,i) = 1.0;
   }
   return sigma;
}

#endif
