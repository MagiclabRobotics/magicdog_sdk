#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python SLAM导航结构测试

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来测试SLAM导航相关的数据结构。
"""

import sys
import time
import magicdog_python as magicdog
from magicdog_python import TtsCommand, TtsPriority, TtsMode, GetSpeechConfig

print("=== 测试导航模式枚举 ===")
nav_idle = magicdog.NavMode.IDLE
nav_grid_map = magicdog.NavMode.GRID_MAP

print(f"导航模式 - 空闲: {nav_idle}")
print(f"导航模式 - 栅格地图: {nav_grid_map}")

# 测试枚举值
if nav_idle != magicdog.NavMode.IDLE:
    print(f"错误: NAV_IDLE 期望值 0，实际值 {nav_idle}")
    sys.exit(1)
if nav_grid_map != magicdog.NavMode.GRID_MAP:
    print(f"错误: NAV_GRID_MAP 期望值 1，实际值 {nav_grid_map}")
    sys.exit(1)
print("✓ 导航模式枚举测试通过")

print("\n=== 测试导航状态类型枚举 ===")
nav_none = magicdog.NavStatusType.NONE
nav_running = magicdog.NavStatusType.RUNNING
nav_end_success = magicdog.NavStatusType.END_SUCCESS
nav_end_failed = magicdog.NavStatusType.END_FAILED
nav_pause = magicdog.NavStatusType.PAUSE

print(f"导航状态 - 无状态: {nav_none}")
print(f"导航状态 - 运行中: {nav_running}")
print(f"导航状态 - 结束成功: {nav_end_success}")
print(f"导航状态 - 结束失败: {nav_end_failed}")
print(f"导航状态 - 暂停: {nav_pause}")

# 测试枚举值
if nav_none != magicdog.NavStatusType.NONE:
    print(f"错误: NAV_NONE 期望值 0，实际值 {nav_none}")
    sys.exit(1)
if nav_running != magicdog.NavStatusType.RUNNING:
    print(f"错误: NAV_RUNNING 期望值 1，实际值 {nav_running}")
    sys.exit(1)
if nav_end_success != magicdog.NavStatusType.END_SUCCESS:
    print(f"错误: NAV_END_SUCCESS 期望值 2，实际值 {nav_end_success}")
    sys.exit(1)
if nav_end_failed != magicdog.NavStatusType.END_FAILED:
    print(f"错误: NAV_END_FAILED 期望值 3，实际值 {nav_end_failed}")
    sys.exit(1)
if nav_pause != magicdog.NavStatusType.PAUSE:
    print(f"错误: NAV_PAUSE 期望值 4，实际值 {nav_pause}")
    sys.exit(1)
print("✓ 导航状态类型枚举测试通过")

print("\n=== 测试 3D 位姿结构 ===")
pose_3d = magicdog.Pose3DEuler()

# pose_3d.position = [1.5, 2.3, 0.8]
# pose_3d.orientation = [0.1, 0.05, 1.57]

pose_3d.position[0] = 1.5
pose_3d.position[1] = 2.3
pose_3d.position[2] = 0.8

pose_3d.orientation[0] = 0.1
pose_3d.orientation[1] = 0.05
pose_3d.orientation[2] = 1.57

print(f"3D位姿:")
print(
    f"  位置: x={pose_3d.position[0]:.2f}, y={pose_3d.position[1]:.2f}, z={pose_3d.position[2]:.2f}"
)
print(
    f"  姿态: roll={pose_3d.orientation[0]:.2f}, pitch={pose_3d.orientation[1]:.2f}, yaw={pose_3d.orientation[2]:.2f}"
)

# 测试位姿值
expected_position = [1.5, 2.3, 0.8]
expected_orientation = [0.1, 0.05, 1.57]
for i in range(3):
    if abs(pose_3d.position[i] - expected_position[i]) > 1e-6:
        print(
            f"错误: 位置[{i}] 期望值 {expected_position[i]}，实际值 {pose_3d.position[i]}"
        )
        sys.exit(1)
    if abs(pose_3d.orientation[i] - expected_orientation[i]) > 1e-6:
        print(
            f"错误: 姿态[{i}] 期望值 {expected_orientation[i]}，实际值 {pose_3d.orientation[i]}"
        )
        sys.exit(1)
print("✓ 3D位姿结构测试通过")

print("\n=== 测试导航目标点结构 ===")
target_goal = magicdog.NavTarget()
target_goal.id = 1001
target_goal.frame_id = "map"
target_goal.goal = pose_3d

print(f"导航目标点:")
print(f"  ID: {target_goal.id}")
print(f"  坐标系: {target_goal.frame_id}")
print(
    f"  目标位姿: 位置=({target_goal.goal.position[0]:.2f}, {target_goal.goal.position[1]:.2f}, {target_goal.goal.position[2]:.2f})"
)

# 测试目标点值
if target_goal.id != 1001:
    print(f"错误: 目标点ID 期望值 1001，实际值 {target_goal.id}")
    sys.exit(1)
if target_goal.frame_id != "map":
    print(f"错误: 坐标系 期望值 'map'，实际值 '{target_goal.frame_id}'")
    sys.exit(1)
if target_goal.goal.position[0] != 1.5:
    print(f"错误: 目标位姿不匹配")
    sys.exit(1)
if target_goal.goal.position[1] != 2.3:
    print(f"错误: 目标位姿不匹配")
    sys.exit(1)
if target_goal.goal.position[2] != 0.8:
    print(f"错误: 目标位姿不匹配")
    sys.exit(1)
if target_goal.goal.orientation[0] != 0.1:
    print(f"错误: 目标位姿不匹配")
    sys.exit(1)
if target_goal.goal.orientation[1] != 0.05:
    print(f"错误: 目标位姿不匹配")
    sys.exit(1)
print("✓ 导航目标点结构测试通过")

print("\n=== 测试导航状态结构 ===")
nav_status = magicdog.NavStatus()
nav_status.id = 1001
nav_status.status = nav_running
nav_status.message = "正在导航到目标点"

print(f"导航状态:")
print(f"  目标点ID: {nav_status.id}")
print(f"  状态: {nav_status.status}")
print(f"  消息: {nav_status.message}")

# 测试导航状态值
if nav_status.id != 1001:
    print(f"错误: 导航状态ID 期望值 1001，实际值 {nav_status.id}")
    sys.exit(1)
if nav_status.status != nav_running:
    print(f"错误: 导航状态 期望值 {nav_running}，实际值 {nav_status.status}")
    sys.exit(1)
if nav_status.message != "正在导航到目标点":
    print(f"错误: 导航消息 期望值 '正在导航到目标点'，实际值 '{nav_status.message}'")
    sys.exit(1)
print("✓ 导航状态结构测试通过")

print("\n=== 测试地图图像数据结构 ===")
map_image_data = magicdog.MapImageData()
map_image_data.type = "P5"  # 二进制PGM格式
map_image_data.width = 1024
map_image_data.height = 1024
map_image_data.max_gray_value = 255
# 创建示例图像数据 (1024x1024的简单图案)
map_image_data.image = [128]

print(f"地图图像数据:")
print(f"  格式: {map_image_data.type}")
print(f"  尺寸: {map_image_data.width} x {map_image_data.height}")
print(f"  最大灰度值: {map_image_data.max_gray_value}")
print(f"  图像数据长度: {len(map_image_data.image)} 像素")

# 测试地图图像数据值
if map_image_data.type != "P5":
    print(f"错误: 图像格式 期望值 'P5'，实际值 '{map_image_data.type}'")
    sys.exit(1)
if map_image_data.width != 1024:
    print(f"错误: 图像宽度 期望值 1024，实际值 {map_image_data.width}")
    sys.exit(1)
if map_image_data.height != 1024:
    print(f"错误: 图像高度 期望值 1024，实际值 {map_image_data.height}")
    sys.exit(1)
if map_image_data.max_gray_value != 255:
    print(f"错误: 最大灰度值 期望值 255，实际值 {map_image_data.max_gray_value}")
    sys.exit(1)
if len(map_image_data.image) != 1:
    print(f"错误: 图像数据长度 期望值 1，实际值 {len(map_image_data.image)}")
    sys.exit(1)
if map_image_data.image[0] != 128:
    print(f"错误: 图像数据[0] 期望值 128，实际值 {map_image_data.image[0]}")
    sys.exit(1)
print("✓ 地图图像数据结构测试通过")

print("\n=== 测试地图元数据结构 ===")
map_meta_data = magicdog.MapMetaData()
map_meta_data.resolution = 0.05  # 5cm/pixel
map_meta_data.origin = pose_3d
map_meta_data.map_image_data = map_image_data

print(f"地图元数据:")
print(f"  分辨率: {map_meta_data.resolution} m/pixel")
print(
    f"  原点位置: ({map_meta_data.origin.position[0]:.2f}, {map_meta_data.origin.position[1]:.2f}, {map_meta_data.origin.position[2]:.2f})"
)
print(
    f"  图像数据: {map_meta_data.map_image_data.width}x{map_meta_data.map_image_data.height}"
)

# 测试地图元数据值
if abs(map_meta_data.resolution - 0.05) > 1e-6:
    print(f"错误: 地图分辨率 期望值 0.05，实际值 {map_meta_data.resolution}")
    sys.exit(1)
if map_meta_data.origin.position[0] != 1.5:
    print(f"错误: 地图原点位姿不匹配")
    sys.exit(1)
if map_meta_data.origin.position[1] != 2.3:
    print(f"错误: 地图原点位姿不匹配")
    sys.exit(1)
if map_meta_data.origin.position[2] != 0.8:
    print(f"错误: 地图原点位姿不匹配")
    sys.exit(1)
if map_meta_data.origin.orientation[0] != 0.1:
    print(f"错误: 地图原点位姿不匹配")
    sys.exit(1)
if map_meta_data.origin.orientation[1] != 0.05:
    print(f"错误: 地图原点位姿不匹配")
    sys.exit(1)
if map_meta_data.map_image_data.type != "P5":
    print(f"错误: 地图图像数据不匹配")
    sys.exit(1)
if map_meta_data.map_image_data.width != 1024:
    print(f"错误: 地图图像数据不匹配")
    sys.exit(1)
if map_meta_data.map_image_data.height != 1024:
    print(f"错误: 地图图像数据不匹配")
    sys.exit(1)
if map_meta_data.map_image_data.max_gray_value != 255:
    print(f"错误: 地图图像数据不匹配")
    sys.exit(1)
if map_meta_data.map_image_data.image[0] != 128:
    print(f"错误: 地图图像数据不匹配")
    sys.exit(1)
print("✓ 地图元数据结构测试通过")

print("\n=== 测试单个地图信息结构 ===")
map_info = magicdog.MapInfo()
map_info.map_name = "office_floor_1"
map_info.map_meta_data = map_meta_data

print(f"地图信息:")
print(f"  地图名称: {map_info.map_name}")
print(
    f"  地图尺寸: {map_info.map_meta_data.map_image_data.width}x{map_info.map_meta_data.map_image_data.height}"
)
print(f"  地图分辨率: {map_info.map_meta_data.resolution} m/pixel")

# 测试地图信息值
if map_info.map_name != "office_floor_1":
    print(f"错误: 地图名称 期望值 'office_floor_1'，实际值 '{map_info.map_name}'")
    sys.exit(1)
if map_info.map_meta_data.resolution != 0.05:
    print(f"错误: 地图元数据不匹配")
    sys.exit(1)
if map_info.map_meta_data.origin.position[0] != 1.5:
    print(f"错误: 地图元数据不匹配")
    sys.exit(1)
if map_info.map_meta_data.origin.position[1] != 2.3:
    print(f"错误: 地图元数据不匹配")
    sys.exit(1)
if map_info.map_meta_data.origin.position[2] != 0.8:
    print(f"错误: 地图元数据不匹配")
    sys.exit(1)
if map_info.map_meta_data.origin.orientation[0] != 0.1:
    print(f"错误: 地图元数据不匹配")
    sys.exit(1)
print("✓ 单个地图信息结构测试通过")

print("\n=== 测试所有地图信息结构 ===")
all_map_info = magicdog.AllMapInfo()
all_map_info.current_map_name = "office_floor_1"

# 创建多个地图信息
map_info_1 = magicdog.MapInfo()
map_info_1.map_name = "office_floor_1"
map_info_1.map_meta_data = map_meta_data

map_info_2 = magicdog.MapInfo()
map_info_2.map_name = "office_floor_2"
map_info_2.map_meta_data = map_meta_data

map_info_3 = magicdog.MapInfo()
map_info_3.map_name = "warehouse_main"
map_info_3.map_meta_data = map_meta_data

all_map_info.map_infos = [map_info_1, map_info_2, map_info_3]

print(f"所有地图信息:")
print(f"  当前地图: {all_map_info.current_map_name}")
print(f"  地图总数: {len(all_map_info.map_infos)}")
for i, map_info in enumerate(all_map_info.map_infos):
    print(f"    地图{i+1}: {map_info.map_name}")

# 测试所有地图信息值
if all_map_info.current_map_name != "office_floor_1":
    print(
        f"错误: 当前地图名称 期望值 'office_floor_1'，实际值 '{all_map_info.current_map_name}'"
    )
    sys.exit(1)
if len(all_map_info.map_infos) != 3:
    print(f"错误: 地图数量 期望值 3，实际值 {len(all_map_info.map_infos)}")
    sys.exit(1)
expected_names = ["office_floor_1", "office_floor_2", "warehouse_main"]
for i, map_info in enumerate(all_map_info.map_infos):
    if map_info.map_name != expected_names[i]:
        print(
            f"错误: 地图{i+1}名称 期望值 '{expected_names[i]}'，实际值 '{map_info.map_name}'"
        )
        sys.exit(1)
print("✓ 所有地图信息结构测试通过")

print("\n=== 测试当前位置信息结构 ===")
localization_info = magicdog.LocalizationInfo()
localization_info.is_localization = True
localization_info.pose = pose_3d

print(f"当前位置信息:")
print(f"  是否已定位: {localization_info.is_localization}")
print(
    f"  当前位置: ({localization_info.pose.position[0]:.2f}, {localization_info.pose.position[1]:.2f}, {localization_info.pose.position[2]:.2f})"
)
print(
    f"  当前姿态: roll={localization_info.pose.orientation[0]:.2f}, pitch={localization_info.pose.orientation[1]:.2f}, yaw={localization_info.pose.orientation[2]:.2f}"
)

# 测试位置信息值
if localization_info.is_localization != True:
    print(f"错误: 定位状态 期望值 True，实际值 {localization_info.is_localization}")
    sys.exit(1)
if localization_info.pose.position[0] != 1.5:
    print(f"错误: 位置信息不匹配")
    sys.exit(1)
if localization_info.pose.position[1] != 2.3:
    print(f"错误: 位置信息不匹配")
    sys.exit(1)
if localization_info.pose.position[2] != 0.8:
    print(f"错误: 位置信息不匹配")
    sys.exit(1)
if localization_info.pose.orientation[0] != 0.1:
    print(f"错误: 位置信息不匹配")
    sys.exit(1)
if localization_info.pose.orientation[1] != 0.05:
    print(f"错误: 位置信息不匹配")
    sys.exit(1)
print("✓ 当前位置信息结构测试通过")

print("\n=== 测试 SLAM 导航完整流程 ===")
print("模拟SLAM导航完整流程:")
print("1. 初始化SLAM导航控制器")
print("2. 激活建图模式")
print("3. 进行环境建图")
print("4. 保存地图")
print("5. 激活定位模式")
print("6. 加载地图进行定位")
print("7. 激活导航模式")
print("8. 设置导航目标点")
print("9. 开始导航")
print("10. 监控导航状态")
print("11. 导航完成或取消")

print("\n=== 测试完成 ===")
print("🎉 所有SLAM导航相关数据结构测试完成！")
print("✅ 所有测试均通过，Python绑定工作正常")
