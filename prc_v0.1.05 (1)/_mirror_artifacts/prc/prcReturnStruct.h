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

/// \file  prcReturnStruct.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef PRCRETURNSTRUCT_H__
#define PRCRETURNSTRUCT_H__


#ifndef PRCCOUNTSSTRUCT_H__
#include<prc/prcCountsStruct.h>
#endif

#ifndef PRCMETRICVALUES_H__
#include<prc/prcMetricValues.h>
#endif


#include<iostream>
#include<vector>

namespace PRC
{

   struct prcReturnStruct
   {
      // Warning: besides counts, most of these values are not calculated on a typical run.
      prcCountsStruct counts;
      double averageWeightedClusterQuality; // ratio of weighted averages
      double averageClusterQuality; // ratio of averages
      double weightedGeometricMean;
      double geometricMean;
      std::vector<prcMetricValues> mvalues;
      prcReturnStruct():counts(0,0,0),averageWeightedClusterQuality(0),averageClusterQuality(0),weightedGeometricMean(0),geometricMean(0), mvalues(0) {}
      prcReturnStruct(prcCountsStruct c, double awcq, double acq, double wgm, double gm,const std::vector<prcMetricValues> &mv):counts(c),averageWeightedClusterQuality(awcq),averageClusterQuality(acq), weightedGeometricMean(wgm),geometricMean(gm),mvalues(mv) {}
      std::ostream & Print(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string Print(const char *indent="", const char *sep="\n") const;
      std::ostream & PrintVerbose(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string PrintVerbose(const char *indent="", const char *sep="\n") const;
   };
}

#include<prc/internal/internal_prcReturnStruct.h>

#endif
