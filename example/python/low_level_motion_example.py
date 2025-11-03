#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来控制机器人。
"""

import sys
import time
import threading

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
    
    print("设置运动控制级别为高级别")
    status = robot.set_motion_control_level(magicdog.ControllerLevel.HIGH_LEVEL)
    if status.code != magicdog.ErrorCode.OK:
        print(f"设置运动控制级别失败: {status.message}")
        robot.shutdown()
        return
    
    print("获取高级别运动控制器")
    high_controller = robot.get_high_level_motion_controller()
    
    print("设置运动模式为被动")
    status = high_controller.set_gait(magicdog.GaitMode.GAIT_PASSIVE)
    if status.code != magicdog.ErrorCode.OK:
        print(f"设置运动模式失败: {status.message}")
        robot.shutdown()
        return

    print("等待运动模式变为被动")
    current_mode = magicdog.GaitMode.GAIT_DEFAULT
    while current_mode != magicdog.GaitMode.GAIT_PASSIVE:
        current_mode = high_controller.get_gait()
        time.sleep(0.1)

    time.sleep(2)

    print("设置运动控制级别为低级别")
    status = robot.set_motion_control_level(magicdog.ControllerLevel.LOW_LEVEL)
    if status.code != magicdog.ErrorCode.OK:
        print(f"设置运动控制级别失败: {status.message}")
        robot.shutdown()
        return

    print("等待运动模式变为低级别")
    while current_mode != magicdog.GaitMode.GAIT_LOWLEVL_SDK:
        current_mode = high_controller.get_gait()
        time.sleep(0.1)

    time.sleep(2)

    print("获取低级别运动控制器")
    low_controller = robot.get_low_level_motion_controller()

    print("设置周期为2ms")
    low_controller.set_period_ms(2)

    is_had_receive_leg_state = False
    mut = threading.Lock()
    receive_state = None
    count = 0
    def leg_state_callback(msg):
        nonlocal is_had_receive_leg_state, receive_state, count
        if not is_had_receive_leg_state:
            with mut:
                is_had_receive_leg_state = True
                receive_state = msg
        if count % 1000 == 0:
            print("receive leg state data.")
        count += 1

    low_controller.subscribe_leg_state(leg_state_callback)
    
    print("等待收到腿部状态数据")
    while not is_had_receive_leg_state:
        time.sleep(0.002)

    time.sleep(10)

    j1 = [0.0000, 1.0477, -2.0944]
    j2 = [0.0000, 0.7231, -1.4455]
    inital_q = [receive_state.state[0].q, receive_state.state[1].q, receive_state.state[2].q,
                receive_state.state[3].q, receive_state.state[4].q, receive_state.state[5].q,
                receive_state.state[6].q, receive_state.state[7].q, receive_state.state[8].q,
                receive_state.state[9].q, receive_state.state[10].q, receive_state.state[11].q]

    command = magicdog.LegJointCommand()
    cnt = 0
    while True:
        if cnt < 1000:
            t = 1.0*cnt/1000.0
            t = min(max(t, 0.0), 1.0)
            for i in range(12):
                command.cmd[i].q_des = (1-t)*inital_q[i] + t*j1[i%3]
        elif cnt < 1750:
            t = 1.0*(cnt-1000)/700.0
            t = min(max(t, 0.0), 1.0)
            for i in range(12):
                command.cmd[i].q_des = (1-t)*j1[i%3] + t*j2[i%3]
        elif cnt < 2500:
            t = 1.0*(cnt-1750)/700.0
            t = min(max(t, 0.0), 1.0)
            for i in range(12):
                command.cmd[i].q_des = (1-t)*j2[i%3] + t*j1[i%3]
        else:
            cnt = 1000

        for i in range(12):
            command.cmd[i].kp = 100
            command.cmd[i].kd = 1.2

        low_controller.publish_leg_command(command)
        time.sleep(0.002)
        cnt += 1

    robot.disconnect()
    robot.shutdown()
    
    print("\n示例程序执行完成！")

if __name__ == "__main__":
    main() 