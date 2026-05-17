# - Checks whether a folder is a subversion wokring copy
# The existing subversion wrappers in cmake do not provide a way to check
# whether a folder really is a working copy of subversion. This module adds
# a function to check this.
#
# Copyright (C) 2011 by Johannes Wienke <jwienke at techfak dot uni-bielefeld dot de>
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation;
# either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#

FIND_PACKAGE(Subversion)

FUNCTION(Subversion_IS_WC FOLDER RESULT_VAR)

    IF(Subversion_FOUND)
    
        # SVN info does not like .. as paths, so be sure that we use a full path
        GET_FILENAME_COMPONENT(ABS_FOLDER ${FOLDER} ABSOLUTE)
        EXECUTE_PROCESS(COMMAND ${Subversion_SVN_EXECUTABLE} info ${ABS_FOLDER}
                        RESULT_VARIABLE INFO_RESULT
                        OUTPUT_VARIABLE IGNORED
                        ERROR_VARIABLE IGNORED)
        IF(INFO_RESULT EQUAL 0)
            SET(${RESULT_VAR} TRUE PARENT_SCOPE)
        ELSE()
            SET(${RESULT_VAR} FALSE PARENT_SCOPE)
        ENDIF()
    
    ELSE()
        MESSAGE(STATUS "Cannot check whether folder ${FOLDER} is a svn working copy because svn was not found. Returning FALSE.")
        SET(${RESULT_VAR} FALSE PARENT_SCOPE)
    ENDIF()

ENDFUNCTION()
