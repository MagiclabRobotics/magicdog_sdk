#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例 - 传感器结构体丰富示例

本文件展示了如何使用 MagicDog SDK 的 Python 绑定来测试机器人各类传感器相关的结构体和枚举。
涵盖了 IMU、点云、图像、激光雷达、相机、三目相机帧、多维数组等典型传感器数据结构。
"""

import sys
import time
import magicdog_python as magicdog
from magicdog_python import (
    TtsCommand,
    TtsPriority,
    TtsMode,
    GetSpeechConfig,
    ErrorCode,
)

# ========== Double4Array/Double3Array 测试 ==========
double4_array = magicdog.Double4Array()
for i in range(4):
    double4_array[i] = i + 1.0
print(f"双精度四元数数组: {double4_array}")

double3_array = magicdog.Double3Array()
for i in range(3):
    double3_array[i] = i + 1.0
print(f"双精度三元数数组: {double3_array}")

# 测试数组值
for i in range(4):
    if abs(double4_array[i] - (i + 1.0)) > 1e-6:
        print(f"错误: Double4Array[{i}] 期望值 {i + 1.0}，实际值 {double4_array[i]}")
        sys.exit(1)
for i in range(3):
    if abs(double3_array[i] - (i + 1.0)) > 1e-6:
        print(f"错误: Double3Array[{i}] 期望值 {i + 1.0}，实际值 {double3_array[i]}")
        sys.exit(1)
print("✓ Double4Array/Double3Array测试通过")

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

# 测试IMU值
if imu.temperature != 25.0:
    print(f"错误: IMU温度 期望值 25.0，实际值 {imu.temperature}")
    sys.exit(1)
if (
    imu.orientation[0] != double4_array[0]
    or imu.orientation[1] != double4_array[1]
    or imu.orientation[2] != double4_array[2]
    or imu.orientation[3] != double4_array[3]
):
    print(f"错误: IMU方向数据不匹配")
    sys.exit(1)
if (
    imu.angular_velocity[0] != double3_array[0]
    or imu.angular_velocity[1] != double3_array[1]
    or imu.angular_velocity[2] != double3_array[2]
):
    print(f"错误: IMU角速度数据不匹配")
    sys.exit(1)
if (
    imu.linear_acceleration[0] != double3_array[0]
    or imu.linear_acceleration[1] != double3_array[1]
    or imu.linear_acceleration[2] != double3_array[2]
):
    print(f"错误: IMU线性加速度数据不匹配")
    sys.exit(1)
print("✓ IMU结构体测试通过")

# ========== Header 结构体 ==========
header = magicdog.Header()
header.stamp = int(time.time() * 1e9)
header.frame_id = "base_link"
print(f"Header: {header}")
print(f"    stamp: {header.stamp}")
print(f"    frame_id: {header.frame_id}")

# 测试Header值
if header.frame_id != "base_link":
    print(f"错误: Header frame_id 期望值 'base_link'，实际值 '{header.frame_id}'")
    sys.exit(1)
print("✓ Header结构体测试通过")

# ========== PointField 结构体 ==========
point_field = magicdog.PointField()
point_field.name = "x"
point_field.offset = 10
point_field.datatype = 1
point_field.count = 1
print(f"PointField: {point_field}")
print(
    f"    name: {point_field.name}, offset: {point_field.offset}, datatype: {point_field.datatype}, count: {point_field.count}"
)

# 测试PointField值
if point_field.name != "x":
    print(f"错误: PointField name 期望值 'x'，实际值 '{point_field.name}'")
    sys.exit(1)
if point_field.offset != 10:
    print(f"错误: PointField offset 期望值 10，实际值 {point_field.offset}")
    sys.exit(1)
if point_field.datatype != 1:
    print(f"错误: PointField datatype 期望值 1，实际值 {point_field.datatype}")
    sys.exit(1)
if point_field.count != 1:
    print(f"错误: PointField count 期望值 1，实际值 {point_field.count}")
    sys.exit(1)
print("✓ PointField结构体测试通过")

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

# 测试PointCloud2值
if point_cloud2.height != 2:
    print(f"错误: PointCloud2 height 期望值 2，实际值 {point_cloud2.height}")
    sys.exit(1)
if point_cloud2.width != 2:
    print(f"错误: PointCloud2 width 期望值 2，实际值 {point_cloud2.width}")
    sys.exit(1)
if point_cloud2.is_bigendian != False:
    print(
        f"错误: PointCloud2 is_bigendian 期望值 False，实际值 {point_cloud2.is_bigendian}"
    )
    sys.exit(1)
if point_cloud2.point_step != 4:
    print(f"错误: PointCloud2 point_step 期望值 4，实际值 {point_cloud2.point_step}")
    sys.exit(1)
if point_cloud2.row_step != 8:
    print(f"错误: PointCloud2 row_step 期望值 8，实际值 {point_cloud2.row_step}")
    sys.exit(1)
if len(point_cloud2.data) != 8:
    print(f"错误: PointCloud2 data长度 期望值 8，实际值 {len(point_cloud2.data)}")
    sys.exit(1)
for i in range(8):
    if point_cloud2.data[i] != i:
        print(f"错误: PointCloud2 data[{i}] 期望值 {i}，实际值 {point_cloud2.data[i]}")
        sys.exit(1)
print("✓ PointCloud2结构体测试通过")

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

# 测试Image值
if image.height != 4:
    print(f"错误: Image height 期望值 4，实际值 {image.height}")
    sys.exit(1)
if image.width != 4:
    print(f"错误: Image width 期望值 4，实际值 {image.width}")
    sys.exit(1)
if image.encoding != "rgb8":
    print(f"错误: Image encoding 期望值 'rgb8'，实际值 '{image.encoding}'")
    sys.exit(1)
if image.is_bigendian != False:
    print(f"错误: Image is_bigendian 期望值 False，实际值 {image.is_bigendian}")
    sys.exit(1)
if image.step != image.width * 3:
    print(f"错误: Image step 期望值 {image.width * 3}，实际值 {image.step}")
    sys.exit(1)
print("✓ Image结构体测试通过")

# ========== DoubleVector/Double9Array/Double12Array ==========
double_vector = magicdog.DoubleVector()
for i in range(3):
    double_vector.append(i + 1.0)
print(f"DoubleVector: {double_vector}")

# 测试DoubleVector值
if len(double_vector) != 3:
    print(f"错误: DoubleVector长度 期望值 3，实际值 {len(double_vector)}")
    sys.exit(1)
for i in range(3):
    if abs(double_vector[i] - (i + 1.0)) > 1e-6:
        print(f"错误: DoubleVector[{i}] 期望值 {i + 1.0}，实际值 {double_vector[i]}")
        sys.exit(1)
print("✓ DoubleVector测试通过")

double9_array = magicdog.Double9Array()
for i in range(9):
    double9_array[i] = i + 1.0
print(f"Double9Array: {double9_array}")

double12_array = magicdog.Double12Array()
for i in range(12):
    double12_array[i] = i + 1.0
print(f"Double12Array: {double12_array}")

# 测试Double9Array值
if len(double9_array) != 9:
    print(f"错误: Double9Array长度 期望值 9，实际值 {len(double9_array)}")
    sys.exit(1)
for i in range(9):
    if abs(double9_array[i] - (i + 1.0)) > 1e-6:
        print(f"错误: Double9Array[{i}] 期望值 {i + 1.0}，实际值 {double9_array[i]}")
        sys.exit(1)
print("✓ Double9Array测试通过")

# 测试Double12Array值
if len(double12_array) != 12:
    print(f"错误: Double12Array长度 期望值 12，实际值 {len(double12_array)}")
    sys.exit(1)
for i in range(12):
    if abs(double12_array[i] - (i + 1.0)) > 1e-6:
        print(f"错误: Double12Array[{i}] 期望值 {i + 1.0}，实际值 {double12_array[i]}")
        sys.exit(1)
print("✓ Double12Array测试通过")

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

# 测试CameraInfo值

if camera_info.height != 480:
    print(f"错误: CameraInfo height 期望值 480，实际值 {camera_info.height}")
    sys.exit(1)
if camera_info.width != 640:
    print(f"错误: CameraInfo width 期望值 640，实际值 {camera_info.width}")
    sys.exit(1)

if camera_info.distortion_model != "plumb_bob":
    print(
        f"错误: CameraInfo distortion_model 期望值 'plumb_bob'，实际值 '{camera_info.distortion_model}'"
    )
    sys.exit(1)
if camera_info.D != double_vector:
    print(f"错误: CameraInfo D 期望值 {double_vector}，实际值 {camera_info.D}")
    sys.exit(1)
if (
    camera_info.K[0] != double9_array[0]
    or camera_info.K[1] != double9_array[1]
    or camera_info.K[2] != double9_array[2]
    or camera_info.K[3] != double9_array[3]
    or camera_info.K[4] != double9_array[4]
    or camera_info.K[5] != double9_array[5]
    or camera_info.K[6] != double9_array[6]
    or camera_info.K[7] != double9_array[7]
    or camera_info.K[8] != double9_array[8]
):
    print(f"错误: CameraInfo K 期望值 {double9_array}，实际值 {camera_info.K}")
    sys.exit(1)

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
print(
    f"    vin_time: {trinocular_camera_frame.vin_time}, decode_time: {trinocular_camera_frame.decode_time}"
)
print(
    f"    imgfl_array 前5项: {[trinocular_camera_frame.imgfl_array[i] for i in range(5)]}"
)
print(
    f"    imgf_array 前5项: {[trinocular_camera_frame.imgf_array[i] for i in range(5)]}"
)
print(
    f"    imgfr_array 前5项: {[trinocular_camera_frame.imgfr_array[i] for i in range(5)]}"
)

# 测试TrinocularCameraFrame值
if trinocular_camera_frame.vin_time != 1234567890:
    print(
        f"错误: TrinocularCameraFrame vin_time 期望值 1234567890，实际值 {trinocular_camera_frame.vin_time}"
    )
    sys.exit(1)
if trinocular_camera_frame.decode_time != 1234567999:
    print(
        f"错误: TrinocularCameraFrame decode_time 期望值 1234567999，实际值 {trinocular_camera_frame.decode_time}"
    )
    sys.exit(1)
if (
    trinocular_camera_frame.imgfl_array[0] != 0
    or trinocular_camera_frame.imgfl_array[1] != 1
    or trinocular_camera_frame.imgfl_array[2] != 2
):
    print(
        f"错误: TrinocularCameraFrame imgfl_array 期望值 {double_vector}，实际值 {trinocular_camera_frame.imgfl_array}"
    )
    sys.exit(1)
if (
    trinocular_camera_frame.imgf_array[0] != 10
    or trinocular_camera_frame.imgf_array[1] != 11
    or trinocular_camera_frame.imgf_array[2] != 12
):
    print(
        f"错误: TrinocularCameraFrame imgf_array 期望值 {double_vector}，实际值 {trinocular_camera_frame.imgf_array}"
    )
    sys.exit(1)
if (
    trinocular_camera_frame.imgfr_array[0] != 20
    or trinocular_camera_frame.imgfr_array[1] != 21
    or trinocular_camera_frame.imgfr_array[2] != 22
):
    print(
        f"错误: TrinocularCameraFrame imgfr_array 期望值 {double_vector}，实际值 {trinocular_camera_frame.imgfr_array}"
    )
    sys.exit(1)
print("✓ TrinocularCameraFrame结构体测试通过")

# ========== CompressedImage 结构体 ==========
compressed_image = magicdog.CompressedImage()
compressed_image.header = header
compressed_image.format = "jpeg"
for i in range(20):
    compressed_image.data.append(i)
print(f"CompressedImage: {compressed_image}")
print(f"    format: {compressed_image.format}")
print(f"    data 前5项: {[compressed_image.data[i] for i in range(5)]}")

# 测试CompressedImage值
if compressed_image.format != "jpeg":
    print(
        f"错误: CompressedImage format 期望值 'jpeg'，实际值 '{compressed_image.format}'"
    )
    sys.exit(1)
if (
    compressed_image.data[0] != 0
    or compressed_image.data[1] != 1
    or compressed_image.data[2] != 2
):
    print(
        f"错误: CompressedImage data 期望值 {double_vector}，实际值 {compressed_image.data}"
    )
    sys.exit(1)
print("✓ CompressedImage结构体测试通过")

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

# 测试LaserScan值

if laser_scan.angle_min != 0:
    print(f"错误: LaserScan angle_min 期望值 0，实际值 {laser_scan.angle_min}")
    sys.exit(1)
if laser_scan.angle_max != 180:
    print(f"错误: LaserScan angle_max 期望值 180，实际值 {laser_scan.angle_max}")
    sys.exit(1)

if (
    laser_scan.ranges[0] != 1.0
    or laser_scan.ranges[1] != 1.5
    or laser_scan.ranges[2] != 2.0
):
    print(f"错误: LaserScan ranges 期望值 {double_vector}，实际值 {laser_scan.ranges}")
    sys.exit(1)
if (
    laser_scan.intensities[0] != 100.0
    or laser_scan.intensities[1] != 101.0
    or laser_scan.intensities[2] != 102.0
):
    print(
        f"错误: LaserScan intensities 期望值 {double_vector}，实际值 {laser_scan.intensities}"
    )
    sys.exit(1)
print("✓ LaserScan结构体测试通过")

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
print(
    f"    layout.dim[0]: label={float_multi_array.layout.dim[0].label}, size={float_multi_array.layout.dim[0].size}, stride={float_multi_array.layout.dim[0].stride}"
)
print(
    f"    layout.dim[1]: label={float_multi_array.layout.dim[1].label}, size={float_multi_array.layout.dim[1].size}, stride={float_multi_array.layout.dim[1].stride}"
)
print(f"    data 前5项: {[float_multi_array.data[i] for i in range(5)]}")

# 测试Float32MultiArray值
if float_multi_array.layout.dim_size != 2:
    print(
        f"错误: Float32MultiArray layout.dim_size 期望值 2，实际值 {float_multi_array.layout.dim_size}"
    )
    sys.exit(1)
if float_multi_array.layout.dim[0].label != "height":
    print(
        f"错误: Float32MultiArray layout.dim[0].label 期望值 'height'，实际值 '{float_multi_array.layout.dim[0].label}'"
    )
    sys.exit(1)

if float_multi_array.layout.dim[1].label != "width":
    print(
        f"错误: Float32MultiArray layout.dim[1].label 期望值 'width'，实际值 '{float_multi_array.layout.dim[1].label}'"
    )
    sys.exit(1)
if float_multi_array.layout.dim[0].size != 3:
    print(
        f"错误: Float32MultiArray layout.dim[0].size 期望值 3，实际值 {float_multi_array.layout.dim[0].size}"
    )
    sys.exit(1)

if float_multi_array.layout.dim[1].size != 2:
    print(
        f"错误: Float32MultiArray layout.dim[1].size 期望值 2，实际值 {float_multi_array.layout.dim[1].size}"
    )
    sys.exit(1)
if float_multi_array.layout.dim[0].stride != 6:
    print(
        f"错误: Float32MultiArray layout.dim[0].stride 期望值 6，实际值 {float_multi_array.layout.dim[0].stride}"
    )
    sys.exit(1)

if float_multi_array.layout.dim[1].stride != 2:
    print(
        f"错误: Float32MultiArray layout.dim[1].stride 期望值 2，实际值 {float_multi_array.layout.dim[1].stride}"
    )
    sys.exit(1)
if float_multi_array.layout.data_offset != 0:
    print(
        f"错误: Float32MultiArray layout.data_offset 期望值 0，实际值 {float_multi_array.layout.data_offset}"
    )
    sys.exit(1)

if (
    float_multi_array.data[0] != 0.0
    or float_multi_array.data[1] != 1.1
    or float_multi_array.data[2] != 2.2
):
    print(
        f"错误: Float32MultiArray data 期望值 {double_vector}，实际值 {float_multi_array.data}"
    )
    sys.exit(1)
print("✓ Float32MultiArray结构体测试通过")

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
print(
    f"    layout.dim[0]: label={byte_multi_array.layout.dim[0].label}, size={byte_multi_array.layout.dim[0].size}, stride={byte_multi_array.layout.dim[0].stride}"
)
print(f"    data 前5项: {[byte_multi_array.data[i] for i in range(5)]}")

# 测试ByteMultiArray值
if byte_multi_array.layout.dim_size != 1:
    print(
        f"错误: ByteMultiArray layout.dim_size 期望值 1，实际值 {byte_multi_array.layout.dim_size}"
    )
    sys.exit(1)
if byte_multi_array.layout.dim[0].label != "length":
    print(
        f"错误: ByteMultiArray layout.dim[0].label 期望值 'length'，实际值 '{byte_multi_array.layout.dim[0].label}'"
    )
    sys.exit(1)

if byte_multi_array.layout.dim[0].size != 10:
    print(
        f"错误: ByteMultiArray layout.dim[0].size 期望值 10，实际值 {byte_multi_array.layout.dim[0].size}"
    )
    sys.exit(1)
if byte_multi_array.layout.dim[0].stride != 10:
    print(
        f"错误: ByteMultiArray layout.dim[0].stride 期望值 10，实际值 {byte_multi_array.layout.dim[0].stride}"
    )
    sys.exit(1)
if byte_multi_array.layout.data_offset != 0:
    print(
        f"错误: ByteMultiArray layout.data_offset 期望值 0，实际值 {byte_multi_array.layout.data_offset}"
    )
    sys.exit(1)

for i in range(10):
    if byte_multi_array.data[i] != i:
        print(
            f"错误: ByteMultiArray data[{i}] 期望值 {i}，实际值 {byte_multi_array.data[i]}"
        )
        sys.exit(1)
print("✓ ByteMultiArray结构体测试通过")

# ========== Int8 结构体 ==========
int8_struct = magicdog.Int8()
int8_struct.data = -8
print(f"Int8: {int8_struct}")
print(f"    data: {int8_struct.data}")

# 测试Int8值
if int8_struct.data != -8:
    print(f"错误: Int8 data 期望值 -8，实际值 {int8_struct.data}")
    sys.exit(1)
print("✓ Int8结构体测试通过")

print("所有传感器结构体示例测试完毕。")
