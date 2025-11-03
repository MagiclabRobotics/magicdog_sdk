#pragma once

#include <cstdint>
#include <string>
#include <unordered_map>
namespace magic::dog {

// 确认一下狗的故障码位置
static std::unordered_map<uint16_t, std::string> error_code_map = {
    {0x0000, "No error"},

    {0x1101, "call ros server failed"},
    {0x1301, "Manager node disappeared"},
    {0x1302, "APP node disappeared"},
    {0x1304, "eame audio node disappeared"},
    {0x1305, "eame motion node disappeared"},
    {0x1306, "LCD node disappeared"},
    {0x1307, "eame realsense node disappeared"},
    {0x1308, "eame binocular node disappeared"},
    {0x1309, "eame lds node disappeared"},
    {0x130A, "sensor board node disappeared"},
    {0x130B, "eame touch node disappeared"},
    {0x130C, "SLAM node disappeared"},
    {0x130D, "NAV node disappeared"},
    {0x130E, "eame ai node disappeared"},
    {0x130F, "Head node disappeared"},
    {0x1310, "cloud processor node disappeared"},

    {0x3201, "laser no data"},
    {0x3202, "binocular camera no data"},
    {0x3203, "binocular camera data error"},
    {0x3204, "binocular camera init failed"},
    {0x320B, "odom no data"},
    {0x320C, "imu no data"},

    {0x6101, "dog connect app fail"},
    {0x6102, "disconnect with APP"},

    {0x9201, "open lcd serial failed"},
    {0x7201, "open head serial failed"},
    {0x7202, "head no data"},
    {0x8201, "open sensor board serial failed"},
    {0x8202, "sensor board no data"},

    {0x2201, "Navigation failed to receive tf data, error"},
    {0x2202, "Navigation failed to receive map data, error"},
    {0x2203, "Navigation failed to receive localization data, error"},
    {0x2204, "Navigation failed to receive ultrasonic data, error"},
    {0x2205, "Navigation failed to receive laser data, error"},
    {0x2206, "Navigation failed to receive rgbd data, errorr"},
    {0x2207, "Navigation failed to receive multi lidar data, error"},
    {0x2208, "Navigation failed to receive point tof data, error"},
    {0x2209, "Navigation failed to receive plane tof data, error"},
    {0x220A, "Navigation failed to receive odom data, error"},

    {0x2101, "Navigation failed to receive tf data, warning"},
    {0x2102, "Navigation failed to receive map data, warning"},
    {0x2103, "Navigation failed to receive localization data, warning"},
    {0x2104, "Navigation failed to receive ultrasonic data, warning"},
    {0x2105, "Navigation failed to receive laser data, warning"},
    {0x2106, "Navigation failed to receive rgbd tof data, warning"},
    {0x2107, "Navigation failed to receive multi lidar data, warning"},
    {0x2108, "Navigation failed to receive point tof data, warning"},
    {0x2109, "Navigation failed to receive plane tof data, warning"},
    {0x210A, "Navigation failed to receive odom data, warning"},

    {0x4201, "slam localization error"},
    {0x4102, "Slam failed to receive lidar data, error"},
    {0x4103, "Slam failed to receive odom data, error"},
    {0x4205, "slam map error"},
};

}  // namespace magic::dog