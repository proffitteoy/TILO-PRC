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

/// \file  prcMetricValues.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef PRCMETRICVALUES_H__
#define PRCMETRICVALUES_H__

#include<iostream>

namespace PRC
{

  struct prcMetricValues
   {
      double mincut;
      double minmaxcutA;
      double minmaxcutB;
      double intA;
      double extA;
      double intB;
      double extB;
      double dA;
      double dB;
      double pinchRatio;
      double ncut;
      double relA;
      double relB;
      double relRatio;
      double crossRatio;
      int loc;
      prcMetricValues():mincut(0),minmaxcutA(0),minmaxcutB(0),intA(0),extA(0),intB(0),extB(0),dA(0),dB(0),
      pinchRatio(0), ncut(0), relA(0), relB(0), relRatio(0), crossRatio(0), loc(-1) {}
      std::ostream & Print(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string Print(const char *indent="", const char *sep="\n") const;
   };

}

#include<prc/internal/internal_prcMetricValues.h>

#endif
