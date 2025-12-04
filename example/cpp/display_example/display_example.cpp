#include "magic_robot.h"
#include "magic_sdk_version.h"

#include <termios.h>
#include <unistd.h>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <thread>

using namespace magic::dog;

// Global robot instance
std::unique_ptr<MagicRobot> robot = nullptr;

void signalHandler(int signum) {
  std::cout << "\nInterrupt signal (" << signum << ") received." << std::endl;
  if (robot) {
    robot->Shutdown();
  }
  exit(signum);
}

void print_help() {
  std::cout << "Key Function Demo Program\n"
            << std::endl;
  std::cout << "Key Function Description:" << std::endl;
  std::cout << "Face expression Functions:" << std::endl;
  std::cout << "  1        Function 1: Get all face expressions" << std::endl;
  std::cout << "  2        Function 2: Set face expression" << std::endl;
  std::cout << "  3        Function 3: Get current face expression" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "  ?        Function ?: Print help" << std::endl;
  std::cout << "  ESC      Exit program" << std::endl;
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

void get_all_face_expressions() {
  auto& display_controller = robot->GetDisplayController();

  std::vector<FaceExpression> face_expressions;
  auto status = display_controller.GetAllFaceExpressions(face_expressions);
  if (status.code != ErrorCode::OK) {
    std::cerr << "get all face expressions failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }

  for (auto& face_expression : face_expressions) {
    std::cout << "Face Expression ID: " << face_expression.id << std::endl;
    std::cout << "Face Expression Name: " << face_expression.name << std::endl;
    std::cout << "Face Expression Description: " << face_expression.description << std::endl;
    std::cout << std::endl;
  }
}

void get_current_face_expression() {
  auto& display_controller = robot->GetDisplayController();

  FaceExpression face_expression;
  auto status = display_controller.GetFaceExpression(face_expression);
  if (status.code != ErrorCode::OK) {
    std::cerr << "get current face expression failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }

  std::cout << "Face Expression ID: " << face_expression.id << std::endl;
  std::cout << "Face Expression Name: " << face_expression.name << std::endl;
  std::cout << "Face Expression Description: " << face_expression.description << std::endl;
}

void set_face_expression(int face_expression_id) {
  auto& display_controller = robot->GetDisplayController();

  auto status = display_controller.SetFaceExpression(face_expression_id);
  if (status.code != ErrorCode::OK) {
    std::cerr << "set face expression failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "set face expression success" << std::endl;
}

int main(int argc, char* argv[]) {
  // Bind SIGINT (Ctrl+C)
  signal(SIGINT, signalHandler);

  print_help();

  std::string local_ip = "192.168.55.10";
  robot = std::make_unique<MagicRobot>();

  // Configure local IP address for direct network connection and initialize SDK
  if (!robot->Initialize(local_ip)) {
    std::cerr << "robot sdk initialize failed." << std::endl;
    robot->Shutdown();
    return -1;
  }

  // Connect to robot
  auto status = robot->Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "connect robot failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    robot->Shutdown();
    return -1;
  }

  std::cout << "Press any key to continue (ESC to exit)..." << std::endl;

  // Wait for user input
  while (true) {
    int key = getch();
    if (key == 27) {  // ESC key
      break;
    }

    std::cout << "Key ASCII: " << key << ", Character: " << static_cast<char>(key) << std::endl;

    switch (key) {
      case '1':
        get_all_face_expressions();
        break;
      case '2':{
        int face_expression_id = 16;
        std::cout << "Please input face expression id: ";
        std::cin >> face_expression_id;
        set_face_expression(face_expression_id);
        std::cin.ignore();
      } 
        break;
      case '3':
        get_current_face_expression();
        break;
      case '?':
        print_help();
        break;
      default:
        std::cout << "Unknown key: " << key << std::endl;
        break;
    }

    // Sleep 10ms, equivalent to usleep(10000)
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }

  // Disconnect from robot
  status = robot->Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "disconnect robot failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    robot->Shutdown();
    return -1;
  }

  std::cout << "disconnect robot success" << std::endl;

  robot->Shutdown();
  std::cout << "robot shutdown" << std::endl;

  return 0;
}