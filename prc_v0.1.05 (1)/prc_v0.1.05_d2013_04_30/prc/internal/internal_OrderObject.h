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

/// \file  internal_OrderObject.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_ORDEROBJECT_H__
#define INTERNAL_ORDEROBJECT_H__


#ifndef ORDEROBJECT_H__
#include<prc/OrderObject.h>
#endif

#include<cassert>
#include<iostream>
#include<iomanip>
#include<iterator>

#include<vector>
#include<list>
#include<utility>
#include<algorithm>
#include<functional>
#include<stdexcept>


// some forward declarations of functions in pinch.h
namespace PRC
{
   template<typename T, typename S, typename V> void calcBoundaries(BoundaryObject &b, const T &a, const S &degrees, const Ordering<V> &order);
   template<typename T, typename S, typename V> std::pair<long,long> doShifts(const BoundaryObject::MarksType &m, Ordering<V> &order, const BoundaryObject &b, T &a, S &degrees,double epsilon);
   template<typename T, typename S,typename V> std::pair<long,long> doRShifts(const BoundaryObject::MarksType &m, Ordering<V> &order, const BoundaryObject &b, T &a, S &degrees,double epsilon);
}

inline
PRC::OrderObject::OrderObject() { usePrefix=false; validCache=false; }

inline
PRC::OrderObject::OrderObject(int size,bool prefixFlag):vdata(size)
{ 
   usePrefix=prefixFlag; 
   validCache=false; 
   for(int i=0;i<size;++i)
      vdata[i]=i;
   updateInverseOrder(); 
}

inline
PRC::OrderObject::OrderObject(const PRC::OrderObject &voo):vdata(voo.vdata){ 
   
   usePrefix = voo.usePrefix;
   updateInverseOrder();  
   if (voo.validCache)
   {
      slopeCache = voo.slopeCache;
      validCache = true;
   }
   else
      validCache = false;
}

inline
PRC::OrderObject::OrderObject(const std::vector<int> &origData,bool prefixFlag):vdata(origData)
{ 
   usePrefix=prefixFlag;
   validCache = false;
   updateInverseOrder(); 
}

inline
PRC::OrderObject::~OrderObject()
{ 
}


inline int PRC::OrderObject::size() const {return vdata.size();}
inline int PRC::OrderObject::baseStart() const {return 0;}

inline const int * PRC::OrderObject::Data() const 
{
   return &(vdata[0]);
}
inline const std::vector<int> & PRC::OrderObject::VData() const {return vdata;}
inline int * PRC::OrderObject::Data() 
{
   return &(vdata[0]);
}

inline
std::string PRC::OrderObject::Print() const
{
   std::ostringstream out;
   std::copy(Data(),Data()+size(), std::ostream_iterator<int>(out," "));
   return out.str();
}

inline
void PRC::OrderObject::Print(std::ostream &out) const
{
   out << this->Print();
}

inline
std::string PRC::OrderObject::PrintInverse() const
{
   std::ostringstream out;
   for(std::map<int,int>::const_iterator p = ivdata.begin(); p!=ivdata.end();++p)
      out << "( "<< p->first <<" -> " << p->second << ") " ;
   return out.str();
}


inline
void PRC::OrderObject::PrintInverse(std::ostream &out) const
{
   out << this->PrintInverse();
}

inline
void PRC::OrderObject::setAt(int index, int value)
{  
   assert(index>= 0 && index < this->size());
   vdata[index] = value;
   ivdata[value] = index;
}
inline
const int & PRC::OrderObject::at(int i) const
{  
   assert(i>= 0 && i < this->size());
   return vdata[i];
}

inline
const int & PRC::OrderObject::operator()(int i) const
{  
   return this->at(i);
}

inline
const int & PRC::OrderObject::operator[](int i) const
{  
   return this->at(i);
}

inline
int  PRC::OrderObject::invAt(int i) const
{  
   std::map<int,int>::const_iterator p = ivdata.find(i);

   if (p == ivdata.end())
   {
      std::cerr << "Error: Value " <<  i << " is not in inverse map.  Exiting"<< std::endl;
      throw std::runtime_error("Error: Index not in inverse map");
   }
   return p->second;
}


inline
void PRC::OrderObject::updateInverseOrder()
{
   ivdata.clear();
   for(int i=0; i<this->size();++i)
   {
      ivdata[vdata[i]] = i;
   }
}


template<typename T> 
inline
void PRC::OrderObject::setFrom(const T &src)
{
   vdata.resize(src.size());
   for(int i=0; i< this->size(); ++i)
      vdata[i] = src[i];
   updateInverseOrder();
   b.resize(vdata.size(),0);  // use prefix value here
   m.resize(0);
}


template<typename T> 
inline
void PRC::OrderObject::copyTo(T &dest) const
{
   if (long(dest.size()) != long(vdata.size()))
      dest.resize(vdata.size());

   for(int i=0; i< this->size(); ++i)
      dest[i] = vdata[i];
}


inline
PRC::BoundaryObject & PRC::OrderObject::boundary() { return this->b;}

inline
const PRC::BoundaryObject & PRC::OrderObject::boundary()const { return this->b;}

inline
PRC::BoundaryObject::MarksType & PRC::OrderObject::marks() { return this->m;}

inline
const PRC::BoundaryObject::MarksType & PRC::OrderObject::marks() const { return this->m;}


inline
void PRC::OrderObject::split(int loc, PRC::OrderObject &a, PRC::OrderObject &b,  bool reverseB) const
{
   assert(loc < this->size());
   assert(loc < this->size());
   a.vdata.resize(loc+1);
   std::copy(this->vdata.begin(),this->vdata.begin()+loc+1,a.vdata.begin());
   b.vdata.resize(this->size() - loc - 1);
   std::copy(this->vdata.begin()+loc+1,this->vdata.end(),b.vdata.begin());
   // try reversing b's order and see if it reduces inversions
   if(reverseB)
      std::reverse(b.vdata.begin(),b.vdata.end());
   a.updateInverseOrder();
   b.updateInverseOrder();
}


#ifdef PY_XML_GEN
// added for pygccxml
template void PRC::OrderObject::setFrom<std::vector<int> >(const std::vector<int> &src);
template void PRC::OrderObject::copyTo<std::vector<int> >(std::vector<int> &dest) const;
#endif


template<typename T> 
inline
double PRC::OrderObject::getPrefixCoeff(int id, const SBase<T> &A) const
{
   return usePrefix?A.getCoeff(id,0):0.0;
}

template<typename T> 
inline
double PRC::OrderObject::getPrefixDegree(const SBase<T> &A) const
{
   return usePrefix?A.degree(0):0.0;
}



inline
void PRC::OrderObject::SetPrefixFlag(bool flag) 
{
   usePrefix = flag;
}

template<typename T>
inline 
double PRC::OrderObject::slope(int i, int j, const SBase<T> &A) const
{
   return  A.slope(i,j,derived());
}

template<typename T>
inline
void PRC::OrderObject::resetCache(const SBase<T> &A) const
{
   return;
}

template<typename T>
inline
void PRC::OrderObject::shiftUpdate(int /* p */, int /* q */, const SBase<T> & /* A */) const
{
   return;
}

inline
bool PRC::OrderObject::haveCache() const
{
   return false;
   //return true;
}


#endif
