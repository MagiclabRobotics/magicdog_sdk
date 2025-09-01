#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例 - 传感器结构体丰富示例

本文件展示了如何使用 MagicDog SDK 的 Python 绑定来测试机器人各类传感器相关的结构体和枚举。
涵盖了 IMU、点云、图像、激光雷达、相机、三目相机帧、多维数组等典型传感器数据结构。
"""

import sys
import time

try:
    import magicdog_python as magicdog
    from magicdog_python import TtsCommand, TtsPriority, TtsMode, GetSpeechConfig, ErrorCode
    print("Successfully imported MagicDog Python module!")
    print(f"Imported magicdog_python path: {sys.path}")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

# ========== Double4Array/Double3Array 测试 ==========
double4_array = magicdog.Double4Array()
for i in range(4):
    double4_array[i] = i + 1.0
print(f"双精度四元数数组: {double4_array}")

double3_array = magicdog.Double3Array()
for i in range(3):
    double3_array[i] = i + 1.0
print(f"双精度三元数数组: {double3_array}")

# ========== IMU 结构体测试 ==========
imu = magicdog.Imu()
imu.timestamp = int(time.time() * 1e9)
imu.orientation = double4_array
imu.angular_velocity = double3_array
imu.linear_acceleration = double3_array
imu.temperature = 25.0
print(f"IMU: {imu}")
print(f"    timestamp: {imu.timestamp}")
print(f"    orientation: {imu.orientation}")
print(f"    angular_velocity: {imu.angular_velocity}")
print(f"    linear_acceleration: {imu.linear_acceleration}")
print(f"    temperature: {imu.temperature}")

# ========== Header 结构体 ==========
header = magicdog.Header()
header.stamp = int(time.time() * 1e9)
header.frame_id = "base_link"
print(f"Header: {header}")
print(f"    stamp: {header.stamp}")
print(f"    frame_id: {header.frame_id}")

# ========== PointField 结构体 ==========
point_field = magicdog.PointField()
point_field.name = "x"
point_field.offset = 10
point_field.datatype = 1
point_field.count = 1
print(f"PointField: {point_field}")
print(f"    name: {point_field.name}, offset: {point_field.offset}, datatype: {point_field.datatype}, count: {point_field.count}")

# ========== PointCloud2 结构体 ==========
point_cloud2 = magicdog.PointCloud2()
point_cloud2.header = header
point_cloud2.height = 2
point_cloud2.width = 2
point_cloud2.fields.append(point_field)
point_cloud2.is_bigendian = False
point_cloud2.point_step = 4
point_cloud2.row_step = 8
for i in range(8):
    point_cloud2.data.append(i)
print(f"PointCloud2: {point_cloud2}")
print(f"    height: {point_cloud2.height}, width: {point_cloud2.width}")
print(f"    fields: {[f.name for f in point_cloud2.fields]}")
print(f"    data: {list(point_cloud2.data)}")

# ========== Image 结构体 ==========
image = magicdog.Image()
image.header = header
image.height = 4
image.width = 4
image.encoding = "rgb8"
image.is_bigendian = False
image.step = image.width * 3
for i in range(image.height * image.step):
    image.data.append(i % 256)
print(f"Image: {image}")
print(f"    height: {image.height}, width: {image.width}, encoding: {image.encoding}")
print(f"    data 前10项: {[image.data[i] for i in range(10)]}")

# ========== DoubleVector/Double9Array/Double12Array ==========
double_vector = magicdog.DoubleVector()
for i in range(3):
    double_vector.append(i + 1.0)
print(f"DoubleVector: {double_vector}")

double9_array = magicdog.Double9Array()
for i in range(9):
    double9_array[i] = i + 1.0
print(f"Double9Array: {double9_array}")

double12_array = magicdog.Double12Array()
for i in range(12):
    double12_array[i] = i + 1.0
print(f"Double12Array: {double12_array}")

# ========== CameraInfo 结构体 ==========
camera_info = magicdog.CameraInfo()
camera_info.header = header
camera_info.height = 480
camera_info.width = 640
camera_info.distortion_model = "plumb_bob"
camera_info.D = double_vector
camera_info.K = double9_array
camera_info.R = double9_array
camera_info.P = double12_array
camera_info.binning_x = 1
camera_info.binning_y = 1
camera_info.roi_x_offset = 0
camera_info.roi_y_offset = 0
camera_info.roi_height = 480
camera_info.roi_width = 640
camera_info.roi_do_rectify = False
print(f"CameraInfo: {camera_info}")
print(f"    distortion_model: {camera_info.distortion_model}")
print(f"    D: {camera_info.D}")
print(f"    K: {camera_info.K}")
print(f"    R: {camera_info.R}")
print(f"    P: {camera_info.P}")

# ========== TrinocularCameraFrame 结构体 ==========
trinocular_camera_frame = magicdog.TrinocularCameraFrame()
trinocular_camera_frame.header = header
trinocular_camera_frame.vin_time = 1234567890
trinocular_camera_frame.decode_time = 1234567999
for i in range(10):
    trinocular_camera_frame.imgfl_array.append(i)
    trinocular_camera_frame.imgf_array.append(i + 10)
    trinocular_camera_frame.imgfr_array.append(i + 20)
print(f"TrinocularCameraFrame: {trinocular_camera_frame}")
print(f"    vin_time: {trinocular_camera_frame.vin_time}, decode_time: {trinocular_camera_frame.decode_time}")
print(f"    imgfl_array 前5项: {[trinocular_camera_frame.imgfl_array[i] for i in range(5)]}")
print(f"    imgf_array 前5项: {[trinocular_camera_frame.imgf_array[i] for i in range(5)]}")
print(f"    imgfr_array 前5项: {[trinocular_camera_frame.imgfr_array[i] for i in range(5)]}")

# ========== CompressedImage 结构体 ==========
compressed_image = magicdog.CompressedImage()
compressed_image.header = header
compressed_image.format = "jpeg"
for i in range(20):
    compressed_image.data.append(i)
print(f"CompressedImage: {compressed_image}")
print(f"    format: {compressed_image.format}")
print(f"    data 前5项: {[compressed_image.data[i] for i in range(5)]}")

# ========== LaserScan 结构体 ==========
laser_scan = magicdog.LaserScan()
laser_scan.header = header
laser_scan.angle_min = 0
laser_scan.angle_max = 180
laser_scan.angle_increment = 1
laser_scan.time_increment = 100
laser_scan.scan_time = 1000
laser_scan.range_min = 1
laser_scan.range_max = 10
for i in range(10):
    laser_scan.ranges.append(1.0 + i * 0.5)
    laser_scan.intensities.append(100.0 + i)
print(f"LaserScan: {laser_scan}")
print(f"    angle_min: {laser_scan.angle_min}")
print(f"    angle_max: {laser_scan.angle_max}")
print(f"    ranges 前5项: {[laser_scan.ranges[i] for i in range(5)]}")
print(f"    intensities 前5项: {[laser_scan.intensities[i] for i in range(5)]}")

# ========== Float32MultiArray 结构体 ==========
float_multi_array = magicdog.Float32MultiArray()
float_multi_array.layout.dim_size = 2
dim1 = magicdog.MultiArrayDimension()
dim1.label = "height"
dim1.size = 3
dim1.stride = 6
dim2 = magicdog.MultiArrayDimension()
dim2.label = "width"
dim2.size = 2
dim2.stride = 2
float_multi_array.layout.dim.append(dim1)
float_multi_array.layout.dim.append(dim2)
float_multi_array.layout.data_offset = 0
for i in range(6):
    float_multi_array.data.append(float(i) * 1.1)
print(f"Float32MultiArray: {float_multi_array}")
print(f"    layout.dim_size: {float_multi_array.layout.dim_size}")
print(f"    layout.dim[0]: label={float_multi_array.layout.dim[0].label}, size={float_multi_array.layout.dim[0].size}, stride={float_multi_array.layout.dim[0].stride}")
print(f"    layout.dim[1]: label={float_multi_array.layout.dim[1].label}, size={float_multi_array.layout.dim[1].size}, stride={float_multi_array.layout.dim[1].stride}")
print(f"    data 前5项: {[float_multi_array.data[i] for i in range(5)]}")

# ========== ByteMultiArray 结构体 ==========
byte_multi_array = magicdog.ByteMultiArray()
byte_multi_array.layout.dim_size = 1
dim = magicdog.MultiArrayDimension()
dim.label = "length"
dim.size = 10
dim.stride = 10
byte_multi_array.layout.dim.append(dim)
byte_multi_array.layout.data_offset = 0
for i in range(10):
    byte_multi_array.data.append(i)
print(f"ByteMultiArray: {byte_multi_array}")
print(f"    layout.dim_size: {byte_multi_array.layout.dim_size}")
print(f"    layout.dim[0]: label={byte_multi_array.layout.dim[0].label}, size={byte_multi_array.layout.dim[0].size}, stride={byte_multi_array.layout.dim[0].stride}")
print(f"    data 前5项: {[byte_multi_array.data[i] for i in range(5)]}")

# ========== Int8 结构体 ==========
int8_struct = magicdog.Int8()
int8_struct.data = -8
print(f"Int8: {int8_struct}")
print(f"    data: {int8_struct.data}")


print("所有传感器结构体示例测试完毕。")
