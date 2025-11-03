#include "magic_robot.h"
#include "magic_sdk_version.h"

#include <unistd.h>
#include <csignal>
#include <iostream>
#include <memory>
#include <chrono>
#include <thread>
#include <cstdlib>

using namespace magic::dog;

// Global robot instance
std::unique_ptr<MagicRobot> robot = nullptr;

void signalHandler(int signum) {
    std::cout << "Interrupt signal (" << signum << ") received." << std::endl;
    if (robot) {
        robot->Shutdown();
    }
    exit(signum);
}

int main() {
    // Bind SIGINT (Ctrl+C)
    signal(SIGINT, signalHandler);
    
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
    
    std::this_thread::sleep_for(std::chrono::seconds(5));
    
    auto& monitor = robot->GetStateMonitor();
    
    RobotState robot_state;
    status = monitor.GetCurrentState(robot_state);
    if (status.code != ErrorCode::OK) {
        std::cerr << "Get current state failed, code: " << status.code 
                  << ", message: " << status.message << std::endl;
        robot->Shutdown();
        return -1;
    }
    
    std::cout << "Health: " << robot_state.bms_data.battery_health
              << ", Percentage: " << robot_state.bms_data.battery_percentage
              << ", State: " << static_cast<int>(robot_state.bms_data.battery_state)
              << ", Power supply status: " << static_cast<int>(robot_state.bms_data.power_supply_status)
              << std::endl;
    
    auto& faults = robot_state.faults;
    for (const auto& fault : faults) {
        std::cout << "Code: " << fault.error_code
                  << ", Message: " << fault.error_message << std::endl;
    }
    
    // Disconnect from robot
    status = robot->Disconnect();
    if (status.code != ErrorCode::OK) {
        std::cerr << "Disconnect robot failed, code: " << status.code 
                  << ", message: " << status.message << std::endl;
    } else {
        std::cout << "Robot disconnected" << std::endl;
    }
    
    robot->Shutdown();
    std::cout << "Robot shutdown" << std::endl;
    
    std::cout << "\nExample program execution completed!" << std::endl;
    
    return 0;
}