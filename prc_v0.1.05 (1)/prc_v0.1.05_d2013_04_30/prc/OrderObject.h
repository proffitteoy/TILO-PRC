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

/// \file  OrderObject.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef ORDEROBJECT_H__
#define ORDEROBJECT_H__

#include<prc/Ordering.h>

#include<vector>
#include<map>

namespace PRC
{

   class OrderObject : public Ordering<OrderObject>
   {
      public:
         typedef Ordering<OrderObject> Base;
         using Base::derived;
         using Base::updateOrder;
         using Base::refineOrder;
         using Base::applyShift;

         // Methods used by Ordering
         int size() const;
         int baseStart() const;
         const int & at(int i) const;
         const int & operator()(int i) const;
         const int & operator[](int i) const;
         void setAt(int index,int value);
         int  invAt(int i) const;
         void updateInverseOrder();
         std::string Print() const;
         std::string PrintInverse() const;
         template<typename T> void copyTo(T &dest) const;
         template<typename T> void setFrom(const T &src);
         BoundaryObject & boundary();
         const BoundaryObject & boundary()const;
         BoundaryObject::MarksType & marks();
         const BoundaryObject::MarksType & marks()const;

         template<typename T> double getPrefixCoeff(int id, const SBase<T> &A)  const;
         template<typename T> double getPrefixDegree(const SBase<T> &A)  const;


         template<typename T> double slope(int i, int j, const SBase<T> &A) const;
         template<typename T> void resetCache(const SBase<T> &A) const;
         template<typename T> void shiftUpdate(int p, int q, const SBase<T> &A) const;
         bool haveCache() const;


      public:
         OrderObject(); 
         OrderObject(int size,bool prefixFlag=false); 
         OrderObject(const OrderObject &voo); 
         OrderObject(const std::vector<int> &origData,bool prefixFlag=false); 
         ~OrderObject();

         void SetPrefixFlag(bool flag);

         const int * Data() const;
         int * Data();
         const std::vector<int> & VData() const;
         void Print(std::ostream &out) const;
         void PrintInverse(std::ostream &out) const;

         template<typename T, typename S>
         std::pair<long,long> refineOrder(const T &A, const S &degrees,double epsilon);
         void split(int loc, OrderObject &a, OrderObject &b,  bool reverseB=false) const;


#ifdef PY_XML_GEN
      public:
         int getAt(int i) { return this->at(i);}
#else
      protected:
#endif
         std::vector<int> vdata;
         std::map<int,int> ivdata;
         BoundaryObject b;
         BoundaryObject::MarksType m;
         bool usePrefix;

         mutable std::vector<double> slopeCache; ///! using std::vector instead of Eigen::Matrix so the python extension obj scans with gccxml 
         mutable bool validCache;  // to do: need to create an object to associate order and matrix, so validCache flag can be maintain properly
   };
}

#include<prc/internal/internal_OrderObject.h>

#endif
