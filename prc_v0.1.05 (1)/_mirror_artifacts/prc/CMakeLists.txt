#set(lib_srcs examples.cc)
#add_library(prcCore SHARED  ${lib_srcs})

#link_directories(${PRC_BINARY_DIR}/lib)
#set(prclibs ${PRC_STANDARD_LIBRARIES_TO_LINK_TO} prcCore)  


add_executable(pinchRatioClustering pinchRatioClustering.cc)
add_executable(genSimMatrix genSimMatrix.cc)


install(TARGETS pinchRatioClustering genSimMatrix DESTINATION bin)
#install(FILES
#  ${prc_directory_files_to_install}
#  DESTINATION ${INCLUDE_INSTALL_DIR}/prc COMPONENT Devel
#  )


add_subdirectory(internal)
