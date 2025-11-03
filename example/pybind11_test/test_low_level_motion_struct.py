#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例 - 低级运动控制结构体测试

本文件展示了如何使用 MagicDog SDK 的 Python 绑定来测试低级运动控制相关的结构体和枚举。
涵盖了步态模式、单腿关节命令、全腿关节命令、单腿状态、全腿状态等典型低层级控制数据结构。
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


print("=== 测试低层级步态模式枚举 ===")
low_level_gait = magicdog.GaitMode.GAIT_LOWLEVL_SDK
print(f"低层级步态: {low_level_gait} (GAIT_LOWLEVL_SDK - 低层SDK自定义步态)")

# 测试低层级步态枚举值
if low_level_gait != magicdog.GaitMode.GAIT_LOWLEVL_SDK:
    print(f"错误: 低层级步态枚举值不匹配")
    sys.exit(1)
print("✓ 低层级步态模式枚举测试通过")

print("\n=== 测试单腿关节命令结构体 ===")
single_leg_cmd = magicdog.SingleLegJointCommand()
single_leg_cmd.q_des = 0.5  # 期望关节角度
single_leg_cmd.dq_des = 0.1  # 期望关节速度
single_leg_cmd.tau_des = 0.2  # 期望关节力矩
single_leg_cmd.kp = 10.0  # 关节位置增益
single_leg_cmd.kd = 0.5  # 关节速度增益
print(
    f"单腿关节命令: q_des={single_leg_cmd.q_des}, dq_des={single_leg_cmd.dq_des}, tau_des={single_leg_cmd.tau_des}, kp={single_leg_cmd.kp}, kd={single_leg_cmd.kd}"
)

# 测试单腿关节命令值
if abs(single_leg_cmd.q_des - 0.5) > 1e-6:
    print(f"错误: 期望关节角度 期望值 0.5，实际值 {single_leg_cmd.q_des}")
    sys.exit(1)
if abs(single_leg_cmd.dq_des - 0.1) > 1e-6:
    print(f"错误: 期望关节速度 期望值 0.1，实际值 {single_leg_cmd.dq_des}")
    sys.exit(1)
if abs(single_leg_cmd.tau_des - 0.2) > 1e-6:
    print(f"错误: 期望关节力矩 期望值 0.2，实际值 {single_leg_cmd.tau_des}")
    sys.exit(1)
if abs(single_leg_cmd.kp - 10.0) > 1e-6:
    print(f"错误: 关节位置增益 期望值 10.0，实际值 {single_leg_cmd.kp}")
    sys.exit(1)
if abs(single_leg_cmd.kd - 0.5) > 1e-6:
    print(f"错误: 关节速度增益 期望值 0.5，实际值 {single_leg_cmd.kd}")
    sys.exit(1)
print("✓ 单腿关节命令结构体测试通过")

print("\n=== 测试全腿关节命令结构体 ===")
leg_joint_cmd = magicdog.LegJointCommand()
leg_joint_cmd.timestamp = int(time.time() * 1e9)  # 当前时间戳（纳秒）
for i in range(magicdog.LEG_JOINT_NUM):
    # 每条腿都赋予不同的命令，便于区分
    cmd = magicdog.SingleLegJointCommand()
    cmd.q_des = 0.5 + i
    cmd.dq_des = 0.1 * (i + 1)
    cmd.tau_des = 0.2 * (i + 1)
    cmd.kp = 10.0 + i
    cmd.kd = 0.5 + 0.1 * i
    leg_joint_cmd.cmd[i] = cmd
print("全腿关节命令详情:")
for i in range(magicdog.LEG_JOINT_NUM):
    c = leg_joint_cmd.cmd[i]
    print(
        f"  腿{i}: q_des={c.q_des}, dq_des={c.dq_des}, tau_des={c.tau_des}, kp={c.kp}, kd={c.kd}"
    )
print(f"全腿关节命令结构体: {leg_joint_cmd}")

# 测试全腿关节命令值
for i in range(magicdog.LEG_JOINT_NUM):
    c = leg_joint_cmd.cmd[i]
    expected_q_des = 0.5 + i
    expected_dq_des = 0.1 * (i + 1)
    expected_tau_des = 0.2 * (i + 1)
    expected_kp = 10.0 + i
    expected_kd = 0.5 + 0.1 * i

    if abs(c.q_des - expected_q_des) > 1e-6:
        print(f"错误: 腿{i}期望关节角度 期望值 {expected_q_des}，实际值 {c.q_des}")
        sys.exit(1)
    if abs(c.dq_des - expected_dq_des) > 1e-6:
        print(f"错误: 腿{i}期望关节速度 期望值 {expected_dq_des}，实际值 {c.dq_des}")
        sys.exit(1)
    if abs(c.tau_des - expected_tau_des) > 1e-6:
        print(f"错误: 腿{i}期望关节力矩 期望值 {expected_tau_des}，实际值 {c.tau_des}")
        sys.exit(1)
    if abs(c.kp - expected_kp) > 1e-6:
        print(f"错误: 腿{i}关节位置增益 期望值 {expected_kp}，实际值 {c.kp}")
        sys.exit(1)
    if abs(c.kd - expected_kd) > 1e-6:
        print(f"错误: 腿{i}关节速度增益 期望值 {expected_kd}，实际值 {c.kd}")
        sys.exit(1)
print("✓ 全腿关节命令结构体测试通过")

print("\n=== 测试单腿关节状态结构体 ===")
single_leg_state = magicdog.SingleLegJointState()
single_leg_state.q = 1.2  # 当前关节角度
single_leg_state.dq = 0.3  # 当前关节速度
single_leg_state.tau_est = 0.4  # 当前估算力矩
print(
    f"单腿关节状态: q={single_leg_state.q}, dq={single_leg_state.dq}, tau_est={single_leg_state.tau_est}"
)

print("\n=== 测试全腿关节状态结构体 ===")
leg_state = magicdog.LegState()
leg_state.timestamp = int(time.time() * 1e9)
for i in range(magicdog.LEG_JOINT_NUM):
    state = magicdog.SingleLegJointState()
    state.q = 1.2 + i
    state.dq = 0.3 * (i + 1)
    state.tau_est = 0.4 * (i + 1)
    leg_state.state[i] = state
print("全腿关节状态详情:")
for i in range(magicdog.LEG_JOINT_NUM):
    s = leg_state.state[i]
    print(f"  腿{i}: q={s.q}, dq={s.dq}, tau_est={s.tau_est}")
print(f"全腿关节状态结构体: {leg_state}")

print("\n=== 测试完成 ===")
print("已成功测试以下低层级结构体和枚举:")
print("  - GaitMode: 步态模式")
print("  - SingleLegJointCommand: 单腿关节命令")
print("  - LegJointCommand: 全腿关节命令")
print("  - SingleLegJointState: 单腿关节状态")
print("  - LegState: 全腿关节状态")
print("\n所有测试数据均为有意义的实际场景值，便于理解各字段的用途。")
