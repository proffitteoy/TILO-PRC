# cmake files based off of cmake files in Eigen
cmake_minimum_required(VERSION 2.6.2)

include(CPack)

# uncomment to build static on MS Windows
#set(CMAKE_USER_MAKE_RULES_OVERRIDE
#   ${CMAKE_CURRENT_SOURCE_DIR}/cmake/c_flag_overrides.cmake)
#set(CMAKE_USER_MAKE_RULES_OVERRIDE_CXX
#   ${CMAKE_CURRENT_SOURCE_DIR}/cmake/cxx_flag_overrides.cmake)


project(PRC)

# guard against in-source builds

if(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
  message(FATAL_ERROR "In-source builds not allowed. Please make a new directory (called a build directory) and run CMake from there. You may need to remove CMakeCache.txt. ")
endif()

# guard against bad build-type strings

if (NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
endif()

string(TOLOWER "${CMAKE_BUILD_TYPE}" cmake_build_type_tolower)
if(    NOT cmake_build_type_tolower STREQUAL "debug"
   AND NOT cmake_build_type_tolower STREQUAL "release"
   AND NOT cmake_build_type_tolower STREQUAL "relwithdebinfo")
  message(FATAL_ERROR "Unknown build type \"${CMAKE_BUILD_TYPE}\". Allowed values are Debug, Release, RelWithDebInfo (case-insensitive).")
endif()

# Allow some variables to be set on cmake command line

if (DEFINED VERBOSE_PINCH )
    add_definitions(-DVERBOSE_PINCH=${VERBOSE_PINCH})
endif()

if (DEFINED PINCH_VERIFY_LEX )
	add_definitions(-DPINCH_VERIFY_LEX=${PINCH_VERIFY_LEX})
endif()

if (DEFINED HAVE_BENCH )
    include_directories(${HAVE_BENCH})
    add_definitions(-DHAVE_BENCH)
endif()

# not creating a library yet, but may eventually need one so setting up location
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PRC_BINARY_DIR}/lib)

set(CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake)

# base on example at http://snikt.net/index.php/2010/04/01/howto-use-cmake-with-cc-projects
# and Eigen's cmake files
set(CPACK_PACKAGE_DESCRIPTION "Finding clusters based on PRC and TILO")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Pinch ratio clusting from topologically intrinsic lexicographic ordering")
set(CPACK_PACKAGE_NAME "Pinch Ratio Clustering")
set(CPACK_PACKAGE_CONTACT "Doug Heisterkamp ")

# retrieve version infomation                                               #
# automatically parse the version number
file(READ "${PROJECT_SOURCE_DIR}/prc/prc_version.h" _prc_version_header)
string(REGEX MATCH "define[ \t]+PRC_WORLD_VERSION[ \t]+([0-9]+)" _prc_world_version_match "${_prc_version_header}")
set(PRC_WORLD_VERSION "${CMAKE_MATCH_1}")
string(REGEX MATCH "define[ \t]+PRC_MAJOR_VERSION[ \t]+([0-9]+)" _prc_major_version_match "${_prc_version_header}")
set(PRC_MAJOR_VERSION "${CMAKE_MATCH_1}")
string(REGEX MATCH "define[ \t]+PRC_MINOR_VERSION[ \t]+([0-9]+)" _prc_minor_version_match "${_prc_version_header}")
set(PRC_MINOR_VERSION "${CMAKE_MATCH_1}")

set(CPACK_PACKAGE_VERSION_WORLD "${PRC_WORLD_VERSION}")
set(CPACK_PACKAGE_VERSION_MAJOR "${PRC_MAJOR_VERSION}")
set(CPACK_PACKAGE_VERSION_MINOR "${PRC_MINOR_VERSION}")
set(VERSION "${CPACK_PACKAGE_VERSION_WORLD}.${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}")
set(PRC_VERSION_NUMBER ${PRC_WORLD_VERSION}.${PRC_MAJOR_VERSION}.${PRC_MINOR_VERSION})


# commented out in tag'ed version so the non working copy does not generate error.
#find_package(Subversion)
#if(Subversion_FOUND)
#  Subversion_WC_INFO(${CMAKE_CURRENT_SOURCE_DIR} ER)
#  set(SUBVERSION_REVISION ${ER_WC_REVISION})
#  set(VERSION "${VERSION}.${SUBVERSION_REVISION}")
#  set(PRC_VERSION_NUMBER ${PRC_VERSION_NUMBER}.${SUBVERSION_REVISION})
#endif(Subversion_FOUND)
set(CPACK_PACKAGE_VERSION_PATCH "150")
set(CPACK_GENERATOR "DEB")
set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}-${CMAKE_SYSTEM_PROCESSOR}")


include(CheckCXXCompilerFlag)

set(PRC_STANDARD_LIBRARIES_TO_LINK_TO "")
find_package(StandardMathLibrary)

if(NOT STANDARD_MATH_LIBRARY_FOUND)
  message(FATAL_ERROR "Can't link to the standard math library.")
else()
	set(PRC_STANDARD_LIBRARIES_TO_LINK_TO "${PRC_STANDARD_LIBRARIES_TO_LINK_TO} ${STANDARD_MATH_LIBRARY}")
endif()

set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_INCLUDE_DIRECTORIES_PROJECT_BEFORE ON)


find_package(OpenMP)
if (OPENMP_FOUND)
	message(STATUS "OpenMP  found.  Using flags " ${OpenMP_CXX_FLAGS})
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_X_FLAGS}")
endif (OPENMP_FOUND)


if(CMAKE_COMPILER_IS_GNUCXX)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall " )
	set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g3 ")
	set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -g0 -O2 ")

	check_cxx_compiler_flag("-Wextra" COMPILER_SUPPORT_WEXTRA)
    if(COMPILER_SUPPORT_WEXTRA)
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wextra ")
    endif()
endif(CMAKE_COMPILER_IS_GNUCXX)

if(MSVC)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_SCL_SECURE_NO_WARNINGS " )
endif(MSVC)

find_package(Eigen3 3.0.0)
if (EIGEN3_FOUND )
    message(STATUS "Eigen  found at " ${EIGEN3_INCLUDE_DIR})
    include_directories(${EIGEN3_INCLUDE_DIR})
else (EIGEN3_FOUND )
    message(STATUS "Eigen not found.  Using version in prc/external/eigen")
    include_directories(${CMAKE_CURRENT_SOURCE_DIR}/external/eigen)
endif (EIGEN3_FOUND)


configure_file(${PRC_SOURCE_DIR}/readme.rst ${CMAKE_CURRENT_BINARY_DIR}/readme.rst COPYONLY)
configure_file(${PRC_SOURCE_DIR}/readme.html ${CMAKE_CURRENT_BINARY_DIR}/readme.html COPYONLY)
# link to -lm

include_directories(${CMAKE_CURRENT_SOURCE_DIR} ${CMAKE_CURRENT_BINARY_DIR})

# the user modifiable install path for header files
set(PRC_INCLUDE_INSTALL_DIR ${PRC_INCLUDE_INSTALL_DIR} CACHE PATH "The directory where we install the header files (optional)")


# set the internal install path for header files which depends on wether the user modifiable
# PRC_INCLUDE_INSTALL_DIR has been set by the user or not.
if(PRC_INCLUDE_INSTALL_DIR)
  set(INCLUDE_INSTALL_DIR
    ${PRC_INCLUDE_INSTALL_DIR}
    CACHE INTERNAL
    "The directory where we install the header files (internal)"
  )
else()
  set(INCLUDE_INSTALL_DIR
    "${CMAKE_INSTALL_PREFIX}/include/prc"
    CACHE INTERNAL
    "The directory where we install the header files (internal)"
  )
endif()


# need to test cmake install before enabling

#install(FILES signature_of_prc_matrix_library DESTINATION ${INCLUDE_INSTALL_DIR} COMPONENT Devel)

# also need to check pkgconfig before enabling

# if(PRC_BUILD_PKGCONFIG)
#     SET(path_separator ":")
#     STRING(REPLACE ${path_separator} ";" pkg_config_libdir_search "$ENV{PKG_CONFIG_LIBDIR}")
#     message(STATUS "searching for 'pkgconfig' directory in PKG_CONFIG_LIBDIR ( $ENV{PKG_CONFIG_LIBDIR} ), ${CMAKE_INSTALL_PREFIX}/share, and ${CMAKE_INSTALL_PREFIX}/lib")
#     FIND_PATH(pkg_config_libdir pkgconfig ${pkg_config_libdir_search} ${CMAKE_INSTALL_PREFIX}/share ${CMAKE_INSTALL_PREFIX}/lib ${pkg_config_libdir_search})
#     if(pkg_config_libdir)
#         SET(pkg_config_install_dir ${pkg_config_libdir})
#         message(STATUS "found ${pkg_config_libdir}/pkgconfig" )
#     else(pkg_config_libdir)
#         SET(pkg_config_install_dir ${CMAKE_INSTALL_PREFIX}/share)
#         message(STATUS "pkgconfig not found; installing in ${pkg_config_install_dir}" )
#     endif(pkg_config_libdir)
#
#    configure_file(prc.pc.in prc.pc)
#    install(FILES ${CMAKE_CURRENT_BINARY_DIR}/prc3.pc
#        DESTINATION ${pkg_config_install_dir}/pkgconfig
#        )
#endif(PRC_BUILD_PKGCONFIG)



add_subdirectory(prc)
#add_subdirectory(test EXCLUDE_FROM_ALL)
add_subdirectory(doc EXCLUDE_FROM_ALL)
add_subdirectory(demos EXCLUDE_FROM_ALL)
#add_subdirectory(bench EXCLUDE_FROMALL) 


message(STATUS "")
message(STATUS "Configured PRC ${PRC_VERSION_NUMBER}")
message(STATUS "")
