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
    from magicdog_python import TtsCommand, TtsPriority, TtsMode, GetSpeechConfig, ErrorCode
    logging.info("Successfully imported MagicDog Python module!")
    logging.info(f"Imported magicdog_python path: {sys.path}")
except ImportError as e:
    logging.error(f"Import failed: {e}")
    sys.exit(1)

def main():
    """Main function"""
    logging.info("MagicDog SDK Audio Python Example Program")
    
    local_ip = "192.168.55.10"
    robot = magicdog.MagicRobot()
    if not robot.initialize(local_ip):
        logging.error("Robot initialization failed")
        return
        
    if not robot.connect():
        logging.error("Robot connection failed")
        robot.shutdown()
        return
    
    logging.info("Robot connected successfully")
    
    sensor_controller = robot.get_sensor_controller()
    # sensor_controller.subscribe_tof(lambda tof: logging.info(f"TOF: {len(tof.data)}"))
    sensor_controller.subscribe_ultra(lambda ultra: logging.info(f"Ultra: {len(ultra.data)}"))
    sensor_controller.subscribe_laser_scan(lambda laser_scan: logging.info(f"Laser Scan: {len(laser_scan.ranges)}"))
    # sensor_controller.subscribe_imu(lambda imu: logging.info(f"IMU: {imu.orientation}"))
    sensor_controller.subscribe_rgbd_color_camera_info(lambda camera_info: logging.info(f"RGBD Color Camera Info: {camera_info.K}"))
    sensor_controller.subscribe_rgbd_depth_image(lambda depth_image: logging.info(f"RGBD Depth Image: {len(depth_image.data)}"))
    sensor_controller.subscribe_rgbd_color_image(lambda color_image: logging.info(f"RGBD Color Image: {len(color_image.data)}"))
    sensor_controller.subscribe_rgb_depth_camera_info(lambda camera_info: logging.info(f"RGB Depth Camera Info: {camera_info.K}"))
    sensor_controller.subscribe_left_binocular_high_img(lambda img: logging.info(f"Left Binocular High Image: {len(img.data)}"))
    sensor_controller.subscribe_left_binocular_low_img(lambda img: logging.info(f"Left Binocular Low Image: {len(img.data)}"))
    sensor_controller.subscribe_right_binocular_low_img(lambda img: logging.info(f"Right Binocular Low Image: {len(img.data)}"))

    status = sensor_controller.open_channel_switch()
    if status.code != ErrorCode.OK:
        logging.error(f"Failed to open channel: {status.message}")
        robot.shutdown()
        return

    status = sensor_controller.open_laser_scan()
    if status.code != ErrorCode.OK:
        logging.error(f"Failed to open laser scan: {status.message}")
        robot.shutdown()
        return
    
    status = sensor_controller.open_rgbd_camera()
    if status.code != ErrorCode.OK:
        logging.error(f"Failed to open RGBD camera: {status.message}")
        robot.shutdown()
        return
    
    status = sensor_controller.open_binocular_camera()
    if status.code != ErrorCode.OK:
        logging.error(f"Failed to open binocular camera: {status.message}")
        robot.shutdown()
        return

    time.sleep(10)

    status = sensor_controller.close_laser_scan()
    if status.code != ErrorCode.OK:
        logging.error(f"Failed to close laser scan: {status.message}")
        robot.shutdown()
        return

    status = sensor_controller.close_rgbd_camera()
    if status.code != ErrorCode.OK:
        logging.error(f"Failed to close RGBD camera: {status.message}")
        robot.shutdown()
        return

    status = sensor_controller.close_binocular_camera()
    if status.code != ErrorCode.OK:
        logging.error(f"Failed to close binocular camera: {status.message}")
        robot.shutdown()
        return

    time.sleep(10)

    status = sensor_controller.close_channel_switch()
    if status.code != ErrorCode.OK:
        logging.error(f"Failed to close channel: {status.message}")
        robot.shutdown()
        return

    # Avoid unprocessed buffered data in lcm
    time.sleep(30)

    robot.disconnect()
    robot.shutdown()
    logging.info("\nExample program execution completed!")

if __name__ == "__main__":
    main() 