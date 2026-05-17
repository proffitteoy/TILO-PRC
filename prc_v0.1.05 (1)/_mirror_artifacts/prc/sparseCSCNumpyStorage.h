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

/// \file  sparseCSCNumpyStorage.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef SPARSECSCNUMPYSTORAGE_H__
#define SPARSECSCNUMPYSTORAGE_H__

#ifndef SBASE_H__
#include<prc/SBase.h>
#endif

#include<Python.h>
#include<numpy/arrayobject.h>
#include<stdexcept>
#include<vector>


namespace PRC
{
   class SparseCSCNumpyStorage : public SBase<SparseCSCNumpyStorage>
   {
      public:
         typedef SparseCSCNumpyStorage SparseCSCNumpyStorageType;
         typedef SBase<SparseCSCNumpyStorageType> Base;
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
         int n;
         int nnz;
         const PyArrayObject *values;
         const PyArrayObject *indices;
         const PyArrayObject *indptr;
         mutable  std::vector<double>  degreeCache;
         int findnnz(int row, int col) const;
      public:
         SparseCSCNumpyStorage(int NumberRows, int NumberNonZero, 
               const PyArrayObject *nz_values,
               const PyArrayObject *row_indices,
               const PyArrayObject *col_starts
               );
         void updateDegrees() const;
   };
}

inline PRC::SparseCSCNumpyStorage::SparseCSCNumpyStorage( int NumberCols, int NumberNonZero, 
               const PyArrayObject *nz_values,
               const PyArrayObject *row_indices,
               const PyArrayObject *col_starts
               ):haveDegrees(false),n(NumberCols),nnz(NumberNonZero),values(nz_values),indices(row_indices),indptr(col_starts),degreeCache() 
{ 
   if ((nz_values == NULL)||(row_indices==NULL)||(col_starts==NULL))
         throw std::runtime_error("Attempted to create SparseCSCNumpyStorage with a Null pointer");
   if (nz_values->nd != 1 )
         throw std::runtime_error("Attempted to create SparseCSCNumpyStorage with a non zero value array that is not 1D.");
   if (row_indices->nd != 1 )
         throw std::runtime_error("Attempted to create SparseCSCNumpyStorage with  row indices array that is not 1D.");
   if (col_starts->nd != 1 )
         throw std::runtime_error("Attempted to create SparseCSCNumpyStorage with column starts array that is not 1D.");

   if (nz_values->dimensions[0] != nnz )
         throw std::runtime_error("Attempted to create SparseCSCNumpyStorage with a non zero value array that is not equal to nnz in size. ");
   if (row_indices->dimensions[0] != nnz )
         throw std::runtime_error("Attempted to create SparseCSCNumpyStorage with a row indices array that is not equal to nnz in size. ");
   if (col_starts->dimensions[0] != n+1 )
         throw std::runtime_error("Attempted to create SparseCSCNumpyStorage with column starts array that is not equal to n in size. ");
}

inline int PRC::SparseCSCNumpyStorage::rows() const { return n;}
inline int PRC::SparseCSCNumpyStorage::cols() const { return n;}
inline double  PRC::SparseCSCNumpyStorage::getCoeff(int row, int col) const 
{ 
   int loc = findnnz(row,col);
   if (loc < 0)
      return 0.0;
   return *(double *)(values->data + loc*values->strides[0]);
}

inline void PRC::SparseCSCNumpyStorage::setCoeff(int row, int col,double value) 
{ 
   int loc = findnnz(row,col);
   if (loc < 0)
         throw std::runtime_error("Attempting to add new non zero location to SparseCSCNumpyStorage.  Create in a different format and then compress to csc. ");
   *(double *)(values->data + loc*values->strides[0]) =  value;
}

inline double  PRC::SparseCSCNumpyStorage::degree(int id) const
{ 
   if (!haveDegrees)
      updateDegrees();
   return degreeCache[id];
}

inline 
void PRC::SparseCSCNumpyStorage::updateDegrees() const
{
   if (long(degreeCache.size()) != long(this->cols()))
      degreeCache.resize(this->cols());

   for(int c=0; c<this->cols();++c)
   {
      double sum=0;
      int cstart = *(int *)(indptr->data+ c*indptr->strides[0]);
      int cstop = *(int *)(indptr->data+ (c+1)*indptr->strides[0]);
      for (int i=cstart; i <cstop;++i)
         sum += *(double *)(values->data + i * values->strides[0]);
      degreeCache[c] = sum;
   }
   haveDegrees = true;
}

template<typename V> 
inline
double PRC::SparseCSCNumpyStorage::slope(int i, int j, const Ordering<V> &order) const
{ 
   assert(i>=-1 && long(i) <long(order.size()) && j >=0 && long(j) < long(order.size()) && "index out of range.");
   double sum = this->degree(order[j]) - order.getPrefixCoeff(order[j],*this);
   int cstart = *(int *)(indptr->data+ order[j]*indptr->strides[0]);
   int cstop = *(int *)(indptr->data+ (order[j]+1)*indptr->strides[0]);
   for (int loc=cstart; loc <cstop;++loc)
   {
      int r =  *(int *)(indices->data+ loc*indices->strides[0]); // current row
      const int p = order.invAt(r);
      if ((p>=0) && (p < i+1))
         sum -= *(double *)(values->data + loc * values->strides[0])  * 2;
   }
   return sum;
};

inline int  PRC::SparseCSCNumpyStorage::findnnz(int row, int col) const 
{
   assert( row >=0 && row <n && col >= 0 && col <n && "row,col index out of range");

   int cstart = *(int *)(indptr->data+ col*indptr->strides[0]);
   int cstop = *(int *)(indptr->data+ (col+1)*indptr->strides[0]);
   if (cstop-cstart < 16)
   {
      for (int loc=cstart; loc <cstop;++loc)
      {
         int r =  *(int *)(indices->data+ loc*indices->strides[0]); // current row
         if (r == row)
            return loc;
      }
   }
   else
   {  // do binary search
      cstop--; // inclusive index
      while (cstart < cstop)
      {
         int mid = cstart + (cstop-cstart)/2;
         if (*(int *)(indices->data+ mid*indices->strides[0]) < row)
            cstart = mid+1;
         else
            cstop = mid;
      }
      if ((cstart==cstop) && (*(int *)(indices->data+ cstart*indices->strides[0]) == row))
         return cstart;
   }
   return -1;
}

template<typename V> 
inline
void PRC::SparseCSCNumpyStorage::calcCuts(long startLoc, long mxALoc, long minLoc, long mxBLoc, long stopLoc, 
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

   for(long p = startLoc ; p <= stopLoc ; ++p)
   {
      long cstart = *(int *)(indptr->data+ order[p]*indptr->strides[0]);
      long cstop = *(int *)(indptr->data+ (order[p]+1)*indptr->strides[0]);
      for (long q=cstart; q <cstop;++q)
      {
         long v =  *(int *)(indices->data+ q*indices->strides[0]); // current row
         long loc = order.invAt(v);

         if ((loc <= p) || (loc<startLoc) || (loc>stopLoc))
            continue;  // only count edges once

         double value = *(double *)(values->data + q * values->strides[0]); 
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
