#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import threading
import tty
import termios
import os
import logging
from typing import Optional
import math
import magicdog_python as magicdog

logging.basicConfig(
    level=logging.INFO,  # Minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

running = True
robot = None
high_controller = None


# Get single character input (no echo)
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        logging.info(f"Received character: {ch}")

        sys.stdout.write("\r")
        sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


# Recovery stand
def recovery_stand():
    global high_controller
    try:
        # Set gait to position control standing
        status = high_controller.set_gait(magicdog.GaitMode.GAIT_STAND_R)
        if status.code != magicdog.ErrorCode.OK:
            logging.error(f"Failed to set position control standing: {status.message}")
        else:
            logging.info("Robot set to position control standing")
    except Exception as e:
        logging.error(f"Error executing position control standing: {e}")


# Force control standing
def balance_stand():
    global high_controller
    try:
        # Set gait to force control standing
        status = high_controller.set_gait(magicdog.GaitMode.GAIT_STAND_B)
        if status.code != magicdog.ErrorCode.OK:
            logging.error(f"Failed to set force control standing: {status.message}")
        else:
            logging.info("Robot set to force control standing")
    except Exception as e:
        logging.error(f"Error executing force control standing: {e}")


# Execute trick
def execute_trick(cmd):
    global high_controller
    try:
        action = get_action(cmd)
        # Execute lie down trick
        status = high_controller.execute_trick(action)
        if status.code != magicdog.ErrorCode.OK:
            logging.error(f"Failed to execute trick: {status.message}")
        else:
            logging.info("Trick executed successfully")
    except Exception as e:
        logging.error(f"Error executing trick: {e}")


# Switch gait to down climb stairs mode
def change_gait_to_down_climb_stairs():
    global high_controller
    try:
        current_gait = high_controller.get_gait()
        if current_gait != magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS:
            status = high_controller.set_gait(magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS)
            if status.code != magicdog.ErrorCode.OK:
                logging.error(f"Failed to set down climb stairs gait: {status.message}")
                return False

            # Wait for gait switch to complete
            while (
                high_controller.get_gait() != magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS
            ):
                time.sleep(0.01)
        logging.info("Gait changed to down climb stairs")
        return True
    except Exception as e:
        logging.error(f"Error changing gait: {e}")
        return False


def print_help():
    logging.info("Key function description:")
    logging.info("")
    logging.info("Gait and Trick Functions:")
    logging.info("  1        Function 1: Recovery stand")
    logging.info("  2        Function 2: Force control standing")
    logging.info("  3        Function 3: Execute trick")
    logging.info("")
    logging.info("Joystick Functions:")
    logging.info("  w        Function w: Move forward")
    logging.info("  a        Function a: Move left")
    logging.info("  s        Function s: Move backward")
    logging.info("  d        Function d: Move right")
    logging.info("  t        Function t: Turn left")
    logging.info("  g        Function g: Turn right")
    logging.info("  x        Function x: Stop movement")
    logging.info("")
    logging.info("Head Position Functions:")
    logging.info("  4        Function 4: Get head position")
    logging.info("  5        Function 5: Set head position")
    logging.info("")
    logging.info("  ?        Function ?: Print help")
    logging.info("  ESC      Exit program")


def send_joystick_command(high_controller, left_x, left_y, right_x, right_y):
    if not change_gait_to_down_climb_stairs():
        return
    joy_command = magicdog.JoystickCommand()
    joy_command.left_x_axis = left_x
    joy_command.left_y_axis = left_y
    joy_command.right_x_axis = right_x
    joy_command.right_y_axis = right_y

    status = high_controller.send_joystick_command(joy_command)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(f"Failed to send joystick command: {status.message}")


def get_current_head_position(high_controller):
    status, euler_angles = high_controller.get_current_head_position()
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            "Failed to get current head position, code: %s, message: %s",
            status.code,
            status.message,
        )
        return

    logging.info("Head Position Roll Angle: %f", euler_angles.roll)
    logging.info("  Pitch Angle: %f", euler_angles.pitch)
    logging.info("  Yaw Angle: %f", euler_angles.yaw)


def set_head_position(high_controller, euler_angles):
    status = high_controller.set_head_position(euler_angles)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            "Failed to set head position, code: %s, message: %s",
            status.code,
            status.message,
        )
        return


def deg2rad(deg):
    """角度转弧度"""
    return deg * math.pi / 180.0


def signal_handler(signum, frame):
    """Signal handler function for graceful exit"""
    global robot, running
    running = False
    logging.info("Received interrupt signal (%s), exiting...", signum)
    if robot:
        robot.shutdown()
        logging.info("Robot shutdown")
    exit(-1)


def get_action(cmd):
    if cmd == "102":
        return magicdog.TrickAction.ACTION_LIE_DOWN
    elif cmd == "103":
        return magicdog.TrickAction.ACTION_RECOVERY_STAND
    elif cmd == "33":
        return magicdog.TrickAction.ACTION_SHAKE_HEAD
    else:
        return magicdog.TrickAction.ACTION_NONE


def main():
    """Main function"""
    print_help()

    global robot, high_controller, running

    logging.info("MagicDog SDK Python Example Program")

    robot = magicdog.MagicRobot()
    if not robot.initialize("192.168.55.10"):
        logging.error("Initialization failed")
        return

    if not robot.connect():
        logging.error("Connection failed")
        robot.shutdown()
        return

    # Set motion control level to high level
    status = robot.set_motion_control_level(magicdog.ControllerLevel.HIGH_LEVEL)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(f"Failed to set motion control level: {status.message}")
        robot.shutdown()
        return

    # Get high level motion controller
    high_controller = robot.get_high_level_motion_controller()

    logging.info("Program started, please use keys to control robot...")

    while running:
        logging.info("Enter command: ")
        key = getch()
        if key == "\x1b":  # ESC key
            break

        # 1. Gait and Trick Functions
        # 1.1 Recovery stand
        if key == "1":
            recovery_stand()
        # 1.2 Force control standing
        elif key == "2":
            balance_stand()
        # 1.3 Execute trick
        elif key == "3":
            str_input = input("Enter parameters: ").strip()
            if not str_input:
                continue
            # Split input parameters by space
            parts = str_input.strip().split()

            # Parse parameters
            cmd = parts[0] if parts else "102"
            logging.info(f"Execute trick: {cmd}")
            execute_trick(cmd)
        # 2. Joystick Functions
        # 2.1 Move forward
        elif key.lower() == "w":
            left_y = 1.0
            left_x = 0.0
            right_x = 0.0
            right_y = 0.0
            send_joystick_command(high_controller, left_x, left_y, right_x, right_y)
        # 2.2 Move backward
        elif key.lower() == "s":
            left_y = -1.0
            left_x = 0.0
            right_x = 0.0
            right_y = 0.0
            send_joystick_command(high_controller, left_x, left_y, right_x, right_y)
        # 2.3 Move left
        elif key.lower() == "a":
            left_x = -1.0
            left_y = 0.0
            right_x = 0.0
            right_y = 0.0
            send_joystick_command(high_controller, left_x, left_y, right_x, right_y)
        # 2.4 Move right
        elif key.lower() == "d":
            left_x = 1.0
            left_y = 0.0
            right_x = 0.0
            right_y = 0.0
            send_joystick_command(high_controller, left_x, left_y, right_x, right_y)
        # 2.5 Turn left
        elif key.lower() == "t":
            left_x = 0.0
            left_y = 0.0
            right_x = -1.0
            right_y = 0.0
            send_joystick_command(high_controller, left_x, left_y, right_x, right_y)
        # 2.6 Turn right
        elif key.lower() == "g":
            left_x = 0.0
            left_y = 0.0
            right_x = 1.0
            right_y = 0.0
            send_joystick_command(high_controller, left_x, left_y, right_x, right_y)
        # 2.7 Stop movement
        elif key.lower() == "x":
            left_x = 0.0
            left_y = 0.0
            right_x = 0.0
            right_y = 0.0
            send_joystick_command(high_controller, left_x, left_y, right_x, right_y)
        # 3. Head Position Functions
        # 3.1 Get current head position
        elif key == "4":
            get_current_head_position(high_controller)
        # 3.2 Set head position
        elif key == "5":
            # 处理头部位置设置命令
            try:
                # 获取用户输入
                user_input = input(
                    "请输入三个角度（roll pitch yaw，以空格分隔，-60度到60度）: "
                )
                values = user_input.split()
                if len(values) != 3:
                    logging.error("错误：需要输入三个数字")
                    return
                # 转换为浮点数
                roll_deg = float(values[0])
                pitch_deg = float(values[1])
                yaw_deg = float(values[2])
                # 验证角度范围
                if (
                    not (-60 <= roll_deg <= 60)
                    or not (-60 <= pitch_deg <= 60)
                    or not (-60 <= yaw_deg <= 60)
                ):
                    logging.error("警告：角度应在 -60 到 60 度范围内")
                # 转换为弧度
                euler_angles = magicdog.EulerAngles()
                euler_angles.roll = deg2rad(roll_deg)
                euler_angles.pitch = deg2rad(pitch_deg)
                euler_angles.yaw = deg2rad(yaw_deg)
                # 输出结果
                logging.info("\n转换结果：")
                logging.info(f"Roll:  {roll_deg}° = {euler_angles.roll:.6f} rad")
                logging.info(f"Pitch: {pitch_deg}° = {euler_angles.pitch:.6f} rad")
                logging.info(f"Yaw:   {yaw_deg}° = {euler_angles.yaw:.6f} rad")
                # 设置头部位置
                set_head_position(high_controller, euler_angles)
            except ValueError:
                logging.error("错误：请输入有效的数字")
            except Exception as e:
                logging.error(f"发生错误：{e}")
        # Help
        elif key.upper() == "?":
            print_help()
        else:
            logging.info(f"Unknown key: {key}")

    # Shutdown high level motion controller
    high_controller.shutdown()
    logging.info("High level motion controller shutdown")

    # Disconnect from robot
    robot.disconnect()
    logging.info("Robot disconnected")

    # Shutdown robot
    robot.shutdown()
    logging.info("Robot shutdown")


if __name__ == "__main__":
    main()
