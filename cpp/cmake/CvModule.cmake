macro(cv_add_module name)
  set(CV_MODULE_NAME ${name})
  if(CV_INITIAL_PASS)
    cmake_parse_arguments(CV_M "" "" "REQUIRED_EXTERNALS;OPTIONAL_EXTERNALS" ${ARGN})
    set(CV_MODULE_${name}_DEPS         "${CV_M_UNPARSED_ARGUMENTS}" CACHE INTERNAL "")
    set(CV_MODULE_${name}_EXT_REQUIRED "${CV_M_REQUIRED_EXTERNALS}" CACHE INTERNAL "")
    set(CV_MODULE_${name}_EXT_OPTIONAL "${CV_M_OPTIONAL_EXTERNALS}" CACHE INTERNAL "")
    set(CV_MODULES_DISCOVERED ${CV_MODULES_DISCOVERED} ${name} CACHE INTERNAL "")
    return()
  endif()
endmacro()

function(cv_create_module)
  cmake_parse_arguments(M "" "" "PRIVATE_LIBS;PUBLIC_EXTERNALS" ${ARGN})

  if(M_UNPARSED_ARGUMENTS)
    message(FATAL_ERROR "Unknown arguments: ${M_UNPARSED_ARGUMENTS}")
  endif()

  set(name ${CV_MODULE_NAME})
  set(target cv_${name})
  set(obj ${target}_obj)
  string(TOUPPER ${name} NAME_U)
  set(deps ${CV_MODULE_${name}_DEPS})
  set(exts ${CV_MODULE_${name}_EXT_REQUIRED} ${CV_MODULE_${name}_EXT_OPTIONAL})

  file(GLOB_RECURSE srcs CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")
  if(NOT srcs)
    message(FATAL_ERROR "cv_${name}: no .cpp files found under src/")
  endif()

  # OBJECT
  add_library(${obj} OBJECT ${srcs})
  
  add_library(${target} $<TARGET_OBJECTS:${obj}>)
  add_library(cv::${name} ALIAS ${target})

  set_target_properties(${target} PROPERTIES
    LINKER_LANGUAGE CXX
    OUTPUT_NAME     ${target}
    EXPORT_NAME     ${name}
    VERSION         ${PROJECT_VERSION}
    SOVERSION       ${PROJECT_VERSION_MAJOR})

  set(gen_inc "${CMAKE_CURRENT_BINARY_DIR}/include")
  generate_export_header(${target}
    BASE_NAME         CVS_${NAME_U}
    EXPORT_MACRO_NAME CVS_${NAME_U}_EXPORT
    EXPORT_FILE_NAME  "${gen_inc}/cv/${name}/export.h")

  if(BUILD_SHARED_LIBS)
    target_compile_definitions(${obj} PUBLIC ${target}_EXPORTS)
  else()
    target_compile_definitions(${obj}    PUBLIC CV_${NAME_U}_STATIC_DEFINE)
    target_compile_definitions(${target} PUBLIC CV_${NAME_U}_STATIC_DEFINE)
  endif()

  target_include_directories(${obj}
    PUBLIC
      ${CMAKE_CURRENT_SOURCE_DIR}/include
      ${gen_inc}
    PRIVATE
      ${CMAKE_CURRENT_SOURCE_DIR}/src)
  target_include_directories(${target}
    PUBLIC
      $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
      $<BUILD_INTERFACE:${gen_inc}>
      $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

  foreach(d IN LISTS deps)
    target_link_libraries(${obj}    PUBLIC cv_${d})
    target_link_libraries(${target} PUBLIC cv_${d})
  endforeach()

  foreach(e IN LISTS exts)
    string(REPLACE ":" "_" ext_target "${e}")
    string(REGEX REPLACE ":.*$" "" ext_name "${e}")
    string(TOUPPER "${ext_name}" EXT_U)

    target_link_libraries(${obj} PUBLIC cv_ext_${ext_target})
    if(e IN_LIST M_PUBLIC_EXTERNALS)
      target_link_libraries(${target} PUBLIC cv_ext_${ext_target})
    else()
      target_link_libraries(${target} PRIVATE cv_ext_${ext_target})
    endif()

    target_compile_definitions(${obj} PUBLIC CV_HAVE_${EXT_U})
    if(e MATCHES "^[^:]+:(.+)$")
      string(TOUPPER "${CMAKE_MATCH_1}" COMP_U)
      target_compile_definitions(${obj} PUBLIC CV_HAVE_${EXT_U}_${COMP_U})
    endif()
  endforeach()

  if(M_PRIVATE_LIBS)
    target_link_libraries(${obj}    PUBLIC  ${M_PRIVATE_LIBS})
    target_link_libraries(${target} PRIVATE ${M_PRIVATE_LIBS})
  endif()

  target_compile_options(${obj} PRIVATE ${CV_WARNING_FLAGS})

  install(TARGETS ${target} EXPORT CvTargets
    LIBRARY  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE  DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME  DESTINATION ${CMAKE_INSTALL_BINDIR})
  install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
  install(FILES "${gen_inc}/cv/${name}/export.h"
          DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/cv/${name})

  if(CV_BUILD_TESTS)
    file(GLOB_RECURSE unit_srcs CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/test/unit/*.cpp")
    file(GLOB_RECURSE api_srcs  CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/test/api/*.cpp")

    if(unit_srcs)
      add_executable(${target}_unit_test ${unit_srcs})
      target_link_libraries(${target}_unit_test PRIVATE ${obj} GTest::gtest_main)
      target_include_directories(${target}_unit_test PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src)
      gtest_discover_tests(${target}_unit_test
        TEST_PREFIX ${name}.unit.
        DISCOVERY_MODE PRE_TEST)
    endif()

    if(api_srcs)
      add_executable(${target}_api_test ${api_srcs})
      target_link_libraries(${target}_api_test PRIVATE ${target} GTest::gtest_main)
      gtest_discover_tests(${target}_api_test
        TEST_PREFIX ${name}.api.
        DISCOVERY_MODE PRE_TEST)
    endif()
  endif()
endfunction()