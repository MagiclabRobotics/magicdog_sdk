#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例 - 监控与状态结构体测试

本文件展示了如何使用 MagicDog SDK 的 Python 绑定来测试机器人监控相关的结构体和枚举。
涵盖了错误码、状态、故障、电池管理系统、机器人整体状态等典型监控数据结构。
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

print("=== 测试错误码枚举 ===")
error_code_ok = magicdog.ErrorCode.OK
error_code_timeout = magicdog.ErrorCode.TIMEOUT
print(f"错误代码(OK): {error_code_ok}")
print(f"错误代码(TIMEOUT): {error_code_timeout}")

print("\n=== 测试状态结构体 ===")
status = magicdog.Status()
status.code = error_code_ok
status.message = "系统运行正常"
print(f"状态: 代码={status.code}, 信息='{status.message}'")

status_error = magicdog.Status()
status_error.code = error_code_timeout
status_error.message = "服务超时"
print(f"状态: 代码={status_error.code}, 信息='{status_error.message}'")

print("\n=== 测试故障结构体 ===")
fault = magicdog.Fault()
fault.error_code = error_code_timeout
fault.error_message = "通信超时"
print(f"故障: 错误码={fault.error_code}, 错误信息='{fault.error_message}'")

fault2 = magicdog.Fault()
fault2.error_code = magicdog.ErrorCode.INTERNAL_ERROR
fault2.error_message = "内部错误"
print(f"故障2: 错误码={fault2.error_code}, 错误信息='{fault2.error_message}'")

print("\n=== 测试电池状态与电源状态枚举 ===")
battery_state = magicdog.BatteryState.GOOD
battery_state_overheat = magicdog.BatteryState.OVERHEAT
print(f"电池状态(GOOD): {battery_state}")
print(f"电池状态(OVERHEAT): {battery_state_overheat}")

power_supply_status = magicdog.PowerSupplyStatus.CHARGING
power_supply_status_full = magicdog.PowerSupplyStatus.FULL
print(f"电池充放电状态(CHARGING): {power_supply_status}")
print(f"电池充放电状态(FULL): {power_supply_status_full}")

print("\n=== 测试电池管理系统数据结构体 ===")
bms_data = magicdog.BmsData()
bms_data.battery_percentage = 50.0
bms_data.battery_health = 85.0
bms_data.battery_state = battery_state
bms_data.power_supply_status = power_supply_status
print(f"电池管理系统数据: 电量={bms_data.battery_percentage}%, 健康度={bms_data.battery_health}%, 状态={bms_data.battery_state}, 供电状态={bms_data.power_supply_status}")

bms_data2 = magicdog.BmsData()
bms_data2.battery_percentage = 10.0
bms_data2.battery_health = 60.0
bms_data2.battery_state = battery_state_overheat
bms_data2.power_supply_status = power_supply_status_full
print(f"电池管理系统数据2: 电量={bms_data2.battery_percentage}%, 健康度={bms_data2.battery_health}%, 状态={bms_data2.battery_state}, 供电状态={bms_data2.power_supply_status}")

print("\n=== 测试机器人整体状态结构体 ===")
robot_state = magicdog.RobotState()
robot_state.faults = magicdog.FaultVector()
robot_state.faults.append(fault)
robot_state.faults.append(fault2)
robot_state.bms_data = bms_data
print(f"机器人状态: 故障数={len(robot_state.faults)}, 电池信息={robot_state.bms_data}")

print("\n详细打印所有故障信息:")
for idx, f in enumerate(robot_state.faults):
    print(f"  故障{idx+1}: 错误码={f.error_code}, 错误信息='{f.error_message}'")

print("\n=== 场景模拟: 机器人监控流程 ===")
print("1. 检查系统状态")
if status.code == magicdog.ErrorCode.OK:
    print("  系统正常运行")
else:
    print(f"  系统异常: {status.message}")

print("2. 检查电池状态")
if bms_data.battery_percentage < 20.0:
    print("  电池电量低，请及时充电")
else:
    print(f"  当前电池电量: {bms_data.battery_percentage}%")

print("3. 检查故障列表")
if len(robot_state.faults) == 0:
    print("  没有检测到故障")
else:
    for f in robot_state.faults:
        print(f"  检测到故障: 错误码={f.error_code}, 信息={f.error_message}")

print("\n=== 测试完成 ===")
print("已成功测试以下监控相关结构体和枚举:")
print("  - ErrorCode: 错误码")
print("  - Status: 状态信息")
print("  - Fault: 故障信息")
print("  - BatteryState: 电池状态")
print("  - PowerSupplyStatus: 电池供电状态")
print("  - BmsData: 电池管理系统数据")
print("  - RobotState: 机器人整体状态")
print("\n所有测试数据均为有意义的实际场景值，便于理解各字段的用途。")