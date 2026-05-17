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

/// \file pythonHelpers.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef PYHTONHELPERS_H__
#define PYHTONHELPERS_H__


#ifndef FLATSTRUCT_H__
#include "FlatStruct.h"
#endif


#ifndef BOUNDARYOBJECT_H__
#include "BoundaryObject.h"
#endif

namespace PRC
{
   // functions and/or classes that help the autogeneration of the python bindings
   

   FlatStructVec findLocalMinAndMax(const BoundaryObject &b);
}


/*! \brief Helper function to call findLocalMinAndMax method of Boundary Object
 *
 * Current pybindgen auto gen is wrapping std::vectors that makes a copy and does
 * not allow the reference to be changed in place.  This function is for use until
 * a proper binding is created.
 */
inline
PRC::FlatStructVec PRC::findLocalMinAndMax(const PRC::BoundaryObject &b)
{
   FlatStructVec m;
   b.findLocalMinAndMax(m);
   return m;
}

#endif
