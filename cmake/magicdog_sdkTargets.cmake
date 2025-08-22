
if(CMAKE_VERSION VERSION_LESS 3.18)
  message(FATAL_ERROR "CMake should be 3.18 or greater.")
endif()
cmake_policy(PUSH)
cmake_policy(VERSION 3.18)

set(CMAKE_IMPORT_FILE_VERSION 1)

set(_targetsDefined)
set(_targetsNotDefined)
set(_expectedTargets magicdog_sdk)
foreach(_expectedTarget IN LISTS _expectedTargets)
  if(NOT TARGET ${_expectedTarget})
    list(APPEND _targetsNotDefined ${_expectedTarget})
  else()
    list(APPEND _targetsDefined ${_expectedTarget})
  endif()
endforeach()

if("${_targetsDefined}" STREQUAL "${_expectedTargets}")
  unset(_targetsDefined)
  unset(_targetsNotDefined)
  unset(_expectedTargets)
  set(CMAKE_IMPORT_FILE_VERSION)
  cmake_policy(POP)
  return()
endif()

if(NOT "${_targetsDefined}" STREQUAL "")
  message(FATAL_ERROR "The following targets were already defined in this export set: ${_targetsDefined}")
endif()

unset(_targetsDefined)
unset(_targetsNotDefined)
unset(_expectedTargets)

message(STATUS ${CMAKE_CURRENT_LIST_FILE})

# Compute the installation prefix
get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH)


if(_IMPORT_PREFIX STREQUAL "/")
  set(_IMPORT_PREFIX "")
endif()

add_library(magicdog_sdk SHARED IMPORTED GLOBAL)
add_library(magicdog::sdk ALIAS magicdog_sdk)

set_target_properties(magicdog_sdk PROPERTIES
    IMPORTED_LOCATION "${_IMPORT_PREFIX}/lib/libmagicdog_sdk.so"
    INTERFACE_INCLUDE_DIRECTORIES "${_IMPORT_PREFIX}/include"
    LINKER_LANGUAGE CXX
)

list(APPEND _IMPORT_CHECK_TARGETS magicdog_sdk)
list(APPEND _IMPORT_CHECK_FILES_FOR_magicdog_sdk "${_IMPORT_PREFIX}/lib/libmagicdog_sdk.so")

foreach(target IN LISTS _IMPORT_CHECK_TARGETS)
  foreach(file IN LISTS _IMPORT_CHECK_FILES_FOR_${target})
    if(NOT EXISTS "${file}")
      message(FATAL_ERROR "The imported target \"${target}\" references the file
  \"${file}\"
but this file does not exist. Possible reasons include:
  * The file was deleted, renamed, or moved
  * An install procedure did not complete successfully
")
    endif()
  endforeach()
  unset(_IMPORT_CHECK_FILES_FOR_${target})
endforeach()

unset(_IMPORT_CHECK_TARGETS)
unset(_IMPORT_PREFIX)
set(CMAKE_IMPORT_FILE_VERSION)
cmake_policy(POP)
