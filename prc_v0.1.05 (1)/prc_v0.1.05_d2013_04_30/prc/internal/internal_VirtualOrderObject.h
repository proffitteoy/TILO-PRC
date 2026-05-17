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

/// \file  internal_VirtualOrderObject.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_VIRTUALORDEROBJECT_H__
#define INTERNAL_VIRTUALORDEROBJECT_H__


#ifndef VIRTUALORDEROBJECT_H__
#include<prc/VirtualOrderObject.h>
#endif

#include<cassert>
#include<iostream>
#include<iterator>

#include<vector>
#include<list>
#include<utility>
#include<algorithm>
#include<functional>
#include<prc/BoundaryObject.h>


inline
PRC::VirtualOrderObject::VirtualOrderObject():storage(NULL),_start(0),_size(0) { usePrefix=false;}

inline
PRC::VirtualOrderObject::VirtualOrderObject(const VirtualOrderObject &voo):storage(voo.storage),_start(voo._start),_size(voo.size()),b(voo.b),m(voo.m) { usePrefix=voo.usePrefix; }

inline
PRC::VirtualOrderObject::VirtualOrderObject(VirtualOrderObject *voo):storage(voo->storage),_start(voo->_start),_size(voo->size()),b(voo->b),m(voo->m) {assert(voo != NULL); usePrefix = voo->usePrefix; }


inline
PRC::VirtualOrderObject::VirtualOrderObject(OrderObject *p):storage(p),_start(0),_size(p->size()),b(),m() { usePrefix=false; }
PRC::VirtualOrderObject::VirtualOrderObject(OrderObject *p,int start,int size):storage(p),_start(start),_size(size),b(),m() 
{ assert(start+size <= p->size());  usePrefix=false; }

inline int PRC::VirtualOrderObject::size() const {return _size;}
inline int PRC::VirtualOrderObject::start() const {return _start;}
inline int PRC::VirtualOrderObject::baseStart() const {return this->start();}


inline int PRC::VirtualOrderObject::origsize() const {assert(storage != NULL); return storage->size();}

inline const int * PRC::VirtualOrderObject::Data() const {assert(storage != NULL); return storage->Data()+this->start();}
inline int * PRC::VirtualOrderObject::Data() {assert(storage != NULL); return storage->Data()+this->start();}

inline
std::string PRC::VirtualOrderObject::Print() const
{
   std::ostringstream out;
   std::copy(Data(),Data()+_size, std::ostream_iterator<int>(out," "));
   return out.str();
}

inline
std::string PRC::VirtualOrderObject::PrintInverse() const
{
   std::ostringstream out;
   for(int id=0; id < storage->size();++id)  
   {
      int index = this->invAt(id);
      if (index>=0 && index < this->size())
         out << " " << index;
      else
         out << " # ";
   }
   return out.str();
}

inline
void PRC::VirtualOrderObject::setAt(int index, int value)
{  
   assert(storage != NULL);
   assert(index>= 0 && index < this->size());
   //*(data+index) = value;
   //*(invdata+value) = data+index;
   storage->setAt(start()+index,value);
}

inline
const int & PRC::VirtualOrderObject::at(int index) const
{  
   assert(storage != NULL);
   assert(index>= 0 && index < this->size());
   return storage->at(start()+index);
}

inline
const int & PRC::VirtualOrderObject::operator()(int index) const
{  
   return this->at(index);
}

inline
const int & PRC::VirtualOrderObject::operator[](int index) const
{  
   return this->at(index);
}




inline
int  PRC::VirtualOrderObject::invAt(int id) const
{  
   assert(storage != NULL);
   return storage->invAt(id) - start();
}

inline
PRC::BoundaryObject & PRC::VirtualOrderObject::boundary() { return this->b;}

inline
const PRC::BoundaryObject & PRC::VirtualOrderObject::boundary()const { return this->b;}

inline
PRC::BoundaryObject::MarksType & PRC::VirtualOrderObject::marks() { return this->m;}

inline
const PRC::BoundaryObject::MarksType & PRC::VirtualOrderObject::marks() const { return this->m;}


inline
void PRC::VirtualOrderObject::split(int loc, PRC::VirtualOrderObject &a, PRC::VirtualOrderObject &b,  bool reverseB) const
{
   assert(loc < this->size());
//   a.data = this->data;
//   a._size = loc+1;
//   a._origsize = this->_origsize;
//   a.invdata = this->invdata;
//   b.data = this->data + loc +1;
//   b._size = this->size() - loc - 1;
//   b.invdata = this->invdata;
//   b._origsize = this->_origsize;
//   // try reversing b's order and see if it reduces inversions
//   if(reverseB)
//      std::reverse(b.data,b.data+b._size);
//
// //   std::cout << "split --- calling update on a" << std::endl;
//   a.updateInverseOrder();
// //   std::cout << "split --- calling update on b" << std::endl;
//   b.updateInverseOrder();


  // std::cout << "splitting at loc = "<<loc << ", current size = " << _size << ", origsize = "<<_origsize << std::endl;
   assert(loc < this->size());
   a.storage = this->storage;
   a._size = loc+1;
   a._start = this->_start;
   b.storage = this->storage;
   b._start = this->_start+ loc +1;
   b._size = this->size() - loc - 1;
   // try reversing b's order and see if it reduces inversions
   if(reverseB)
      std::reverse(b.Data(),b.Data()+b.size());

//   std::cout << "split --- calling update on a" << std::endl;
   a.updateInverseOrder();
//   std::cout << "split --- calling update on b" << std::endl;
   b.updateInverseOrder();
}

inline
void PRC::VirtualOrderObject::updateInverseOrder()
{
//   std::cout << "updating inverse with size= "<<this->size() << std::endl;
//   std::cout << " data at " << data << ",  invdata at " << invdata << std::endl;
   for(int i=0; i<this->size();++i)
   {
//      std::cout << " setting invAt("<<this->at(i)<<") <-- " << i << std::endl;
      //*(this->invdata+this->at(i)) = data+i;
      this->setAt(i,this->at(i));
   }
}

template<typename T> 
inline
void PRC::VirtualOrderObject::setFrom(const T &src)
{
   assert(src.size() == this->size() && "Invalid order size for copying");
   for(int i=0; i< this->size(); ++i)
      this->setAt(i,src[i]);
}

template<typename T> 
inline
void PRC::VirtualOrderObject::copyTo(T &dest) const
{
   if (dest.size() != this->size())
      dest.resize(this->size());
   for(int i=0; i< this->size(); ++i)
      dest[i] = this->at(i);
}


template<typename T> 
inline
double PRC::VirtualOrderObject::getPrefixCoeff(int id , const SBase<T> &A) const
{
   return usePrefix?A.getCoeff(id,0):0.0;
}

template<typename T> 
inline
double PRC::VirtualOrderObject::getPrefixDegree(const SBase<T> &A) const
{
   return usePrefix?A.degree(0):0.0;
}


template<typename T>
inline 
double PRC::VirtualOrderObject::slope(int i, int j, const SBase<T> &A) const
{
   return A.slope(i,j,derived());
}

template<typename T>
inline
void PRC::VirtualOrderObject::resetCache(const SBase<T> &) const
{
}

template<typename T>
inline
void PRC::VirtualOrderObject::shiftUpdate(int , int , const SBase<T> &) const
{
}

inline
bool PRC::VirtualOrderObject::haveCache() const
{
   return false;
}


#endif
