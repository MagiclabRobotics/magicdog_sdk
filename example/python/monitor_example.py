#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来控制机器人。
"""

import sys
import time

# 添加构建目录到 Python 路径
sys.path.append('../../build')

try:
    import magicdog_python as magicdog
    print("成功导入 MagicDog Python 模块！")
except ImportError as e:
    print(f"导入失败: {e}")
    print("请先运行 build_python.sh 构建 Python 绑定")
    sys.exit(1)

def main():
    """主函数"""
    print("MagicDog SDK Python 示例程序")

    robot = magicdog.MagicRobot()
    if not robot.initialize("192.168.55.10"):
        print("初始化失败")
        return
    
    robot.set_timeout(5000)
    
    if not robot.connect():
        print("连接失败")
        robot.shutdown()
        return

    time.sleep(10)

    monitor = robot.get_state_monitor()

    state = monitor.get_current_state()
    print(f"health: {state.bms_data.battery_health}, percentage: {state.bms_data.battery_percentage}, state: {state.bms_data.battery_state}, power_supply_status: {state.bms_data.power_supply_status}")

    for fault in state.faults:
        print(f"code: {fault.error_code}, message: {fault.error_message}")
    
    robot.disconnect()
    robot.shutdown()
    
    print("\n示例程序执行完成！")

if __name__ == "__main__":
    main() 