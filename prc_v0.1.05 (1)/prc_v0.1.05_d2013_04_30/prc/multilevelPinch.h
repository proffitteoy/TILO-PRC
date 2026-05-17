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

/// \file  multilevelPinch.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef MULTILEVELPINCH_H__
#define MULTILEVELPINCH_H__

#ifndef PINCH_H__
#include<prc/pinch.h>
#endif

#ifndef RUNCONFIGS_H__
#include<prc/runConfigs.h>
#endif


namespace PRC
{
   typedef Eigen::SparseMatrix<double,Eigen::ColMajor,int>  MLSparseMatrixType;
   typedef Eigen::MatrixXd  MLDenseMatrixType;

   template<typename MatType>
   prcReturnStruct multilevelPRC(const shared_ptr<MatType> &A, Eigen::VectorXi &labels,int K,const prcPolicyStruct &policy);
   template<typename MatType>
   prcReturnStruct multilevelPRC(const shared_ptr<MatType> &A, Eigen::VectorXi &order, Eigen::VectorXi &labels,int K,const prcPolicyStruct &policy);
   template<typename MatType, typename V>
   prcReturnStruct multilevelPRC(const shared_ptr<MatType> &A, Ordering<V> &vorder, Eigen::VectorXi &labels,int K,const prcPolicyStruct &policy);
}

#include<prc/internal/internal_multilevelPinch.h>

#endif
