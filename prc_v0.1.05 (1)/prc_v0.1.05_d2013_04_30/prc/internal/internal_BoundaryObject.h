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

/// \file  internal_BoundaryObject.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_BOUNDARYOBJECT_H__
#define INTERNAL_BOUNDARYOBJECT_H__

#ifndef  BOUNDARYOBJECT_H__
#include<prc/BoundaryObject.h>
#endif

#include<cassert>
#include<iostream>
#include<iterator>
#include<vector>
#include<algorithm>
#include<functional>
#include<prc/FlatStruct.h>

inline
std::string PRC::PrintMarks(const PRC::BoundaryObject::MarksType &m)
{
   std::ostringstream out;
   for(PRC::BoundaryObject::MarksType::const_iterator p = m.begin(); p != m.end();++p)
   {
      p->Print(out);
      if (p+1 != m.end())
         out << ", ";
   }
   return out.str();
}


inline
void PRC::PrintMarks(std::ostream &out, const PRC::BoundaryObject::MarksType &m)
{
   out << PrintMarks(m);
}

inline 
PRC::BoundaryObject::BoundaryObject():fixedBoundary(0) {}

inline
PRC::BoundaryObject::BoundaryObject(int size, double inFixed):fixedBoundary(inFixed),b(size)
{
   std::fill(b.begin(),b.end(),0);
}


inline int PRC::BoundaryObject::size() const {return int(b.size());} 

inline const double  * PRC::BoundaryObject::data() const 
{
 //  return b.data();
 return &(b[0]);
}

inline double  * PRC::BoundaryObject::data()  
{
 //  return b.data();
 return &(b[0]);
}


inline const PRC::BoundaryObject::storage_type & PRC::BoundaryObject::dataAsVector() const {return b;}

inline
std::string PRC::BoundaryObject::Print() const
{
   std::ostringstream out;
   out << fixedBoundary << " | ";
   std::copy(b.begin(),b.end(), std::ostream_iterator<double>(out," "));
   return out.str();
}


inline
void PRC::BoundaryObject::Print(std::ostream &out) const
{
   out << this->Print();
}


inline
void PRC::BoundaryObject::resize(int size,double inFixed)
{
   b.resize(size);
   fixedBoundary = inFixed;
   std::fill(b.begin(),b.end(),0);
}

inline
double & PRC::BoundaryObject::at(int i)
{  // index range of -1 to size-1 
   assert(i>=-1 && i< this->size());
   if (i<0)
      return fixedBoundary;
   else
      return b[i];
}

inline
const double & PRC::BoundaryObject::at(int i) const
{  // index range of -1 to size-1 
   assert(i>=-1 && i< this->size());
   if (i<0)
      return fixedBoundary;
   else
      return b[i];
}


inline
double & PRC::BoundaryObject::operator()(int i)
{  
   return this->at(i);
}

inline
const double & PRC::BoundaryObject::operator()(int i) const
{  
   return this->at(i);
}
inline
double & PRC::BoundaryObject::operator[](int i)
{  
   return this->at(i);
}

inline
const double & PRC::BoundaryObject::operator[](int i) const
{  
   return this->at(i);
}


inline
void PRC::BoundaryObject::findLocalMinAndMax(MarksType &m) const
{
   int p=0;
   m.clear();
	int n = this->size();
   FlatStruct curMin(0,0,FlatStruct::LocalMin);
   FlatStruct curMax(0,0,FlatStruct::LocalMax);
   bool searchMin = true;
   if (this->at(0) > this->at(-1))
      searchMin = false; // search for max
   else if (this->at(0) < this->at(-1))
      searchMin = true; // search for min
   else  // tied, need to scan ahead to decide
   {
      int i=p+1;
      while (i<n && this->at(i) == this->at(i-1))
         ++i;
      if (i>=n)
      {  // all values are the same.  What should be done? --- no local min, no local max, so return with empty mark array

         // need to check other functions, in case they used the assumption that marks is not empty (typically should have at least a local max somewhere)
         return;
      }
      else
      {
         searchMin = (this->at(i) < this->at(0))?true:false;
      }
   }

   while (p<n)
   {
      int j = p;
      if (searchMin)
      {  // search for local min
         while ((j+1 < n) && (this->at(j) >= this->at(j+1)))
            j++;
         int k = j;
         while (( k > p ) && ( this->at(k) == this->at(k-1)))
               --k;
         curMin.start = k;
         curMin.stop = j;
         if ( (j+1<n) )
            m.push_back(curMin);
      }
      else // search for local max
      {
         while ((j+1 < n) && (this->at(j) <= this->at(j+1)))
            ++j;
         int k = j;
         while (( k > p ) && ( this->at(k) == this->at(k-1)))
            --k;
         curMax.start = k;
         curMax.stop = j;
         if ( (j+1<n) || (this->at(k) > this->at(k-1)))
            m.push_back(curMax);
      }
      p = j+1;
      searchMin = !searchMin;
   }
}

#endif
