#include "magic_robot.h"

#include <unistd.h>
#include <csignal>

#include <iostream>

using namespace magic::dog;

magic::dog::MagicRobot robot;

void signalHandler(int signum) {
  std::cout << "Interrupt signal (" << signum << ") received.\n";

  robot.Shutdown();
  // Exit process
  exit(signum);
}

int main() {
  // Bind SIGINT (Ctrl+C)
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
  // Wait 10s
  usleep(10000000);

  auto& monitor = robot.GetStateMonitor();

  auto state = monitor.GetCurrentState();

  std::cout << "Health: " << state.bms_data.battery_health
            << ", Percentage: " << state.bms_data.battery_percentage
            << ", State: " << std::to_string((int8_t)state.bms_data.battery_state)
            << ", Power supply status: " << std::to_string((int8_t)state.bms_data.power_supply_status)
            << std::endl;

  auto& faults = state.faults;
  for (auto& [code, msg] : faults) {
    std::cout << "Code: " << std::to_string(code)
              << ", Message: " << msg;
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