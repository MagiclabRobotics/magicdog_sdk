#include "magic_robot.h"
#include "magic_sdk_version.h"
#include "magic_type.h"

#include <unistd.h>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <map>
#include <memory>
#include <string>
#include <thread>

using namespace magic::dog;

// Global robot instance
std::unique_ptr<MagicRobot> robot = nullptr;

// Sensor manager class
class SensorManager {
 public:
  SensorManager(SensorController& controller) : controller_(controller) {}

  // Channel Control
  bool open_channel() {
    if (channel_opened_) {
      std::cout << "Channel already opened" << std::endl;
      return true;
    }

    auto status = robot->OpenChannelSwitch();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to open channel: " << status.message << std::endl;
      return false;
    }

    channel_opened_ = true;
    std::cout << "✓ Channel opened successfully" << std::endl;
    return true;
  }

  bool close_channel() {
    if (!channel_opened_) {
      std::cout << "Channel already closed" << std::endl;
      return true;
    }

    auto status = robot->CloseChannelSwitch();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to close channel: " << status.message << std::endl;
      return false;
    }

    channel_opened_ = false;
    std::cout << "✓ Channel closed successfully" << std::endl;
    return true;
  }

  // Sensor Open/Close
  bool open_laser_scan() {
    if (sensors_state_["laser_scan"]) {
      std::cout << "Laser scan already opened" << std::endl;
      return true;
    }

    auto status = controller_.OpenLaserScan();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to open laser scan: " << status.message << std::endl;
      return false;
    }

    sensors_state_["laser_scan"] = true;
    std::cout << "✓ Laser scan opened" << std::endl;
    return true;
  }

  bool close_laser_scan() {
    if (!sensors_state_["laser_scan"]) {
      std::cout << "Laser scan already closed" << std::endl;
      return true;
    }

    // Unsubscribe if subscribed
    if (subscriptions_["laser_scan"]) {
      toggle_laser_scan_subscription();
    }

    auto status = controller_.CloseLaserScan();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to close laser scan: " << status.message << std::endl;
      return false;
    }

    sensors_state_["laser_scan"] = false;
    std::cout << "✓ Laser scan closed" << std::endl;
    return true;
  }

  bool open_rgbd_camera() {
    if (sensors_state_["rgbd_camera"]) {
      std::cout << "RGBD camera already opened" << std::endl;
      return true;
    }

    auto status = controller_.OpenRgbdCamera();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to open RGBD camera: " << status.message << std::endl;
      return false;
    }

    sensors_state_["rgbd_camera"] = true;
    std::cout << "✓ RGBD camera opened" << std::endl;
    return true;
  }

  bool close_rgbd_camera() {
    if (!sensors_state_["rgbd_camera"]) {
      std::cout << "RGBD camera already closed" << std::endl;
      return true;
    }

    // Unsubscribe all RGBD subscriptions if subscribed
    if (subscriptions_["rgbd_color_info"]) {
      toggle_rgbd_color_info_subscription();
    }
    if (subscriptions_["rgbd_depth_image"]) {
      toggle_rgbd_depth_image_subscription();
    }
    if (subscriptions_["rgbd_color_image"]) {
      toggle_rgbd_color_image_subscription();
    }
    if (subscriptions_["rgb_depth_info"]) {
      toggle_rgb_depth_info_subscription();
    }

    auto status = controller_.CloseRgbdCamera();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to close RGBD camera: " << status.message << std::endl;
      return false;
    }

    sensors_state_["rgbd_camera"] = false;
    std::cout << "✓ RGBD camera closed" << std::endl;
    return true;
  }

  bool open_binocular_camera() {
    if (sensors_state_["binocular_camera"]) {
      std::cout << "Binocular camera already opened" << std::endl;
      return true;
    }

    auto status = controller_.OpenBinocularCamera();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to open binocular camera: " << status.message << std::endl;
      return false;
    }

    sensors_state_["binocular_camera"] = true;
    std::cout << "✓ Binocular camera opened" << std::endl;
    return true;
  }

  bool close_binocular_camera() {
    if (!sensors_state_["binocular_camera"]) {
      std::cout << "Binocular camera already closed" << std::endl;
      return true;
    }

    // Unsubscribe all binocular subscriptions if subscribed
    if (subscriptions_["left_binocular_high"]) {
      toggle_left_binocular_high_subscription();
    }
    if (subscriptions_["left_binocular_low"]) {
      toggle_left_binocular_low_subscription();
    }
    if (subscriptions_["right_binocular_low"]) {
      toggle_right_binocular_low_subscription();
    }

    auto status = controller_.CloseBinocularCamera();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to close binocular camera: " << status.message << std::endl;
      return false;
    }

    sensors_state_["binocular_camera"] = false;
    std::cout << "✓ Binocular camera closed" << std::endl;
    return true;
  }

  // Subscribe/Unsubscribe Methods
  void toggle_ultra_subscription() {
    if (subscriptions_["ultra"]) {
      controller_.UnsubscribeUltra();
      subscriptions_["ultra"] = false;
      std::cout << "✓ Ultra sensor unsubscribed" << std::endl;
    } else {
      controller_.SubscribeUltra([](const std::shared_ptr<Float32MultiArray> ultra) {
        std::cout << "Ultra: " << ultra->data.size() << std::endl;
      });
      subscriptions_["ultra"] = true;
      std::cout << "✓ Ultra sensor subscribed" << std::endl;
    }
  }

  void toggle_head_touch_subscription() {
    if (subscriptions_["head_touch"]) {
      controller_.UnsubscribeHeadTouch();
      subscriptions_["head_touch"] = false;
      std::cout << "✓ Head touch sensor unsubscribed" << std::endl;
    } else {
      controller_.SubscribeHeadTouch([](const std::shared_ptr<HeadTouch> touch) {
        std::cout << "Head Touch: " << int(touch->data) << std::endl;
      });
      subscriptions_["head_touch"] = true;
      std::cout << "✓ Head touch sensor subscribed" << std::endl;
    }
  }

  void toggle_imu_subscription() {
    if (subscriptions_["imu"]) {
      controller_.UnsubscribeImu();
      subscriptions_["imu"] = false;
      std::cout << "✓ IMU sensor unsubscribed" << std::endl;
    } else {
      static int imu_counter = 0;
      controller_.SubscribeImu([&](const std::shared_ptr<Imu> imu) {
        imu_counter++;
        if (imu_counter % 500 == 0) {
          std::cout << "IMU: " << imu->temperature << std::endl;
        }
      });
      subscriptions_["imu"] = true;
      std::cout << "✓ IMU sensor subscribed" << std::endl;
    }
  }

  void toggle_laser_scan_subscription() {
    if (subscriptions_["laser_scan"]) {
      controller_.UnsubscribeLaserScan();
      subscriptions_["laser_scan"] = false;
      std::cout << "✓ Laser scan unsubscribed" << std::endl;
    } else {
      controller_.SubscribeLaserScan([](const std::shared_ptr<LaserScan> scan) {
        std::cout << "Laser Scan: " << scan->ranges.size() << " ranges" << std::endl;
      });
      subscriptions_["laser_scan"] = true;
      std::cout << "✓ Laser scan subscribed" << std::endl;
    }
  }

  void toggle_rgbd_color_info_subscription() {
    if (subscriptions_["rgbd_color_info"]) {
      controller_.UnsubscribeRgbdColorCameraInfo();
      subscriptions_["rgbd_color_info"] = false;
      std::cout << "✓ RGBD color camera info unsubscribed" << std::endl;
    } else {
      controller_.SubscribeRgbdColorCameraInfo([](const std::shared_ptr<CameraInfo> info) {
        std::cout << "RGBD Color Info: K=" << info->K[0] << ", " << info->K[1] << ", " << info->K[2] << ", " << info->K[3] << ", " << info->K[4] << ", " << info->K[5] << ", " << info->K[6] << ", " << info->K[7] << ", " << info->K[8] << std::endl;
      });
      subscriptions_["rgbd_color_info"] = true;
      std::cout << "✓ RGBD color camera info subscribed" << std::endl;
    }
  }

  void toggle_rgbd_depth_image_subscription() {
    if (subscriptions_["rgbd_depth_image"]) {
      controller_.UnsubscribeRgbdDepthImage();
      subscriptions_["rgbd_depth_image"] = false;
      std::cout << "✓ RGBD depth image unsubscribed" << std::endl;
    } else {
      controller_.SubscribeRgbdDepthImage([](const std::shared_ptr<Image> img) {
        std::cout << "RGBD Depth Image: " << img->data.size() << " bytes" << std::endl;
      });
      subscriptions_["rgbd_depth_image"] = true;
      std::cout << "✓ RGBD depth image subscribed" << std::endl;
    }
  }

  void toggle_rgbd_color_image_subscription() {
    if (subscriptions_["rgbd_color_image"]) {
      controller_.UnsubscribeRgbdColorImage();
      subscriptions_["rgbd_color_image"] = false;
      std::cout << "✓ RGBD color image unsubscribed" << std::endl;
    } else {
      controller_.SubscribeRgbdColorImage([](const std::shared_ptr<Image> img) {
        std::cout << "RGBD Color Image: " << img->data.size() << " bytes" << std::endl;
      });
      subscriptions_["rgbd_color_image"] = true;
      std::cout << "✓ RGBD color image subscribed" << std::endl;
    }
  }

  void toggle_rgb_depth_info_subscription() {
    if (subscriptions_["rgb_depth_info"]) {
      controller_.UnsubscribeRgbDepthCameraInfo();
      subscriptions_["rgb_depth_info"] = false;
      std::cout << "✓ RGB depth camera info unsubscribed" << std::endl;
    } else {
      controller_.SubscribeRgbDepthCameraInfo([](const std::shared_ptr<CameraInfo> info) {
        std::cout << "RGB Depth Info: K=" << info->K[0] << ", " << info->K[1] << ", " << info->K[2] << ", " << info->K[3] << ", " << info->K[4] << ", " << info->K[5] << ", " << info->K[6] << ", " << info->K[7] << ", " << info->K[8] << std::endl;
      });
      subscriptions_["rgb_depth_info"] = true;
      std::cout << "✓ RGB depth camera info subscribed" << std::endl;
    }
  }

  void toggle_left_binocular_high_subscription() {
    if (subscriptions_["left_binocular_high"]) {
      controller_.UnsubscribeLeftBinocularHighImg();
      subscriptions_["left_binocular_high"] = false;
      std::cout << "✓ Left binocular high image unsubscribed" << std::endl;
    } else {
      controller_.SubscribeLeftBinocularHighImg([](const std::shared_ptr<CompressedImage> img) {
        std::cout << "Left Binocular High: " << img->data.size() << " bytes" << std::endl;
      });
      subscriptions_["left_binocular_high"] = true;
      std::cout << "✓ Left binocular high image subscribed" << std::endl;
    }
  }

  void toggle_left_binocular_low_subscription() {
    if (subscriptions_["left_binocular_low"]) {
      controller_.UnsubscribeLeftBinocularLowImg();
      subscriptions_["left_binocular_low"] = false;
      std::cout << "✓ Left binocular low image unsubscribed" << std::endl;
    } else {
      controller_.SubscribeLeftBinocularLowImg([](const std::shared_ptr<CompressedImage> img) {
        std::cout << "Left Binocular Low: " << img->data.size() << " bytes" << std::endl;
      });
      subscriptions_["left_binocular_low"] = true;
      std::cout << "✓ Left binocular low image subscribed" << std::endl;
    }
  }

  void toggle_right_binocular_low_subscription() {
    if (subscriptions_["right_binocular_low"]) {
      controller_.UnsubscribeRightBinocularLowImg();
      subscriptions_["right_binocular_low"] = false;
      std::cout << "✓ Right binocular low image unsubscribed" << std::endl;
    } else {
      controller_.SubscribeRightBinocularLowImg([](const std::shared_ptr<CompressedImage> img) {
        std::cout << "Right Binocular Low: " << img->data.size() << " bytes" << std::endl;
      });
      subscriptions_["right_binocular_low"] = true;
      std::cout << "✓ Right binocular low image subscribed" << std::endl;
    }
  }

  void toggle_depth_image_subscription() {
    if (subscriptions_["depth_image"]) {
      controller_.UnsubscribeDepthImage();
      subscriptions_["depth_image"] = false;
      std::cout << "✓ Depth image unsubscribed" << std::endl;
    } else {
      controller_.SubscribeDepthImage([](const std::shared_ptr<Image> img) {
        std::cout << "Depth Image: " << img->data.size() << " bytes" << std::endl;
      });
      subscriptions_["depth_image"] = true;
      std::cout << "✓ Depth image subscribed" << std::endl;
    }
  }

  void show_status() {
    std::cout << "\n"
              << std::string(70, '=') << std::endl;
    std::cout << "SENSOR STATUS" << std::endl;
    std::cout << std::string(70, '=') << std::endl;
    std::cout << "Channel Switch:                " << (channel_opened_ ? "OPEN" : "CLOSED") << std::endl;
    std::cout << "Laser Scan:                    " << (sensors_state_["laser_scan"] ? "OPEN" : "CLOSED") << std::endl;
    std::cout << "RGBD Camera:                   " << (sensors_state_["rgbd_camera"] ? "OPEN" : "CLOSED") << std::endl;
    std::cout << "Binocular Camera:              " << (sensors_state_["binocular_camera"] ? "OPEN" : "CLOSED") << std::endl;
    std::cout << "\nSUBSCRIPTIONS:" << std::endl;
    std::cout << "  Ultra:                       " << (subscriptions_["ultra"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  Head Touch:                  " << (subscriptions_["head_touch"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  IMU:                         " << (subscriptions_["imu"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  Laser Scan:                  " << (subscriptions_["laser_scan"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  RGBD Color Info:             " << (subscriptions_["rgbd_color_info"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  RGBD Depth Image:            " << (subscriptions_["rgbd_depth_image"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  RGBD Color Image:            " << (subscriptions_["rgbd_color_image"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  RGB Depth Info:              " << (subscriptions_["rgb_depth_info"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  Left Binocular High:         " << (subscriptions_["left_binocular_high"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  Left Binocular Low:          " << (subscriptions_["left_binocular_low"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  Right Binocular Low:         " << (subscriptions_["right_binocular_low"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << "  Depth Image:                 " << (subscriptions_["depth_image"] ? "✓ SUBSCRIBED" : "✗ UNSUBSCRIBED") << std::endl;
    std::cout << std::string(70, '=') << "\n"
              << std::endl;
  }

 private:
  SensorController& controller_;
  bool channel_opened_ = false;
  std::map<std::string, bool> sensors_state_ = {
      {"laser_scan", false},
      {"rgbd_camera", false},
      {"binocular_camera", false}};
  std::map<std::string, bool> subscriptions_ = {
      {"ultra", false},
      {"head_touch", false},
      {"imu", false},
      {"laser_scan", false},
      {"rgbd_color_info", false},
      {"rgbd_depth_image", false},
      {"rgbd_color_image", false},
      {"rgb_depth_info", false},
      {"left_binocular_high", false},
      {"left_binocular_low", false},
      {"right_binocular_low", false},
      {"depth_image", false}};
};

void print_menu() {
  std::cout << "\n"
            << std::string(70, '=') << std::endl;
  std::cout << "SENSOR CONTROL MENU" << std::endl;
  std::cout << std::string(70, '=') << std::endl;
  std::cout << "Channel Control:" << std::endl;
  std::cout << "  1 - Open Channel Switch       2 - Close Channel Switch" << std::endl;
  std::cout << "\nSensor Control:" << std::endl;
  std::cout << "  3 - Open Laser Scan            4 - Close Laser Scan" << std::endl;
  std::cout << "  5 - Open RGBD Camera           6 - Close RGBD Camera" << std::endl;
  std::cout << "  7 - Open Binocular Camera      8 - Close Binocular Camera" << std::endl;
  std::cout << "\nSubscription Toggle (lowercase=toggle, UPPERCASE=unsubscribe):" << std::endl;
  std::cout << "  u/U - Ultra                    l/L - Laser Scan Data" << std::endl;
  std::cout << "  h/H - Head Touch               i/I - IMU" << std::endl;
  std::cout << "\nRGBD Subscriptions (lowercase=toggle, UPPERCASE=unsubscribe):" << std::endl;
  std::cout << "  r/R - RGBD Color Info            d/D - RGBD Depth Image" << std::endl;
  std::cout << "  c/C - RGBD Color Image           p/P - RGB Depth Info" << std::endl;
  std::cout << "\nBinocular Subscriptions:" << std::endl;
  std::cout << "  b/B - Left Binocular High        n/N - Left Binocular Low" << std::endl;
  std::cout << "  m/M - Right Binocular Low" << std::endl;
  std::cout << "\nOther Subscriptions:" << std::endl;
  std::cout << "  e/E - Depth Image" << std::endl;
  std::cout << "\nCommands:" << std::endl;
  std::cout << "  s - Show Status                ESC - Quit              ? - Help" << std::endl;
  std::cout << std::string(70, '=') << std::endl;
}

void signalHandler(int signum) {
  std::cout << "\nInterrupt signal (" << signum << ") received." << std::endl;
  if (robot) {
    robot->Shutdown();
  }
  exit(signum);
}

int main() {
  // Bind SIGINT (Ctrl+C)
  signal(SIGINT, signalHandler);

  std::cout << "\n"
            << std::string(70, '=') << std::endl;
  std::cout << "MagicDog SDK Sensor Interactive Example" << std::endl;
  std::cout << std::string(70, '=') << "\n"
            << std::endl;

  robot = std::make_unique<MagicRobot>();
  if (!robot->Initialize("192.168.55.10")) {
    std::cerr << "Robot initialization failed" << std::endl;
    return -1;
  }

  auto status = robot->Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Robot connection failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    robot->Shutdown();
    return -1;
  }

  std::cout << "✓ Robot connected successfully\n"
            << std::endl;

  SensorManager sensor_manager(robot->GetSensorController());

  print_menu();

  try {
    while (true) {
      std::cout << "\nEnter your choice: ";
      std::string choice;
      std::getline(std::cin, choice);

      if (choice.empty()) {
        continue;
      }

      char ch = choice[0];

      if (ch == 27) {  // ESC key
        std::cout << "ESC key pressed, exiting program..." << std::endl;
        break;
      }

      // Channel control
      if (choice == "1") {
        sensor_manager.open_channel();
      } else if (choice == "2") {
        sensor_manager.close_channel();
      }
      // Sensor control
      else if (choice == "3") {
        sensor_manager.open_laser_scan();
      } else if (choice == "4") {
        sensor_manager.close_laser_scan();
      } else if (choice == "5") {
        sensor_manager.open_rgbd_camera();
      } else if (choice == "6") {
        sensor_manager.close_rgbd_camera();
      } else if (choice == "7") {
        sensor_manager.open_binocular_camera();
      } else if (choice == "8") {
        sensor_manager.close_binocular_camera();
      }
      // Basic sensor subscriptions
      else if (ch == 'u') {  // ~20HZ
        sensor_manager.toggle_ultra_subscription();
      } else if (ch == 'U') {  // ~20HZ
        sensor_manager.toggle_ultra_subscription();
      } else if (ch == 'h') {  // trigger
        sensor_manager.toggle_head_touch_subscription();
      } else if (ch == 'H') {  // trigger
        sensor_manager.toggle_head_touch_subscription();
      } else if (ch == 'i') {  // ~500HZ
        sensor_manager.toggle_imu_subscription();
      } else if (ch == 'I') {  // ~500HZ
        sensor_manager.toggle_imu_subscription();
      } else if (ch == 'l') {
        sensor_manager.toggle_laser_scan_subscription();
      } else if (ch == 'L') {
        sensor_manager.toggle_laser_scan_subscription();
      }
      // RGBD subscriptions
      else if (ch == 'r') {
        sensor_manager.toggle_rgbd_color_info_subscription();
      } else if (ch == 'R') {
        sensor_manager.toggle_rgbd_color_info_subscription();
      } else if (ch == 'd') {
        sensor_manager.toggle_rgbd_depth_image_subscription();
      } else if (ch == 'D') {
        sensor_manager.toggle_rgbd_depth_image_subscription();
      } else if (ch == 'c') {
        sensor_manager.toggle_rgbd_color_image_subscription();
      } else if (ch == 'C') {
        sensor_manager.toggle_rgbd_color_image_subscription();
      } else if (ch == 'p') {
        sensor_manager.toggle_rgb_depth_info_subscription();
      } else if (ch == 'P') {
        sensor_manager.toggle_rgb_depth_info_subscription();
      }
      // Binocular subscriptions
      else if (ch == 'b') {
        sensor_manager.toggle_left_binocular_high_subscription();
      } else if (ch == 'B') {
        sensor_manager.toggle_left_binocular_high_subscription();
      } else if (ch == 'n') {
        sensor_manager.toggle_left_binocular_low_subscription();
      } else if (ch == 'N') {
        sensor_manager.toggle_left_binocular_low_subscription();
      } else if (ch == 'm') {
        sensor_manager.toggle_right_binocular_low_subscription();
      } else if (ch == 'M') {
        sensor_manager.toggle_right_binocular_low_subscription();
      } else if (ch == 'e') {
        sensor_manager.toggle_depth_image_subscription();
      } else if (ch == 'E') {
        sensor_manager.toggle_depth_image_subscription();
      }
      // Commands
      else if (ch == 's') {
        sensor_manager.show_status();
      } else if (choice == "?" || choice == "help") {
        print_menu();
      } else {
        std::cout << "Invalid choice: '" << choice << "'. Press '?' for help." << std::endl;
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "Error occurred: " << e.what() << std::endl;
  }

  // Cleanup: unsubscribe all and close all sensors
  std::cout << "Cleaning up..." << std::endl;

  status = robot->Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "robot disconnect failed, code: " << status.code
              << ", message: " << status.message << std::endl;
  } else {
    std::cout << "robot disconnect" << std::endl;
  }

  robot->Shutdown();
  std::cout << "robot shutdown" << std::endl;

  return 0;
}