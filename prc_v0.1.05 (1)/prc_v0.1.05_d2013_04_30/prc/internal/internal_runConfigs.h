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

/// \file internal_runConfigs.h
///
/// Last changed by = $Author: drh $
/// Last changed date = $Date: 2013-04-30 19:05:53 -0500 (Tue, 30 Apr 2013) $
/// Lastest revision = $Revision: 149 $


#ifndef INTERNAL_RUNCONFIGS_H__
#define INTERNAL_RUNCONFIGS_H__

#ifndef RUNCONFIGS_H__
#include<prc/runConfigs.h>
#endif

#include<cstdlib>
#include<sstream>


inline PRC::TagModeEnum PRC::TagFromInt(int v)
{
   switch(v)
   {
      case 1 : return FRONT_TAGS;
      case -1: return REAR_TAGS;
      case 0: return NO_TAGS;
      default:
         std::cerr << "Invalid Tag location : << " << v << ", expected 0,1,or -1." << std::endl;
   }
   return NO_TAGS;
}

inline
const char * PRC::EnumName(TagModeEnum v)
{
   switch(v)
   {
      case FRONT_TAGS :  return "FRONT_TAGS";
      case REAR_TAGS: return "REAR_TAGS";
      case NO_TAGS: return "NO_TAGS";
      default:
              break;
   }
   return "Unknown tag location"; 
}

inline PRC::FileStructureEnum PRC::FileStructureEnumFromInt(int v)
{
   FileStructureEnum res = POINT_DATA; 
   switch(v)
   {
      case 0 : res= POINT_DATA; 
					break;
      case 1:  res = ADJACENCY_DATA;
					break;
      default:
         std::cerr << "Invalid FileStructureEnum : << " << v << ", expected 0 or 1." << std::endl;
         exit(-1);
   }
   return res; 
}
inline
const char * PRC::EnumName(FileStructureEnum v)
{
   switch(v)
   {
      case POINT_DATA :  return "POINT_DATA";
      case ADJACENCY_DATA: return "ADJACENCY_DATA";
      default:
              break;
   }
   return "Unknown FileStructureEnum"; 
}

inline
PRC::PointSimilarityEnum PRC::PointSimilarityFromInt(int v)
{
   switch(v)
   {
      case 0 : return UNDEFINED_ADJ_SIM;
      case 1: return GAUSS_ADJ_SIM;
      case 2: return KNN_ADJ_SIM;
      case 3: return PRECALC_ADJ_SIM;
      default:
         std::cerr << "Invalid Point similarity  : << " << v << ", expected 0,1,2, or 3." << std::endl;
   }
   return UNDEFINED_ADJ_SIM;
}

inline
const char * PRC::EnumName(PointSimilarityEnum v)
{
   switch(v)
   {
      case UNDEFINED_ADJ_SIM :  return "UNDEFINED_ADJ_SIM";
      case GAUSS_ADJ_SIM: return "GAUSS_ADJ_SIM";
      case KNN_ADJ_SIM: return "KNN_ADJ_SIM";
      case PRECALC_ADJ_SIM: return "PRECALC_ADJ_SIM";
      default:
              break;
   }
   return "UNDEFINED_ADJ_SIM";
}

inline
std::string  PRC::runConfigStruct::Print( const char *indent)
{
   std::ostringstream out;
   out << indent << "seed = " << this->seed << "\n";
   out << indent << "number of partitions = " << this->numberOfPartitions << "\n";
   out << indent << "verbose level = " << this->verboseLevel << "\n";
   out << indent << "use transduction = " << this->useTransduction << "\n";
   out << indent << "save lexical order information flag = " << this->saveOrder << "\n";
   out << indent << "save partition labels flag = " << this->saveLabels << "\n";
   out << indent << "add seed suffix flag = " << this->seedSuffix << "\n";
   out << indent << "outputLabelsSuffix = " << this->outputLabelSuffix << "\n";
   out << indent << "outputOrderSuffix = " << this->outputOrderSuffix << "\n";
   out << indent << "infoSuffix = " << this->infoSuffix << "\n";
   out << indent << "use multilevel PRC flag = " << this->useMultiLevelPRC << "\n";
   out << indent << "initOrderFile = " << this->initOrderFile << "\n";
   out << indent << "initLabelsFile = " << this->initLabelsFile << "\n";
   out << indent << "number of initial orderings = " << this->numberInitOrderings << "\n";
   out << indent << "save multiple run flag = " << this->saveMultipleRuns << "\n";
   return out.str();
}


inline
std::ostream & PRC::runConfigStruct::Print(std::ostream &out, const char *indent)
{
   out << this->Print(indent);
   return out;
}

inline
int PRC::runConfigStruct::checkCmdLineOption(int i, int argc,const char *argv[])
{
   int consumed = 0;
   std::istringstream line;
   if ((i>= argc)||(argv[i] == NULL) || (argv[i][0] != '-') || argv[i][1] != '-')
      return 0;
   std::string optname = &(argv[i][2]);
   if (optname == "seed")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      long tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a long seed for the run configuration." << std::endl;
         exit(-1);
      }
      if (tmp >0)
         this->seed = tmp;
      else
         this->seed = 0;
      consumed=2;
   }
   else if (optname == "numpart")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer number of partitions for run configuration." << std::endl;
         exit(-1);
      }
      if (tmp >=2)
         this->numberOfPartitions = tmp;
      else
      {
         std::cerr << "Invalid number of partitions : "<< tmp << std::endl;
         exit(-1);
      }
      consumed=2;
   }
   else if (optname == "verbose")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer verbose level for run configuration." << std::endl;
         exit(-1);
      }
      this->verboseLevel = tmp;
      consumed=2;
   }
   else if (optname == "useTransduction")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean value useTransduction for run configuration." << std::endl;
         exit(-1);
      }
      if (tmp)
      {
         std::cout << "Transduction is not implemented yet.  Ignoring option." << std::endl;
         tmp = false;
      }
      this->useTransduction = tmp;
      consumed=2;
   }
   else if (optname == "saveOrder")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean value saveOrder for run configuration." << std::endl;
         exit(-1);
      }
      this->saveOrder = tmp;
      consumed=2;
   }
   else if (optname == "saveLabels")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean value saveLabels for run configuration." << std::endl;
         exit(-1);
      }
      this->saveLabels = tmp;
      consumed=2;
   }
   else if (optname == "seedSuffixFlag")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean value seedSuffixfor run configuration." << std::endl;
         exit(-1);
      }
      this->seedSuffix = tmp;
      consumed=2;
   }
   else if (optname == "outputLabelSuffix")
   {
      if (argv[i+1] != NULL)  
         this->outputLabelSuffix = argv[i+1];
      consumed=2;
   }
   else if (optname == "outputOrderSuffix")
   {
      if (argv[i+1] != NULL)  
         this->outputOrderSuffix = argv[i+1];
      consumed=2;
   }
   else if (optname == "infoSuffix")
   {
      if (argv[i+1] != NULL)  
         this->infoSuffix = argv[i+1];
      consumed=2;
   }
   else if (optname == "useMultiLevelPRC")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean value useMultiLevelPRC for run configuration." << std::endl;
         exit(-1);
      }
      this->useMultiLevelPRC = tmp;
      consumed=2;
   }
   else if (optname == "initOrderFile")
   {
      if (argv[i+1] != NULL)  
         this->initOrderFile = argv[i+1];
      consumed=2;
   }
   else if (optname == "initLabelsFile")
   {
      if (argv[i+1] != NULL)  
         this->initLabelsFile = argv[i+1];
      consumed=2;
   }
   else if (optname == "numInitOrderings")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer number of initial orderings for run configuration." << std::endl;
         exit(-1);
      }
      if (tmp >0)
         this->numberInitOrderings = tmp;
      else
      {
         std::cerr << "Invalid number initial orderings : "<< tmp << std::endl;
         exit(-1);
      }
      consumed=2;
   }
   else if (optname == "saveMultipleRuns")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean value saveMultipleRuns for run configuration." << std::endl;
         exit(-1);
      }
      this->saveMultipleRuns = tmp;
      consumed=2;
   }

   return consumed;
}

inline
void PRC::runConfigStruct::cmdLineUsage(std::ostream &out, const char *indent)
{
   out << indent << "--seed  long   // use 0 to set from current time\n";
   out << indent << "--numpart  integer  // number of partitions to find. must be >= 2 \n";
   out << indent << "--verbose  integer  // higher values generate more output. \n";
   out << indent << "--useTransduction  boolean // not implemented yet. \n";
   out << indent << "--saveOrder boolean // save TILO order and boundary to file. \n";
   out << indent << "--saveLabels boolean // save partition labels to file. \n";
   out << indent << "--seedSuffixFlag boolean //add the seed value to output file names. \n";
   out << indent << "--outputLabelSuffix string // label file name is combination of data file,label suffix\n";
   out << indent << "                           // number partitions, and possible the seed value.\n";
   out << indent << "                           // default is _part_ \n";
   out << indent << "--outputOrderSuffix string // order file name is combination of data file,order suffix\n";
   out << indent << "                           // number partitions, and possible the seed value.\n";
   out << indent << "                           // default is _tilo_ \n";
   out << indent << "--infoSuffix string        // extra information attached before seed in output file names.\n";
   out << indent << "--useMultiLevelPRC boolean //default false (currently disabled)\n";
   out << indent << "--initOrderFile string     // name of file containing an initial linear order to";
   out << indent << "                           // use instead of random order. \n";
   out << indent << "--initLabelsFile string    // name of file containing an initial labels to";
   out << indent << "                           // use instead of random order. \n";
   out << indent << "--numInitOrderings  integer   // number of initial orderings.  PRC will run for each order \n";
   out << indent << "                           // and return the one with the best pinch ratio.\n";
   out << indent << "--saveMultipleRuns boolean // save partition labels of each run in addition to the best run. \n";
}

inline
std::string  PRC::dataConfigStruct::Print( const char *indent)
{
   std::ostringstream out;
   out << indent << "data input file name = " << this->inputFileName << "\n";
   out << indent << "file data type = " << EnumName(this->fileType) << "\n";
   out << indent << "use Sparse Matrix = " << this->useSparseMatrix << "\n";
   out << indent << "comma separated = " << this->commaSeparated << "\n";
   out << indent << "comment delimiter = " << this->commentDelimiter << "\n";
   std::string tmpIndent = indent;
   tmpIndent += "   ";
   out << indent << "point file configuration : \n"; pointDataConfig.Print(out,tmpIndent.c_str());
   out << indent << "adjacency file configuration : \n"; adjDataConfig.Print(out,tmpIndent.c_str());
   return out.str();
}


inline
std::ostream & PRC::dataConfigStruct::Print(std::ostream &out, const char *indent)
{
   out << this->Print(indent);
   return out;
}

inline
int PRC::dataConfigStruct::checkCmdLineOption(int i, int argc,const char *argv[])
{
   int consumed = 0;
   std::istringstream line;
   if (((i>= argc)||argv[i] == NULL) || (argv[i][0] != '-') || argv[i][1] != '-')
      return 0;
   
   consumed = this->pointDataConfig.checkCmdLineOption(i,argc,argv);
   if (consumed>0)
      return consumed;

   consumed = this->adjDataConfig.checkCmdLineOption(i,argc,argv);
   if (consumed>0)
      return consumed;

   std::string optname = &(argv[i][2]);
   if (optname == "dataInput")
   {
      if (argv[i+1] != NULL)
         inputFileName = argv[i+1];
      consumed=2;
   }
   else if (optname == "fileType")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer file type for data configuration." << std::endl;
         exit(-1);
      }
      if ((tmp >=0) && (tmp <=1))
         this->fileType = FileStructureEnumFromInt(tmp);
      else
      {
         std::cerr << "Invalid file type value : "<< tmp << std::endl;
         exit(-1);
      }
      consumed=2;
   }
   else if (optname == "useSparseMatrix")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean useSparseMatrix flag for data configuration." << std::endl;
         exit(-1);
      }
      this->useSparseMatrix = tmp;
      consumed=2;
   }

   else if (optname == "commaSeparated")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      bool tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into a boolean comma separated flag for data configuration." << std::endl;
         exit(-1);
      }
      this->commaSeparated = tmp;
      consumed=2;
   }
   else if (optname == "commentDelimeter")
   {
      if (argv[i+1] != NULL)
         commentDelimiter = argv[i+1];
      consumed=2;
   }
   return consumed;
}


inline
void PRC::dataConfigStruct::cmdLineUsage(std::ostream &out, const char *indent)
{
   out << indent << "--dataInput string   // data file name\n";
   out << indent << "--fileType  integer  // 0->point data file, 1->adjacency matrix file\n";
   out << indent << "--useSparseMatrix boolean  // default true  \n";
   out << indent << "--commaSeparated boolean  // default false  \n";
   out << indent << "--commentDelimiter string  // default # \n";
   this->pointDataConfig.cmdLineUsage(out,indent);
   this->adjDataConfig.cmdLineUsage(out,indent);
}

inline
std::string  PRC::pointDataConfigStruct::Print(const char *indent)
{
   std::ostringstream out;
   out << indent << "tag location = " << EnumName(this->tagLoc) << "\n";
   out << indent << "point similarity type = " << EnumName(this->simType) << "\n";
   return out.str();
}


inline
std::ostream & PRC::pointDataConfigStruct::Print(std::ostream &out, const char *indent)
{
   out << this->Print(indent);
   return out;
}

inline
int PRC::pointDataConfigStruct::checkCmdLineOption(int i, int argc,const char *argv[])
{
   int consumed = 0;
   std::istringstream line;
   if ((i>= argc)||(argv[i] == NULL) || (argv[i][0] != '-') || argv[i][1] != '-')
      return 0;
   
   std::string optname = &(argv[i][2]);
   if (optname == "tagLoc")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer tag location for point data configuration." << std::endl;
         exit(-1);
      }
      this->tagLoc = TagFromInt(tmp);
      consumed=2;
   }
   if (optname == "pointSimilarity")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer point similarity for point data configuration." << std::endl;
         exit(-1);
      }
      this->simType = PointSimilarityFromInt(tmp);
      consumed=2;
   }
   return consumed;
}


inline
void PRC::pointDataConfigStruct::cmdLineUsage(std::ostream &out, const char *indent)
{
   out << indent << "--tagLoc integer   //  0->no class tags (default),\n";
   out << indent << "                   //  1->front location,\n";
   out << indent << "                   // -1->tail location\n";
   out << indent << "--pointSimilarity integer   //  1-> Gaussian similarity,\n";
   out << indent << "                            //  2-> K nearest neighbor similarity,\n";
}


inline
std::string PRC::adjDataConfigStruct::Print(const char *indent)
{
   std::ostringstream out;
   out << indent << "adjacent node offset = " << nodeOffset << "\n";
   return out.str();
}


inline
std::ostream & PRC::adjDataConfigStruct::Print(std::ostream &out, const char *indent)
{
   out << this->Print(indent);
   return out;
}

inline
int PRC::adjDataConfigStruct::checkCmdLineOption(int i, int argc,const char *argv[])
{
   int consumed = 0;
   std::istringstream line;
   if ((i>= argc)||(argv[i] == NULL) || (argv[i][0] != '-') || argv[i][1] != '-')
      return 0;
   std::string optname = &(argv[i][2]);
   if (optname == "adjNodeOffset")
   {
      line.clear();
      line.str(argv[i+1]);  // if NULL, then line will be empty
      int tmp;
      if (!(line >> tmp))
      {
         std::cerr << "Failed to convert "<<argv[i+1] <<" into an integer node offset for adjacency matrix data configuration." << std::endl;
         exit(-1);
      }
      this->nodeOffset = tmp;
      consumed=2;
   }

   return consumed;
}


inline
void PRC::adjDataConfigStruct::cmdLineUsage(std::ostream &out, const char *indent)
{
   out << indent << "--adjNodeOffset integer // node index offset in data file. Default is 1.\n";
   out << indent << "                        // Needed when data file starts with one based\n";
   out << indent << "                        // instead of zero based indexing.\n";
}

#endif
