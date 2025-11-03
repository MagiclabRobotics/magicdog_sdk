#pragma once

#include "magic_export.h"
#include "magic_type.h"

#include <atomic>
#include <functional>
#include <memory>
#include <string>

namespace magic::dog::slam {

class SlamNavController;
using SlamNavControllerPtr = std::unique_ptr<SlamNavController>;

class MAGIC_EXPORT_API SlamNavController final : public NonCopyable {
  using LocalizationInfoPtr = std::shared_ptr<LocalizationInfo>;
  using OdometryPtr = std::shared_ptr<Odometry>;
  using NavStatusPtr = std::shared_ptr<NavStatus>;

  using LocalizationInfoCallback = std::function<void(const LocalizationInfoPtr)>;
  using OdometryCallback = std::function<void(const OdometryPtr)>;
  using NavStatusCallback = std::function<void(const NavStatusPtr)>;

 public:
  /**
   * @brief Constructor, creates a SlamNavController instance.
   */
  SlamNavController();

  /**
   * @brief Destructor, releases SlamNavController instance resources.
   */
  ~SlamNavController();

  /**
   * @brief Initialize SLAM navigation controller.
   * @return Whether initialization was successful.
   */
  bool Initialize();

  /**
   * @brief Release resources, clean up SLAM navigation controller.
   */
  void Shutdown();

  /**
   * @brief Switch to idle mode
   * @return Operation status, returns Status::OK on success
   */
  Status SwitchToIdle();

  /**
   * @brief Switch to localization mode
   * @return Operation status, returns Status::OK on success
   */
  Status SwitchToLocation();

  /**
   * @brief Start mapping mode
   * @return Operation status, returns Status::OK on success
   */
  Status StartMapping();

  /**
   * @brief Cancel current mapping task
   * @return Operation status, returns Status::OK on success
   */
  Status CancelMapping();

  /**
   * @brief End mapping and save map, when in mapping mode
   * @param map_name Map name
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status, returns Status::OK on success
   */
  Status SaveMap(const std::string& map_name);

  /**
   * @brief load map and set as the current map
   * @param map_name Map name
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status, returns Status::OK on success
   */
  Status LoadMap(const std::string& map_name);

  /**
   * @brief Delete map
   * @param map_name Name of the map to delete
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status, returns Status::OK on success
   */
  Status DeleteMap(const std::string& map_name);

  /**
   * @brief Get all map information
   * @param all_map_info All map information (output parameter)
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status, returns Status::OK on success
   * @brief Get all map information
   * @param all_map_info All map information (output parameter)
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status, returns Status::OK on success
   */
  Status GetAllMapInfo(AllMapInfo& all_map_info);

  /**
   * @brief Initialize pose
   * @param pose Pose information to publish
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status, returns Status::OK on success
   * @brief Initialize pose
   * @param pose Pose information to publish
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status, returns Status::OK on success
   */
  Status InitPose(const Pose3DEuler& pose);

  /**
   * @brief Get current pose information
   * @param localization_info Current position and attitude information (output parameter)
   * @return Operation status, returns Status::OK on success
   */
  Status GetCurrentLocalizationInfo(LocalizationInfo& localization_info);

  /**
   * @brief activate navigation mode
   * @param mode Target navigation mode (NavigationMode enumeration type)
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status, returns Status::OK on success
   */
  Status ActivateNavMode(NavMode mode);

  /**
   * @brief Set global navigation target point and start navigation task
   * @param goal Global coordinates of the target point
   * @return Operation status, returns Status::OK on success
   */
  Status SetNavTarget(const NavTarget& goal);

  /**
   * @brief Pause current navigation task
   * @return Operation status, returns Status::OK on success
   */
  Status PauseNavTask();

  /**
   * @brief Resume paused navigation task
   * @return Operation status, returns Status::OK on success
   */
  Status ResumeNavTask();

  /**
   * @brief Cancel current navigation task
   * @return Operation status, returns Status::OK on success
   */
  Status CancelNavTask();

  /**
   * @brief Get current navigation status
   * @param status Navigation status
   * @return Operation status, returns Status::OK on success
   */
  Status GetNavTaskStatus(NavStatus& status);

  /**
   * @brief Subscribe to odometry data
   * @param callback Callback function to handle odometry data
   */
  void SubscribeOdometry(const OdometryCallback& callback);

  /**
   * @brief Unsubscribe from odometry data
   */
  void UnsubscribeOdometry();

 private:
  std::atomic_bool is_shutdown_{true};  // Mark whether it has been initialized
};

}  // namespace magic::dog::slam