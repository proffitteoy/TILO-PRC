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

/// \file  SBase.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef SBASE_H__
#define SBASE_H__

namespace PRC
{
   template<typename Derived> struct Ordering;
}




namespace PRC
{
   template<typename Derived> struct SBase
   {
         
      Derived& derived();
      const Derived& derived() const;
      int rows() const;
      int cols() const;
      double getCoeff(int row, int col)  const;
      void setCoeff(int row, int col, double value);
      double degree(int id) const;
      template<typename V> double slope(int i, int j, const Ordering<V> &order) const;
      template<typename V> void calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
                 double &aInt, double &aExt, double &bInt, double &bExt,const Ordering<V> &order) const ;

   };
}

template<typename Derived>
inline 
Derived& PRC::SBase<Derived>::derived() { return *static_cast<Derived*>(this); }

template<typename Derived>
inline
const Derived& PRC::SBase<Derived>::derived() const { return *static_cast<const Derived*>(this); }

template<typename Derived> 
inline
int PRC::SBase<Derived>::rows() const { return derived().rows(); }

template<typename Derived> 
inline
int PRC::SBase<Derived>::cols() const { return derived().cols(); }

template<typename Derived> 
inline
double PRC::SBase<Derived>::getCoeff(int row, int col) const { return derived().getCoeff(row,col); }

template<typename Derived> 
inline
void PRC::SBase<Derived>::setCoeff(int row, int col, double value) { derived().setCoeff(row,col,value); }

template<typename Derived> 
inline
double  PRC::SBase<Derived>::degree(int id) const { return derived().degree(id); }

template<typename Derived> 
template<typename V> 
inline
double PRC::SBase<Derived>::slope(int i, int j, const Ordering<V> &order) const { return derived().slope(i,j,order);}

template<typename Derived> 
template<typename V> 
inline
void PRC::SBase<Derived>::calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
                 double &aInt, double &aExt, double &bInt, double &bExt,const Ordering<V> &order) const
{
return derived().calcCuts(startLoc,mxALoc, minLoc, mxBLoc, stopLoc, 
                 aInt, aExt, bInt, bExt,order);
}


#endif
