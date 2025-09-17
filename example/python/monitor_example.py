#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python Usage Example

This file demonstrates how to use MagicDog SDK Python bindings to control the robot.
"""

import sys
import time
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

    time.sleep(10)

    monitor = robot.get_state_monitor()

    state = monitor.get_current_state()
    logging.info(f"health: {state.bms_data.battery_health}, percentage: {state.bms_data.battery_percentage}, state: {state.bms_data.battery_state}, power_supply_status: {state.bms_data.power_supply_status}")

    for fault in state.faults:
        logging.info(f"code: {fault.error_code}, message: {fault.error_message}")
    
    robot.disconnect()
    robot.shutdown()
    
    logging.info("\nExample program execution completed!")

if __name__ == "__main__":
    main() 