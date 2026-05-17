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
// PRC. If not, see <http://www.gnu.org/licenses/>.

// The following lines uses subversion's keyword expansion to insert the
// last time the file was modified and by who.

/// \file  internal_prcReturnStruct.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef INTERNAL_PRCRETURNSTRUCT_H__
#define INTERNAL_PRCRETURNSTRUCT_H__

#ifndef PRCRETURNSTRUCT_H__
#include<prc/prcReturnStruct.h>
#endif

#include<sstream>

inline
std::string PRC::prcReturnStruct::Print(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << counts.Print(indent,sep);
   return out.str();
};

inline
std::ostream & PRC::prcReturnStruct::Print(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->Print(indent,sep);
   return out;
};


inline
std::string PRC::prcReturnStruct::PrintVerbose(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << counts.Print(indent,sep);
   out << indent << "Warning: following values may not be calculated on every run:" << sep;
   out << indent << "average weighted cluster quality =  " << averageWeightedClusterQuality << sep;
   out << indent << "average cluster quality =  " << averageClusterQuality << sep;
   out << indent << "weighted geometric mean =  " << weightedGeometricMean << sep;
   out << indent << "geometric mean =  " << geometricMean << sep;
   if (mvalues.size() > 0) {
      out << indent ;
      for(std::vector<prcMetricValues>::const_iterator p = mvalues.begin(); p != mvalues.end();++p) {
         out << "|"<< p->Print("",sep);
      }
   }
   return out.str();
};

inline
std::ostream & PRC::prcReturnStruct::PrintVerbose(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->PrintVerbose(indent,sep);
   return out;
};


#endif
