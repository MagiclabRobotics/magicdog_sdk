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
 * @brief Provides a unified management interface for the robot system, including initialization, connection management, and access to various sub-controllers.
 *
 * This class is the core entry point of the robot system, responsible for resource initialization, communication connection management, obtaining robot status,
 * and providing a unified interface for accessing high-level/low-level controllers, audio controller, and sensor controller to the outside.
 */
class MAGIC_EXPORT_API MagicRobot final : public NonCopyable {
 public:
  /**
   * @brief Constructor, creates a MagicRobot instance.
   */
  MagicRobot();

  /**
   * @brief Destructor, releases resources of the MagicRobot instance.
   */
  ~MagicRobot();

  /**
   * @brief Initialize the robot system, including controllers, network, and other submodules.
   * @param local_ip Local IP address, used for communication binding or identity identification.
   * @return Whether initialization is successful.
   */
  bool Initialize(const std::string& local_ip);

  /**
   * @brief Shutdown the robot system and release resources.
   */
  void Shutdown();

  /**
   * @brief Release robot system resources.
   */
  void Release();

  /**
   * @brief Establish a communication connection with the robot service.
   * @param timeout_ms Timeout in milliseconds.
   * @return gRPC call status, returns Status::OK on success.
   */
  Status Connect(int timeout_ms = 5000);

  /**
   * @brief Disconnect from the robot service.
   * @param timeout_ms Timeout in milliseconds.
   * @return gRPC call status.
   */
  Status Disconnect(int timeout_ms = 5000);

  /**
   * @brief Get the SDK version.
   * @return The current SDK version string, e.g., "1.2.3".
   */
  std::string GetSDKVersion() const;

  /**
   * @brief Get the current motion control level.
   * @return The current control mode (high-level control or low-level control).
   */
  ControllerLevel GetMotionControlLevel();

  /**
   * @brief Set the motion control level (high-level or low-level).
   * @param level Enum type control level.
   * @return Status of the setting result.
   */
  Status SetMotionControlLevel(ControllerLevel level);

  /**
   * @brief Get the high-level motion controller object.
   * @return Reference type, for users to call high-level motion control interfaces.
   */
  HighLevelMotionController& GetHighLevelMotionController();

  /**
   * @brief Get the low-level motion controller object.
   * @return Reference type, for users to control specific joints/components.
   */
  LowLevelMotionController& GetLowLevelMotionController();

  /**
   * @brief Get the audio controller object.
   * @return Reference type, can be used for voice playback, volume adjustment, etc.
   */
  AudioController& GetAudioController();

  /**
   * @brief Get the sensor controller object.
   * @return Reference type, used to access sensor data such as battery, IMU, camera, etc.
   */
  SensorController& GetSensorController();

  /**
   * @brief Get the state monitor object.
   * @return Reference type, used to obtain the current status information of the robot.
   */
  StateMonitor& GetStateMonitor();

 private:
  std::atomic_bool is_shutdown_{true};  // Indicates whether it has been initialized
};
}  // namespace magic::dog