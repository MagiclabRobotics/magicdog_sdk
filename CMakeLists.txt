cmake_minimum_required(VERSION 3.18)

project(magicdog_sdk LANGUAGES C CXX)

# Project Options
option(BUILD_EXAMPLES "Build examples" ON)

# Set cmake path
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# Some necessary settings
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Set default build type as Release
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_CXX_VISIBILITY_INLINES_HIDDEN ON)
set(BUILD_SHARED_LIBS ON)

message(STATUS "Current system architecture: ${CMAKE_SYSTEM_PROCESSOR}")

set(MAGICDOG_SDK_PATH ${CMAKE_CURRENT_SOURCE_DIR}/lib/${CMAKE_SYSTEM_PROCESSOR})
find_library(
  MAGICDOG_SDK_LIB magicdog_sdk
  PATHS ${MAGICDOG_SDK_PATH}
  NO_DEFAULT_PATH)

if(NOT MAGICDOG_SDK_LIB)
  message(FATAL_ERROR "Magiclab SDK library for the architecture is not found")
else()
  message(STATUS "Magiclab SDK library found at: ${MAGICDOG_SDK_LIB}")
endif()

message(STATUS "Importing: ${MAGICDOG_SDK_LIB}")

# Python SDK module path
set(MAGICDOG_PYTHON_SDK_PATH
    ${CMAKE_CURRENT_SOURCE_DIR}/lib/${CMAKE_SYSTEM_PROCESSOR})

# Determine Python module filename based on architecture
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64")
  set(PYTHON_MODULE_NAME "magicdog_python.cpython-310-x86_64-linux-gnu.so")
elseif(CMAKE_SYSTEM_PROCESSOR STREQUAL "aarch64")
  set(PYTHON_MODULE_NAME "magicdog_python.cpython-310-aarch64-linux-gnu.so")
else()
  message(FATAL_ERROR "Unsupported architecture: ${CMAKE_SYSTEM_PROCESSOR}")
endif()

set(MAGICDOG_PYTHON_SDK_LIB ${MAGICDOG_PYTHON_SDK_PATH}/${PYTHON_MODULE_NAME})

if(NOT EXISTS ${MAGICDOG_PYTHON_SDK_LIB})
  message(
    FATAL_ERROR
      "Magiclab Python SDK module for the architecture is not found: ${MAGICDOG_PYTHON_SDK_LIB}"
  )
else()
  message(
    STATUS "Magiclab Python SDK module found at: ${MAGICDOG_PYTHON_SDK_LIB}")
endif()

message(STATUS "Importing: ${MAGICDOG_PYTHON_SDK_LIB}")

add_library(magicdog_sdk SHARED IMPORTED GLOBAL)
add_library(magicdog::sdk ALIAS magicdog_sdk)

set_target_properties(magicdog_sdk PROPERTIES IMPORTED_LOCATION
                                              ${MAGICDOG_SDK_LIB})
target_include_directories(
  magicdog_sdk INTERFACE $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
                         $<INSTALL_INTERFACE:include>)

# build examples
if(BUILD_EXAMPLES)
  add_subdirectory(example/cpp)
endif()

include(GNUInstallDirs)

install(FILES cmake/magicdog_sdkTargets.cmake
        DESTINATION lib/cmake/magicdog_sdk)
install(FILES ${MAGICDOG_SDK_LIB} DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(FILES ${MAGICDOG_PYTHON_SDK_LIB} DESTINATION ${CMAKE_INSTALL_LIBDIR})
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

include(CMakePackageConfigHelpers)
write_basic_package_version_file(
  magicdog_sdkConfigVersion.cmake
  VERSION
    "${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}.${${PROJECT_NAME}_VERSION_PATCH}"
  COMPATIBILITY ExactVersion)

configure_file(cmake/magicdog_sdkConfig.cmake.in magicdog_sdkConfig.cmake @ONLY)
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/magicdog_sdkConfig.cmake"
              "${CMAKE_CURRENT_BINARY_DIR}/magicdog_sdkConfigVersion.cmake"
        DESTINATION lib/cmake/magicdog_sdk)
