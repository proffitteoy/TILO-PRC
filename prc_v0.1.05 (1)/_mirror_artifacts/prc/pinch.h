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

/// \file  pinch.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef PINCH_H__
#define PINCH_H__

#ifdef HAVE_BENCH
#include<BenchTimer.h>
#endif

#include<iostream>
#include<vector>
#include<utility>
#include<Eigen/Core>

#ifndef PRCUTILS_H__
#include<prc/prcutils.h>
#endif

#ifndef PRCPOLICIES_H__
#include<prc/prcPolicies.h>
#endif

#ifndef BOUNDARYOBJECT_H__
#include<prc/BoundaryObject.h>
#endif

#ifndef ORDERING_H__
#include<prc/Ordering.h>
#endif

#ifndef PRCCOUNTSSTRUCT_H__
#include<prc/prcCountsStruct.h>
#endif

#ifndef PRCRETURNSTRUCT_H__
#include<prc/prcReturnStruct.h>
#endif


#ifndef PRCMETRICVALUES_H__
#include<prc/prcMetricValues.h>
#endif


#ifndef SBASE_H__
#include<prc/SBase.h>
#endif


namespace PRC
{

   template<typename T,  typename V> prcCountsStruct TILO( Ordering<V> &order,const SBase<T> &A,const tiloPolicyStruct &policy=tiloPolicyStruct());
   template<typename T,  typename V> prcCountsStruct RefineTILO( Ordering<V> &order,const SBase<T> &A,const tiloPolicyStruct &policy=tiloPolicyStruct());

   template<typename T> prcReturnStruct pinchRatioClustering(const SBase<T> &a, Eigen::VectorXi &labels,int K,const prcPolicyStruct &policy);
   template<typename T> prcReturnStruct pinchRatioClustering(const SBase<T> &a, Eigen::VectorXi &order, Eigen::VectorXi &labels,int K,const prcPolicyStruct &policy);
   template<typename T, typename V> prcReturnStruct pinchRatioClustering(const SBase<T> &a, Ordering<V> &vorder, Eigen::VectorXi &labels,int K,const prcPolicyStruct &policy);
   template<typename T, typename V> prcReturnStruct pinchRatioClustering(const SBase<T> &a, Ordering<V> &vorder, std::vector<int> &labels,int K,const prcPolicyStruct &policy);

   template<typename T, typename V> void calcBoundaries(BoundaryObject &b, const SBase<T> &a, const Ordering<V> &order);
}

#include<prc/internal/internal_pinch.h>

#endif
