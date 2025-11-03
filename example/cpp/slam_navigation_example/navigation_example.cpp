#include "magic_robot.h"
#include "magic_sdk_version.h"

#include <signal.h>
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

using namespace magic::dog;
using namespace std;

// Global variables
std::unique_ptr<MagicRobot> robot = nullptr;
std::atomic<bool> running(true);
std::string current_slam_mode = "IDLE";
NavMode current_nav_mode = NavMode::IDLE;
int odometry_counter = 0;

void signalHandler(int signum) {
  std::cout << "Interrupt signal (" << signum << ") received.\n";
  running = false;
  if (robot) {
    robot->Shutdown();
    std::cout << "Robot shutdown" << std::endl;
  }
  exit(-1);
}

void printHelp() {
  std::cout << "SLAM and Navigation Function Demo Program" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "preparation Functions:" << std::endl;
  std::cout << "  1        Function 1: Recovery stand" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Localization Functions:" << std::endl;
  std::cout << "  2        Function 2: Switch to localization mode" << std::endl;
  std::cout << "  4        Function 4: Initialize pose" << std::endl;
  std::cout << "  5        Function 5: Get current pose information" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Navigation Functions:" << std::endl;
  std::cout << "  3        Function 3: Switch to navigation mode" << std::endl;
  std::cout << "  6        Function 6: Set navigation target goal" << std::endl;
  std::cout << "  7        Function 7: Pause navigation" << std::endl;
  std::cout << "  8        Function 8: Resume navigation" << std::endl;
  std::cout << "  9        Function 9: Cancel navigation" << std::endl;
  std::cout << "  0        Function 0: Get navigation status" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Odometry Functions:" << std::endl;
  std::cout << "  C        Function C: Subscribe odometry stream" << std::endl;
  std::cout << "  V        Function V: Unsubscribe odometry stream" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Close Functions:" << std::endl;
  std::cout << "  L        Function L: Close navigation" << std::endl;
  std::cout << "  P        Function P: Close SLAM" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "  ?        Function ?: Print help" << std::endl;
  std::cout << "  ESC      Exit program" << std::endl;
}

// ==================== Navigation Functions ====================

// Position control standing
void recoveryStand() {
  try {
    auto& highController = robot->GetHighLevelMotionController();

    // Set gait to position control standing
    auto status = highController.SetGait(GaitMode::GAIT_STAND_R);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to set position control standing: " << status.message << std::endl;
    } else {
      std::cout << "Robot set to position control standing" << std::endl;
    }
  } catch (const std::exception& e) {
    std::cerr << "Error executing position control standing: " << e.what() << std::endl;
  }
}

void switchToLocalizationMode() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Switch to localization mode
    auto status = controller.SwitchToLocation();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to switch to localization mode, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    current_slam_mode = "LOCALIZATION";
    std::cout << "Successfully switched to localization mode" << std::endl;
    std::cout << "Robot is now in localization mode, ready to localize on existing maps" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while switching to localization mode: " << e.what() << std::endl;
  }
}

void initializePose(double x, double y, double yaw) {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Create initial pose (set to origin)
    Pose3DEuler initialPose;
    initialPose.position = {x, y, 0.0};         // x, y, z
    initialPose.orientation = {0.0, 0.0, yaw};  // roll, pitch, yaw

    std::cout << "Initializing robot pose to origin..." << std::endl;

    // Initialize pose
    auto status = controller.InitPose(initialPose);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to initialize pose, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully initialized pose" << std::endl;
    std::cout << "Robot pose has been set to origin (" << x << ", " << y << ", " << yaw << ")" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while initializing pose: " << e.what() << std::endl;
  }
}

void getCurrentLocalizationInfo() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Get current pose information
    LocalizationInfo poseInfo;
    auto status = controller.GetCurrentLocalizationInfo(poseInfo);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to get current pose information, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully retrieved current pose information" << std::endl;
    std::cout << "Localization status: " << (poseInfo.is_localization ? "Localized" : "Not localized") << std::endl;
    std::cout << "Position: [" << poseInfo.pose.position[0] << ", "
              << poseInfo.pose.position[1] << ", " << poseInfo.pose.position[2] << "]" << std::endl;
    std::cout << "Orientation: [" << poseInfo.pose.orientation[0] << ", "
              << poseInfo.pose.orientation[1] << ", " << poseInfo.pose.orientation[2] << "]" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while getting current pose information: " << e.what() << std::endl;
  }
}

void switchToNavigationMode() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Switch to navigation mode
    auto status = controller.ActivateNavMode(NavMode::GRID_MAP);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to switch to navigation mode, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    current_nav_mode = NavMode::GRID_MAP;
    std::cout << "Successfully switched to navigation mode" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while switching to navigation mode: " << e.what() << std::endl;
  }
}

void setNavigationTarget(double x, double y, double yaw) {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();
    auto& highController = robot->GetHighLevelMotionController();

    // Disable joy stick
    highController.DisableJoyStick();
    std::cout << "Successfully disabled joy stick" << std::endl;

    // change gait to slow
    // To use Navigation, you must switch to the down stairs gait
    auto status = highController.SetGait(GaitMode::GAIT_DOWN_CLIMB_STAIRS);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to set gait to slow: " << status.message << std::endl;
      return;
    }
    std::cout << "Successfully set gait to slow" << std::endl;

    // Create target goal
    NavTarget targetGoal;
    targetGoal.id = 1;
    targetGoal.frame_id = "map";

    targetGoal.goal.position = {x, y, 0.0};
    targetGoal.goal.orientation = {0.0, 0.0, yaw};

    // Set target goal
    status = controller.SetNavTarget(targetGoal);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to set navigation target, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully set navigation target: position=("
              << targetGoal.goal.position[0] << ", " << targetGoal.goal.position[1] << ", "
              << targetGoal.goal.position[2] << "), orientation=("
              << targetGoal.goal.orientation[0] << ", " << targetGoal.goal.orientation[1] << ", "
              << targetGoal.goal.orientation[2] << ")" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while setting navigation target: " << e.what() << std::endl;
  }
}

void pauseNavigation() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Pause navigation
    auto status = controller.PauseNavTask();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to pause navigation, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully paused navigation" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while pausing navigation: " << e.what() << std::endl;
  }
}

void resumeNavigation() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Resume navigation
    auto status = controller.ResumeNavTask();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to resume navigation, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully resumed navigation" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while resuming navigation: " << e.what() << std::endl;
  }
}

void cancelNavigation() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Cancel navigation
    auto status = controller.CancelNavTask();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to cancel navigation, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully cancelled navigation" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while cancelling navigation: " << e.what() << std::endl;
  }
}

void getNavigationStatus() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Get navigation status
    NavStatus navStatus;
    auto status = controller.GetNavTaskStatus(navStatus);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to get navigation status, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    // Display navigation status information
    std::cout << "=== Navigation Status ===" << std::endl;
    std::cout << "Target ID: " << navStatus.id << std::endl;
    std::cout << "Status: " << static_cast<int>(navStatus.status) << std::endl;
    std::cout << "Message: " << navStatus.message << std::endl;

    // Provide status interpretation
    std::string statusMeaning;
    switch (navStatus.status) {
      case NavStatusType::NONE:
        statusMeaning = "No navigation target set";
        break;
      case NavStatusType::RUNNING:
        statusMeaning = "Navigation is running";
        break;
      case NavStatusType::END_SUCCESS:
        statusMeaning = "Navigation completed successfully";
        break;
      case NavStatusType::END_FAILED:
        statusMeaning = "Navigation failed";
        break;
      case NavStatusType::PAUSE:
        statusMeaning = "Navigation is paused";
        break;
      default:
        statusMeaning = "Unknown status value";
        break;
    }

    std::cout << "Status meaning: " << statusMeaning << std::endl;
    std::cout << "========================" << std::endl;

  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while getting navigation status: " << e.what() << std::endl;
  }
}

void closeNavigation() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Switch to idle mode to close navigation
    auto status = controller.ActivateNavMode(NavMode::IDLE);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to close navigation, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    current_nav_mode = NavMode::IDLE;
    std::cout << "Successfully closed navigation system" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while closing navigation: " << e.what() << std::endl;
  }
}

void openOdometryStream() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Open odometry stream
    auto status = robot->OpenChannelSwitch();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to open odometry stream, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }
    std::cout << "Successfully opened odometry stream" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while opening odometry stream: " << e.what() << std::endl;
  }
}

void closeOdometryStream() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Close odometry stream
    auto status = robot->CloseChannelSwitch();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to close odometry stream, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }
    std::cout << "Successfully closed odometry stream" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while closing odometry stream: " << e.what() << std::endl;
  }
}

void subscribeOdometryStream() {
  try {
    // Open channel switch
    robot->OpenChannelSwitch();

    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Define odometry callback
    auto odometryCallback = [](const std::shared_ptr<Odometry> data) {
      if (odometry_counter % 10 == 0) {
        std::cout << "Odometry position data: " << data->position[0] << ", "
                  << data->position[1] << ", " << data->position[2] << std::endl;
        std::cout << "Odometry orientation data: " << data->orientation[0] << ", "
                  << data->orientation[1] << ", " << data->orientation[2] << ", "
                  << data->orientation[3] << std::endl;
        std::cout << "Odometry linear velocity data: " << data->linear_velocity[0] << ", "
                  << data->linear_velocity[1] << ", " << data->linear_velocity[2] << std::endl;
        std::cout << "Odometry angular velocity data: " << data->angular_velocity[0] << ", "
                  << data->angular_velocity[1] << ", " << data->angular_velocity[2] << std::endl;
      }
      odometry_counter++;
    };

    // Subscribe odometry stream
    controller.SubscribeOdometry(odometryCallback);
    std::cout << "Successfully subscribed odometry stream" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while subscribing odometry stream: " << e.what() << std::endl;
  }
}

void unsubscribeOdometryStream() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();
    robot->CloseChannelSwitch();  // Close channel switch
    std::cout << "Successfully unsubscribed odometry stream" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while unsubscribing odometry stream: " << e.what() << std::endl;
  }
}

void closeSlam() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Switch to idle mode to close SLAM
    auto status = controller.SwitchToIdle();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to close SLAM, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    current_slam_mode = "IDLE";
    std::cout << "Successfully closed SLAM system" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while closing SLAM: " << e.what() << std::endl;
  }
}

// ==================== Utility Functions ====================

std::string getUserInput() {
  std::string input;
  std::cout << "Enter command: ";
  std::getline(std::cin, input);
  return input;
}

int main(int argc, char* argv[]) {
  // Bind signal handler
  signal(SIGINT, signalHandler);

  // Create robot instance
  robot = std::make_unique<MagicRobot>();

  printHelp();
  std::cout << "Press any key to continue (ESC to exit)..." << std::endl;

  try {
    // Configure local IP address for direct network connection and initialize SDK
    std::string localIp = "192.168.55.10";
    if (!robot->Initialize(localIp)) {
      std::cerr << "Failed to initialize robot SDK" << std::endl;
      robot->Shutdown();
      return -1;
    }

    // Connect to robot
    auto status = robot->Connect();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to connect to robot, code: " << status.code
                << ", message: " << status.message << std::endl;
      robot->Shutdown();
      return -1;
    }

    std::cout << "Successfully connected to robot" << std::endl;

    // Set motion control level to high level
    status = robot->SetMotionControlLevel(ControllerLevel::HighLevel);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to set motion control level: " << status.message << std::endl;
      robot->Shutdown();
      return -1;
    }

    // Initialize SLAM navigation controller
    auto& slamNavController = robot->GetSlamNavController();
    if (!slamNavController.Initialize()) {
      std::cerr << "Failed to initialize SLAM navigation controller" << std::endl;
      robot->Disconnect();
      robot->Shutdown();
      return -1;
    }

    std::cout << "Successfully initialized SLAM navigation controller" << std::endl;

    // Main loop
    while (running.load()) {
      try {
        std::string strInput = getUserInput();

        // Split input parameters by space
        std::vector<std::string> parts;
        std::stringstream ss(strInput);
        std::string segment;
        while (std::getline(ss, segment, ' ')) {
          parts.push_back(segment);
        }

        if (parts.empty()) {
          std::this_thread::sleep_for(std::chrono::milliseconds(10));  // Brief delay
          continue;
        }

        // Parse parameters
        std::string key = parts[0];
        std::vector<std::string> args(parts.begin() + 1, parts.end());

        if (key == "\x1b") {  // ESC key
          break;
        }

        // 1. Preparation Functions
        if (key == "1") {
          // recovery stand
          recoveryStand();
        }
        // 2. Localization Functions
        // 2.1 Switch to localization mode
        else if (key == "2") {
          switchToLocalizationMode();
        }
        // 2.2 Initialize pose
        else if (key == "4") {
          double x = args.empty() ? 0.0 : std::stod(args[0]);
          double y = args.size() < 2 ? 0.0 : std::stod(args[1]);
          double yaw = args.size() < 3 ? 0.0 : std::stod(args[2]);
          std::cout << "input initial pose, x: " << x << ", y: " << y << ", yaw: " << yaw << std::endl;
          initializePose(x, y, yaw);
        }
        // 2.3 Get current localization information
        else if (key == "5") {
          getCurrentLocalizationInfo();
        }
        // 3. Navigation Functions
        // 3.1 Switch to navigation mode
        else if (key == "3") {
          switchToNavigationMode();
        }
        // 3.2 Set navigation target
        else if (key == "6") {
          double x = args.empty() ? 0.0 : std::stod(args[0]);
          double y = args.size() < 2 ? 0.0 : std::stod(args[1]);
          double yaw = args.size() < 3 ? 0.0 : std::stod(args[2]);
          std::cout << "input navigation target, x: " << x << ", y: " << y << ", yaw: " << yaw << std::endl;
          setNavigationTarget(x, y, yaw);
        }
        // 3.3 Pause navigation
        else if (key == "7") {
          pauseNavigation();
        }
        // 3.4 Resume navigation
        else if (key == "8") {
          resumeNavigation();
        }
        // 3.5 Cancel navigation
        else if (key == "9") {
          cancelNavigation();
        }
        // 3.6 Get navigation status
        else if (key == "0") {
          getNavigationStatus();
        }
        // 4. Odometry Functions
        // 4.1 Subscribe odometry stream
        else if (key == "C" || key == "c") {
          subscribeOdometryStream();
        }
        // 4.2 Unsubscribe odometry stream
        else if (key == "V" || key == "v") {
          unsubscribeOdometryStream();
        }
        // 5. Close Functions
        // 5.1 Close navigation
        else if (key == "L" || key == "l") {
          closeNavigation();
        }
        // 5.2 Close SLAM
        else if (key == "P" || key == "p") {
          closeSlam();
        }
        // Help
        else if (key == "?") {
          printHelp();
        } else {
          std::cout << "Unknown key: " << key << std::endl;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(10));  // Brief delay

      } catch (const std::exception& e) {
        std::cerr << "Exception occurred while processing user input: " << e.what() << std::endl;
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred during program execution: " << e.what() << std::endl;
    return -1;
  }

  // Clean up resources
  try {
    std::cout << "Clean up resources" << std::endl;

    // Close SLAM navigation controller
    auto& slamNavController = robot->GetSlamNavController();
    slamNavController.Shutdown();
    std::cout << "SLAM navigation controller closed" << std::endl;

    // Disconnect
    robot->Disconnect();
    std::cout << "Robot connection disconnected" << std::endl;

    // Shutdown robot
    robot->Shutdown();
    std::cout << "Robot shutdown" << std::endl;

  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while cleaning up resources: " << e.what() << std::endl;
  }

  return 0;
}
