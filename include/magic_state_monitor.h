#pragma once

#include "magic_export.h"
#include "magic_type.h"

#include <atomic>
#include <memory>
#include <string>

namespace magic::dog::monitor {

class StateMonitor;
using StateMonitorPtr = std::unique_ptr<StateMonitor>;

/**
 * @class StateMonitor
 * @brief 封装状态控制功能的类，提供状态查询等接口。
 *
 * 该类通常用于控制机器人或智能设备的状态管理，支持状态查询与初始化，
 * 并提供资源释放机制。
 */

class MAGIC_EXPORT_API StateMonitor final : public NonCopyable {
 public:
  /**
   * @brief 构造函数，创建 StateMonitor 实例。
   */
  StateMonitor();

  /**
   * @brief 析构函数，释放 StateMonitor 实例资源。
   */
  ~StateMonitor();

  /**
   * @brief 初始化状态控制器。
   * @return 是否初始化成功。
   */
  bool Initialize();

  /**
   * @brief 释放资源，清理状态控制器。
   */
  void Shutdown();

  /**
   * @brief 获取当前机器人运行状态（聚合的状态信息）。
   * @return robot_state 用于接收机器人当前状态。
   */
  RobotState GetCurrentState() const;

 private:
  std::atomic_bool is_shutdown_{true};  // 标记是否已初始化
};

}  // namespace magic::dog::monitor