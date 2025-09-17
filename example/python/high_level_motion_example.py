#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python Usage Example

This file demonstrates how to use MagicDog SDK Python bindings to control the robot.
"""

import sys
import time
import threading
import tty
import termios
import os
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,  # Minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

try:
    import magicdog_python as magicdog
    logging.info("Successfully imported MagicDog Python module!")
except ImportError as e:
    logging.error(f"Import failed: {e}")
    sys.exit(1)


left_x = 0.0
left_y = 0.0
right_x = 0.0
right_y = 0.0
exit_flag = False
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
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Position control standing
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

# Execute trick - lie down
def execute_trick():
    global high_controller
    try:
        # Execute lie down trick
        status = high_controller.execute_trick(magicdog.TrickAction.ACTION_LIE_DOWN)
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
            while high_controller.get_gait() != magicdog.GaitMode.GAIT_DOWN_CLIMB_STAIRS:
                time.sleep(0.01)
        return True
    except Exception as e:
        logging.error(f"Error changing gait: {e}")
        return False

# Define a function to simulate joystick input based on key presses
def update_joy_command():
    global left_x, left_y, right_x, right_y, exit_flag
    logging.info("Key function description:")
    logging.info("  1        Function 1: Position control standing")
    logging.info("  2        Function 2: Force control standing")
    logging.info("  3        Function 3: Execute trick - lie down")
    logging.info("  w        Move forward")
    logging.info("  a        Move left")
    logging.info("  s        Move backward")
    logging.info("  d        Move right")
    logging.info("  t        Turn left")
    logging.info("  g        Turn right")
    logging.info("  x        Stop movement")
    logging.info("  ESC      Exit program")
    
    while not exit_flag:
        key = getch()
        if key == '\x1b':  # ESC key
            exit_flag = True
            break
        elif key == '1':
            # Position control standing
            recovery_stand()
        elif key == '2':
            # Force control standing
            balance_stand()
        elif key == '3':
            # Execute trick - lie down
            execute_trick()
        elif key == 'w':
            if change_gait_to_down_climb_stairs():
                left_y = 1.0
                left_x = 0.0
                right_x = 0.0
                right_y = 0.0
        elif key == 's':
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
        elif key == 'x':
            if change_gait_to_down_climb_stairs():
                left_x = 0.0
                left_y = 0.0
                right_x = 0.0
                right_y = 0.0

# Joystick command sending thread
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
            logging.error(f"Failed to send joystick command: {status.message}")
            break
        time.sleep(0.01)  # 10ms interval, consistent with C++ code

def main():
    """Main function"""
    global robot, high_controller
    
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

    # Create a thread for receiving keyboard input
    key_thread = threading.Thread(target=update_joy_command)
    key_thread.daemon = True  # Set as daemon thread
    key_thread.start()
    
    # Create joystick command sending thread
    joy_send_thread = threading.Thread(target=joy_thread, args=(high_controller,))
    joy_send_thread.daemon = True  # Set as daemon thread
    joy_send_thread.start()

    logging.info("Program started, please use keys to control robot...")
    
    # Main thread waits for exit signal
    global exit_flag
    try:
        while not exit_flag:
            time.sleep(0.1)
    except KeyboardInterrupt:
        logging.info("\nReceived interrupt signal, exiting...")
        exit_flag = True

    logging.info("Closing robot connection...")
    robot.shutdown()
    robot.disconnect()

    logging.info("\nExample program execution completed!")

if __name__ == "__main__":
    main() 