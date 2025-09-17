#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python Usage Example

This file demonstrates how to use MagicDog SDK Python bindings to control the robot.
"""

import sys
import time
import threading
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

def main():
    """Main function"""
    logging.info("MagicDog SDK Python Example Program")
    
    robot = magicdog.MagicRobot()
    if not robot.initialize("192.168.55.10"):
        logging.error("Initialization failed")
        return
    
    if not robot.connect():
        logging.error("Connection failed")
        robot.shutdown()
        return
    
    logging.info("Setting motion control level to high level")
    status = robot.set_motion_control_level(magicdog.ControllerLevel.HIGH_LEVEL)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(f"Failed to set motion control level: {status.message}")
        robot.shutdown()
        return
    
    logging.info("Getting high level motion controller")
    high_controller = robot.get_high_level_motion_controller()
    
    logging.info("Setting motion mode to passive")
    status = high_controller.set_gait(magicdog.GaitMode.GAIT_PASSIVE)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(f"Failed to set motion mode: {status.message}")
        robot.shutdown()
        return

    logging.info("Waiting for motion mode to change to passive")
    current_mode = magicdog.GaitMode.GAIT_DEFAULT
    while current_mode != magicdog.GaitMode.GAIT_PASSIVE:
        current_mode = high_controller.get_gait()
        time.sleep(0.1)

    time.sleep(2)

    logging.info("Setting motion control level to low level")
    status = robot.set_motion_control_level(magicdog.ControllerLevel.LOW_LEVEL)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(f"Failed to set motion control level: {status.message}")
        robot.shutdown()
        return

    logging.info("Waiting for motion mode to change to low level")
    while current_mode != magicdog.GaitMode.GAIT_LOWLEVL_SDK:
        current_mode = high_controller.get_gait()
        time.sleep(0.1)

    time.sleep(2)

    logging.info("Getting low level motion controller")
    low_controller = robot.get_low_level_motion_controller()

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
            logging.info("Received leg state data.")
        count += 1

    low_controller.subscribe_leg_state(leg_state_callback)
    
    logging.info("Waiting to receive leg state data")
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
    
    logging.info("\nExample program execution completed!")

if __name__ == "__main__":
    main() 