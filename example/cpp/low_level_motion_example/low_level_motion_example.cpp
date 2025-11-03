#include "magic_robot.h"
#include "magic_sdk_version.h"
#include "magic_type.h"

#include <unistd.h>
#include <csignal>
#include <iostream>
#include <memory>
#include <mutex>
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
    
    std::cout << "Setting motion control level to high level" << std::endl;
    status = robot->SetMotionControlLevel(ControllerLevel::HighLevel);
    if (status.code != ErrorCode::OK) {
        std::cerr << "Failed to set motion control level: " << status.message << std::endl;
        robot->Shutdown();
        return -1;
    }
    
    std::cout << "Getting high level motion controller" << std::endl;
    auto& high_controller = robot->GetHighLevelMotionController();
    
    std::cout << "Setting motion mode to passive" << std::endl;
    status = high_controller.SetGait(GaitMode::GAIT_PASSIVE);
    if (status.code != ErrorCode::OK) {
        std::cerr << "Failed to set motion mode: " << status.message << std::endl;
        robot->Shutdown();
        return -1;
    }
    
    std::cout << "Waiting for motion mode to change to passive" << std::endl;
    GaitMode current_mode = GaitMode::GAIT_DEFAULT;
    while (current_mode != GaitMode::GAIT_PASSIVE) {
        status = high_controller.GetGait(current_mode);
        if (status.code != ErrorCode::OK) {
            std::cerr << "Failed to get gait: " << status.message << std::endl;
            robot->Shutdown();
            return -1;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    std::cout << "Setting motion control level to low level" << std::endl;
    status = robot->SetMotionControlLevel(ControllerLevel::LowLevel);
    if (status.code != ErrorCode::OK) {
        std::cerr << "Failed to set motion control level: " << status.message << std::endl;
        robot->Shutdown();
        return -1;
    }
    
    std::cout << "Waiting for motion mode to change to low level" << std::endl;
    while (current_mode != GaitMode::GAIT_LOWLEVL_SDK) {
        status = high_controller.GetGait(current_mode);
        if (status.code != ErrorCode::OK) {
            std::cerr << "Failed to get gait: " << status.message << std::endl;
            robot->Shutdown();
            return -1;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    std::cout << "Getting low level motion controller" << std::endl;
    auto& low_controller = robot->GetLowLevelMotionController();
    
    bool is_had_receive_leg_state = false;
    std::mutex mut;
    LegState receive_state;
    int count = 0;
    
    auto leg_state_callback = [&](const std::shared_ptr<LegState> msg) {
        if (!is_had_receive_leg_state) {
            std::lock_guard<std::mutex> guard(mut);
            is_had_receive_leg_state = true;
            receive_state = *msg;
        }
        if (count % 1000 == 0) {
            std::cout << "Received leg state data." << std::endl;
        }
        count++;
    };
    
    low_controller.SubscribeLegState(leg_state_callback);
    
    std::cout << "Waiting to receive leg state data" << std::endl;
    while (!is_had_receive_leg_state) {
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }
    
    std::this_thread::sleep_for(std::chrono::seconds(10));
    
    // Joint angles for different poses
    double j1[] = {0.0000, 1.0477, -2.0944};  // base height 0.2
    double j2[] = {0.0000, 0.7231, -1.4455};  // base height 0.3
    
    // Get initial joint positions
    double initial_q[12] = {
        receive_state.state[0].q, receive_state.state[1].q, receive_state.state[2].q,
        receive_state.state[3].q, receive_state.state[4].q, receive_state.state[5].q,
        receive_state.state[6].q, receive_state.state[7].q, receive_state.state[8].q,
        receive_state.state[9].q, receive_state.state[10].q, receive_state.state[11].q
    };
    
    LegJointCommand command;
    int cnt = 0;
    
    std::cout << "Starting joint control loop..." << std::endl;
    
    while (true) {
        double t;
        
        if (cnt < 1000) {
            t = 1.0 * cnt / 1000.0;
            t = std::min(std::max(t, 0.0), 1.0);
            for (int i = 0; i < 12; ++i) {
                command.cmd[i].q_des = (1 - t) * initial_q[i] + t * j1[i % 3];
            }
        } else if (cnt < 1750) {
            t = 1.0 * (cnt - 1000) / 700.0;
            t = std::min(std::max(t, 0.0), 1.0);
            for (int i = 0; i < 12; ++i) {
                command.cmd[i].q_des = (1 - t) * j1[i % 3] + t * j2[i % 3];
            }
        } else if (cnt < 2500) {
            t = 1.0 * (cnt - 1750) / 700.0;
            t = std::min(std::max(t, 0.0), 1.0);
            for (int i = 0; i < 12; ++i) {
                command.cmd[i].q_des = (1 - t) * j2[i % 3] + t * j1[i % 3];
            }
        } else {
            cnt = 1000;
        }
        
        // Set control gains
        for (int i = 0; i < 12; ++i) {
            command.cmd[i].kp = 100;
            command.cmd[i].kd = 1.2;
        }
        
        low_controller.PublishLegCommand(command);
        std::this_thread::sleep_for(std::chrono::milliseconds(2));
        cnt++;
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