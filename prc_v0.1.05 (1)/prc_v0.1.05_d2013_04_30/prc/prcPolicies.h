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

/// \file prcPolicies.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef PRCPOLICIES_H__
#define PRCPOLICIES_H__

#include<iostream>
#include<iterator>
#include<string>

namespace PRC
{
   enum KNN_ADJ_MODE {KNN_EITHER_ADJ_ONE=0, KNN_BOTH_ADJ_ONE=1, KNN_BOTH_EITHER_ONE_ONEHALF=2, KNN_EITHER_ADJ_GAUSS=3};

   enum GAUSSSIM_ADJ_MODE {GS_ADJ_THRESHOLD=0,GS_ADJ_ALL=1}; // TODO: add more modes
   
   enum prcMetricEnum { 
      PinchRatio=0,        // local min boundary over min local max boundary 
      RelRatio=1,          //  relative ratio of cut a2,a1 and a2,b
      CrossRatio=2,          //  cross ratio of cuts a2,a1 and a2,b, b1,b2, b1,a
      NCut=3 //  normalize cut
   };

   prcMetricEnum  prcMetricEnumFromInt(int m);
   const char *  prcMetricEnumName(prcMetricEnum m);

   struct tiloPolicyStruct
   {
      long maxIterations;
      double tiloEpsilon;
      tiloPolicyStruct(): maxIterations(10000000),tiloEpsilon(1e-12){} 
      std::ostream &Print(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string Print(const char *indent="", const char *sep="\n") const;
      int checkCmdLineOption(int i, int argc,const char *argv[]);
      void cmdLineUsage(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string cmdLineUsage(const char *indent="", const char *sep="\n") const;
   };


   struct prcPolicyStruct
   {
      tiloPolicyStruct  tiloPolicy; 
      prcMetricEnum  metric;
      bool prcRecurseTILO;  ///!< rerun TILO on partitions to update the thick width value when making splits
      bool reverseOrderOnSplit;  ///!< reverse order on second partition of a split ... may decrease later shifts when running TILO
      bool prcReturnRecursiveOrder; ///! if false, original TILO order is returned. if true, the order at the end of the recursive splitting is returned.
      bool prcRefineTILO; ///! if true, the lexicographic order is completely refined.  If false, TILO stops as soon as the local min/max are determined.
      bool prcEvalAllMetrics; ///! if true, calculate all metrics, other calculate only the one being used for splitting.
      bool prcReturnMetrics; ///! if true, returns metric values at each split location.
      prcPolicyStruct(): tiloPolicy(),metric(PinchRatio),prcRecurseTILO(false),reverseOrderOnSplit(false),prcReturnRecursiveOrder(false),prcRefineTILO(false),prcEvalAllMetrics(false),prcReturnMetrics(false){} 
      std::ostream &Print(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string Print(const char *indent="", const char *sep="\n") const;
      int checkCmdLineOption(int i, int argc,const char *argv[]);
      void cmdLineUsage(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string cmdLineUsage(const char *indent="", const char *sep="\n") const;
   };

   struct gaussAdjPolicyStruct
   {
      GAUSSSIM_ADJ_MODE mode;
      double sigma;
      double threshold;
      gaussAdjPolicyStruct(): mode(GS_ADJ_THRESHOLD),sigma(-1),threshold(1e-10){}
      static const char * ModeName(GAUSSSIM_ADJ_MODE m);
      static GAUSSSIM_ADJ_MODE ModeFromInt(int m);
      std::ostream &Print(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string Print(const char *indent="", const char *sep="\n") const;
      int checkCmdLineOption(int i, int argc,const char *argv[]);
      void cmdLineUsage(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string cmdLineUsage(const char *indent="", const char *sep="\n") const;
   };

   struct knnAdjPolicyStruct
   {
      KNN_ADJ_MODE mode;
      int k;
      double sigma;
      knnAdjPolicyStruct(): mode(KNN_EITHER_ADJ_GAUSS),k(-1),sigma(-1){}
      static const char * ModeName(KNN_ADJ_MODE m);
      static KNN_ADJ_MODE ModeFromInt(int m);
      std::ostream & Print(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string Print(const char *indent="", const char *sep="\n") const;
      int checkCmdLineOption(int i, int argc,const char *argv[]);
      void cmdLineUsage(std::ostream &out, const char *indent="", const char *sep="\n") const;
      std::string cmdLineUsage(const char *indent="", const char *sep="\n") const;
   };
}

#include<prc/internal/internal_prcPolicies.h>

#endif
