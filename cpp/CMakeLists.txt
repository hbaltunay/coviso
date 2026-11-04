cmake_minimum_required(VERSION 3.20)
project(cv VERSION 0.1.0 LANGUAGES CXX)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

option(BUILD_SHARED_LIBS "Generate a shared (.so) library" ON)
option(CV_BUILD_TESTS "Compile the tests (requires GoogleTest)" OFF)
set(CV_BUILD_LIST "" CACHE STRING "Modules to be compiled, separated by ';' (empty = all). Dependencies are added automatically.")

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "" FORCE)
endif()

include(GNUInstallDirs)
include(GenerateExportHeader)
include(CMakePackageConfigHelpers)
include(CvCompilerOptions)
include(CvExternals)
include(CvModule)
include(CvResolve)

if(CV_BUILD_TESTS)
  enable_testing()
  find_package(GTest REQUIRED)
  include(GoogleTest)
endif()

# ==============================================================================
# DISCOVER
# ==============================================================================

set(CV_MODULES_DISCOVERED "" CACHE INTERNAL "")
set(CV_INITIAL_PASS ON)

file(GLOB subdirs RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}/modules"
     "${CMAKE_CURRENT_SOURCE_DIR}/modules/*")

foreach(m IN LISTS subdirs)
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/modules/${m}/CMakeLists.txt")
    add_subdirectory(modules/${m} "${CMAKE_CURRENT_BINARY_DIR}/.discovery/${m}")
  endif()
endforeach()

set(CV_INITIAL_PASS OFF)

# ==============================================================================
# RESOLVE
# ==============================================================================

set(CV_EXT_TARGETS "" CACHE INTERNAL "")
cv_resolve_modules(CV_MODULES)
set(CV_MODULES_ENABLED "$(CV_MODULES)" CACHE INTERNAL "")

message(STATUS "CV modules (build order): ${CV_MODULES}")
foreach(m IN LISTS CV_MODULES)
  message(STATUS "  ${m} -> ${CV_MODULE_${m}_DEPS}")
endforeach()

# ==============================================================================
# MODULES
# ==============================================================================

foreach(m IN LISTS CV_MODULES)
  add_subdirectory(modules/${m})
endforeach()

add_library(cv_all INTERFACE)
add_library(cv::cv ALIAS cv_all)
foreach(m IN LISTS CV_MODULES)
  target_link_libraries(cv_all INTERFACE cv_${m})
endforeach()
cv_external_export()

# ==============================================================================
# INSTALL
# ==============================================================================

install(EXPORT CvTargets
        NAMESPACE cv::
        FILE CvTargets.cmake
        DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Cv)

configure_package_config_file(
  cmake/CvConfig.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/CvConfig.cmake"
  INSTALL_DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Cv)
write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/CvConfigVersion.cmake"
  COMPATIBILITY SameMajorVersion)
install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/CvConfig.cmake"
  "${CMAKE_CURRENT_BINARY_DIR}/CvConfigVersion.cmake"
  DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/Cv)

# ==============================================================================
# APPS
# ==============================================================================

add_subdirectory(apps)