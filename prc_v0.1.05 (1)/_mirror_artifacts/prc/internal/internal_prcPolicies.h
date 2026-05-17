// This file is part of PRC, a C++ library for thin position clustering.
//
// Copyright (C) 2012 Doug Heisterkamp <drh@ieee.org>
//
// PRC is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 3 of the License, or (at your option) any later version.
//prcMetricEnum 
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

/// \file internal_prcPolicies.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_PRCPOLICIES_H__
#define INTERNAL_PRCPOLICIES_H__

#ifndef PRCPOLICIES_H__
#include<prc/prcPolicies.h>
#endif

#include<cassert>
#include<sstream>
#include<cstdlib>

/* added std:string Print for use with python binding */
inline
std::string PRC::tiloPolicyStruct::Print(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << indent << "TILO maxIterations = " << this->maxIterations << sep;
   out << indent << "TILO epsilon = " << this->tiloEpsilon << sep;
   return out.str();
}


inline
std::ostream & PRC::tiloPolicyStruct::Print(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->Print(indent,sep);
   return out;
}

inline
std::string  PRC::prcPolicyStruct::Print(const char *indent, const char *sep) const
{
   std::ostringstream out;
   std::string tmpIndent = indent;
   tmpIndent += indent;
   out << indent << "TILO Policies : "<< sep<< tiloPolicy.Print(tmpIndent.c_str(),sep);
   out << indent << "prcRecurseTILO = " << prcRecurseTILO << sep;
   out << indent << "reverseOrderOnSplit = " << reverseOrderOnSplit << sep;
   out << indent << "prcReturnRecurviseOrder = " << prcReturnRecursiveOrder << sep;
   out << indent << "prcMetric = " << metric << sep;
   out << indent << "prcRefineTILO = " << prcRefineTILO << sep;
   out << indent << "prcEvalAllMetrics = " << prcEvalAllMetrics << sep;
   out << indent << "prcReturnMetrics = " << prcReturnMetrics << sep;
   return out.str();
}

inline
std::ostream &  PRC::prcPolicyStruct::Print(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->Print(indent,sep);
   return out;
}

inline
const char * PRC::gaussAdjPolicyStruct::ModeName(GAUSSSIM_ADJ_MODE m)
{
   switch(m)
   {
      case GS_ADJ_THRESHOLD : return "GS_ADJ_THRESHOLD";
      case GS_ADJ_ALL :  return "GS_ADJ_ALL";
      default :
             break;
   }
   return "UNKNOWN MODE";
}

inline
const char *  PRC::prcMetricEnumName(prcMetricEnum m)
{
   switch(m)
   {
      case  0 : return "PinchRatio";
      case  1 : return "RelRatio";
      case  2 : return "CrossRatio";
      case  3 : return "NCut";
      default :
             break;
   }
   return "UNKNOWN MODE";
}


inline
PRC::prcMetricEnum  PRC::prcMetricEnumFromInt(int m)
{
   switch(m)
   {
      case  0 : return PinchRatio;
      case  1 : return RelRatio;
      case  2 : return CrossRatio;
      case  3 : return NCut;
      default:
          assert(false && "Unknown prcMetricEnum");
   }
   return PinchRatio;
}


inline
PRC::GAUSSSIM_ADJ_MODE  PRC::gaussAdjPolicyStruct::ModeFromInt(int m)
{
   switch(m)
   {
      case  0 : return GS_ADJ_THRESHOLD;
      case  1 : return GS_ADJ_ALL;
      default:
          assert(false && "Unknown KNN ADJ MODE");
   }
   return  GS_ADJ_THRESHOLD;
}


inline
std::string PRC::gaussAdjPolicyStruct::Print(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << indent << "mode = " << ModeName(mode) << sep;
   out << indent << "sigma = " << sigma << sep;
   out << indent << "threshold = " << threshold << sep;
   return out.str();
}

inline
std::ostream & PRC::gaussAdjPolicyStruct::Print(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->Print(indent,sep);
   return out;
}

inline
const char * PRC::knnAdjPolicyStruct::ModeName(KNN_ADJ_MODE m)
{
   switch(m)
   {
      case KNN_EITHER_ADJ_ONE : return "KNN_EITHER_ADJ_ONE";
      case KNN_BOTH_ADJ_ONE :  return "KNN_BOTH_ADJ_ONE";
      case KNN_BOTH_EITHER_ONE_ONEHALF : return "KNN_BOTH_EITHER_ONE_ONEHALF";
      case KNN_EITHER_ADJ_GAUSS : return "KNN_EITHER_ADJ_GAUSS";
      default :
             break;
   }
   return "UNKNOWN MODE";
}

inline
PRC::KNN_ADJ_MODE PRC::knnAdjPolicyStruct::ModeFromInt(int m)
{
   switch(m)
   {
      case  0 : return KNN_EITHER_ADJ_ONE;
      case  1 : return KNN_BOTH_ADJ_ONE;
      case  2 : return  KNN_BOTH_EITHER_ONE_ONEHALF;
      case  3 : return KNN_EITHER_ADJ_GAUSS;
      default:
          assert(false && "Unknown KNN ADJ MODE");
   }
   return  KNN_EITHER_ADJ_GAUSS;
}


inline
std::string PRC::knnAdjPolicyStruct::Print(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << indent << "mode = " << ModeName(mode) << sep;
   out << indent << "k = " << k << sep;
   out << indent << "sigma = " << sigma << sep;
   return out.str();
}


inline
std::ostream & PRC::knnAdjPolicyStruct::Print(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->Print(indent,sep);
   return out;
}

inline
int PRC::knnAdjPolicyStruct::checkCmdLineOption(int i, int argc,const char *argv[])
{
   int consumed = 0;
   std::istringstream line;
   if ((i>= argc)||(argv[i] == NULL) || (argv[i][0] != '-') || argv[i][1] != '-')
      return 0;
   std::string optname = &(argv[i][2]);
   if (optname == "knnAdjMode")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer mode for the knn adj policy." << std::endl;
         exit(-1);
      }
      if ((tmp >=0)&&(tmp <=3))
         this->mode = knnAdjPolicyStruct::ModeFromInt(tmp);
      else
      {
         std::cerr << "Invalid knn adj mode : "<< tmp << std::endl;
         exit(-1);
      }
      consumed=2;
   }
   else if (optname == "knnAdjK")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer k for knn adj policy." << std::endl;
         exit(-1);
      }
      if (tmp >=-1)
         this->k = tmp;
      else
      {
         std::cerr << "Invalid knn k value : "<< tmp << std::endl;
         exit(-1);
      }
      consumed=2;
   }
   else if (optname == "knnAdjSigma")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      double tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a double sigma for knn adj policy." << std::endl;
         exit(-1);
      }
      this->sigma= tmp;
      consumed=2;
   }
   return consumed;
}


inline
int PRC::gaussAdjPolicyStruct::checkCmdLineOption(int i, int argc,const char *argv[])
{
   int consumed = 0;
   std::istringstream line;
   if ((i>= argc)||(argv[i] == NULL) || (argv[i][0] != '-') || argv[i][1] != '-')
      return 0;
   std::string optname = &(argv[i][2]);
   if (optname == "gausssimAdjMode")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer mode for the gaussian similarity adj policy." << std::endl;
         exit(-1);
      }
      if ((tmp >=0)&&(tmp <=1))
         this->mode = gaussAdjPolicyStruct::ModeFromInt(tmp);
      else
      {
         std::cerr << "Invalid gaussian similarity adj mode : "<< tmp << std::endl;
         exit(-1);
      }
      consumed=2;
   }
   else if (optname == "gausssimAdjSigma")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      double tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a double sigma for gauss sim adj policy." << std::endl;
         exit(-1);
      }
      this->sigma= tmp;
      consumed=2;
   }
   else if (optname == "gausssimAdjThreshold")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      double tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a double threshold for gauss sim adj policy." << std::endl;
         exit(-1);
      }
      this->threshold= tmp;
      consumed=2;
   }
   return consumed;
}


inline
int PRC::prcPolicyStruct::checkCmdLineOption(int i, int argc,const char *argv[])
{
   int consumed = 0;
   std::istringstream line;
   if ((i>= argc)||(argv[i] == NULL) || (argv[i][0] != '-') || argv[i][1] != '-')
      return 0;
   std::string optname = &(argv[i][2]);
   consumed = this->tiloPolicy.checkCmdLineOption(i,argc,argv);

   if (consumed > 0) 
      return consumed;

   if (optname == "policyPRCRecurseTILO")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean for prcRecurseTILO policy." << std::endl;
         exit(-1);
      }
      this->prcRecurseTILO = tmp;
      consumed=2;
   }
   else if (optname == "policyReverseOrderOnSplit")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean for reverse order on split policy." << std::endl;
         exit(-1);
      }
      this->reverseOrderOnSplit = tmp;
      consumed=2;
   }
   else if (optname == "policyReturnRecursiveOrder")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean for return reverse recursive order." << std::endl;
         exit(-1);
      }
      this->prcReturnRecursiveOrder = tmp;
      consumed=2;
   }
   else if (optname == "policyPRCMetric")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer prcMetric for the policy." << std::endl;
         exit(-1);
      }
      if ((tmp >=0) && (tmp <=3))
         this->metric = prcMetricEnum(tmp);
      else
      {
         std::cerr << "Invalid prcMetric : "<< tmp << " : should be in 0..4 range"<< std::endl;
         exit(-1);
      }
      consumed=2;
   }
   else if (optname == "policyRefineTILO")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean for refining TILO policy." << std::endl;
         exit(-1);
      }
      this->prcRefineTILO = tmp;
      consumed=2;
   }
   else if (optname == "policyEvalAllMetrics")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean for prcEvalAllMetrics." << std::endl;
         exit(-1);
      }
      this->prcEvalAllMetrics = tmp;
      consumed=2;
   }
   else if (optname == "policyReturnMetrics")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean for prcReturnMetrics." << std::endl;
         exit(-1);
      }
      this->prcReturnMetrics = tmp;
      consumed=2;
   }
   return consumed;
}

inline
int PRC::tiloPolicyStruct::checkCmdLineOption(int i, int argc,const char *argv[])
{
   int consumed = 0;
   std::istringstream line;
   if ((i>= argc)||(argv[i] == NULL) || (argv[i][0] != '-') || argv[i][1] != '-')
      return 0;
   std::string optname = &(argv[i][2]);
   if (optname == "tiloMaxIteration")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      long tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a long max iteration for the policy." << std::endl;
         exit(-1);
      }
      if (tmp >=0)
         this->maxIterations = tmp;
      else
      {
         std::cerr << "Invalid max iterations : "<< tmp << std::endl;
         exit(-1);
      }
      consumed=2;
   }
   else if (optname == "tiloEpsilon")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      double tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a double tiloEpsilon for the policy." << std::endl;
         exit(-1);
      }
      if (tmp >=0)
         this->tiloEpsilon = tmp;
      else
      {
         std::cerr << "Invalid max iterations : "<< tmp << std::endl;
         exit(-1);
      }
      consumed=2;
   }
   return consumed;
}


inline
std::string PRC::prcPolicyStruct::cmdLineUsage(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << this->tiloPolicy.cmdLineUsage(indent,sep);
   out << indent << "--policyPRCRecurseTILO   boolean"<<sep;
   out << indent << "--policyReverseOrderOnSplit   boolean"<<sep;
   out << indent << "--policyReturnRecursiveOrder   boolean"<<sep;
   out << indent << "--policyPRCMetric   integer  // 0 -> PinchRatio"<<sep;
   out << indent << "                             // 1 -> RelRatio"<<sep;
   out << indent << "                             // 2 -> CrossRatio"<<sep;
   out << indent << "                             // 3 -> NCut"<<sep;
   out << indent << "--policyRefineTILO   boolean (default false)"<<sep;
   out << indent << "--policyEvalAllMetrics   boolean (default false)"<<sep;
   out << indent << "--policyReturnMetrics    boolean (default false)"<<sep;
   return out.str();
}

inline
void PRC::prcPolicyStruct::cmdLineUsage(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->cmdLineUsage(indent,sep);
}

inline
std::string PRC::tiloPolicyStruct::cmdLineUsage(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << indent << "--tiloMaxIteration  long"<<sep;
   out << indent << "--tiloEpsilon  double"<<sep;
   return out.str();
}

inline
void PRC::tiloPolicyStruct::cmdLineUsage(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->cmdLineUsage(indent,sep);
}

inline
std::string PRC::gaussAdjPolicyStruct::cmdLineUsage(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << indent << "--gausssimAdjMode   int  // 0->GS_ADJ_THRESHOLD, 1->GS_ADJ_ALL"<<sep;
   out << indent << "--gausssimAdjSigma   double  // use -1 to calculate from knn distance"<<sep;
   out << indent << "--gausssimAdjThreshold   double  // set values less than this to zero if thresholding similarity"<<sep;
   return out.str();
}

inline
void PRC::gaussAdjPolicyStruct::cmdLineUsage(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->cmdLineUsage(indent,sep);
}

inline
std::string PRC::knnAdjPolicyStruct::cmdLineUsage(const char *indent, const char *sep) const
{
   std::ostringstream out;
   out << indent << "--knnAdjMode int  // 0->KNN_EITHER_ADJ_ONE"<<sep;
   out << indent << "                  // 1->KNN_BOTH_ADJ_ONE"<<sep;
   out << indent << "                  // 2->KNN_BOTH_EITHER_ONE_ONEHALF"<<sep;
   out << indent << "                  // 3->KNN_EITHER_ADJ_GAUSS (default)"<<sep;
   out << indent << "--knnAdjK  int  // number of nearest neighbors, use -1 to calculate as log(n)+1"<<sep;
   out << indent << "--knnAdjSigma   double  // for Gaussian similarity to knn."<<sep;
   out << indent << "                        //  Use -1 to estimate from average knn distance."<<sep;
   return out.str();
}
inline
void PRC::knnAdjPolicyStruct::cmdLineUsage(std::ostream &out, const char *indent, const char *sep) const
{
   out << this->cmdLineUsage(indent,sep);
}
#endif
