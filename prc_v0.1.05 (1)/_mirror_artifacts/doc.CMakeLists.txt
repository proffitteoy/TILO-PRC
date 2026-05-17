# check if doxygen is even installed
find_package(Doxygen)
if (DOXYGEN_FOUND STREQUAL "NO")
    message(STATUS "Doxygen not found. Please get a copy http://www.doxygen.org.  Skipping doc directory.")
else (DOXYGEN_FOUND STREQUAL "NO")
    # prepare doxygen configuration file
    configure_file(${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
    # add doxygen as target
    add_custom_target(doxygen ${DOXYGEN_EXECUTABLE} ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
    # cleanup $build/api-doc on "make clean"
    #set_property(DIRECTORY APPEND PROPERTY ADDITIONAL_MAKE_CLEAN_FILES doc)
    # add doxygen as dependency to doc-target
    get_target_property(DOC_TARGET doc TYPE)
    if(NOT DOC_TARGET)
        add_custom_target(doc)
    endif()
    add_dependencies(doc doxygen)
    # install HTML API documentation and manual pages
    #set(DOC_PATH "share/doc/${CPACK_PACKAGE_NAME}-${VERSION}")

    #install(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/api-doc/html DESTINATION ${DOC_PATH})

    #set(DOC_FILES AUTHORS NEWS README)
    #set(DOC_PATH "share/doc/testprogram-0.1")
    #install(FILES ${DOC_FILES} DESTINATION ${DOC_PATH})
endif (DOXYGEN_FOUND STREQUAL "NO")
