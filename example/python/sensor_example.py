#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来控制机器人。
"""

import sys
import time

# 添加构建目录到 Python 路径，插入到最前面
sys.path.insert(0, '../../build')

try:
    import magicdog_python as magicdog
    from magicdog_python import TtsCommand, TtsPriority, TtsMode, GetSpeechConfig, ErrorCode
    print("成功导入 MagicDog Python 模块！")
    # 打印导入的 magicdog_python 的路径
    print(f"导入的 magicdog_python 的路径: {sys.path}")
except ImportError as e:
    print(f"导入失败: {e}")
    print("请先运行 build_python.sh 构建 Python 绑定")
    sys.exit(1)

def main():
    """主函数"""
    print("MagicDog SDK Audio Python 示例程序")
    
    local_ip = "192.168.55.10"
    robot = magicdog.MagicRobot()
    if not robot.initialize(local_ip):
        print("机器人初始化失败")
        return

    robot.set_timeout(5000)
    if not robot.connect():
        print("机器人连接失败")
        robot.shutdown()
        return
    
    print("机器人连接成功")
    
    sensor_controller = robot.get_sensor_controller()
    # sensor_controller.subscribe_tof(lambda tof: print(f"TOF: {len(tof.data)}"))
    sensor_controller.subscribe_ultra(lambda ultra: print(f"Ultra: {len(ultra.data)}"))
    sensor_controller.subscribe_lidar(lambda lidar: print(f"Lidar: {len(lidar.ranges)}"))
    # sensor_controller.subscribe_imu(lambda imu: print(f"IMU: {imu.orientation}"))
    sensor_controller.subscribe_rgbd_color_camera_info(lambda camera_info: print(f"RGBD Color Camera Info: {camera_info.K}"))
    sensor_controller.subscribe_rgbd_depth_image(lambda depth_image: print(f"RGBD Depth Image: {len(depth_image.data)}"))
    sensor_controller.subscribe_rgbd_color_image(lambda color_image: print(f"RGBD Color Image: {len(color_image.data)}"))
    sensor_controller.subscribe_rgb_depth_camera_info(lambda camera_info: print(f"RGB Depth Camera Info: {camera_info.K}"))
    sensor_controller.subscribe_left_binocular_high_img(lambda img: print(f"Left Binocular High Image: {len(img.data)}"))
    sensor_controller.subscribe_left_binocular_low_img(lambda img: print(f"Left Binocular Low Image: {len(img.data)}"))
    sensor_controller.subscribe_right_binocular_low_img(lambda img: print(f"Right Binocular Low Image: {len(img.data)}"))

    status = sensor_controller.open_channel_switch()
    if status.code != ErrorCode.OK:
        print(f"打开通道失败: {status.message}")
        robot.shutdown()
        return

    status = sensor_controller.open_lidar()
    if status.code != ErrorCode.OK:
        print(f"打开激光雷达失败: {status.message}")
        robot.shutdown()
        return
    
    status = sensor_controller.open_rgbd_camera()
    if status.code != ErrorCode.OK:
        print(f"打开RGBD相机失败: {status.message}")
        robot.shutdown()
        return
    
    status = sensor_controller.open_binocular_camera()
    if status.code != ErrorCode.OK:
        print(f"打开立体相机失败: {status.message}")
        robot.shutdown()
        return

    time.sleep(10)

    status = sensor_controller.close_lidar()
    if status.code != ErrorCode.OK:
        print(f"关闭激光雷达失败: {status.message}")
        robot.shutdown()
        return

    status = sensor_controller.close_rgbd_camera()
    if status.code != ErrorCode.OK:
        print(f"关闭RGBD相机失败: {status.message}")
        robot.shutdown()
        return

    status = sensor_controller.close_binocular_camera()
    if status.code != ErrorCode.OK:
        print(f"关闭立体相机失败: {status.message}")
        robot.shutdown()
        return

    time.sleep(10)

    status = sensor_controller.close_channel_switch()
    if status.code != ErrorCode.OK:
        print(f"关闭通道失败: {status.message}")
        robot.shutdown()
        return

    # 避免 lcm 中有缓冲数据未处理完
    time.sleep(10)

    robot.disconnect()
    robot.shutdown()
    print("\n示例程序执行完成！")

if __name__ == "__main__":
    main() 