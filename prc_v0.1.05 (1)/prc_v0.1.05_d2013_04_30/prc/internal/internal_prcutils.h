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

/// \file internal_prcutils.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_PRCUTILS_H__
#define INTERNAL_PRCUTILS_H__

#ifndef PRCUTILS_H__
#include<prc/prcutils.h>
#endif

#include<iterator>
#include<fstream>
#include<string>
#include<sstream>


template<typename V>
inline void PRC::printStdVec(std::ostream &out,const std::vector<V> &a)
{
   std::copy(a.begin(),a.end(), std::ostream_iterator<V>(out," "));
}

template<typename V>
inline void PRC::printStdVec(std::ostream &out,const std::vector<std::vector<V> > &a,const std::string &indent)
{
   for(typename std::vector<std::vector<V> >::const_iterator p=a.begin();p!=a.end;++p)
   {
      out << indent;
      std::copy(p->begin(),p->end(), std::ostream_iterator<V>(out," "));
      out << std::endl;
   }
}

template<typename V,std::size_t  N> 
inline void PRC::printStdVec(std::ostream &out,const std::vector<PRC::array<V,N> > &a,const std::string &indent)
{
   for(typename std::vector<PRC::array<V,N> >::const_iterator p=a.begin();p!=a.end();++p)
   {
      out << indent;
      for(std::size_t  i=0; i<N-1; i++)
         out << (*p)[i] << " ";
      out << (*p)[N-1] << std::endl;
   }
}


template<class T> 
inline
typename T::value_type *  PRC::stdVecData(T &v)
{
#ifdef _MSC_VER
#if (_MSC_VER > 1500)
      return v.data();  // MSVC 2010 has data()
#else
      return  &(v[0]);
#endif
#else
      return v.data();  // MSVC 2010 has data()
#endif
}

template<typename T> 
inline
const typename T::value_type *  PRC::stdVecData(const T &v)
{
#ifdef _MSC_VER
#if (_MSC_VER > 1500)
      return v.data();  // MSVC 2010 has data()
#else
      return  &(v[0]);
#endif
#else
      return v.data();  // MSVC 2010 has data()
#endif
}



inline
bool PRC::loadtxt(std::ifstream &fin,Eigen::MatrixXd &result)
{
   std::vector<std::vector<double> > d;
   std::vector<double> v;
   std::string buf;
   std::istringstream line;
   int featureDim = -1;
   while (std::getline(fin,buf))
   {   
      line.clear();
      v.clear();
      line.str(buf);
      double tmpD = 0.0;
      while (line)
      {  
         if (line>> tmpD)
              v.push_back(tmpD);
      }
      if (featureDim < 0)
         featureDim = int(v.size());
      else
         if (long(featureDim) != long(v.size()))
            return false;
      d.push_back(v);
   }
   result.resize(d.size(),featureDim);
   for(int row=0;row<result.rows();++row)
      for(int col=0;col<result.cols();++col)
         result(row,col) = d[row][col];
   return true;
}

inline
bool loadSparseGraph(std::ifstream &fin,Eigen::SparseMatrix<double,Eigen::ColMajor,int> &result,int nodeOffset, Eigen::MatrixXd &vertexWeights)
{
   std::string buf;
   std::istringstream line;
   int numNodes = 0;
   int numEdges = 0;
   int format = 0;
   int ncon = 0;

   if (!std::getline(fin,buf))
         return false;
   line.clear();
   line.str(buf);
   if (!(line >> numNodes >> numEdges))
      return false;
   line >> format;
   bool fmtVSizes = format >= 100;
   bool fmtVWeights = format%100 >= 10;
   bool fmtEWeights = format%10 >= 1;
   line >> ncon;

   int vwSize = 2; 
   if (ncon>0)
      vwSize += ncon-1;
   vertexWeights.resize(numNodes,vwSize);
   vertexWeights.fill(1.0);

   std::vector<Eigen::Triplet<double> > tripletList;
   tripletList.reserve(3*numEdges);
   result.resize(numNodes,numNodes);
   result.setZero();
   int count = 0;
   int tmpNode;
   int wCount =0;
   double tmpW;
   while (std::getline(fin,buf))
   {   
      if (count >= numNodes)
         break;
      line.clear();
      line.str(buf);
      wCount = 0;

      if (fmtVSizes)
      {
         if (! (line >> vertexWeights(count,wCount++)))
         {
            std::cerr << "Invalid line in graph file.  Expected a vertex size on line " << count+1<<std::endl;
            return false;
         }
      }

      if (fmtVWeights)
      {
         for (int k=0; k < std::max(1,ncon); ++k)
         {
            if (! (line >> vertexWeights(count,wCount++)))
            {
               std::cerr << "Invalid line in graph file.  Expected a vertex weight " << k<<" on line " << count+1<<std::endl;
               return false;
            }
         }
      }

      while (line>>tmpNode)
      {  
         tmpW = 1.0;
         tmpNode -= nodeOffset; // graculs starts indexing at 1 in external file format
         if (fmtEWeights)
            if (!(line>> tmpW)) return false;
         if (tmpNode > numNodes)
         {
            std::cerr << "node id out of range" << std::endl;
            return false;
         }
         tripletList.push_back(Eigen::Triplet<double>(count,tmpNode,tmpW));
      }
      ++count;
   }
   result.setFromTriplets(tripletList.begin(),tripletList.end());
   return true;
}


/*! read file in adjacent list format */
inline
bool loadGraph(std::ifstream &fin,Eigen::MatrixXd &result, int nodeOffset, Eigen::MatrixXd &vertexWeights)
{
   std::string buf;
   std::istringstream line;
   int numNodes = 0;
   int numEdges = 0;
   int format = 0;
   int ncon = 0;

   if (!std::getline(fin,buf))
         return false;
   line.clear();
   line.str(buf);
   if (!(line >> numNodes >> numEdges))
      return false;
   line >> format;

   bool fmtVSizes = format >= 100;
   bool fmtVWeights = format%100 >= 10;
   bool fmtEWeights = format%10 >= 1;
   line >> ncon;

   int vwSize = 2; 
   if (ncon>0)
      vwSize += ncon-1;
   vertexWeights.resize(numNodes,vwSize);
   vertexWeights.fill(1.0);


   result.setZero(numNodes,numNodes);
   int count = 0;
   int tmpNode;
   int wCount =0;
   double tmpW;

   while (std::getline(fin,buf))
   {   

      if (count >= numNodes)
         break;
      line.clear();
      line.str(buf);
      wCount = 0;
      if (fmtVSizes)
      {
         if (! (line >> vertexWeights(count,wCount++)))
         {
            std::cerr << "Invalid line in graph file.  Expected a vertex size on line " << count+1<<std::endl;
            return false;
         }
      }

      if (fmtVWeights)
      {
         for (int k=0; k < std::max(1,ncon); ++k)
         {
            if (! (line >> vertexWeights(count,wCount++)))
            {
               std::cerr << "Invalid line in graph file.  Expected a vertex weight " << k<<" on line " << count+1<<std::endl;
               return false;
            }
         }
      }


      while (line>>tmpNode)
      {  
         tmpW = 1.0;
         tmpNode -= nodeOffset; // graculs starts indexing at 1 in external file format
         if (fmtEWeights)
            if (!(line>> tmpW)) return false;
         if (tmpNode >= numNodes)
         {
            std::cerr << "node id out of range" << std::endl;
            return false;
         }
         result(count,tmpNode) = tmpW;
      }
      ++count;
   }
   return true;
}

inline
bool PRC::loadtxt(std::ifstream &fin,Eigen::VectorXi &result)
{
   std::vector<int> d;
   int tmpI=0;
   while (fin>>tmpI) 
      d.push_back(tmpI);
   result.resize(d.size());
   std::copy(d.begin(),d.end(),result.data());
   return d.size() > 0; 
}

inline
bool PRC::loadtxt(std::ifstream &fin,Eigen::VectorXd &result)
{
   std::vector<double> d;
   double tmpD=0;
   while (fin>>tmpD) 
      d.push_back(tmpD);
   result.resize(d.size());
   std::copy(d.begin(),d.end(),result.data());
   return d.size() > 0; 
}

#endif
