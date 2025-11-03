#include "magic_robot.h"
#include "magic_type.h"

#include <unistd.h>
#include <csignal>

#include <iostream>
#include <memory>

using namespace magic::dog;

magic::dog::MagicRobot robot;

void signalHandler(int signum) {
  std::cout << "Interrupt signal (" << signum << ") received.\n";

  robot.Shutdown();
  // 退出进程
  exit(signum);
}

int main() {
  // 绑定 SIGINT（Ctrl+C）
  signal(SIGINT, signalHandler);

  std::string local_ip = "192.168.55.10";
  // 配置本机网线直连机器的IP地址，并进行SDK初始化
  if (!robot.Initialize(local_ip)) {
    std::cerr << "robot sdk initialize failed." << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 设置rpc超时时间为5s
  robot.SetTimeout(5000);

  // 连接机器人
  auto status = robot.Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "connect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  auto& controller = robot.GetSensorController();

  status = controller.OpenChannelSwith();
  if (status.code != ErrorCode::OK) {
    std::cerr << "open channel failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // controller.SubscribeTof([](const std::shared_ptr<Tof>) {
  //   static unsigned int count = 0;
  //   if (count++ % 10 == 0) {
  //     std::cout << "receive tof." << std::endl;
  //   }
  // });
  // controller.SubscribeUltra([](const std::shared_ptr<Ultra>) {
  //   static unsigned int count = 0;
  //   if (count++ % 10 == 0) {
  //     std::cout << "receive ultra." << std::endl;
  //   }
  // });
  // controller.SubscribeHeadTouch([](const std::shared_ptr<HeadTouch>) {
  //   std::cout << "receive head touch." << std::endl;
  // });

  // 打开lidar
  // status = controller.OpenLidar();
  // if (status.code != ErrorCode::OK) {
  //   std::cerr << "open lidar failed"
  //             << ", code: " << status.code
  //             << ", message: " << status.message << std::endl;
  //   robot.Shutdown();
  //   return -1;
  // }

  // controller.SubscribeImu([](const std::shared_ptr<Imu> msg) {
  //   static unsigned int count = 0;
  //   if (count++ % 10000 == 0) {
  //     std::cout << "receive imu." << std::endl;
  //   }
  // });

  // controller.SubscribeLidar([] (const std::shared_ptr<LaserScan>) {
  //   std::cout << "receive lidar point cloud." << std::endl;
  // });

  // controller.SubscribeRgbdColorCameraInfo([](const std::shared_ptr<CameraInfo> msg) {
  //   std::cout << "receive rgbd color camera info." << std::endl;
  // });
  // controller.SubscribeRgbdDepthImage([](const std::shared_ptr<Image> msg) {
  //   std::cout << "receive rgbd depth image." << std::endl;
  // });
  // controller.SubscribeRgbdColorImage([](const std::shared_ptr<Image> msg) {
  //   std::cout << "receive rgbd color image." << std::endl;
  // });
  // controller.SubscribeRgbDepthCameraInfo([](const std::shared_ptr<CameraInfo> msg) {
  //   std::cout << "receive rgb depth camera info." << std::endl;
  // });

  // status = controller.OpenRgbdCamera();
  // if (status.code != ErrorCode::OK) {
  //   std::cerr << "open rgbd camera failed"
  //             << ", code: " << status.code
  //             << ", message: " << status.message << std::endl;
  //   robot.Shutdown();
  //   return -1;
  // }

  controller.SubscribeLeftBinocularHighImg([](const std::shared_ptr<CompressedImage> msg) {
    std::cout << "receive left binocular high img." << std::endl;
  });
  controller.SubscribeLeftBinocularLowImg([](const std::shared_ptr<CompressedImage> msg) {
    std::cout << "receive left binocular low img." << std::endl;
  });
  controller.SubscribeRightBinocularLowImg([](const std::shared_ptr<CompressedImage> msg) {
    std::cout << "receive right binocular low img." << std::endl;
  });
  controller.SubscribeDepthImage([](const std::shared_ptr<Image> msg) {
    std::cout << "receive depth image." << std::endl;
  });

  status = controller.OpenBinocularCamera();
  if (status.code != ErrorCode::OK) {
    std::cerr << "open binocular camera failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  usleep(50000000);

  // 关闭lidar
  // status = controller.CloseLidar();
  // if (status.code != ErrorCode::OK) {
  //   std::cerr << "close lidar failed"
  //             << ", code: " << status.code
  //             << ", message: " << status.message << std::endl;
  //   robot.Shutdown();
  //   return -1;
  // }

  // 关闭RGBD相机
  // status = controller.CloseRgbdCamera();
  // if (status.code != ErrorCode::OK) {
  //   std::cerr << "close rgbd camera failed"
  //             << ", code: " << status.code
  //             << ", message: " << status.message << std::endl;
  //   robot.Shutdown();
  //   return -1;
  // }

  // 关闭双目相机
  status = controller.CloseBinocularCamera();
  if (status.code != ErrorCode::OK) {
    std::cerr << "close binocular camera failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
  }

  status = controller.CloseChannelSwith();
  if (status.code != ErrorCode::OK) {
    std::cerr << "close channel failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 断开与机器人的链接
  status = robot.Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "disconnect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  robot.Shutdown();

  return 0;
}