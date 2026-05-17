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

/// \file  Ordering.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef ORDERING_H__
#define ORDERING_H__

#include<string>



#ifndef BOUNDARYOBJECT_H__
#include<prc/BoundaryObject.h>
#endif


// some forward declarations of functions in pinch.h
namespace PRC
{
   template<typename Derived> struct Ordering;
   template<typename Derived> struct SBase;
   template<typename T, typename V> void calcBoundaries(BoundaryObject &b, const SBase<T> &a, const Ordering<V> &order);
   template<typename T, typename V> std::pair<long,long> doShifts(const BoundaryObject::MarksType &m, Ordering<V> &order, const BoundaryObject &b, const SBase<T> &a,double epsilon);
   template<typename T, typename V> std::pair<long,long> doRShifts(const BoundaryObject::MarksType &m, Ordering<V> &order, const BoundaryObject &b, const SBase<T> &a,double epsilon);
}


namespace PRC
{
   template<typename Derived> struct Ordering
   {
         
      Derived& derived();
      const Derived& derived() const;
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

      template<typename T> std::pair<long,long> updateOrder(const SBase<T> &A, double epsilon);
      template<typename T> std::pair<long,long> refineOrder(const SBase<T> &A, double epsilon);

      template<typename T> double getPrefixCoeff(int row, const SBase<T> &A)  const;
      template<typename T> double getPrefixDegree(const SBase<T> &A)  const;

      template<typename T> double slope(int i, int j, const SBase<T> &A) const;
      template<typename T> void applyShift(int a, int b, const SBase<T> &A);
      template<typename T> void resetCache(const SBase<T> &A) const;
      template<typename T> void shiftUpdate(int p, int q, const SBase<T> &A) const;
      bool haveCache() const;


   };
}

template<typename Derived>
inline 
Derived& PRC::Ordering<Derived>::derived() { return *static_cast<Derived*>(this); }

template<typename Derived>
inline
const Derived& PRC::Ordering<Derived>::derived() const { return *static_cast<const Derived*>(this); }

template<typename Derived> 
inline
int PRC::Ordering<Derived>::size() const { return derived().size(); }


template<typename Derived> 
inline
int PRC::Ordering<Derived>::baseStart() const { return derived().baseStart(); }


template<typename Derived> 
inline
const int & PRC::Ordering<Derived>::at(int i) const { return derived().at(i); }

template<typename Derived> 
inline
const int & PRC::Ordering<Derived>::operator()(int i) const { return derived().at(i);} 

template<typename Derived> 
inline
const int & PRC::Ordering<Derived>::operator[](int i) const { return derived().at(i);}

template<typename Derived> 
inline
void PRC::Ordering<Derived>::setAt(int index,int value) { derived().setAt(index,value);}

template<typename Derived> 
inline
int  PRC::Ordering<Derived>::invAt(int i) const { return derived().invAt(i);}

template<typename Derived> 
inline
void PRC::Ordering<Derived>::updateInverseOrder() { derived().updateInverseOrder();}

template<typename Derived> 
inline
std::string PRC::Ordering<Derived>::Print() const { return derived().Print();}

template<typename Derived> 
inline
std::string PRC::Ordering<Derived>::PrintInverse() const { return derived().PrintInverse();}

template<typename Derived> 
template<typename T> 
inline
void PRC::Ordering<Derived>::copyTo(T &dest) const {derived().copyTo(dest);}

template<typename Derived> 
template<typename T> 
inline
void PRC::Ordering<Derived>::setFrom(const T &src) { derived().setFrom(src);}

template<typename Derived> 
inline
PRC::BoundaryObject & PRC::Ordering<Derived>::boundary() {return derived().boundary();}
template<typename Derived> 
inline
const PRC::BoundaryObject & PRC::Ordering<Derived>::boundary()const {return derived().boundary();}

template<typename Derived> 
inline
PRC::BoundaryObject::MarksType & PRC::Ordering<Derived>::marks() { return derived().marks();}
template<typename Derived> 
inline
const PRC::BoundaryObject::MarksType & PRC::Ordering<Derived>::marks()const { return derived().marks();}

template<typename Derived> 
template<typename T>
inline
std::pair<long,long> PRC::Ordering<Derived>::updateOrder(const SBase<T> &A, double epsilon)
{
#if VERBOSE_PINCH > 50
   std::cout << "     starting updateOrder: order = " << derived().Print() << std::endl;
#endif

#if defined(TIME_ORDER_UPDATE) && defined(HAVE_BENCH)
   Eigen::BenchTimer timerO;
   timerO.start();
#endif

   PRC::calcBoundaries(derived().boundary(),A,derived());

#if defined(TIME_ORDER_UPDATE) && defined(HAVE_BENCH)
   timerO.stop();
   std::cout << "OOO Calc Bound took :  "<<timerO.value() <<std::endl;
   timerO.reset(); timerO.start();
#endif

#if VERBOSE_PINCH > 50
   std::cout << "     new boundaries  = " << derived().boundary().Print() << std::endl;
#endif

   derived().boundary().findLocalMinAndMax(derived().marks());

#if VERBOSE_PINCH > 50
   std::cout << "     new marks  = " << PrintMarks(derived().marks()) << std::endl;
#endif

#if defined(TIME_ORDER_UPDATE) && defined(HAVE_BENCH)
   timerO.stop();
   std::cout << "OOO findLocalMM took :  "<<timerO.value() <<std::endl;
   timerO.reset(); timerO.start();
#endif


   std::pair<long,long> temp = PRC::doShifts(derived().marks(),derived(),derived().boundary(),A,epsilon);

#if defined(TIME_ORDER_UPDATE) && defined(HAVE_BENCH)
   timerO.stop();
   std::cout << "OOO doShifts took :  "<<timerO.value() <<std::endl;
   timerO.reset(); 
#endif


#if VERBOSE_PINCH > 50
   std::cout << "     finished updateOrder:after shifts, order = " << derived().Print() << std::endl;
#endif

   return temp;
}

template<typename Derived> 
template<typename T>
inline
std::pair<long,long> PRC::Ordering<Derived>::refineOrder(const SBase<T> &A, double epsilon)
{
#if VERBOSE_PINCH > 50
   std::cout << "     starting refineOrder: order = " << derived().Print() << std::endl;
#endif

#if defined(TIME_ORDER_UPDATE) && defined(HAVE_BENCH)
   Eigen::BenchTimer timerO;
   timerO.start();
#endif

   PRC::calcBoundaries(derived().boundary(),A,derived());


#if defined(TIME_ORDER_UPDATE) && defined(HAVE_BENCH)
   timerO.stop();
   std::cout << "ROOO Calc Bound took :  "<<timerO.value() <<std::endl;
   timerO.reset(); timerO.start();
#endif

#if VERBOSE_PINCH > 50
   std::cout << "     new boundaries  = " << derived().boundary().Print() << std::endl;
#endif

   derived().boundary().findLocalMinAndMax(derived().marks());

#if VERBOSE_PINCH > 50
   std::cout << "     new marks  = " << PrintMarks(derived().marks()) << std::endl;
#endif

#if defined(TIME_ORDER_UPDATE) && defined(HAVE_BENCH)
   timerO.stop();
   std::cout << "ROOO findLocalMM took :  "<<timerO.value() <<std::endl;
   timerO.reset(); timerO.start();
#endif

   std::pair<long,long> temp = PRC::doRShifts(derived().marks(),derived(),derived().boundary(),A,epsilon);

#if defined(TIME_ORDER_UPDATE) && defined(HAVE_BENCH)
   timerO.stop();
   std::cout << "ROOO doShifts took :  "<<timerO.value() <<std::endl;
   timerO.reset(); 
#endif


#if VERBOSE_PINCH > 50
   std::cout << "     finished updateOrder:after shifts, order = " << derived().Print() << std::endl;
#endif

   return temp;
}

template<typename Derived> 
template<typename T>
inline
double PRC::Ordering<Derived>::getPrefixCoeff(int id, const SBase<T> &A) const
{ return derived().getPrefixCoeff(id, A);
}

template<typename Derived> 
template<typename T>
inline
double PRC::Ordering<Derived>::getPrefixDegree(const SBase<T> &A) const
{ return derived().getPrefixDegree( A);
}


template<typename Derived> 
template<typename T>
inline
double PRC::Ordering<Derived>::slope(int i, int j , const SBase<T> &A) const
{
   double s = 0;
   if (derived().haveCache()) {
      s = derived().slope(i,j,A);
   }else{
      s = A.slope(i,j,derived());
   }
   return s;
}

/** \brief cyclic shift a to b in current order
 *
 *  apply incremental update to slope cache and boundary
 */
template<typename Derived> 
template<typename T>
inline
void PRC::Ordering<Derived>::applyShift(int p, int q , const SBase<T> & A)
{
   if (p <= q)
   {
      int otmp = derived().at(p);
      for(int x=p; x<q;++x)
         derived().setAt(x, derived().at(x+1));
      derived().setAt(q,otmp);
   }
   else
   {
      int otmp = derived().at(p);
      for(int x=p; x>q;--x)
      {
         derived().setAt(x,derived().at(x-1));
      }
      derived().setAt(q,otmp);
   }
   derived().shiftUpdate(p,q,A);
}


template<typename Derived> 
template<typename T>
inline
void PRC::Ordering<Derived>::resetCache(const SBase<T> &A ) const { return derived().resetCache(A);}

template<typename Derived> 
template<typename T>
inline
void PRC::Ordering<Derived>::shiftUpdate(int p, int q, const SBase<T> &A ) const { return derived().shiftUpdate;}

template<typename Derived> 
inline
bool PRC::Ordering<Derived>::haveCache() const { return derived().haveCache();}


#endif
