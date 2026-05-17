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

/// \file  internal_gausssimSparse.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $



#ifndef INTERNAL_GAUSSSIMSPARSE_H__
#define INTERNAL_GAUSSSIMSPARSE_H__

#ifndef GAUSSSIMSPARSE_H__
#include<prc/gausssimSparse.h>
#endif

#ifndef GAUSSSIM_H__
#include<prc/gausssim.h>
#endif


#include<cassert>
#include<cmath>
#include<vector>
#include<Eigen/Core>
#include<Eigen/SparseCore>


template<typename T, typename S> 
inline 
double PRC::gaussSimSparseMatrix(const T &data, S &result, double sigma, GAUSSSIM_ADJ_MODE mode,double eps,bool zeroDiagonal)
{
	int n = int(data.rows());
   if ( sigma <=0 )
   {
      sigma = findAverageKNNDist(data,-1);
   }

   double g =-1.0/(2.0*sigma*sigma);
   result.resize(data.rows(),data.rows());
   result.setZero();
   std::vector<Eigen::Triplet<double> > tripletList;
   tripletList.reserve(20*n);
   for(int i=0;i<n;++i)
   {
      for(int j=i+1; j<n;++j)
      {
         double d = exp((data.row(i)-data.row(j)).squaredNorm()*g);
         if ((mode == GS_ADJ_ALL) || ( (mode == GS_ADJ_THRESHOLD) && (d > eps)))
         {
            tripletList.push_back(Eigen::Triplet<double>(i,j,d));
            tripletList.push_back(Eigen::Triplet<double>(j,i,d));
         }
      }
      if (!zeroDiagonal)
            tripletList.push_back(Eigen::Triplet<double>(i,i,1.0));
   }
   result.setFromTriplets(tripletList.begin(),tripletList.end());
   return sigma;
}
#endif
