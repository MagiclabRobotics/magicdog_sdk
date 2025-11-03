#include "magic_robot.h"
#include "magic_sdk_version.h"

#include <termios.h>
#include <unistd.h>
#include <atomic>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <thread>

using namespace magic::dog;

// Global variables
std::unique_ptr<MagicRobot> robot = nullptr;
std::atomic<bool> running(true);

void signalHandler(int signum) {
  std::cout << "\nInterrupt signal (" << signum << ") received." << std::endl;
  running = false;
  if (robot) {
    robot->Shutdown();
  }
  exit(signum);
}

void print_help() {
  std::cout << "Key function description:" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Gait and Trick Functions:" << std::endl;
  std::cout << "  1        Function 1: Recovery Stand" << std::endl;
  std::cout << "  2        Function 2: Force control standing" << std::endl;
  std::cout << "  3        Function 3: Execute trick - lie down" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Joystick Functions:" << std::endl;
  std::cout << "  w        Move forward" << std::endl;
  std::cout << "  a        Move left" << std::endl;
  std::cout << "  s        Move backward" << std::endl;
  std::cout << "  d        Move right" << std::endl;
  std::cout << "  t        Turn left" << std::endl;
  std::cout << "  g        Turn right" << std::endl;
  std::cout << "  x        Stop movement" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "  ?        Function ?: Print help" << std::endl;
  std::cout << "  ESC      Exit program" << std::endl;
}

int getch() {
  struct termios oldt, newt;
  int ch;
  tcgetattr(STDIN_FILENO, &oldt);
  newt = oldt;
  newt.c_lflag &= ~(ICANON | ECHO);
  tcsetattr(STDIN_FILENO, TCSANOW, &newt);
  ch = getchar();
  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
  return ch;
}

// Recovery Stand
void recovery_stand() {
  try {
    auto& high_controller = robot->GetHighLevelMotionController();
    auto status = high_controller.SetGait(GaitMode::GAIT_STAND_R);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to set position control standing: " << status.message << std::endl;
    } else {
      std::cout << "Robot set to position control standing" << std::endl;
    }
  } catch (const std::exception& e) {
    std::cerr << "Error executing position control standing: " << e.what() << std::endl;
  }
}

// Force control standing
void balance_stand() {
  try {
    auto& high_controller = robot->GetHighLevelMotionController();
    auto status = high_controller.SetGait(GaitMode::GAIT_STAND_B);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to set force control standing: " << status.message << std::endl;
    } else {
      std::cout << "Robot set to force control standing" << std::endl;
    }
  } catch (const std::exception& e) {
    std::cerr << "Error executing force control standing: " << e.what() << std::endl;
  }
}

// Execute trick
void execute_trick(const std::string& cmd) {
  try {
    TrickAction action;
    if (cmd == "102") {
      action = TrickAction::ACTION_LIE_DOWN;
    } else if (cmd == "103") {
      action = TrickAction::ACTION_RECOVERY_STAND;
    } else if (cmd == "33") {
      action = TrickAction::ACTION_SHAKE_HEAD;
    } else {
      action = TrickAction::ACTION_NONE;
    }

    auto& high_controller = robot->GetHighLevelMotionController();
    auto status = high_controller.ExecuteTrick(action);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to execute trick: " << status.message << std::endl;
    } else {
      std::cout << "Trick executed successfully" << std::endl;
    }
  } catch (const std::exception& e) {
    std::cerr << "Error executing trick: " << e.what() << std::endl;
  }
}

// Switch gait to down climb stairs mode
bool change_gait_to_down_climb_stairs() {
  try {
    GaitMode current_gait;
    auto& high_controller = robot->GetHighLevelMotionController();
    auto status = high_controller.GetGait(current_gait);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Failed to get current gait: " << status.message << std::endl;
      return false;
    }

    if (current_gait != GaitMode::GAIT_DOWN_CLIMB_STAIRS) {
      status = high_controller.SetGait(GaitMode::GAIT_DOWN_CLIMB_STAIRS);
      if (status.code != ErrorCode::OK) {
        std::cerr << "Failed to set down climb stairs gait: " << status.message << std::endl;
        return false;
      }

      // Wait for gait switch to complete
      while (current_gait != GaitMode::GAIT_DOWN_CLIMB_STAIRS) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        status = high_controller.GetGait(current_gait);
        if (status.code != ErrorCode::OK) {
          std::cerr << "Failed to get gait during transition: " << status.message << std::endl;
          return false;
        }
      }
    }
    std::cout << "Gait changed to down climb stairs" << std::endl;
    return true;
  } catch (const std::exception& e) {
    std::cerr << "Error changing gait: " << e.what() << std::endl;
    return false;
  }
}

void send_joystick_command(float left_x, float left_y, float right_x, float right_y) {
  if (!change_gait_to_down_climb_stairs()) {
    return;
  }

  JoystickCommand joy_command;
  joy_command.left_x_axis = left_x;
  joy_command.left_y_axis = left_y;
  joy_command.right_x_axis = right_x;
  joy_command.right_y_axis = right_y;

  auto& high_controller = robot->GetHighLevelMotionController();
  auto status = high_controller.SendJoyStickCommand(joy_command);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Failed to send joystick command: " << status.message << std::endl;
  }
}

int main(int argc, char* argv[]) {
  print_help();

  std::cout << "MagicDog SDK C++ Example Program" << std::endl;

  robot = std::make_unique<MagicRobot>();
  if (!robot->Initialize("192.168.55.10")) {
    std::cerr << "Initialization failed" << std::endl;
    return -1;
  }

  auto status = robot->Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Connection failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    robot->Shutdown();
    return -1;
  }

  // Set motion control level to high level
  status = robot->SetMotionControlLevel(ControllerLevel::HighLevel);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Failed to set motion control level: " << status.message << std::endl;
    robot->Shutdown();
    return -1;
  }

  std::cout << "Program started, please use keys to control robot..." << std::endl;

  while (running) {
    std::cout << "Enter command: ";
    int key = getch();
    if (key == 27) {  // ESC key
      break;
    }

    if (key == '3') {
      std::string str_input;
      std::cout << "Enter parameters: ";
      std::getline(std::cin, str_input);
      if (str_input.empty()) {
        continue;
      }

      // Parse parameters
      std::string cmd = str_input.substr(0, str_input.find(' '));
      if (cmd.empty()) {
        cmd = "102";
      }
      std::cout << "Execute trick: " << cmd << std::endl;
      execute_trick(cmd);
      continue;
    }

    switch (key) {
      case '1':
        recovery_stand();
        break;
      case '2':
        balance_stand();
        break;
      case 'w':
        send_joystick_command(0.0, 1.0, 0.0, 0.0);
        break;
      case 's':
        send_joystick_command(0.0, -1.0, 0.0, 0.0);
        break;
      case 'a':
        send_joystick_command(-1.0, 0.0, 0.0, 0.0);
        break;
      case 'd':
        send_joystick_command(1.0, 0.0, 0.0, 0.0);
        break;
      case 't':
        send_joystick_command(0.0, 0.0, -1.0, 0.0);
        break;
      case 'g':
        send_joystick_command(0.0, 0.0, 1.0, 0.0);
        break;
      case 'x':
        send_joystick_command(0.0, 0.0, 0.0, 0.0);
        break;
      case '?':
        print_help();
        break;
      default:
        std::cout << "Unknown key: " << key << std::endl;
        break;
    }
  }

  // Disconnect from robot
  status = robot->Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Disconnect robot failed, code: " << status.code
              << ", message: " << status.message << std::endl;
  } else {
    std::cout << "Robot disconnected" << std::endl;
  }

  // Shutdown robot
  robot->Shutdown();
  std::cout << "Robot shutdown" << std::endl;

  return 0;
}