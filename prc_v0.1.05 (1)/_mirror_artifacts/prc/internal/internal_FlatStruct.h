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

/// \file  internal_FlatStruct.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_FLATSTRUCT_H__
#define INTERNAL_FLATSTRUCT_H__

#ifndef FLATSTRUCT_H__
#include<prc/FlatStruct.h>
#endif


#include<sstream>


inline
PRC::FlatStruct::FlatStruct():start(0),stop(0),type(LocalMin){}

inline
PRC::FlatStruct::FlatStruct(int begin, int end, FlatType t):start(begin),stop(end),type(t){}

inline
std::string  PRC::FlatStruct::Print() const
{
   std::ostringstream out;
   switch(type)
   {
      case LocalMin : out << "min "; 
                      break;
      case LocalMax : out << "max "; 
                      break;
   }
   out << start << " " << stop;
   return out.str();
}


inline
void PRC::FlatStruct::Print(std::ostream &out) const
{
   out << this->Print();
}

#endif
