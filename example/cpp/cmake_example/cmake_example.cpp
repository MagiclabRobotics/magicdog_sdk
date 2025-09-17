#include "magic_robot.h"

#include <termios.h>
#include <unistd.h>
#include <csignal>

#include <iostream>
#include <thread>

using namespace magic::dog;

magic::dog::MagicRobot robot;
std::atomic<bool> is_running(true);

std::atomic<float> left_x_axis(0.0);
std::atomic<float> left_y_axis(0.0);
std::atomic<float> right_x_axis(0.0);
std::atomic<float> right_y_axis(0.0);

void signalHandler(int signum) {
  std::cout << "Interrupt signal (" << signum << ") received.\n";
  is_running.store(false);

  robot.Shutdown();
  // Exit process
  exit(signum);
}

void print_help(const char* prog_name) {
  std::cout << "Key Function Demo Program\n\n";
  std::cout << "Usage: " << prog_name << "\n";
  std::cout << "Key Function Description:\n";
  std::cout << "  ESC      Exit program\n";
  std::cout << "  1        Function 1: Position control standing\n";
  std::cout << "  2        Function 2: Force control standing\n";
  std::cout << "  3        Function 3: Execute trick - lie down\n";
  std::cout << "  w        Function 4: Move forward\n";
  std::cout << "  a        Function 5: Move left\n";
  std::cout << "  x        Function 6: Move backward\n";
  std::cout << "  s        Function 7: Stop movement\n";
  std::cout << "  d        Function 7: Move right\n";
  std::cout << "  t        Function 8: Turn left\n";
  std::cout << "  g        Function 9: Turn right\n";
}

int getch() {
  struct termios oldt, newt;
  int ch;
  tcgetattr(STDIN_FILENO, &oldt);  // Get current terminal settings
  newt = oldt;
  newt.c_lflag &= ~(ICANON | ECHO);  // Disable buffering and echo
  tcsetattr(STDIN_FILENO, TCSANOW, &newt);
  ch = getchar();                           // Read key press
  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);  // Restore settings
  return ch;
}

void RecoveryStand() {
  // Get high level motion controller
  auto& controller = robot.GetHighLevelMotionController();

  // Set gait
  auto status = controller.SetGait(GaitMode::GAIT_STAND_R);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Set robot gait failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
}

void BalanceStand() {
  // Get high level motion controller
  auto& controller = robot.GetHighLevelMotionController();

  // Set posture display gait
  auto status = controller.SetGait(GaitMode::GAIT_STAND_B);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Set robot gait failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "Robot gait set to GAIT_BALANCE_STAND successfully." << std::endl;
}

void ExecuteTrick() {
  // Get high level motion controller
  auto& controller = robot.GetHighLevelMotionController();

  // Execute trick
  auto status = controller.ExecuteTrick(TrickAction::ACTION_LIE_DOWN);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Execute robot trick failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "Robot trick executed successfully." << std::endl;
}

void JoyStickCommand(float left_x_axis,
                     float left_y_axis,
                     float right_x_axis,
                     float right_y_axis) {
  ::left_x_axis.store(left_x_axis);
  ::left_y_axis.store(left_y_axis);
  ::right_x_axis.store(right_x_axis);
  ::right_y_axis.store(right_y_axis);
}

void JoyThread() {
  auto& controller = robot.GetHighLevelMotionController();
  while (is_running.load()) {
    JoystickCommand joy_command;
    joy_command.left_x_axis = left_x_axis;
    joy_command.left_y_axis = left_y_axis;
    joy_command.right_x_axis = right_x_axis;
    joy_command.right_y_axis = right_y_axis;
    auto status = controller.SendJoyStickCommand(joy_command);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Send joystick command failed"
                << ", code: " << status.code
                << ", message: " << status.message << std::endl;
    }
    usleep(10000);
  }
}

int main(int argc, char* argv[]) {
  // 绑定 SIGINT（Ctrl+C）
  signal(SIGINT, signalHandler);

  std::string local_ip = "192.168.54.111";
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

  // Switch motion control level to high level controller, default is high level controller
  status = robot.SetMotionControlLevel(ControllerLevel::HighLevel);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Switch robot motion control level failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  std::thread joy_thread(JoyThread);

  print_help(argv[0]);

  std::cout << "Press any key to continue (ESC to exit)..."
            << std::endl;

  auto change_gait_to_down_climb_stairs = [](auto& robot) -> bool {
    GaitMode current_gait = GaitMode::GAIT_PASSIVE;
    auto status = robot.GetHighLevelMotionController().GetGait(current_gait);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Get robot gait failed"
                << ", code: " << status.code
                << ", message: " << status.message << std::endl;
      return false;
    }
    if (current_gait != GaitMode::GAIT_DOWN_CLIMB_STAIRS) {
      status = robot.GetHighLevelMotionController().SetGait(GaitMode::GAIT_DOWN_CLIMB_STAIRS);
      if (status.code != ErrorCode::OK) {
        std::cerr << "Set robot gait failed"
                  << ", code: " << status.code
                  << ", message: " << status.message << std::endl;
        return false;
      }
    } else {
      return true;
    }

    status = robot.GetHighLevelMotionController().GetGait(current_gait);
    if (status.code != ErrorCode::OK) {
      std::cerr << "Get robot gait failed"
                << ", code: " << status.code
                << ", message: " << status.message << std::endl;
      return false;
    }
    while (current_gait != GaitMode::GAIT_DOWN_CLIMB_STAIRS) {
      usleep(10000);
      status = robot.GetHighLevelMotionController().GetGait(current_gait);
      if (status.code != ErrorCode::OK) {
        std::cerr << "Get robot gait failed"
                  << ", code: " << status.code
                  << ", message: " << status.message << std::endl;
        return false;
      }
    }
    return true;
  };
  // Wait for user input
  while (1) {
    int key = getch();
    if (key == 27)
      break;  // ESC键ASCII码为27

    std::cout << "Key ASCII: " << key << ", Character: " << static_cast<char>(key) << std::endl;
    switch (key) {
      case '1': {
        RecoveryStand();
        break;
      }
      case '2': {
        BalanceStand();
        break;
      }
      case '3': {
        ExecuteTrick();
        break;
      }
      case 'w': {
        if (!change_gait_to_down_climb_stairs(robot)) {
          std::cerr << "Change robot gait to down climb stairs failed" << std::endl;
          break;
        }
        JoyStickCommand(0.0, 1.0, 0.0, 0.0);  // Forward
        break;
      }
      case 'a': {
        if (!change_gait_to_down_climb_stairs(robot)) {
          std::cerr << "Change robot gait to down climb stairs failed" << std::endl;
          break;
        }
        JoyStickCommand(-1.0, 0.0, 0.0, 0.0);  // Left
        break;
      }
      case 'x': {
        if (!change_gait_to_down_climb_stairs(robot)) {
          std::cerr << "Change robot gait to down climb stairs failed" << std::endl;
          break;
        }
        JoyStickCommand(0.0, -1.0, 0.0, 0.0);  // Backward
        break;
      }
      case 'd': {
        if (!change_gait_to_down_climb_stairs(robot)) {
          std::cerr << "Change robot gait to down climb stairs failed" << std::endl;
          break;
        }
        JoyStickCommand(1.0, 0.0, 0.0, 0.0);  // Right
        break;
      }
      case 't': {
        if (!change_gait_to_down_climb_stairs(robot)) {
          std::cerr << "Change robot gait to down climb stairs failed" << std::endl;
          break;
        }
        JoyStickCommand(0.0, 0.0, -1.0, 0.0);  // Turn left
        break;
      }
      case 'g': {
        if (!change_gait_to_down_climb_stairs(robot)) {
          std::cerr << "Change robot gait to down climb stairs failed" << std::endl;
          break;
        }
        JoyStickCommand(0.0, 0.0, 1.0, 0.0);  // Turn right
        break;
      }
      case 's': {
        if (!change_gait_to_down_climb_stairs(robot)) {
          std::cerr << "Change robot gait to down climb stairs failed" << std::endl;
          break;
        }
        JoyStickCommand(0.0, 0.0, 0.0, 0.0);  // Stop
        break;
      }
      default:
        std::cout << "Unknown key: " << key << std::endl;
        break;
    }

    usleep(10000);
  }

  is_running.store(false);
  joy_thread.join();

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