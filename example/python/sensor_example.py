#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import logging
from typing import Optional, Dict
import magicdog_python as magicdog
from magicdog_python import ErrorCode


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

imu_counter = 0


class SensorManager:
    """Manages sensor subscriptions and channels"""

    def __init__(self, robot, sensor_controller):
        self.robot = robot
        self.sensor_controller = sensor_controller
        self.channel_opened = False
        self.sensors_state = {
            "laser_scan": False,
            "rgbd_camera": False,
            "binocular_camera": False,
        }
        self.subscriptions = {
            "ultra": False,
            "head_touch": False,
            "imu": False,
            "laser_scan": False,
            "rgbd_color_info": False,
            "rgbd_depth_image": False,
            "rgbd_color_image": False,
            "rgb_depth_info": False,
            "left_binocular_high": False,
            "left_binocular_low": False,
            "right_binocular_low": False,
            "depth_image": False,
        }

    # === Channel Control ===
    def open_channel(self) -> bool:
        """Open sensor channel switch"""
        if self.channel_opened:
            logging.warning("Channel already opened")
            return True

        status = self.robot.open_channel_switch()
        if status.code != ErrorCode.OK:
            logging.error(f"Failed to open channel: {status.message}")
            return False

        self.channel_opened = True
        logging.info("✓ Channel opened successfully")
        return True

    def close_channel(self) -> bool:
        """Close sensor channel switch"""
        if not self.channel_opened:
            logging.warning("Channel already closed")
            return True

        status = self.robot.close_channel_switch()
        if status.code != ErrorCode.OK:
            logging.error(f"Failed to close channel: {status.message}")
            return False

        self.channel_opened = False
        logging.info("✓ Channel closed successfully")
        return True

    # === Sensor Open/Close ===
    def open_laser_scan(self) -> bool:
        """Open laser scan sensor"""
        if self.sensors_state["laser_scan"]:
            logging.warning("Laser scan already opened")
            return True

        status = self.sensor_controller.open_laser_scan()
        if status.code != ErrorCode.OK:
            logging.error(f"Failed to open laser scan: {status.message}")
            return False

        self.sensors_state["laser_scan"] = True
        logging.info("✓ Laser scan opened")
        return True

    def close_laser_scan(self) -> bool:
        """Close laser scan sensor"""
        if not self.sensors_state["laser_scan"]:
            logging.warning("Laser scan already closed")
            return True

        # Unsubscribe if subscribed
        if self.subscriptions["laser_scan"]:
            self.toggle_laser_scan_subscription()

        status = self.sensor_controller.close_laser_scan()
        if status.code != ErrorCode.OK:
            logging.error(f"Failed to close laser scan: {status.message}")
            return False

        self.sensors_state["laser_scan"] = False
        logging.info("✓ Laser scan closed")
        return True

    def open_rgbd_camera(self) -> bool:
        """Open RGBD camera"""
        if self.sensors_state["rgbd_camera"]:
            logging.warning("RGBD camera already opened")
            return True

        status = self.sensor_controller.open_rgbd_camera()
        if status.code != ErrorCode.OK:
            logging.error(f"Failed to open RGBD camera: {status.message}")
            return False

        self.sensors_state["rgbd_camera"] = True
        logging.info("✓ RGBD camera opened")
        return True

    def close_rgbd_camera(self) -> bool:
        """Close RGBD camera"""
        if not self.sensors_state["rgbd_camera"]:
            logging.warning("RGBD camera already closed")
            return True

        # Unsubscribe all RGBD subscriptions if subscribed
        if self.subscriptions["rgbd_color_info"]:
            self.toggle_rgbd_color_info_subscription()
        if self.subscriptions["rgbd_depth_image"]:
            self.toggle_rgbd_depth_image_subscription()
        if self.subscriptions["rgbd_color_image"]:
            self.toggle_rgbd_color_image_subscription()
        if self.subscriptions["rgb_depth_info"]:
            self.toggle_rgb_depth_info_subscription()

        status = self.sensor_controller.close_rgbd_camera()
        if status.code != ErrorCode.OK:
            logging.error(f"Failed to close RGBD camera: {status.message}")
            return False

        self.sensors_state["rgbd_camera"] = False
        logging.info("✓ RGBD camera closed")
        return True

    def open_binocular_camera(self) -> bool:
        """Open binocular camera"""
        if self.sensors_state["binocular_camera"]:
            logging.warning("Binocular camera already opened")
            return True

        status = self.sensor_controller.open_binocular_camera()
        if status.code != ErrorCode.OK:
            logging.error(f"Failed to open binocular camera: {status.message}")
            return False

        self.sensors_state["binocular_camera"] = True
        logging.info("✓ Binocular camera opened")
        return True

    def close_binocular_camera(self) -> bool:
        """Close binocular camera"""
        if not self.sensors_state["binocular_camera"]:
            logging.warning("Binocular camera already closed")
            return True

        # Unsubscribe all binocular subscriptions if subscribed
        if self.subscriptions["left_binocular_high"]:
            self.toggle_left_binocular_high_subscription()
        if self.subscriptions["left_binocular_low"]:
            self.toggle_left_binocular_low_subscription()
        if self.subscriptions["right_binocular_low"]:
            self.toggle_right_binocular_low_subscription()

        status = self.sensor_controller.close_binocular_camera()
        if status.code != ErrorCode.OK:
            logging.error(f"Failed to close binocular camera: {status.message}")
            return False

        self.sensors_state["binocular_camera"] = False
        logging.info("✓ Binocular camera closed")
        return True

    # === Subscribe/Unsubscribe Methods ===
    def toggle_ultra_subscription(self):
        """Toggle ultra sensor subscription"""
        if self.subscriptions["ultra"]:
            self.sensor_controller.unsubscribe_ultra()
            self.subscriptions["ultra"] = False
            logging.info("✓ Ultra sensor unsubscribed")
        else:
            self.sensor_controller.subscribe_ultra(
                lambda ultra: logging.info(f"Ultra: {len(ultra.data)}")
            )
            self.subscriptions["ultra"] = True
            logging.info("✓ Ultra sensor subscribed")

    def toggle_head_touch_subscription(self):
        """Toggle head touch sensor subscription"""
        if self.subscriptions["head_touch"]:
            self.sensor_controller.unsubscribe_head_touch()
            self.subscriptions["head_touch"] = False
            logging.info("✓ Head touch sensor unsubscribed")
        else:
            self.sensor_controller.subscribe_head_touch(
                lambda touch: logging.info(f"Head Touch: {touch}")
            )
            self.subscriptions["head_touch"] = True
            logging.info("✓ Head touch sensor subscribed")

    def toggle_imu_subscription(self):
        """Toggle IMU sensor subscription"""
        if self.subscriptions["imu"]:
            self.sensor_controller.unsubscribe_imu()
            self.subscriptions["imu"] = False
            logging.info("✓ IMU sensor unsubscribed")
        else:

            def imu_callback(imu):
                global imu_counter
                imu_counter += 1
                if imu_counter % 500 == 0:
                    logging.info(f"IMU: {imu}")

            self.sensor_controller.subscribe_imu(imu_callback)
            self.subscriptions["imu"] = True
            logging.info("✓ IMU sensor subscribed")

    def toggle_laser_scan_subscription(self):
        """Toggle laser scan subscription"""
        if self.subscriptions["laser_scan"]:
            self.sensor_controller.unsubscribe_laser_scan()
            self.subscriptions["laser_scan"] = False
            logging.info("✓ Laser scan unsubscribed")
        else:
            self.sensor_controller.subscribe_laser_scan(
                lambda scan: logging.info(f"Laser Scan: {len(scan.ranges)} ranges")
            )
            self.subscriptions["laser_scan"] = True
            logging.info("✓ Laser scan subscribed")

    def toggle_rgbd_color_info_subscription(self):
        """Toggle RGBD color camera info subscription"""
        if self.subscriptions["rgbd_color_info"]:
            self.sensor_controller.unsubscribe_rgbd_color_camera_info()
            self.subscriptions["rgbd_color_info"] = False
            logging.info("✓ RGBD color camera info unsubscribed")
        else:
            self.sensor_controller.subscribe_rgbd_color_camera_info(
                lambda info: logging.info(f"RGBD Color Info: K={info.K}")
            )
            self.subscriptions["rgbd_color_info"] = True
            logging.info("✓ RGBD color camera info subscribed")

    def toggle_rgbd_depth_image_subscription(self):
        """Toggle RGBD depth image subscription"""
        if self.subscriptions["rgbd_depth_image"]:
            self.sensor_controller.unsubscribe_rgbd_depth_image()
            self.subscriptions["rgbd_depth_image"] = False
            logging.info("✓ RGBD depth image unsubscribed")
        else:
            self.sensor_controller.subscribe_rgbd_depth_image(
                lambda img: logging.info(f"RGBD Depth Image: {len(img.data)} bytes")
            )
            self.subscriptions["rgbd_depth_image"] = True
            logging.info("✓ RGBD depth image subscribed")

    def unsubscribe_rgbd_depth_image_subscription(self):
        """Unsubscribe RGBD depth image subscription"""
        self.sensor_controller.unsubscribe_rgbd_depth_image()
        self.subscriptions["rgbd_depth_image"] = False
        logging.info("✓ RGBD depth image unsubscribed")

    def toggle_rgbd_color_image_subscription(self):
        """Toggle RGBD color image subscription"""
        if self.subscriptions["rgbd_color_image"]:
            self.sensor_controller.unsubscribe_rgbd_color_image()
            self.subscriptions["rgbd_color_image"] = False
            logging.info("✓ RGBD color image unsubscribed")
        else:
            self.sensor_controller.subscribe_rgbd_color_image(
                lambda img: logging.info(f"RGBD Color Image: {len(img.data)} bytes")
            )
            self.subscriptions["rgbd_color_image"] = True
            logging.info("✓ RGBD color image subscribed")

    def toggle_rgb_depth_info_subscription(self):
        """Toggle RGB depth camera info subscription"""
        if self.subscriptions["rgb_depth_info"]:
            self.sensor_controller.unsubscribe_rgb_depth_camera_info()
            self.subscriptions["rgb_depth_info"] = False
            logging.info("✓ RGB depth camera info unsubscribed")
        else:
            self.sensor_controller.subscribe_rgb_depth_camera_info(
                lambda info: logging.info(f"RGB Depth Info: K={info.K}")
            )
            self.subscriptions["rgb_depth_info"] = True
            logging.info("✓ RGB depth camera info subscribed")

    def toggle_left_binocular_high_subscription(self):
        """Toggle left binocular high image subscription"""
        if self.subscriptions["left_binocular_high"]:
            self.sensor_controller.unsubscribe_left_binocular_high_img()
            self.subscriptions["left_binocular_high"] = False
            logging.info("✓ Left binocular high image unsubscribed")
        else:
            self.sensor_controller.subscribe_left_binocular_high_img(
                lambda img: logging.info(f"Left Binocular High: {len(img.data)} bytes")
            )
            self.subscriptions["left_binocular_high"] = True
            logging.info("✓ Left binocular high image subscribed")

    def toggle_left_binocular_low_subscription(self):
        """Toggle left binocular low image subscription"""
        if self.subscriptions["left_binocular_low"]:
            self.sensor_controller.unsubscribe_left_binocular_low_img()
            self.subscriptions["left_binocular_low"] = False
            logging.info("✓ Left binocular low image unsubscribed")
        else:
            self.sensor_controller.subscribe_left_binocular_low_img(
                lambda img: logging.info(f"Left Binocular Low: {len(img.data)} bytes")
            )
            self.subscriptions["left_binocular_low"] = True
            logging.info("✓ Left binocular low image subscribed")

    def toggle_right_binocular_low_subscription(self):
        """Toggle right binocular low image subscription"""
        if self.subscriptions["right_binocular_low"]:
            self.sensor_controller.unsubscribe_right_binocular_low_img()
            self.subscriptions["right_binocular_low"] = False
            logging.info("✓ Right binocular low image unsubscribed")
        else:
            self.sensor_controller.subscribe_right_binocular_low_img(
                lambda img: logging.info(f"Right Binocular Low: {len(img.data)} bytes")
            )
            self.subscriptions["right_binocular_low"] = True
            logging.info("✓ Right binocular low image subscribed")

    def toggle_depth_image_subscription(self):
        """Toggle depth image subscription"""
        if self.subscriptions["depth_image"]:
            self.sensor_controller.unsubscribe_depth_image()
            self.subscriptions["depth_image"] = False
            logging.info("✓ Depth image unsubscribed")
        else:
            self.sensor_controller.subscribe_depth_image(
                lambda img: logging.info(f"Depth Image: {len(img.data)} bytes")
            )
            self.subscriptions["depth_image"] = True
            logging.info("✓ Depth image subscribed")

    def show_status(self):
        """Display current sensor status"""
        logging.info("\n" + "=" * 70)
        logging.info("SENSOR STATUS")
        logging.info("=" * 70)
        logging.info(
            f"Channel Switch:                {'OPEN' if self.channel_opened else 'CLOSED'}"
        )
        logging.info(
            f"Laser Scan:                    {'OPEN' if self.sensors_state['laser_scan'] else 'CLOSED'}"
        )
        logging.info(
            f"RGBD Camera:                   {'OPEN' if self.sensors_state['rgbd_camera'] else 'CLOSED'}"
        )
        logging.info(
            f"Binocular Camera:              {'OPEN' if self.sensors_state['binocular_camera'] else 'CLOSED'}"
        )
        logging.info("\nSUBSCRIPTIONS:")
        logging.info(
            f"  Ultra:                       {'✓ SUBSCRIBED' if self.subscriptions['ultra'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  Head Touch:                  {'✓ SUBSCRIBED' if self.subscriptions['head_touch'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  IMU:                         {'✓ SUBSCRIBED' if self.subscriptions['imu'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  Laser Scan:                  {'✓ SUBSCRIBED' if self.subscriptions['laser_scan'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  RGBD Color Info:             {'✓ SUBSCRIBED' if self.subscriptions['rgbd_color_info'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  RGBD Depth Image:            {'✓ SUBSCRIBED' if self.subscriptions['rgbd_depth_image'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  RGBD Color Image:            {'✓ SUBSCRIBED' if self.subscriptions['rgbd_color_image'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  RGB Depth Info:              {'✓ SUBSCRIBED' if self.subscriptions['rgb_depth_info'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  Left Binocular High:         {'✓ SUBSCRIBED' if self.subscriptions['left_binocular_high'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  Left Binocular Low:          {'✓ SUBSCRIBED' if self.subscriptions['left_binocular_low'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  Right Binocular Low:         {'✓ SUBSCRIBED' if self.subscriptions['right_binocular_low'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info(
            f"  Depth Image:                 {'✓ SUBSCRIBED' if self.subscriptions['depth_image'] else '✗ UNSUBSCRIBED'}"
        )
        logging.info("=" * 70 + "\n")


def print_menu():
    """Print interactive menu"""
    logging.info("\n" + "=" * 70)
    logging.info("SENSOR CONTROL MENU")
    logging.info("=" * 70)
    logging.info("Channel Control:")
    logging.info("  1 - Open Channel Switch       2 - Close Channel Switch")
    logging.info("\nSensor Control:")
    logging.info("  3 - Open Laser Scan            4 - Close Laser Scan")
    logging.info("  5 - Open RGBD Camera           6 - Close RGBD Camera")
    logging.info("  7 - Open Binocular Camera      8 - Close Binocular Camera")
    logging.info("\nSubscription Toggle (lowercase=toggle, UPPERCASE=unsubscribe):")
    logging.info("  u/U - Ultra                    l/L - Laser Scan Data")
    logging.info("  h/H - Head Touch               i/I - IMU")
    logging.info("\nRGBD Subscriptions (lowercase=toggle, UPPERCASE=unsubscribe):")
    logging.info("  r/R - RGBD Color Info            d/D - RGBD Depth Image")
    logging.info("  c/C - RGBD Color Image           p/P - RGB Depth Info")
    logging.info("\nBinocular Subscriptions:")
    logging.info("  b/B - Left Binocular High        n/N - Left Binocular Low")
    logging.info("  m/M - Right Binocular Low")
    logging.info("\nOther Subscriptions:")
    logging.info("  e/E - Depth Image")
    logging.info("\nCommands:")
    logging.info("  s - Show Status                ESC - Quit              ? - Help")
    logging.info("=" * 70)


def main():
    """Main function"""
    logging.info("\n" + "=" * 70)
    logging.info("MagicDog SDK Sensor Interactive Example")
    logging.info("=" * 70 + "\n")

    local_ip = "192.168.55.10"
    robot = magicdog.MagicRobot()

    if not robot.initialize(local_ip):
        logging.error("Robot initialization failed")
        return

    if not robot.connect():
        logging.error("Robot connection failed")
        robot.shutdown()
        return

    logging.info("✓ Robot connected successfully\n")

    sensor_controller = robot.get_sensor_controller()
    sensor_manager = SensorManager(robot, sensor_controller)

    print_menu()

    try:
        while True:
            choice = input("\nEnter your choice: ").strip().lower()

            if choice == "\x1b":  # ESC key
                logging.info("ESC key pressed, exiting program...")
                break

            # Channel control
            if choice == "1":
                sensor_manager.open_channel()
            elif choice == "2":
                sensor_manager.close_channel()

            # Sensor control
            elif choice == "3":
                sensor_manager.open_laser_scan()
            elif choice == "4":
                sensor_manager.close_laser_scan()
            elif choice == "5":
                sensor_manager.open_rgbd_camera()
            elif choice == "6":
                sensor_manager.close_rgbd_camera()
            elif choice == "7":
                sensor_manager.open_binocular_camera()
            elif choice == "8":
                sensor_manager.close_binocular_camera()

            # Basic sensor subscriptions
            elif choice.lower() == "u":
                sensor_manager.toggle_ultra_subscription()
            elif choice.lower() == "h":
                sensor_manager.toggle_head_touch_subscription()
            elif choice.lower() == "i":
                sensor_manager.toggle_imu_subscription()
            elif choice.lower() == "l":
                sensor_manager.toggle_laser_scan_subscription()

            # RGBD subscriptions
            elif choice.lower() == "r":
                sensor_manager.toggle_rgbd_color_info_subscription()
            elif choice.lower() == "d":
                sensor_manager.toggle_rgbd_depth_image_subscription()
            elif choice.lower() == "c":
                sensor_manager.toggle_rgbd_color_image_subscription()
            elif choice.lower() == "p":
                sensor_manager.toggle_rgb_depth_info_subscription()
            # Binocular subscriptions
            elif choice.lower() == "b":
                sensor_manager.toggle_left_binocular_high_subscription()
            elif choice.lower() == "n":
                sensor_manager.toggle_left_binocular_low_subscription()
            elif choice.lower() == "m":
                sensor_manager.toggle_right_binocular_low_subscription()
            elif choice.lower() == "e":
                sensor_manager.toggle_depth_image_subscription()

            # Commands
            elif choice.lower() == "s":
                sensor_manager.show_status()
            elif choice == "?" or choice == "help":
                print_menu()
            else:
                logging.warning(f"Invalid choice: '{choice}'. Press '?' for help.")

    except KeyboardInterrupt:
        logging.info("\nReceived keyboard interrupt, shutting down...")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        import traceback

        traceback.print_exc()
    finally:
        # Cleanup: unsubscribe all and close all sensors
        logging.info("Cleaning up...")

        # Unsubscribe from all active subscriptions
        for sensor_name, is_subscribed in sensor_manager.subscriptions.items():
            if is_subscribed:
                logging.info(f"Unsubscribing from {sensor_name}...")

        if sensor_manager.sensors_state["laser_scan"]:
            sensor_manager.close_laser_scan()
        if sensor_manager.sensors_state["rgbd_camera"]:
            sensor_manager.close_rgbd_camera()
        if sensor_manager.sensors_state["binocular_camera"]:
            sensor_manager.close_binocular_camera()
        if sensor_manager.channel_opened:
            sensor_manager.close_channel()

        # Allow time for cleanup
        time.sleep(1)

        sensor_controller.shutdown()
        logging.info("sensor controller shutdown")

        robot.disconnect()
        logging.info("robot disconnect")

        robot.shutdown()
        logging.info("robot shutdown")


if __name__ == "__main__":
    main()
