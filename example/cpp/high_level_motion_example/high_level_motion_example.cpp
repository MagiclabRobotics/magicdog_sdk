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
  // 退出进程
  exit(signum);
}

void print_help(const char* prog_name) {
  std::cout << "按键功能演示程序\n\n";
  std::cout << "用法: " << prog_name << "\n";
  std::cout << "按键功能说明:\n";
  std::cout << "  ESC      退出程序\n";
  std::cout << "  1        功能1:位控站立\n";
  std::cout << "  2        功能2:力控站立\n";
  std::cout << "  3        功能3:执行特技-趴下\n";
  std::cout << "  w        功能4:向前移动\n";
  std::cout << "  a        功能5:向左移动\n";
  std::cout << "  x        功能6:向后移动\n";
  std::cout << "  s        功能7:停止移动\n";
  std::cout << "  d        功能7:向右移动\n";
  std::cout << "  t        功能8:左转向\n";
  std::cout << "  g        功能9:右转向\n";
}

int getch() {
  struct termios oldt, newt;
  int ch;
  tcgetattr(STDIN_FILENO, &oldt);  // 获取当前终端设置
  newt = oldt;
  newt.c_lflag &= ~(ICANON | ECHO);  // 关闭缓冲和回显
  tcsetattr(STDIN_FILENO, TCSANOW, &newt);
  ch = getchar();                           // 读取按键
  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);  // 恢复设置
  return ch;
}

void RecoveryStand() {
  // 获取高层运控控制器
  auto& controller = robot.GetHighLevelMotionController();

  // 设置步态
  auto status = controller.SetGait(GaitMode::GAIT_STAND_R);
  if (status.code != ErrorCode::OK) {
    std::cerr << "set robot gait failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
}

void BalanceStand() {
  // 获取高层运控控制器
  auto& controller = robot.GetHighLevelMotionController();

  // 设置姿态展示步态
  auto status = controller.SetGait(GaitMode::GAIT_STAND_B);
  if (status.code != ErrorCode::OK) {
    std::cerr << "set robot gait failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "robot gait set to GAIT_BALANCE_STAND successfully." << std::endl;
}

void ExecuteTrick() {
  // 获取高层运控控制器
  auto& controller = robot.GetHighLevelMotionController();

  // 执行特技
  auto status = controller.ExecuteTrick(TrickAction::ACTION_LIE_DOWN);
  if (status.code != ErrorCode::OK) {
    std::cerr << "execute robot trick failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "robot trick executed successfully." << std::endl;
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
        std::cerr << "send joystick command failed"
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
  // 配置本机网线直连机器的IP地址，并进行SDK初始化
  if (!robot.Initialize(local_ip)) {
    std::cerr << "robot sdk initialize failed." << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 设置rpc超时时间为5s
  robot.SetTimeout(5000);

  // 连接机器人
  auto status = robot.Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "connect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 切换运控控制器为底层控制器，默认是高层控制器
  status = robot.SetMotionControlLevel(ControllerLevel::HighLevel);
  if (status.code != ErrorCode::OK) {
    std::cerr << "switch robot motion control level failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  std::thread joy_thread(JoyThread);

  print_help(argv[0]);

  std::cout << "按任意键继续 (ESC退出)..."
            << std::endl;

  auto change_gait_to_down_climb_stairs = [](auto& robot) -> bool {
    GaitMode current_gait = GaitMode::GAIT_PASSIVE;
    auto status = robot.GetHighLevelMotionController().GetGait(current_gait);
    if (status.code != ErrorCode::OK) {
        std::cerr << "get robot gait failed"
                << ", code: " << status.code
                << ", message: " << status.message << std::endl;
        return false;
    }
    if (current_gait != GaitMode::GAIT_DOWN_CLIMB_STAIRS) {
        status = robot.GetHighLevelMotionController().SetGait(GaitMode::GAIT_DOWN_CLIMB_STAIRS);
        if (status.code != ErrorCode::OK) {
            std::cerr << "set robot gait failed"
                        << ", code: " << status.code
                        << ", message: " << status.message << std::endl;
            return false;
        }
    } else {
        return true;
    }

    status = robot.GetHighLevelMotionController().GetGait(current_gait);
    if (status.code != ErrorCode::OK) {
        std::cerr << "get robot gait failed"
                    << ", code: " << status.code
                    << ", message: " << status.message << std::endl;
        return false;
    }
    while (current_gait != GaitMode::GAIT_DOWN_CLIMB_STAIRS) {
        usleep(10000);
        status = robot.GetHighLevelMotionController().GetGait(current_gait);
        if (status.code != ErrorCode::OK) {
            std::cerr << "get robot gait failed"
                        << ", code: " << status.code
                        << ", message: " << status.message << std::endl;
            return false;
        }
    }
    return true;
  };
  // 等待用户输入
  while (1) {
    int key = getch();
    if (key == 27)
      break;  // ESC键ASCII码为27

    std::cout << "按键ASCII: " << key << ", 字符: " << static_cast<char>(key) << std::endl;
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
            std::cerr << "change robot gait to down climb stairs failed" << std::endl;
            break;
        }
        JoyStickCommand(0.0, 1.0, 0.0, 0.0);  // 向前
        break;
      }
      case 'a': {
        if (!change_gait_to_down_climb_stairs(robot)) {
            std::cerr << "change robot gait to down climb stairs failed" << std::endl;
            break;
        }
        JoyStickCommand(-1.0, 0.0, 0.0, 0.0);  // 向左
        break;
      }
      case 'x': {
        if (!change_gait_to_down_climb_stairs(robot)) {
            std::cerr << "change robot gait to down climb stairs failed" << std::endl;
            break;
        }
        JoyStickCommand(0.0, -1.0, 0.0, 0.0);  // 向后
        break;
      }
      case 'd': {
        if (!change_gait_to_down_climb_stairs(robot)) {
            std::cerr << "change robot gait to down climb stairs failed" << std::endl;
            break;
        }
        JoyStickCommand(1.0, 0.0, 0.0, 0.0);  // 向右
        break;
      }
      case 't': {
        if (!change_gait_to_down_climb_stairs(robot)) {
            std::cerr << "change robot gait to down climb stairs failed" << std::endl;
            break;
        }
        JoyStickCommand(0.0, 0.0, -1.0, 0.0);  // 左转
        break;
      }
      case 'g': {
        if (!change_gait_to_down_climb_stairs(robot)) {
            std::cerr << "change robot gait to down climb stairs failed" << std::endl;
            break;
        }
        JoyStickCommand(0.0, 0.0, 1.0, 0.0);  // 右转
        break;
      }
      case 's': {
        if (!change_gait_to_down_climb_stairs(robot)) {
            std::cerr << "change robot gait to down climb stairs failed" << std::endl;
            break;
        }
        JoyStickCommand(0.0, 0.0, 0.0, 0.0);  // 停止
        break;
      }
      default:
        std::cout << "未知按键: " << key << std::endl;
        break;
    }

    usleep(10000);
  }

  is_running.store(false);
  joy_thread.join();

  // 断开与机器人的链接
  status = robot.Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "disconnect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  robot.Shutdown();

  return 0;
}