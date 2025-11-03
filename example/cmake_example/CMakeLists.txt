cmake_minimum_required(VERSION 3.18)

project(magicdog_sdk_example LANGUAGES C CXX)

# Assuming the SDK is installed in the directory: /opt/magic_robotics/magicdog_sdk

set(CMAKE_PREFIX_PATH /opt/magic_robotics/magicdog_sdk)

find_package(magicdog_sdk REQUIRED)

add_executable(cmake_example cmake_example.cpp)

target_link_libraries(cmake_example PRIVATE magicdog::sdk)
