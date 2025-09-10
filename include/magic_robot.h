#pragma once

#include <atomic>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "magic_export.h"
#include "magic_type.h"

#include "magic_audio.h"
#include "magic_motion.h"
#include "magic_sensor.h"
#include "magic_state_monitor.h"

namespace magic::dog {
using namespace motion;
using namespace sensor;
using namespace audio;
using namespace monitor;

/**
 * @class MagicRobot
 * @brief 提供对机器人系统的统一管理接口，包括初始化、连接管理、各子控制器的访问等。
 *
 * 该类是机器人系统的核心入口，负责初始化资源、管理通信连接、获取机器人状态，
 * 并向外部提供访问高层/低层控制器、音频控制器、传感器控制器的统一接口。
 */
class MAGIC_EXPORT_API MagicRobot final : public NonCopyable {
 public:
  /**
   * @brief 构造函数，创建 MagicRobot 实例。
   */
  MagicRobot();

  /**
   * @brief 析构函数，释放 MagicRobot 实例资源。
   */
  ~MagicRobot();

  /**
   * @brief 初始化机器人系统，包括控制器、网络等子模块。
   * @param local_ip 本地IP地址，用于通信绑定或身份标识。
   * @return 初始化是否成功。
   */
  bool Initialize(const std::string& local_ip);

  /**
   * @brief 关闭机器人系统，释放资源。
   */
  void Shutdown();

  /**
   * @brief 释放机器人系统资源。
   */
  void Release();

  /**
   * @brief 与机器人服务建立通信连接。
   * @return gRPC调用状态，成功返回 Status::OK。
   */
  Status Connect();

  /**
   * @brief 断开与机器人服务的连接。
   * @return gRPC调用状态。
   */
  Status Disconnect();

  /**
   * @brief 获取SDK版本号。
   * @return 当前SDK的版本字符串，例如 "1.2.3"。
   */
  std::string GetSDKVersion() const;

  /**
   * @brief 设置接口调用的超时时间。
   * @param timeout 超时时间，单位为毫秒。默认超时时间为5000毫秒。
   */
  void SetTimeout(int timeout);

  /**
   * @brief 获取当前运动控制级别。
   * @return 当前控制模式（高层控制或低层控制）。
   */
  ControllerLevel GetMotionControlLevel();

  /**
   * @brief 设置运动控制级别（高层或低层）。
   * @param level 枚举类型的控制级别。
   * @return 设置结果状态。
   */
  Status SetMotionControlLevel(ControllerLevel level);

  /**
   * @brief 获取高层运动控制器对象。
   * @return 引用类型，供用户调用高层运动控制接口。
   */
  HighLevelMotionController& GetHighLevelMotionController();

  /**
   * @brief 获取低层运动控制器对象。
   * @return 引用类型，供用户控制具体关节/部件。
   */
  LowLevelMotionController& GetLowLevelMotionController();

  /**
   * @brief 获取音频控制器对象。
   * @return 引用类型，可用于播放语音、调节音量等。
   */
  AudioController& GetAudioController();

  /**
   * @brief 获取传感器控制器对象。
   * @return 引用类型，用于访问电量、IMU、摄像头等传感器数据。
   */
  SensorController& GetSensorController();

  /**
   * @brief 获取状态监控器对象。
   * @return 引用类型，用于获取机器人当前状态信息。
   */
  StateMonitor& GetStateMonitor();

 private:
  std::atomic_bool is_shutdown_{true};  // 标记是否已初始化
};
}  // namespace magic::dog