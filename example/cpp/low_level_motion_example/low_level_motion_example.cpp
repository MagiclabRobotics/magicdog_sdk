#include "magic_robot.h"
#include "magic_type.h"

#include <unistd.h>
#include <csignal>

#include <iostream>
#include <mutex>

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

  status = robot.SetMotionControlLevel(ControllerLevel::HighLevel);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Switch robot motion control level to HighLevel failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  auto& high_controller = robot.GetHighLevelMotionController();
  status = high_controller.SetGait(magic::dog::GaitMode::GAIT_PASSIVE);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Switch robot motion gait failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  GaitMode current_mode = GaitMode::GAIT_DEFAULT;
  while (current_mode != GaitMode::GAIT_PASSIVE) {
    high_controller.GetGait(current_mode);
    usleep(100000);
  }

  sleep(2);

  // Switch motion control level to low level controller, default is high level controller
  status = robot.SetMotionControlLevel(ControllerLevel::LowLevel);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Switch robot motion control level failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  while (current_mode != GaitMode::GAIT_LOWLEVL_SDK) {
    high_controller.GetGait(current_mode);
    usleep(100000);
  }

  sleep(2);

  // Get low level controller
  auto& controller = robot.GetLowLevelMotionController();

  current_mode = GaitMode::GAIT_NONE;
  while (current_mode != GaitMode::GAIT_LOWLEVL_SDK) {
    high_controller.GetGait(current_mode);
    usleep(100000);
  }

  bool is_had_receive_leg_state = false;
  std::mutex mut;
  LegState receive_state;
  controller.SubscribeLegState([&](const std::shared_ptr<LegState> msg) {
    static unsigned int count = 0;
    if (!is_had_receive_leg_state) {
      std::lock_guard<std::mutex> guard(mut);
      is_had_receive_leg_state = true;
      receive_state = *msg;
    }

    if (count++ % 1000 == 0)
      std::cout << "Received leg state data." << std::endl;
  });

  while (!is_had_receive_leg_state) {
    usleep(2000);
  }

  sleep(10);

  float j1[] = {0.0000, 1.0477, -2.0944};  // base height 0.2
  float j2[] = {0.0000, 0.7231, -1.4455};  // base height 0.3
  float inital_q[12] = {receive_state.state[0].q, receive_state.state[1].q, receive_state.state[2].q,
                        receive_state.state[3].q, receive_state.state[4].q, receive_state.state[5].q,
                        receive_state.state[6].q, receive_state.state[7].q, receive_state.state[8].q,
                        receive_state.state[9].q, receive_state.state[10].q, receive_state.state[11].q};

  LegJointCommand command;
  unsigned long int cnt = 0;
  while (true) {
    if (cnt < 1000) {
      double t = 1.0 * cnt / 1000.0;
      t = std::min(std::max(t, 0.0), 1.0);

      for (int i = 0; i < 12; ++i) {
        command.cmd[i].q_des = (1 - t) * inital_q[i] + t * j1[i % 3];
      }
    } else if (cnt < 1750) {
      double t = 1.0 * (cnt - 1000) / 700.0;
      t = std::min(std::max(t, 0.0), 1.0);

      for (int i = 0; i < 12; ++i) {
        command.cmd[i].q_des = (1 - t) * j1[i % 3] + t * j2[i % 3];
      }
    } else if (cnt < 2500) {
      double t = 1.0 * (cnt - 1750) / 700.0;
      t = std::min(std::max(t, 0.0), 1.0);

      for (int i = 0; i < 12; ++i) {
        command.cmd[i].q_des = (1 - t) * j2[i % 3] + t * j1[i % 3];
      }
    } else {
      cnt = 1000;
    }

    for (int i = 0; i < 12; ++i) {
      command.cmd[i].kp = 100;
      command.cmd[i].kd = 1.2;
    }

    controller.PublishLegCommand(command);
    usleep(2000);
    cnt++;
  }

  usleep(10000000);

  // Disconnect from robot
  status = robot.Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Disconnect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    return -1;
  }

  robot.Shutdown();

  return 0;
}