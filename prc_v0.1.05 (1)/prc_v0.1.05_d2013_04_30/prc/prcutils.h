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

/// \file prcutils.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef PRCUTILS_H__
#define PRCUTILS_H__

#ifndef PRCFORWARDDECLARATIONS_H__
#include<prc/prcForwardDeclarations.h>
#endif


#ifdef _MSC_VER
#include<array>
#else
#if (__cplusplus >= 201103L)           
//  if using -std=c++0x option to g++ then
//  Note: g++ currently not setting _cplusplus.  But should start doing so in version 4.7
//  but using older approach is OK until then.
   #include<array>
   #include<memory>
#else
   #include<tr1/array>
   #include<tr1/memory>
#endif
#endif

namespace PRC
{
 // bring array into PRC namespace to ignore different namespace based on version
#ifdef _MSC_VER
#if (_MSC_VER > 1500)
   using std::array; // MSVC 2010 array is in std namespace
   using std::shared_ptr; 
#else
   using std::tr1::array;  // for MSVC 2008, array is in tr1 namespace inspite of including as include<array>
   using std::tr1::shared_ptr; 
#endif
#else
#if (__cplusplus >= 201103L)           
//  if using -std=c++0x option to g++ then
//  Note: g++ currently not setting _cplusplus.  But should start doing so in version 4.7
//  but using older approach is OK until then.
   using std::array;
   using std::shared_ptr; 
#else
   using std::tr1::array; 
   using std::tr1::shared_ptr; 
#endif
#endif
}


#include<iostream>
#include<vector>
#include<Eigen/Core>
#include<Eigen/SparseCore>

namespace PRC
{
   /* a helper function  ... should make general for multiple file types */
   bool loadtxt(std::ifstream &fin,Eigen::MatrixXd &result);
   bool loadtxt(std::ifstream &fin,Eigen::VectorXi &result);
   bool loadtxt(std::ifstream &fin,Eigen::VectorXd &result);
   bool loadSparseGraph(std::ifstream &fin,Eigen::SparseMatrix<double,Eigen::ColMajor,int> &result,int nodeOffset, Eigen::MatrixXd &vertexWeights);
   bool loadGraph(std::ifstream &fin,Eigen::MatrixXd &result,int nodeOffset, Eigen::MatrixXd &vertexWeights);
   template<typename V> void printStdVec(std::ostream &out,const std::vector<V> &a);
   template<typename V> void printStdVec(std::ostream &out,const std::vector<std::vector<V> > &a,const std::string &indent="   ");
   template<typename V,std::size_t  N> void printStdVec(std::ostream &out,const std::vector<PRC::array<V,N> > &a,const std::string &indent="   ");
   // a couple of helper functions to handle MSVC 2008 stl being out of date
   template<typename T> typename T::value_type * stdVecData(T &v);
   template<typename T> const typename T::value_type * stdVecData(const T &v);

}


#include<prc/internal/internal_prcutils.h>

#endif
