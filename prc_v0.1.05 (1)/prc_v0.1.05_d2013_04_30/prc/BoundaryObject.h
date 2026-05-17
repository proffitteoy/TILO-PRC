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

/// \file  BoundaryObject.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef BOUNDARYOBJECT_H__
#define BOUNDARYOBJECT_H__

#include<iostream>
#include<vector>
#include<string>
#include<prc/FlatStruct.h>

namespace PRC
{

   /// \brief stores the boundary values associated with an ordering of a vertices
   ///
   /// The boundary at i is the graph cut of the set of vertices 0 to i from the 
   /// set i+1 to n-1.
   ///
   /// Note i==0 include the first vertex, so boundary allows indexing by -1.  A 
   /// special value, fixedBoundary, is used to represent any boundary values before
   /// the first vertex.  This is for furture use with fixed nodes in a cluster that
   /// are not allowed to be shifted out of the cluster.
   ///
   class BoundaryObject
   {
      public:
         typedef FlatStructVec MarksType;
         typedef std::vector<double> storage_type;
      public:
         BoundaryObject();
         BoundaryObject(int size, double inFixed); 
         int size() const;
         std::string Print() const;
         void Print(std::ostream &out) const;
         void resize(int size,double inFixed);
         double & at(int i);
         const double & at(int i) const;
         double & operator()(int i);
         const double & operator()(int i) const;
         double & operator[](int i);
         const double & operator[](int i) const;
         void findLocalMinAndMax(MarksType &m) const;
         const double * data() const;
         double * data();
         const storage_type & dataAsVector() const;

#ifdef PY_XML_GEN
      public:
         double fixedBoundary;
         storage_type b;
         double  py_at(int i){return at(i);}
#else
      protected:
         double fixedBoundary;
         storage_type b;
#endif

   };

   void PrintMarks(std::ostream &out, const BoundaryObject::MarksType &m);
   std::string PrintMarks(const BoundaryObject::MarksType &m);
}

#include<prc/internal/internal_BoundaryObject.h>

#endif
