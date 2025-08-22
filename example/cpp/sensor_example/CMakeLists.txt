

add_executable(sensor_example sensor_example.cpp)

target_link_libraries(sensor_example PRIVATE magicdog::sdk)
