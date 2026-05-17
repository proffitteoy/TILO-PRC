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

/// \file  internal_prcCountsStruct.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef INTERNAL_PRCCOUNTSSTRUCT_H__
#define INTERNAL_PRCCOUNTSSTRUCT_H__

#ifndef PRCCOUNTSSTRUCT_H__
#include<prc/prcCountsStruct.h>
#endif

#include<sstream>

inline
std::string PRC::prcCountsStruct::Print( const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << indent << "number of shifts =  " << numberOfShifts << sep;
   out << indent << "number of inversions =  " <<numberOfInversions  << sep;
   out << indent << "number of iterations =  " <<numberOfIterations  << sep;
   return out.str();
};


inline
std::ostream & PRC::prcCountsStruct::Print(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->Print(indent,sep);
   return out;
};


#endif
