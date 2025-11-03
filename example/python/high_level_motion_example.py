#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来控制机器人。
"""

import sys
import time
import threading
import tty
import termios
import os

# 添加构建目录到 Python 路径
sys.path.append('../../build')

try:
    import magicdog_python as magicdog
    print("成功导入 MagicDog Python 模块！")
except ImportError as e:
    print(f"导入失败: {e}")
    print("请先运行 build_python.sh 构建 Python 绑定")
    sys.exit(1)


left_x = 0.0
left_y = 0.0
right_x = 0.0
right_y = 0.0
exit_flag = False
robot = None
high_controller = None

# 获取单个字符输入（无回显）
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# 位控站立
def recovery_stand():
    global high_controller
    try:
        # 设置步态为位控站立
        status = high_controller.set_gait(magicdog.GaitMode.GAIT_STAND_R)
        if status.code != magicdog.ErrorCode.OK:
            print(f"设置位控站立失败: {status.message}")
        else:
            print("机器人已设置为位控站立")
    except Exception as e:
        print(f"执行位控站立时出错: {e}")

# 力控站立
def balance_stand():
    global high_controller
    try:
        # 设置步态为力控站立
        status = high_controller.set_gait(magicdog.GaitMode.GAIT_STAND_B)
        if status.code != magicdog.ErrorCode.OK:
            print(f"设置力控站立失败: {status.message}")
        else:
            print("机器人已设置为力控站立")
    except Exception as e:
        print(f"执行力控站立时出错: {e}")

# 执行特技-趴下
def execute_trick():
    global high_controller
    try:
        # 执行趴下特技
        status = high_controller.execute_trick(magicdog.TrickAction.ACTION_LIE_DOWN)
        if status.code != magicdog.ErrorCode.OK:
            print(f"执行特技失败: {status.message}")
        else:
            print("特技执行成功")
    except Exception as e:
        print(f"执行特技时出错: {e}")

# 切换步态为下楼梯模式
def change_gait_to_down_climb_stairs():
    global high_controller
    try:
        current_gait = high_controller.get_gait()
        if current_gait != magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS:
            status = high_controller.set_gait(magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS)
            if status.code != magicdog.ErrorCode.OK:
                print(f"设置下楼梯步态失败: {status.message}")
                return False
            
            # 等待步态切换完成
            while high_controller.get_gait() != magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS:
                time.sleep(0.01)
        return True
    except Exception as e:
        print(f"切换步态时出错: {e}")
        return False

# 定义一个函数，根据按键模拟摇杆的输入
def update_joy_command():
    global left_x, left_y, right_x, right_y, exit_flag
    print("按键功能说明:")
    print("  1        功能1: 位控站立")
    print("  2        功能2: 力控站立")
    print("  3        功能3: 执行特技-趴下")
    print("  w        向前移动")
    print("  a        向左移动")
    print("  x        向后移动")
    print("  d        向右移动")
    print("  t        左转向")
    print("  g        右转向")
    print("  s        停止移动")
    print("  ESC      退出程序")
    
    while not exit_flag:
        key = getch()
        if key == '\x1b':  # ESC键
            exit_flag = True
            break
        elif key == '1':
            # 位控站立
            recovery_stand()
        elif key == '2':
            # 力控站立
            balance_stand()
        elif key == '3':
            # 执行特技-趴下
            execute_trick()
        elif key == 'w':
            if change_gait_to_down_climb_stairs():
                left_y = 1.0
                left_x = 0.0
                right_x = 0.0
                right_y = 0.0
        elif key == 'x':
            if change_gait_to_down_climb_stairs():
                left_y = -1.0
                left_x = 0.0
                right_x = 0.0
                right_y = 0.0
        elif key == 'a':
            if change_gait_to_down_climb_stairs():
                left_x = -1.0
                left_y = 0.0
                right_x = 0.0
                right_y = 0.0
        elif key == 'd':
            if change_gait_to_down_climb_stairs():
                left_x = 1.0
                left_y = 0.0
                right_x = 0.0
                right_y = 0.0
        elif key == 't':
            if change_gait_to_down_climb_stairs():
                left_x = 0.0
                left_y = 0.0
                right_x = -1.0
                right_y = 0.0
        elif key == 'g':
            if change_gait_to_down_climb_stairs():
                left_x = 0.0
                left_y = 0.0
                right_x = 1.0
                right_y = 0.0
        elif key == 's':
            if change_gait_to_down_climb_stairs():
                left_x = 0.0
                left_y = 0.0
                right_x = 0.0
                right_y = 0.0

# 摇杆命令发送线程
def joy_thread(high_controller):
    global left_x, left_y, right_x, right_y, exit_flag
    while not exit_flag:
        joy_command = magicdog.JoystickCommand()
        joy_command.left_x_axis = left_x
        joy_command.left_y_axis = left_y
        joy_command.right_x_axis = right_x
        joy_command.right_y_axis = right_y

        status = high_controller.send_joystick_command(joy_command)
        if status.code != magicdog.ErrorCode.OK:
            print(f"发送摇杆命令失败: {status.message}")
            break
        time.sleep(0.01)  # 10ms间隔，与C++代码保持一致

def main():
    """主函数"""
    global robot, high_controller
    
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

    # 设置运动控制级别为高级别
    status = robot.set_motion_control_level(magicdog.ControllerLevel.HIGH_LEVEL)
    if status.code != magicdog.ErrorCode.OK:
        print(f"设置运动控制级别失败: {status.message}")
        robot.shutdown()
        return

    # 获取高级别运动控制器
    high_controller = robot.get_high_level_motion_controller()

    # 创建一个线程，用于接收键盘输入
    key_thread = threading.Thread(target=update_joy_command)
    key_thread.daemon = True  # 设置为守护线程
    key_thread.start()
    
    # 创建摇杆命令发送线程
    joy_send_thread = threading.Thread(target=joy_thread, args=(high_controller,))
    joy_send_thread.daemon = True  # 设置为守护线程
    joy_send_thread.start()

    print("程序已启动，请使用按键控制机器人...")
    
    # 主线程等待退出信号
    global exit_flag
    try:
        while not exit_flag:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n收到中断信号，正在退出...")
        exit_flag = True

    print("正在关闭机器人连接...")
    robot.shutdown()
    robot.disconnect()

    print("\n示例程序执行完成！")

if __name__ == "__main__":
    main() 