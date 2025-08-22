add_executable(high_level_motion_example high_level_motion_example.cpp)

target_link_libraries(
  high_level_motion_example
  PRIVATE magicdog::sdk)