#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例 - 高级运动控制结构体测试

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来测试高级运动控制相关的结构体。
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


print("=== 测试系统状态结构体 ===")
# 测试成功状态
success_status = magicdog.Status()
success_status.code = magicdog.ErrorCode.OK
success_status.message = "系统运行正常，所有服务已就绪"
print(f"成功状态: 代码={success_status.code}, 消息='{success_status.message}'")

# 测试错误状态
error_status = magicdog.Status()
error_status.code = magicdog.ErrorCode.SERVICE_NOT_READY
error_status.message = "语音服务未就绪，请稍后重试"
print(f"错误状态: 代码={error_status.code}, 消息='{error_status.message}'")

# 测试状态值
if success_status.code != magicdog.ErrorCode.OK:
    print(f"错误: 成功状态代码不匹配")
    sys.exit(1)
if success_status.message != "系统运行正常，所有服务已就绪":
    print(f"错误: 成功状态消息不匹配")
    sys.exit(1)
if error_status.code != magicdog.ErrorCode.SERVICE_NOT_READY:
    print(f"错误: 错误状态代码不匹配")
    sys.exit(1)
if error_status.message != "语音服务未就绪，请稍后重试":
    print(f"错误: 错误状态消息不匹配")
    sys.exit(1)
print("✓ 系统状态结构体测试通过")

print("\n=== 测试控制器层级枚举 ===")
controller_level = magicdog.ControllerLevel.HIGH_LEVEL
print(
    f"控制器层级: {controller_level} (HIGH_LEVEL - 高层级控制器，负责路径规划和任务调度)"
)

low_level = magicdog.ControllerLevel.LOW_LEVEL
print(f"控制器层级: {low_level} (LOW_LEVEL - 低层级控制器，负责关节控制和稳定性)")

# 测试控制器层级枚举值
if controller_level != magicdog.ControllerLevel.HIGH_LEVEL:
    print(f"错误: 高层级控制器枚举值不匹配")
    sys.exit(1)
if low_level != magicdog.ControllerLevel.LOW_LEVEL:
    print(f"错误: 低层级控制器枚举值不匹配")
    sys.exit(1)
print("✓ 控制器层级枚举测试通过")

print("\n=== 测试摇杆控制指令 ===")
# 测试前进指令
forward_command = magicdog.JoystickCommand()
forward_command.left_x_axis = 0.0  # 不左右移动
forward_command.left_y_axis = 0.8  # 前进80%速度
forward_command.right_x_axis = 0.0  # 不旋转
forward_command.right_y_axis = 0.0  # 待定功能
print("前进指令:")
print(f"  左摇杆X轴: {forward_command.left_x_axis} (0.0 = 不左右移动)")
print(f"  左摇杆Y轴: {forward_command.left_y_axis} (0.8 = 前进80%速度)")
print(f"  右摇杆X轴: {forward_command.right_x_axis} (0.0 = 不旋转)")
print(f"  右摇杆Y轴: {forward_command.right_y_axis} (待定功能)")

# 测试前进指令值
if abs(forward_command.left_x_axis - 0.0) > 1e-6:
    print(f"错误: 前进指令左摇杆X轴 期望值 0.0，实际值 {forward_command.left_x_axis}")
    sys.exit(1)
if abs(forward_command.left_y_axis - 0.8) > 1e-6:
    print(f"错误: 前进指令左摇杆Y轴 期望值 0.8，实际值 {forward_command.left_y_axis}")
    sys.exit(1)
if abs(forward_command.right_x_axis - 0.0) > 1e-6:
    print(f"错误: 前进指令右摇杆X轴 期望值 0.0，实际值 {forward_command.right_x_axis}")
    sys.exit(1)
if abs(forward_command.right_y_axis - 0.0) > 1e-6:
    print(f"错误: 前进指令右摇杆Y轴 期望值 0.0，实际值 {forward_command.right_y_axis}")
    sys.exit(1)
print("✓ 前进指令测试通过")

# 测试左转指令
turn_left_command = magicdog.JoystickCommand()
turn_left_command.left_x_axis = -0.6  # 左转60%速度
turn_left_command.left_y_axis = 0.0  # 不前进后退
turn_left_command.right_x_axis = 0.0  # 不旋转
turn_left_command.right_y_axis = 0.0  # 待定功能
print("\n左转指令:")
print(f"  左摇杆X轴: {turn_left_command.left_x_axis} (-0.6 = 左转60%速度)")
print(f"  左摇杆Y轴: {turn_left_command.left_y_axis} (0.0 = 不前进后退)")
print(f"  右摇杆X轴: {turn_left_command.right_x_axis} (0.0 = 不旋转)")
print(f"  右摇杆Y轴: {turn_left_command.right_y_axis} (待定功能)")

# 测试左转指令值
if abs(turn_left_command.left_x_axis - -0.6) > 1e-6:
    print(
        f"错误: 左转指令左摇杆X轴 期望值 -0.6，实际值 {turn_left_command.left_x_axis}"
    )
    sys.exit(1)
if abs(turn_left_command.left_y_axis - 0.0) > 1e-6:
    print(f"错误: 左转指令左摇杆Y轴 期望值 0.0，实际值 {turn_left_command.left_y_axis}")
    sys.exit(1)
if abs(turn_left_command.right_x_axis - 0.0) > 1e-6:
    print(
        f"错误: 左转指令右摇杆X轴 期望值 0.0，实际值 {turn_left_command.right_x_axis}"
    )
    sys.exit(1)
if abs(turn_left_command.right_y_axis - 0.0) > 1e-6:
    print(
        f"错误: 左转指令右摇杆Y轴 期望值 0.0，实际值 {turn_left_command.right_y_axis}"
    )
    sys.exit(1)
print("✓ 左转指令测试通过")

# 测试旋转指令
rotate_command = magicdog.JoystickCommand()
rotate_command.left_x_axis = 0.0  # 不左右移动
rotate_command.left_y_axis = 0.0  # 不前进后退
rotate_command.right_x_axis = 0.7  # 右旋转70%速度
rotate_command.right_y_axis = 0.0  # 待定功能
print("\n旋转指令:")
print(f"  左摇杆X轴: {rotate_command.left_x_axis} (0.0 = 不左右移动)")
print(f"  左摇杆Y轴: {rotate_command.left_y_axis} (0.0 = 不前进后退)")
print(f"  右摇杆X轴: {rotate_command.right_x_axis} (0.7 = 右旋转70%速度)")
print(f"  右摇杆Y轴: {rotate_command.right_y_axis} (待定功能)")

# 测试旋转指令值

if abs(rotate_command.left_x_axis - 0.0) > 1e-6:
    print(f"错误: 旋转指令左摇杆X轴 期望值 0.0，实际值 {rotate_command.left_x_axis}")
    sys.exit(1)
if abs(rotate_command.left_y_axis - 0.0) > 1e-6:
    print(f"错误: 旋转指令左摇杆Y轴 期望值 0.0，实际值 {rotate_command.left_y_axis}")
    sys.exit(1)
if abs(rotate_command.right_x_axis - 0.7) > 1e-6:
    print(f"错误: 旋转指令右摇杆X轴 期望值 0.7，实际值 {rotate_command.right_x_axis}")
    sys.exit(1)
if abs(rotate_command.right_y_axis - 0.0) > 1e-6:
    print(f"错误: 旋转指令右摇杆Y轴 期望值 0.0，实际值 {rotate_command.right_y_axis}")
    sys.exit(1)
print("✓ 旋转指令测试通过")

print("\n=== 测试步态模式枚举 ===")
# 测试常用步态
walk_gait = magicdog.GaitMode.GAIT_WALK
print(f"步态模式: {walk_gait} (GAIT_WALK - 缓走，适合室内平稳环境)")

trot_gait = magicdog.GaitMode.GAIT_TROT
print(f"步态模式: {trot_gait} (GAIT_TROT - 小跑，适合户外快速移动)")

stand_gait = magicdog.GaitMode.GAIT_STAND_B
print(f"步态模式: {stand_gait} (GAIT_STAND_B - 力控站立，姿态展示)")

crawl_gait = magicdog.GaitMode.GAIT_CRAWL
print(f"步态模式: {crawl_gait} (GAIT_CRAWL - 爬行，适合低矮空间)")

print("\n=== 测试特技动作枚举 ===")
# 测试基础动作
wiggle_hip = magicdog.TrickAction.ACTION_WIGGLE_HIP
print(f"特技动作: {wiggle_hip} (ACTION_WIGGLE_HIP - 扭屁股，娱乐动作)")

stretch = magicdog.TrickAction.ACTION_STRETCH
print(f"特技动作: {stretch} (ACTION_STRETCH - 伸懒腰，热身动作)")

push_up = magicdog.TrickAction.ACTION_PUSH_UP
print(f"特技动作: {push_up} (ACTION_PUSH_UP - 俯卧撑，健身动作)")

# 测试高级动作
back_flip = magicdog.TrickAction.ACTION_BACK_FLIP
print(f"特技动作: {back_flip} (ACTION_BACK_FLIP - 后空翻，高难度动作)")

front_flip = magicdog.TrickAction.ACTION_FRONT_FLIP
print(f"特技动作: {front_flip} (ACTION_FRONT_FLIP - 前空翻，高难度动作)")

high_jump = magicdog.TrickAction.ACTION_HIGH_JUMP
print(f"特技动作: {high_jump} (ACTION_HIGH_JUMP - 跳高，跳跃动作)")

# 测试舞蹈动作
swing_dance = magicdog.TrickAction.ACTION_SWING_DANCE
print(f"特技动作: {swing_dance} (ACTION_SWING_DANCE - 摇摆舞，舞蹈动作)")

random_dance = magicdog.TrickAction.ACTION_RANDOM_DANCE
print(f"特技动作: {random_dance} (ACTION_RANDOM_DANCE - 随机跳舞，娱乐动作)")

# 测试实用动作
sit_down = magicdog.TrickAction.ACTION_SIT_DOWN
print(f"特技动作: {sit_down} (ACTION_SIT_DOWN - 坐下，实用动作)")

lie_down = magicdog.TrickAction.ACTION_LIE_DOWN
print(f"特技动作: {lie_down} (ACTION_LIE_DOWN - 趴下，实用动作)")

recovery_stand = magicdog.TrickAction.ACTION_RECOVERY_STAND
print(f"特技动作: {recovery_stand} (ACTION_RECOVERY_STAND - 起立，恢复动作)")

print("\n=== 测试动作组合场景 ===")
print("场景1: 机器人表演秀")
print(f"  1. 入场: {magicdog.TrickAction.ACTION_SLOW_GO_FRONT} (过来)")
print(f"  2. 热身: {magicdog.TrickAction.ACTION_STRETCH} (伸懒腰)")
print(f"  3. 表演: {magicdog.TrickAction.ACTION_SWING_DANCE} (摇摆舞)")
print(f"  4. 谢幕: {magicdog.TrickAction.ACTION_HAPPY_NEW_YEAR} (拜年)")

print("\n场景2: 健身训练")
print(f"  1. 准备: {magicdog.TrickAction.ACTION_STRETCH} (伸懒腰)")
print(f"  2. 训练: {magicdog.TrickAction.ACTION_PUSH_UP} (俯卧撑)")
print(f"  3. 放松: {magicdog.TrickAction.ACTION_ACT_CUTE} (撒娇)")

print("\n场景3: 紧急情况处理")
print(f"  1. 检测: {magicdog.TrickAction.ACTION_EMERGENCY_STOP} (急停)")
print(f"  2. 保护: {magicdog.TrickAction.ACTION_LIE_DOWN} (趴下)")
print(f"  3. 恢复: {magicdog.TrickAction.ACTION_RECOVERY_STAND} (起立)")

print("\n=== 测试完成 ===")
print("已成功测试以下结构体和枚举:")
print("  - Status: 系统状态信息")
print("  - ControllerLevel: 控制器层级")
print("  - JoystickCommand: 摇杆控制指令")
print("  - GaitMode: 步态模式")
print("  - TrickAction: 特技动作")
print("\n所有测试数据都使用了有意义的实际场景值，便于理解各字段的用途。")
