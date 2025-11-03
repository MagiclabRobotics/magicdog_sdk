#include "magic_robot.h"
#include "magic_sdk_version.h"

#include <fcntl.h>
#include <signal.h>
#include <termios.h>
#include <unistd.h>
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
  std::cout << "SLAM Function Demo Program" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "preparation Functions:" << std::endl;
  std::cout << "  1        Function 1: Recovery stand" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "SLAM Functions:" << std::endl;
  std::cout << "  2        Function 2: Start mapping" << std::endl;
  std::cout << "  3        Function 3: Cancel mapping" << std::endl;
  std::cout << "  4        Function 4: Save map" << std::endl;
  std::cout << "  5        Function 5: Load map" << std::endl;
  std::cout << "  6        Function 6: Delete map" << std::endl;
  std::cout << "  7        Function 7: Get all map information and save map image as PGM file" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Joystick Functions:" << std::endl;
  std::cout << "  W        Function W: forward" << std::endl;
  std::cout << "  A        Function A: backward" << std::endl;
  std::cout << "  S        Function S: left" << std::endl;
  std::cout << "  D        Function D: right" << std::endl;
  std::cout << "  T        Function T: turn left" << std::endl;
  std::cout << "  G        Function G: turn right" << std::endl;
  std::cout << "  X        Function X: stop" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Close Functions:" << std::endl;
  std::cout << "  P        Function P: Close SLAM" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "  ?        Function H: Print help" << std::endl;
  std::cout << "  ESC      Exit program" << std::endl;
}

// ==================== SLAM Functions ====================

void loadMap(const std::string& mapToLoad) {
  try {
    if (mapToLoad.empty()) {
      std::cerr << "Map to load is not provided" << std::endl;
      return;
    }

    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    std::cout << "Loading map: " << mapToLoad << std::endl;
    controller.LoadMap(mapToLoad);
    std::cout << "Successfully loaded map: " << mapToLoad << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while loading map: " << e.what() << std::endl;
  }
}

void startMapping() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Start mapping
    auto status = controller.StartMapping();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to start mapping, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    current_slam_mode = "MAPPING";
    std::cout << "Successfully started mapping" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while starting mapping: " << e.what() << std::endl;
  }
}

void cancelMapping() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Cancel mapping
    auto status = controller.CancelMapping();
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to cancel mapping, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully cancelled mapping" << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while cancelling mapping: " << e.what() << std::endl;
  }
}

void saveMap() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Check if in mapping mode
    if (current_slam_mode != "MAPPING") {
      std::cout << "Warning: Currently not in mapping mode, may not be able to save map" << std::endl;
    }

    // Generate map name with timestamp
    auto now = std::chrono::system_clock::now();
    auto timestamp = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();
    std::string mapName = "map_" + std::to_string(timestamp);

    std::cout << "Saving map: " << mapName << std::endl;

    // Save map
    auto status = controller.SaveMap(mapName);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to save map, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully saved map: " << mapName << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while saving map: " << e.what() << std::endl;
  }
}

void deleteMap(const std::string& mapToDelete) {
  try {
    if (mapToDelete.empty()) {
      std::cerr << "Map to delete is not provided" << std::endl;
      return;
    }

    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    std::cout << "Deleting map: " << mapToDelete << std::endl;

    // Delete map
    auto status = controller.DeleteMap(mapToDelete);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to delete map, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully deleted map: " << mapToDelete << std::endl;
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while deleting map: " << e.what() << std::endl;
  }
}

void getAllMapInfo() {
  try {
    // Get SLAM navigation controller
    auto& controller = robot->GetSlamNavController();

    // Get all map information
    AllMapInfo allMapInfo;
    auto status = controller.GetAllMapInfo(allMapInfo);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to get map information, code: " << status.code
                << ", message: " << status.message << std::endl;
      return;
    }

    std::cout << "Successfully retrieved map information" << std::endl;
    std::cout << "Current map: " << allMapInfo.current_map_name << std::endl;
    std::cout << "Total maps: " << allMapInfo.map_infos.size() << std::endl;

    if (!allMapInfo.map_infos.empty()) {
      std::cout << "Map details:" << std::endl;
      for (size_t i = 0; i < allMapInfo.map_infos.size(); ++i) {
        const auto& mapInfo = allMapInfo.map_infos[i];
        std::cout << "  Map " << (i + 1) << ": " << mapInfo.map_name << std::endl;
        std::cout << "    Origin: ["
                  << mapInfo.map_meta_data.origin.position[0] << ", "
                  << mapInfo.map_meta_data.origin.position[1] << ", "
                  << mapInfo.map_meta_data.origin.position[2] << "]" << std::endl;
        std::cout << "    Orientation: ["
                  << mapInfo.map_meta_data.origin.orientation[0] << ", "
                  << mapInfo.map_meta_data.origin.orientation[1] << ", "
                  << mapInfo.map_meta_data.origin.orientation[2] << "]" << std::endl;
        std::cout << "    Resolution: " << mapInfo.map_meta_data.resolution << " m/pixel" << std::endl;
        std::cout << "    Size: " << mapInfo.map_meta_data.map_image_data.width
                  << " x " << mapInfo.map_meta_data.map_image_data.height << std::endl;
        std::cout << "    Max gray value: " << mapInfo.map_meta_data.map_image_data.max_gray_value << std::endl;
        std::cout << "    Image type: " << mapInfo.map_meta_data.map_image_data.type << std::endl;
      }
    } else {
      std::cout << "No available maps" << std::endl;
    }
  } catch (const std::exception& e) {
    std::cerr << "Exception occurred while getting map information: " << e.what() << std::endl;
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

// Switch gait to down climb stairs mode
bool changeGaitToDownClimbStairs() {
  try {
    auto& highController = robot->GetHighLevelMotionController();
    GaitMode currentGait;
    auto status = highController.GetGait(currentGait);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to get gait: " << status.message << std::endl;
      return false;
    }

    if (currentGait != GaitMode::GAIT_DOWN_CLIMB_STAIRS) {
      auto status = highController.SetGait(GaitMode::GAIT_DOWN_CLIMB_STAIRS);
      if (status.code != ErrorCode::OK) {
        std::cerr << "Failed to set down climb stairs gait: " << status.message << std::endl;
        return false;
      }

      // Wait for gait switch to complete
      while (currentGait != GaitMode::GAIT_DOWN_CLIMB_STAIRS) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        status = highController.GetGait(currentGait);
        if (status.code != ErrorCode::OK) {
          std::cerr << "Failed to get gait during transition: " << status.message << std::endl;
          return false;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
      }
    }

    std::cout << "Gait changed to down climb stairs" << std::endl;
    return true;
  } catch (const std::exception& e) {
    std::cerr << "Error changing gait: " << e.what() << std::endl;
    return false;
  }
}

void sendJoystickCommand(double leftX, double leftY, double rightX, double rightY) {
  if (!changeGaitToDownClimbStairs()) {
    return;
  }

  auto& highController = robot->GetHighLevelMotionController();
  JoystickCommand joyCommand;
  joyCommand.left_x_axis = leftX;
  joyCommand.left_y_axis = leftY;
  joyCommand.right_x_axis = rightX;
  joyCommand.right_y_axis = rightY;

  auto status = highController.SendJoyStickCommand(joyCommand);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Failed to send joystick command: " << status.message << std::endl;
  }
}

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

// Get single character input (no echo)
char getch() {
  char ch;
  struct termios oldt, newt;

  tcgetattr(STDIN_FILENO, &oldt);
  newt = oldt;
  newt.c_lflag &= ~(ICANON | ECHO);
  tcsetattr(STDIN_FILENO, TCSANOW, &newt);

  ch = getchar();

  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);

  std::cout << "Received character: " << ch << std::endl;
  return ch;
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
        std::cout << "Enter command: ";
        char key = getch();
        if (key == 27) {  // ESC key
          break;
        }
        // 1. Preparation Functions
        // 1.1 Recovery stand
        if (key == '1') {
          recoveryStand();
        }
        // 2. SLAM Functions
        // 2.1 Start mapping
        else if (key == '2') {
          startMapping();
        }
        // 2.2 Cancel mapping
        else if (key == '3') {
          cancelMapping();
        }
        // 2.3 Save map
        else if (key == '4') {
          saveMap();
        }
        // 2.4 Load map
        else if (key == '5') {
          std::string strInput;
          std::cout << "Enter parameters: ";
          std::getline(std::cin, strInput);
          if (strInput.empty()) {
            continue;
          }
          // Split input parameters by space
          std::vector<std::string> parts;
          std::stringstream ss(strInput);
          std::string segment;
          while (std::getline(ss, segment, ' ')) {
            parts.push_back(segment);
          }
          // Parse parameters
          std::string mapToLoad = parts.empty() ? "" : parts[0];
          loadMap(mapToLoad);
        }
        // 2.5 Delete map
        else if (key == '6') {
          std::string strInput;
          std::cout << "Enter parameters: ";
          std::getline(std::cin, strInput);
          if (strInput.empty()) {
            continue;
          }
          // Split input parameters by space
          std::vector<std::string> parts;
          std::stringstream ss(strInput);
          std::string segment;
          while (std::getline(ss, segment, ' ')) {
            parts.push_back(segment);
          }
          // Parse parameters
          std::string mapToDelete = parts.empty() ? "" : parts[0];
          deleteMap(mapToDelete);
        }
        // 2.6 Get all map information
        else if (key == '7') {
          getAllMapInfo();
        }
        // 4. Joystick Functions
        // 4.1 Move forward
        else if (key == 'w' || key == 'W') {
          sendJoystickCommand(0.0, 1.0, 0.0, 0.0);  // Move forward
        }
        // 4.2 Move backward
        else if (key == 's' || key == 'S') {
          sendJoystickCommand(0.0, -1.0, 0.0, 0.0);  // Move backward
        }
        // 4.3 Move left
        else if (key == 'a' || key == 'A') {
          sendJoystickCommand(-1.0, 0.0, 0.0, 0.0);  // Move left
        }
        // 4.4 Move right
        else if (key == 'd' || key == 'D') {
          sendJoystickCommand(1.0, 0.0, 0.0, 0.0);  // Move right
        }
        // 4.5 Turn left
        else if (key == 't' || key == 'T') {
          sendJoystickCommand(0.0, 0.0, -1.0, 0.0);  // Turn left
        }
        // 4.6 Turn right
        else if (key == 'g' || key == 'G') {
          sendJoystickCommand(0.0, 0.0, 1.0, 0.0);  // Turn right
        }
        // 4.7 Stop movement
        else if (key == 'x' || key == 'X') {
          sendJoystickCommand(0.0, 0.0, 0.0, 0.0);  // Stop movement
        }
        // 5. Close Functions
        // 5.1 Close SLAM
        else if (key == 'p' || key == 'P') {
          closeSlam();
        }
        // Help
        else if (key == '?' || key == 'h' || key == 'H') {
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
