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

/// \file  denseNumpyStorage.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef DENSENUMPYSTORAGE_H__
#define DENSENUMPYSTORAGE_H__

#ifndef SBASE_H__
#include<prc/SBase.h>
#endif

#include<Python.h>
#include<numpy/arrayobject.h>
#include<stdexcept>
#include<vector>


namespace PRC
{
   class DenseNumpyStorage : public SBase<DenseNumpyStorage>
   {
      public:
         typedef DenseNumpyStorage DenseNumpyStorageType;
         typedef SBase<DenseNumpyStorageType> Base;
         using Base::derived;
         int rows() const;
         int cols() const;
         double  getCoeff(int row, int col)  const;
         void setCoeff(int row, int col,double value);
         double degree(int id) const;
         template<typename V> double slope(int i, int j, const Ordering<V> &order) const;
         template<typename V> void calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
                 double &aInt, double &aExt, double &bInt, double &bExt,const Ordering<V> &order) const ;
      protected:
         mutable bool haveDegrees;
         const PyArrayObject *adjMatrix;
         mutable  std::vector<double>  degreeCache;
      public:
         DenseNumpyStorage(const PyArrayObject *p);
         void updateDegrees() const;
   };
}

inline PRC::DenseNumpyStorage::DenseNumpyStorage(const PyArrayObject *p):haveDegrees(false),adjMatrix(p),degreeCache() 
{ 
   if (p == NULL)
         throw std::runtime_error("Attempted to create DenseNumpyStorage with a Null pointer");
   if (p->nd != 2 )
         throw std::runtime_error("Attempted to create DenseNumpyStorage with a matrix that is not 2D.");
   if (p->dimensions[0] != p->dimensions[1] )
         throw std::runtime_error("Attempted to create DenseNumpyStorage with a matrix that is not square.");
}

inline int PRC::DenseNumpyStorage::rows() const { return adjMatrix->dimensions[0];}
inline int PRC::DenseNumpyStorage::cols() const { return adjMatrix->dimensions[1];}
inline double  PRC::DenseNumpyStorage::getCoeff(int row, int col) const 
{ 
   // TODO : switch to using numpy macros for access
   return *(double *)(adjMatrix->data + row*adjMatrix->strides[0] +col*adjMatrix->strides[1]);
}

inline void PRC::DenseNumpyStorage::setCoeff(int row, int col,double value) 
{ 
   // TODO : switch to using numpy macros for access
   *(double *)(adjMatrix->data + row*adjMatrix->strides[0] +col*adjMatrix->strides[1]) = value;
}

inline double  PRC::DenseNumpyStorage::degree(int id) const
{ 
   if (!haveDegrees)
      updateDegrees();
   return degreeCache[id];
}

inline 
void PRC::DenseNumpyStorage::updateDegrees() const
{
   if (long(degreeCache.size()) != long(this->cols()))
      degreeCache.resize(this->cols());
   for(int c=0; c<this->cols();++c)
   {
      double sum=0;
      for (int r=0; r < this->rows();++r)
         sum += this->getCoeff(r,c);
      degreeCache[c] = sum;
   }
   haveDegrees = true;
}

template<typename V> 
inline
double PRC::DenseNumpyStorage::slope(int i, int j, const Ordering<V> &order) const
{ 
   // Note: dense storage could cache slopes and use an incremental update.  Not implemented yet.
   assert(i>=-1 && long(i) <long(order.size()) && j >=0 && long(j) < long(order.size()) && "index out of range.");
   double sum = this->degree(order[j]) -2 * order.getPrefixCoeff(order[j],*this);
   for(int p=0; p<i+1;++p)
   {
      sum -= 2* this->getCoeff(order[p],order[j]);
   }
   return sum;
};


template<typename V> 
inline
void PRC::DenseNumpyStorage::calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
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
