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

/// \file  prcCountsStruct.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef PRCCOUNTSSTRUCT_H__
#define PRCCOUNTSSTRUCT_H__

#include<iostream>

namespace PRC
{

   struct prcCountsStruct
   {
      long numberOfShifts;
      long numberOfInversions;
      long numberOfIterations;
      prcCountsStruct():numberOfShifts(0),numberOfInversions(0),numberOfIterations(0) {}
      prcCountsStruct(long shifts, long inversions,long iterations):numberOfShifts(shifts),numberOfInversions(inversions),numberOfIterations(iterations){}
      std::ostream & Print(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string  Print( const char *indent="", const char *sep="\n") const;
   };
}

#include<prc/internal/internal_prcCountsStruct.h>

#endif
