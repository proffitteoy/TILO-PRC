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

/// \file purity.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef PRC_PURITY_H__
#define PRC_PURITY_H__

#include<map>


namespace PRC
{
   template<typename T, typename S> double calcPurity(const T & predlabels , const S &trueLabels);
}

namespace internalPRC
{
   template< template<typename , typename > class C> struct pairValueCMP 
   {
      template<typename K,typename V>
      bool operator()(const C<K,V> &left, const C<K,V> & right) const { return left.second < right.second; }
      template<typename K,typename V>
      bool operator()(const C<K,V> &left, const V & right) const { return left.second < right; }
   };
}


template<typename T, typename S> inline double PRC::calcPurity(const T & predLabels , const S &trueLabels)
{
   //first determine the class label of each partition using majority vote
   typedef std::map<int,int> tcmap;
   typedef std::map<int,tcmap> ctcmap;
   ctcmap d;

   for (int i = 0; i < predLabels.size(); ++i)
   {
      ctcmap::iterator p = d.find(predLabels[i]);
      if ( p != d.end())
      {
         tcmap::iterator q = p->second.find(trueLabels[i]);
         if ( q != p->second.end())
            q->second += 1;
         else
            p->second[trueLabels[i]] = 1;
      }
      else
      {  // first items of this predicted class
         tcmap tmpMap;
         tmpMap[trueLabels[i]] = 1;
         d[predLabels[i]] = tmpMap;
      }
   }

   int maxCountSum = 0;

   for (ctcmap::iterator p=d.begin(); p != d.end(); ++p)
   {
      tcmap::iterator q = std::max_element(p->second.begin(),p->second.end(), internalPRC::pairValueCMP<std::pair >());
      if (q != p->second.end())
         maxCountSum += q->second;
   }

   return double(maxCountSum)/predLabels.size();

}

#endif
