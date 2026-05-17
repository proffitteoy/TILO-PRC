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

/// \file  internal_prcMetricValues.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $

#ifndef INTERNAL_PRCMETRICVALUES_H__
#define INTERNAL_PRCMETRICVALUES_H__

#ifndef PRCMETRICVALUES_H__
#include<prc/prcMetricValues.h>
#endif

#include<sstream>

inline
std::string PRC::prcMetricValues::Print(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << indent << "mincut " << this->mincut << sep;
   out << indent <<  "minmaxcutA " << this->minmaxcutA << sep;
   out << indent <<  "minmaxcutB " << this->minmaxcutB << sep;
   out << indent <<  "intA " << this->intA << sep;
   out << indent <<  "extA " << this->extA << sep;
   out << indent <<  "intB " << this->intB << sep;
   out << indent << "extB " << this->extB << sep;
   out << indent <<  "dA " << this->dA << sep;
   out << indent <<  "dB " << this->dB << sep;

   out << indent <<  "pinchRatio " << this->pinchRatio << sep ;
   out << indent <<  "ncut " << this->ncut << sep ;
   out << indent <<  "relA " << this->relA << sep ;
   out << indent <<  "relB " << this->relB << sep ;
   out << indent <<  "relRatio " << this->relRatio << sep ;
   out << indent <<  "crossRatio " << this->crossRatio << sep ;
   out << indent <<  "loc " << this->loc  ;
   return out.str();
};


inline
std::ostream & PRC::prcMetricValues::Print(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->Print(indent,sep);
   return out;
};


#endif
