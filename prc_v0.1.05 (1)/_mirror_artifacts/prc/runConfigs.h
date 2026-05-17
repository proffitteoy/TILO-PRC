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

/// \file runConfigs.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef RUNCONFIGS_H__
#define RUNCONFIGS_H__

#include<iostream>
#include<iterator>

namespace PRC
{
   enum TagModeEnum {NO_TAGS=0,FRONT_TAGS=1,REAR_TAGS=2};
   enum FileStructureEnum { POINT_DATA=0, ADJACENCY_DATA=1};
   enum PointSimilarityEnum {UNDEFINED_ADJ_SIM=0,GAUSS_ADJ_SIM=1,KNN_ADJ_SIM=2,PRECALC_ADJ_SIM=3};

   TagModeEnum TagFromInt(int v);
   const char * EnumName(TagModeEnum v);
   
   FileStructureEnum FileStructureEnumFromInt(int v);
   const char * EnumName(FileStructureEnum v);
   
   PointSimilarityEnum PointSimilarityFromInt(int v);
   const char * EnumName(PointSimilarityEnum v);

   struct runConfigStruct
   {
      long seed;
      int numberOfPartitions;
      int verboseLevel;
      bool useTransduction;
      std::string outputLabelSuffix;
      std::string outputOrderSuffix;
      std::string infoSuffix;
      bool saveOrder;
      bool saveLabels;
      bool seedSuffix;
      bool useMultiLevelPRC;
      std::string initOrderFile;
      std::string initLabelsFile;
      int numberInitOrderings;
      bool saveMultipleRuns;

      runConfigStruct():seed(0),numberOfPartitions(2),verboseLevel(1),useTransduction(false),
                  outputLabelSuffix("_part_"),outputOrderSuffix("_tilo_"),infoSuffix(""),saveOrder(true),
                  saveLabels(true),seedSuffix(false),useMultiLevelPRC(false),initOrderFile(""),initLabelsFile(""),
                  numberInitOrderings(1),saveMultipleRuns(false){} 
      std::ostream &Print(std::ostream &out, const char *indent="");
      std::string Print(const char *indent="");
      int checkCmdLineOption(int i, int argc,const char *argv[]);
      void cmdLineUsage(std::ostream &out, const char *indent="");
   };

   struct pointDataConfigStruct
   {
      TagModeEnum tagLoc;
      PointSimilarityEnum simType;
      pointDataConfigStruct():tagLoc(NO_TAGS),simType(GAUSS_ADJ_SIM){} 
      std::ostream &Print(std::ostream &out, const char *indent="");
      std::string Print(const char *indent="");
      int checkCmdLineOption(int i, int argc,const char *argv[]);
      void cmdLineUsage(std::ostream &out, const char *indent="");
   };

   struct adjDataConfigStruct
   {
      int nodeOffset;
      adjDataConfigStruct():nodeOffset(1){} 
      std::ostream &Print(std::ostream &out, const char *indent="");
      std::string Print(const char *indent="");
      int checkCmdLineOption(int i, int argc,const char *argv[]);
      void cmdLineUsage(std::ostream &out, const char *indent="");
   };



   struct dataConfigStruct
   {
      std::string inputFileName;
      FileStructureEnum fileType;
      bool useSparseMatrix;
      bool commaSeparated;
      std::string commentDelimiter;
      pointDataConfigStruct pointDataConfig;
      adjDataConfigStruct adjDataConfig;
      dataConfigStruct():inputFileName(""),fileType(POINT_DATA),useSparseMatrix(true),commaSeparated(false),commentDelimiter("#"),
                       pointDataConfig(),adjDataConfig() {} 
      std::ostream &Print(std::ostream &out, const char *indent="");
      std::string Print(const char *indent="");
      int checkCmdLineOption(int i, int argc,const char *argv[]);
      void cmdLineUsage(std::ostream &out, const char *indent="");
   };
}

#include<prc/internal/internal_runConfigs.h>

#endif
