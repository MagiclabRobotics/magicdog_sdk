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
 * @brief A class encapsulating state control functions, providing interfaces such as state query.
 *
 * This class is typically used for state management of robots or intelligent devices, supporting state query and initialization,
 * and providing a resource release mechanism.
 */

class MAGIC_EXPORT_API StateMonitor final : public NonCopyable {
 public:
  /**
   * @brief Constructor, creates a StateMonitor instance.
   */
  StateMonitor();

  /**
   * @brief Destructor, releases resources of the StateMonitor instance.
   */
  ~StateMonitor();

  /**
   * @brief Initialize the state controller.
   * @return Whether initialization is successful.
   */
  bool Initialize();

  /**
   * @brief Release resources and clean up the state controller.
   */
  void Shutdown();

  /**
   * @brief Get the current robot running state (aggregated state information).
   * @return robot_state to receive the current robot state.
   */
  Status GetCurrentState(RobotState& robot_state);

 private:
  std::atomic_bool is_shutdown_{true};  // Indicates whether it has been initialized
};

}  // namespace magic::dog::monitor