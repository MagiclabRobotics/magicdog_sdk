cmake_minimum_required(VERSION 3.5)
project(magicdog_motion_sdk)

set(CMAKE_C_FLAGS "-O3 -fPIC")
set(CMAKE_CXX_STANDARD 14)
# set(CMAKE_BUILD_TYPE "Debug")

include_directories("./include")

link_directories(lib)
message(STATUS "CMAKE_SYSTEM_PROCESSOR: ${CMAKE_SYSTEM_PROCESSOR}")
if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64.*")
  set(MAGICLAB_SDK_LIBS libmagiclab_mjr_sdk_x86.a)
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64*")
  set(MAGICLAB_SDK_LIBS libmagiclab_mjr_sdk_aarch64.a)
endif()

# build
add_executable(low_level_joint_interpolation
  example/low_level_joint_interpolation.cpp
)
target_link_libraries(low_level_joint_interpolation
  ${MAGICLAB_SDK_LIBS}
  lcm
  -lpthread
)

add_executable(high_level_walk
  example/high_level_walk.cpp
)
target_link_libraries(high_level_walk
  ${MAGICLAB_SDK_LIBS}
  lcm
  -lpthread
)
