function(_cv_ext_register target)
  set_property(GLOBAL APPEND PROPERTY CV_EXT_TARGETS ${target})
endfunction()

function(_cv_ext_config_add line)
  set_property(GLOBAL APPEND_STRING PROPERTY CV_EXT_CONFIG "${line}\n")
endfunction()

# ==============================================================================
# GSTREAMER
# ==============================================================================

function(cv_find_external_gstreamer out_var)
  set(${out_var} FALSE PARENT_SCOPE)
  find_package(PkgConfig QUIET)
  if(NOT PkgConfig_FOUND)
    return()
  endif()
  pkg_check_modules(CV_GST QUIET IMPORTED_TARGET GLOBAL gstreamer-1.0)
  if(CV_GST_FOUND)
    add_library(cv_ext_gstreamer INTERFACE)
    target_link_libraries(cv_ext_gstreamer INTERFACE PkgConfig::CV_GST)
    set(${out_var} TRUE PARENT_SCOPE)
    _cv_ext_register(cv_ext_gstreamer)
    _cv_ext_config_add("find_dependency(PkgConfig)")
    _cv_ext_config_add("pkg_check_modules(CV_GST REQUIRED QUIET IMPORTED_TARGET GLOBAL gstreamer-1.0)")
  endif()
endfunction()

function(cv_find_external_component_gstreamer comp out_var)
  set(${out_var} FALSE PARENT_SCOPE)
  find_package(PkgConfig QUIET)
  if(NOT PkgConfig_FOUND)
    return()
  endif()
  string(MAKE_C_IDENTIFIER "${comp}" cid)
  pkg_check_modules(CV_GST_${cid} QUIET IMPORTED_TARGET GLOBAL gstreamer-${comp}-1.0)
  if(CV_GST_${cid}_FOUND)
    add_library(cv_ext_gstreamer_${comp} INTERFACE)
    target_link_libraries(cv_ext_gstreamer_${comp} INTERFACE
      cv_ext_gstreamer PkgConfig::CV_GST_${cid})
    set(${out_var} TRUE PARENT_SCOPE)
    _cv_ext_register(cv_ext_gstreamer_${comp})
    _cv_ext_config_add("pkg_check_modules(CV_GST_${cid} REQUIRED QUIET IMPORTED_TARGET GLOBAL gstreamer-${comp}-1.0)")
  endif()
endfunction()

# ==============================================================================
# OPENCV
# ==============================================================================

function(cv_find_external_opencv out_var)
  set(${out_var} FALSE PARENT_SCOPE)
  find_package(OpenCV QUIET)
  if(OpenCV_FOUND)
    add_library(cv_ext_opencv INTERFACE)
    if(OpenCV_INCLUDE_DIRS)
      target_include_directories(cv_ext_opencv INTERFACE
        "$<BUILD_INTERFACE:${OpenCV_INCLUDE_DIRS}>")
    endif()
    target_link_libraries(cv_ext_opencv INTERFACE ${OpenCV_LIBS})
    set(${out_var} TRUE PARENT_SCOPE)
    _cv_ext_register(cv_ext_opencv)
    _cv_ext_config_add("find_dependency(OpenCV)")
  endif()
endfunction()

function(cv_find_external_component_opencv comp out_var)
  set(${out_var} FALSE PARENT_SCOPE)
  if(TARGET opencv_${comp})
    add_library(cv_ext_opencv_${comp} INTERFACE)
    target_link_libraries(cv_ext_opencv_${comp} INTERFACE
      cv_ext_opencv opencv_${comp})
    set(${out_var} TRUE PARENT_SCOPE)
    _cv_ext_register(cv_ext_opencv_${comp})
  endif()
endfunction()

# ==============================================================================
# NLOHMANN-JSON
# ==============================================================================

function(cv_find_external_nlohmann_json out_var)
  set(${out_var} FALSE PARENT_SCOPE)
  find_package(nlohmann_json QUIET)
  if(nlohmann_json_FOUND)
    add_library(cv_ext_nlohmann_json INTERFACE)
    target_link_libraries(cv_ext_nlohmann_json INTERFACE nlohmann_json::nlohmann_json)
    set(${out_var} TRUE PARENT_SCOPE)
    _cv_ext_register(cv_ext_nlohmann_json)
    _cv_ext_config_add("find_dependency(nlohmann_json)")
  endif()
endfunction()

# ==============================================================================
# SPDLOG
# ==============================================================================

function(cv_find_external_spdlog out_var)
  set(${out_var} FALSE PARENT_SCOPE)
  find_package(spdlog QUIET)
  if(spdlog_FOUND)
    add_library(cv_ext_spdlog INTERFACE)
    target_link_libraries(cv_ext_spdlog INTERFACE spdlog::spdlog)
    set(${out_var} TRUE PARENT_SCOPE)
    _cv_ext_register(cv_ext_spdlog)
    _cv_ext_config_add("find_dependency(spdlog)")
  endif()
endfunction()

# ==============================================================================
# CORE
# ==============================================================================

function(cv_external_available token out_var)
  string(REGEX REPLACE ":.*$" "" name "${token}")
  set(comp "")
  if(token MATCHES "^[^:]+:(.+)$")
    set(comp "${CMAKE_MATCH_1}")
  endif()

  get_property(pkg_known GLOBAL PROPERTY CV_EXTPKG_${name} SET)
  if(NOT pkg_known)
    if(NOT COMMAND cv_find_external_${name})
      message(FATAL_ERROR
        "Unknown external dependency '${name}'. "
        "Define cv_find_external_${name}() within cmake/CvExternals.cmake.")
    endif()
    set(found FALSE)
    cmake_language(CALL cv_find_external_${name} found)
    set_property(GLOBAL PROPERTY CV_EXTPKG_${name} ${found})
    if(found)
      message(STATUS "External CV dependency: ${name} found")
    else()
      message(STATUS "External CV dependency: ${name} not found")
    endif()
  endif()
  get_property(pkg_found GLOBAL PROPERTY CV_EXTPKG_${name})
  if(NOT pkg_found)
    set(${out_var} FALSE PARENT_SCOPE)
    return()
  endif()

  if(NOT comp)
    set(${out_var} TRUE PARENT_SCOPE)
    return()
  endif()

  string(MAKE_C_IDENTIFIER "${name}_${comp}" key)
  get_property(comp_known GLOBAL PROPERTY CV_EXTCOMP_${key} SET)
  if(NOT comp_known)
    if(NOT COMMAND cv_find_external_component_${name})
      message(FATAL_ERROR
        "'${token}' was requested, but component support for '${name}' is not defined. "
        "Define cv_find_external_component_${name}() within cmake/CvExternals.cmake.")
    endif()
    set(cfound FALSE)
    cmake_language(CALL cv_find_external_component_${name} ${comp} cfound)
    set_property(GLOBAL PROPERTY CV_EXTCOMP_${key} ${cfound})
    if(cfound)
      message(STATUS "External CV dependency: ${name}:${comp} found")
    else()
      message(STATUS "External CV dependency: ${name}:${comp} not found")
    endif()
  endif()
  get_property(comp_found GLOBAL PROPERTY CV_EXTCOMP_${key})
  set(${out_var} ${comp_found} PARENT_SCOPE)
endfunction()

function(cv_external_export)
  get_property(ext_targets GLOBAL PROPERTY CV_EXT_TARGETS)
  if(ext_targets)
    install(TARGETS ${ext_targets} EXPORT CvTargets)
  endif()
endfunction()