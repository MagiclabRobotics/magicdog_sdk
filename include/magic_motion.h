#pragma once

#include "magic_export.h"
#include "magic_type.h"

#include <atomic>
#include <functional>
#include <memory>
#include <string>

namespace magic::dog::motion {

class LowLevelMotionController;
using LowLevelMotionControllerPtr = std::unique_ptr<LowLevelMotionController>;

class HighLevelMotionController;
using HighLevelMotionControllerPtr = std::unique_ptr<HighLevelMotionController>;

/**
 * @brief Abstract base class defining the common interface for robot motion controllers.
 *
 * MotionControllerBase is the base class for all motion controllers, providing pure virtual functions for initialization and shutdown.
 * Derived classes must implement these interfaces to meet specific control requirements.
 */
class MAGIC_EXPORT_API MotionControllerBase : public NonCopyable {
 public:
  /**
   * @brief Constructor.
   */
  MotionControllerBase() = default;

  /**
   * @brief Virtual destructor to ensure derived class resources are released properly.
   */
  virtual ~MotionControllerBase() = default;

  /**
   * @brief Initialize the controller.
   * @return Returns true if initialization is successful, otherwise false.
   */
  virtual bool Initialize() = 0;

  /**
   * @brief Shutdown the controller and release related resources.
   */
  virtual void Shutdown() = 0;

 protected:
  std::atomic_bool is_shutdown_{true};  // Indicates whether the controller is initialized
};

/**
 * @class HighLevelMotionController
 * @brief High-level motion controller for semantic-level robot actions (e.g., walking, tricks, head movement, etc.).
 *
 * This class inherits from MotionControllerBase and is mainly for high-level user interfaces, hiding low-level details.
 */
class MAGIC_EXPORT_API HighLevelMotionController final : public MotionControllerBase {
 public:
  /// Constructor, initializes the internal state of the high-level controller.
  HighLevelMotionController();

  /// Destructor, releases resources.
  virtual ~HighLevelMotionController();

  /**
   * @brief Initialize the controller and prepare high-level control functions.
   * @return Whether initialization is successful.
   */
  virtual bool Initialize() override;

  /**
   * @brief Shutdown the controller and release related resources.
   */
  virtual void Shutdown() override;

  /**
   * @brief Set the robot's gait mode (e.g., stand lock, balance stand, humanoid walk, etc., see GaitMode definition).
   * @param gait_mode Gait mode as an enum.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status SetGait(const GaitMode gait_mode, int timeout_ms = 5000);

  /**
   * @brief Get the robot's gait mode (e.g., stand lock, balance stand, humanoid walk, etc., see GaitMode definition).
   * @param gait_mode Gait mode as an enum.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status GetGait(GaitMode& gait_mode, int timeout_ms = 5000);

  /**
   * @brief Execute a specified trick action (e.g., bow, wave, etc.).
   * @param trick_action Trick action identifier.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   * @note Trick actions are usually predefined complex action sequences and must be performed under GaitMode::GAIT_BALANCE_STAND(46).
   */
  Status ExecuteTrick(const TrickAction trick_action, int timeout_ms = 5000);

  /**
   * @brief Send real-time joystick control commands. Recommended frequency: 20Hz.
   * @param joy_command Control command containing left and right joystick coordinates.
   * @return Operation status.
   */
  Status SendJoyStickCommand(JoystickCommand& joy_command);

  /**
   * @brief Enable joystick control command.
   * @return Operation status.
   */
  Status EnableJoyStick();

  /**
   * @brief Disable joystick control command.
   * @return Operation status.
   */
  Status DisableJoyStick();

  /**
   * @brief Get all gait speed ratios for forward, lateral, and rotational movement.
   * @param gait_speed_ratios All gait speed ratios for forward, lateral, and rotational movement.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status GetAllGaitSpeedRatio(AllGaitSpeedRatio& gait_speed_ratios, int timeout_ms = 5000);

  /**
   * @brief Set gait speed ratios for forward, lateral, and rotational movement.
   * @param gait_speed_ratios Gait speed ratios for forward, lateral, and rotational movement.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status SetGaitSpeedRatio(GaitMode gait_mode, const GaitSpeedRatio& gait_speed_ratio, int timeout_ms = 5000);

  /**
   * @brief Get the enable status of the head motor.
   * @param enabled Output parameter, true if enabled, false if not.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status GetHeadMotorEnabled(bool& enabled, int timeout_ms = 5000);

  /**
   * @brief Enable the head motor.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status EnableHeadMotor(int timeout_ms = 5000);

  /**
   * @brief Disable the head motor.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status DisableHeadMotor(int timeout_ms = 5000);
};

/**
 * @class LowLevelMotionController
 * @brief Low-level motion controller for direct control of joint actions of various motion components (e.g., arms, legs, head, waist, etc.).
 *
 * Intended for low-level developers or control systems, providing interfaces for sending commands and reading states of each body part.
 */
class MAGIC_EXPORT_API LowLevelMotionController final : public MotionControllerBase {
  // Message pointer type definition (smart pointer for memory management)
  using LegJointStatePtr = std::shared_ptr<LegState>;  // Leg joint state message pointer

  // Callback function type definition for various joint data
  using LegJointStateCallback = std::function<void(const LegJointStatePtr)>;  // Leg joint state callback function type

 public:
  /// Constructor, initializes the low-level controller.
  LowLevelMotionController();

  /// Destructor, releases resources.
  virtual ~LowLevelMotionController();

  /**
   * @brief Initialize the controller and establish low-level motion control connection.
   * @return Whether initialization is successful.
   */
  virtual bool Initialize() override;

  /**
   * @brief Shutdown the controller and release low-level resources.
   */
  virtual void Shutdown() override;

  // === Leg control ===

  /**
   * @brief Subscribe to leg joint state data.
   * @param callback Callback function for processing received leg joint state data.
   */
  void SubscribeLegState(LegJointStateCallback callback);

  /**
   * @brief Unsubscribe from leg joint state data.
   */
  void UnsubscribeLegState();

  /**
   * @brief Publish leg joint control command.
   * @param command Leg joint control command containing target angle/velocity and other control information.
   * @return Operation status.
   */
  Status PublishLegCommand(const LegJointCommand& command);
};

}  // namespace magic::dog::motion