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
  // Exit process
  exit(signum);
}

int main() {
  // 绑定 SIGINT（Ctrl+C）
  signal(SIGINT, signalHandler);

  std::string local_ip = "192.168.55.10";
  // Configure local IP address for direct network connection to machine and initialize SDK
  if (!robot.Initialize(local_ip)) {
    std::cerr << "Robot SDK initialization failed." << std::endl;
    robot.Shutdown();
    return -1;
  }

  // Connect to robot
  auto status = robot.Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Connect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  auto& controller = robot.GetSensorController();

  status = controller.OpenChannelSwith();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Open channel failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  controller.SubscribeLeftBinocularHighImg([](const std::shared_ptr<CompressedImage> msg) {
    std::cout << "Received left binocular high image." << std::endl;
  });
  controller.SubscribeLeftBinocularLowImg([](const std::shared_ptr<CompressedImage> msg) {
    std::cout << "Received left binocular low image." << std::endl;
  });
  controller.SubscribeRightBinocularLowImg([](const std::shared_ptr<CompressedImage> msg) {
    std::cout << "Received right binocular low image." << std::endl;
  });
  controller.SubscribeDepthImage([](const std::shared_ptr<Image> msg) {
    std::cout << "Received depth image." << std::endl;
  });

  status = controller.OpenBinocularCamera();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Open binocular camera failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  usleep(50000000);

  // Close binocular camera
  status = controller.CloseBinocularCamera();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Close binocular camera failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
  }

  status = controller.CloseChannelSwith();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Close channel failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // Disconnect from robot
  status = robot.Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Disconnect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  robot.Shutdown();

  return 0;
}