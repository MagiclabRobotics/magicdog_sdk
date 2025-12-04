#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import signal
import termios
import tty
import logging
from typing import Optional
import magicdog_python as magicdog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Global robot instance
robot = None


def signal_handler(signum, frame):
    """Handle Ctrl+C signal"""
    logging.info(f"\nInterrupt signal ({signum}) received.")
    if robot:
        robot.shutdown()
    sys.exit(signum)


def print_help():
    """Print help information"""
    logging.info("Key Function Description:")
    logging.info("")
    logging.info("Face expression Functions:")
    logging.info("  1        Function 1: Get all face expressions")
    logging.info("  2        Function 2: Set face expression")
    logging.info("  3        Function 3: Get current face expression")
    logging.info("")
    logging.info("  ?        Function ?: Print help")
    logging.info("  ESC      Exit program")


def getch():
    """Get a single character from standard input"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_all_face_expressions(display_controller):
    """Get all face expressions"""
    status, all_face_expressions = display_controller.get_all_face_expressions()
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            "Failed to get all face expressions, code: %s, message: %s",
            status.code,
            status.message,
        )
        return
    logging.info("Total face expressions: %d", len(all_face_expressions))

    for i, face_expression in enumerate(all_face_expressions):
        logging.info("Face expression %d: %d", i + 1, face_expression.id)
        logging.info("  Name: %s", face_expression.name)
        logging.info("  Description: %s", face_expression.description)


def set_face_expression(display_controller, face_expression_id):
    """Set face expression"""
    status = display_controller.set_face_expression(face_expression_id)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            "Failed to set face expression, code: %s, message: %s",
            status.code,
            status.message,
        )
        return


def get_current_face_expression(display_controller):
    """Get all face expressions"""
    status, face_expression = display_controller.get_current_face_expression()
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            "Failed to get current face expression, code: %s, message: %s",
            status.code,
            status.message,
        )
        return

    logging.info("Face expression: %d", face_expression.id)
    logging.info("  Name: %s", face_expression.name)
    logging.info("  Description: %s", face_expression.description)


def main():
    """Main function"""
    global robot

    # Bind SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    print_help()

    local_ip = "192.168.55.10"
    robot = magicdog.MagicRobot()

    # Configure local IP address for direct network connection and initialize SDK
    if not robot.initialize(local_ip):
        logging.error("robot sdk initialize failed.")
        robot.shutdown()
        return -1

    # Connect to robot
    status = robot.connect()
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            f"connect robot failed, code: {status.code}, message: {status.message}"
        )
        robot.shutdown()
        return -1

    logging.info("Press any key to continue (ESC to exit)...")

    display_controller = robot.get_display_controller()

    # Wait for user input
    while True:
        key = getch()
        if key == "\x1b":  # ESC key
            break

        key_ascii = ord(key)
        logging.info(f"Key ASCII: {key_ascii}, Character: {key}")

        # 1. Face expression Functions
        # 1.1 Get all face expressions
        if key == "1":
            get_all_face_expressions(display_controller)
        # 1.2 Set face expression
        elif key == "2":
            face_expression_id = 16
            try:
                user_input = input("Please input face expression id: ")
                face_expression_id = int(user_input)
            except ValueError:
                logging.info("invalid input, using default value 16.")
            set_face_expression(display_controller, face_expression_id)
        # 1.3 Get current face expression
        elif key == "3":
            get_current_face_expression(display_controller)
        # Help
        elif key == "?":
            print_help()
        else:
            logging.info(f"Unknown key: {key_ascii}")

        # Sleep 10ms, equivalent to usleep(10000)
        time.sleep(0.01)

    display_controller.shutdown()
    logging.info("display controller shutdown")

    # Disconnect from robot
    robot.disconnect()
    logging.info("disconnect robot success")

    robot.shutdown()
    logging.info("robot shutdown")

    return 0


if __name__ == "__main__":
    sys.exit(main())
