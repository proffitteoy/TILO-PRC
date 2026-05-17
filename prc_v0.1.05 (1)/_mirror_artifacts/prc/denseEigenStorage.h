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

/// \file  denseEigenStorage.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef DENSEEIGENSTORAGE_H__
#define DENSEEIGENSTORAGE_H__

#ifndef SBASE_H__
#include<prc/SBase.h>
#endif

#include<Eigen/Core>

namespace PRC
{
   template<typename Derived>
   class DenseEigenStorage : public SBase<DenseEigenStorage<Derived> >
   {
      public:
         typedef DenseEigenStorage<Derived> DenseEigenStorageType;
         typedef SBase<DenseEigenStorageType> Base;
         using Base::derived;
         int rows() const;
         int cols() const;
         double  getCoeff(int row, int col)  const;
         void setCoeff(int row, int col, double value);
         double degree(int id) const;
         template<typename V> double slope(int i, int j, const Ordering<V> &order) const;
         template<typename V> void calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
                 double &aInt, double &aExt, double &bInt, double &bExt,const Ordering<V> &order) const ;
      protected:
         mutable bool haveDegrees;
         Derived adjMatrix;
         mutable Eigen::VectorXd degreeCache;
      public:
         DenseEigenStorage();
         DenseEigenStorage(const Derived &m);
         const Derived & AdjMatrix()const;
         Derived & AdjMatrix();
         void updateDegrees() const;
   };

   // partial specialization for smart pointer
   template<typename Derived>
   class DenseEigenStorage<PRC::shared_ptr<Derived> > : public SBase<DenseEigenStorage<PRC::shared_ptr<Derived> > >
   {
      public:
         typedef DenseEigenStorage<PRC::shared_ptr<Derived> > DenseEigenStorageType;
         typedef SBase<DenseEigenStorageType> Base;
         using Base::derived;
         int rows() const;
         int cols() const;
         double  getCoeff(int row, int col)  const;
         void  setCoeff(int row, int col,double value);
         double degree(int id) const;
         template<typename V> double slope(int i, int j, const Ordering<V> &order) const;
         template<typename V> void calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
                 double &aInt, double &aExt, double &bInt, double &bExt,const Ordering<V> &order) const ;
      protected:
         mutable bool haveDegrees;
         PRC::shared_ptr<Derived> adjMatrix;
         mutable Eigen::VectorXd degreeCache;
      public:
         DenseEigenStorage();
         DenseEigenStorage(const PRC::shared_ptr<Derived> &m);
         const Derived & AdjMatrix()const;
         Derived & AdjMatrix();

         const PRC::shared_ptr<Derived> & AdjMatrixPtr()const;
         PRC::shared_ptr<Derived> & AdjMatrixPtr();

         void updateDegrees() const;
   };

}

template<typename Derived> inline PRC::DenseEigenStorage<Derived>::DenseEigenStorage():haveDegrees(false),adjMatrix(),degreeCache() { }
template<typename Derived> inline PRC::DenseEigenStorage<Derived>::DenseEigenStorage(const Derived &m):haveDegrees(false),adjMatrix(m),degreeCache() { }

template<typename Derived> inline int PRC::DenseEigenStorage<Derived>::rows() const { return AdjMatrix().rows();}
template<typename Derived> inline int PRC::DenseEigenStorage<Derived>::cols() const { return AdjMatrix().cols();}
template<typename Derived> inline double  PRC::DenseEigenStorage<Derived>::getCoeff(int row, int col) const { return AdjMatrix().coeff(row,col);}
template<typename Derived> inline void PRC::DenseEigenStorage<Derived>::setCoeff(int row, int col,double value) { AdjMatrix().coeff(row,col)=value;}
template<typename Derived> inline double  PRC::DenseEigenStorage<Derived>::degree(int id) const
{ 
   if (!haveDegrees)
      updateDegrees();
   return degreeCache(id);
}

template<typename Derived> 
inline 
const Derived & PRC::DenseEigenStorage<Derived>::AdjMatrix() const { return adjMatrix;}

template<typename Derived> 
inline 
Derived & PRC::DenseEigenStorage<Derived>::AdjMatrix() 
{ 
   haveDegrees = false;
   return adjMatrix;
}

template<typename Derived> 
inline 
void PRC::DenseEigenStorage<Derived>::updateDegrees() const
{
   if (degreeCache.size() != this->cols())
      degreeCache.resize(this->cols());
   for(int c=0; c<this->cols();++c)
   {
      degreeCache(c) = adjMatrix.col(c).sum();
   }
   haveDegrees = true;
}


template<typename Derived> 
template<typename V> 
inline
double PRC::DenseEigenStorage<Derived>::slope(int i, int j, const Ordering<V> &order) const
{ 
   // Note: dense storage could cache slopes and use an incremental update.  Not implemented yet.
   assert(i>=-1 && long(i) <long(order.size()) && j >=0 && long(j) < long(order.size()) && "index out of range.");
   double sum = this->degree(order[j]) - 2* order.getPrefixCoeff(order[j],*this);
   for(int p=0; p<i+1;++p)
   {
      sum -= 2* this->getCoeff(order[p],order[j]);
   }
   return sum;
}


template<typename Derived> 
template<typename V> 
inline
void PRC::DenseEigenStorage<Derived>::calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
                 double &aInt, double &aExt, double &bInt, double &bExt,const Ordering<V> &order) const
{
/*  startLoc <= mxALoc <= minLoc <= mxBLoc <= stopLoc
 *  regions : a_1 : startLoc .. mxALoc
 *            a_2 : mxALoc+1 .. minLoc
 *            b_1 : minLoc+1 .. mxBLoc
 *            b_2 : mxBLoc+1 .. stopLoc
 *  calc values aInt = cut of a_1 and a_2
 *              aExt = cut of a_2 and b_1 + b_2
 *              bInt = cut of b_1 and b_2
 *              bExt = cut of b_1 and a_1 + b_2
 */
   aInt = bInt = aExt = bExt = 0;
   for(int p = startLoc ; p <= stopLoc ; ++p)
   {
      for(int loc = p+1; loc <= stopLoc; ++loc)
      {
         double value = this->getCoeff(order[p],order[loc]);
         if ((p <= mxALoc) && (loc > mxALoc && loc <= minLoc))
               aInt += value;

         if ((p>mxALoc)&&(p<=minLoc) && (loc > minLoc && loc <= stopLoc))
               aExt += value;

         if ( (p >minLoc) && (p<=mxBLoc) && (loc > mxBLoc && loc <= stopLoc))
               bInt += value;

         if  ((p<=minLoc) && (loc > minLoc && loc <= mxBLoc))
               bExt += value;
      }
   }
}



// smart pointer partial specialization
//
template<typename Derived> inline PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::DenseEigenStorage():haveDegrees(false),adjMatrix(),degreeCache() { }
template<typename Derived> inline PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::DenseEigenStorage(const PRC::shared_ptr<Derived> &m):haveDegrees(false),adjMatrix(m),degreeCache() { }

template<typename Derived> inline int PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::rows() const { return AdjMatrix().rows();}
template<typename Derived> inline int PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::cols() const { return AdjMatrix().cols();}
template<typename Derived> inline double  PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::getCoeff(int row, int col) const { return AdjMatrix().coeff(row,col);}
template<typename Derived> inline void PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::setCoeff(int row, int col, double value) { return AdjMatrix().coeff(row,col) = value;}
template<typename Derived> inline double  PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::degree(int id) const
{ 
   if (!haveDegrees)
      updateDegrees();
   return degreeCache(id);
}

template<typename Derived> 
inline 
const Derived & PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::AdjMatrix() const { return *adjMatrix;}

template<typename Derived> 
inline 
Derived & PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::AdjMatrix() 
{ 
   haveDegrees = false;
   return *adjMatrix;
}


template<typename Derived> 
inline 
const PRC::shared_ptr<Derived> & PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::AdjMatrixPtr() const { return adjMatrix;}

template<typename Derived> 
inline 
PRC::shared_ptr<Derived> & PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::AdjMatrixPtr() 
{ 
   haveDegrees = false;
   return adjMatrix;
}


template<typename Derived> 
inline 
void PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::updateDegrees() const
{
   if (degreeCache.size() != this->cols())
      degreeCache.resize(this->cols());
   for(int c=0; c<this->cols();++c)
   {
      degreeCache(c) = AdjMatrix().col(c).sum();
   }
   haveDegrees = true;
}


template<typename Derived> 
template<typename V> 
inline
double PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::slope(int i, int j, const Ordering<V> &order) const
{ 
   // Note: dense storage could cache slopes and use an incremental update.  Not implemented yet.
   assert(i>=-1 && long(i) <long(order.size()) && j >=0 && long(j) < long(order.size()) && "index out of range.");
   double sum = this->degree(order[j]) -2 * order.getPrefixCoeff(order[j],*this);
   for(int p=0; p<i+1;++p)
   {
      sum -= 2* this->getCoeff(order[p],order[j]);
   }
   return sum;
}


template<typename Derived> 
template<typename V> 
inline
void PRC::DenseEigenStorage<PRC::shared_ptr<Derived> >::calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
                 double &aInt, double &aExt, double &bInt, double &bExt,const Ordering<V> &order) const
{
/*  startLoc <= mxALoc <= minLoc <= mxBLoc <= stopLoc
 *  regions : a_1 : startLoc .. mxALoc
 *            a_2 : mxALoc+1 .. minLoc
 *            b_1 : minLoc+1 .. mxBLoc
 *            b_2 : mxBLoc+1 .. stopLoc
 *  calc values aInt = cut of a_1 and a_2
 *              aExt = cut of a_2 and b_1 + b_2
 *              bInt = cut of b_1 and b_2
 *              bExt = cut of b_1 and a_1 + b_2
 */
   aInt = bInt = aExt = bExt = 0;
   for(int p = startLoc ; p <= stopLoc ; ++p)
   {
      for(int loc = p+1; loc <= stopLoc; ++loc)
      {
         double value = this->getCoeff(order[p],order[loc]);
         if ((p <= mxALoc) && (loc > mxALoc && loc <= minLoc))
               aInt += value;

         if ((p>mxALoc)&&(p<=minLoc) && (loc > minLoc && loc <= stopLoc))
               aExt += value;

         if ( (p >minLoc) && (p<=mxBLoc) && (loc > mxBLoc && loc <= stopLoc))
               bInt += value;

         if  ((p<=minLoc) && (loc > minLoc && loc <= mxBLoc))
               bExt += value;
      }
   }
}


#endif
