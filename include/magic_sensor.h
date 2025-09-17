#pragma once

#include "magic_export.h"
#include "magic_type.h"

#include <atomic>
#include <functional>
#include <memory>
#include <string>

namespace magic::dog::sensor {

class SensorController;
using SensorControllerPtr = std::unique_ptr<SensorController>;

/**
 * @class SensorController
 * @brief Sensor controller class, encapsulating initialization, start/stop, and data acquisition interfaces for various robot sensors.
 *
 * Supports acquiring information from TOF, IMU, RGBD, ultrasonic, laser scan, binocular camera, fisheye camera, etc., providing a unified access method,
 * for use by upper-level controllers or state fusion modules.
 */
class MAGIC_EXPORT_API SensorController final : public NonCopyable {
  // Message pointer type definitions (smart pointers for memory management)
  using TofPtr = std::shared_ptr<Float32MultiArray>;            // TOF data pointer
  using UltraPtr = std::shared_ptr<Float32MultiArray>;          // Ultrasonic data pointer
  using HeadTouchPtr = std::shared_ptr<HeadTouch>;              // Head touch data pointer
  using LaserScanPtr = std::shared_ptr<LaserScan>;              // Laser scan data pointer
  using ImagePtr = std::shared_ptr<Image>;                      // Image data pointer
  using CameraInfoPtr = std::shared_ptr<CameraInfo>;            // Camera intrinsic data pointer
  using CompressedImagePtr = std::shared_ptr<CompressedImage>;  // Compressed image data pointer
  using ImuPtr = std::shared_ptr<Imu>;                          // IMU (Inertial Measurement Unit) message pointer

  // Callback function type definitions for various sensor data
  using TofCallback = std::function<void(const TofPtr)>;
  using UltraCallback = std::function<void(const UltraPtr)>;
  using HeadTouchCallback = std::function<void(const HeadTouchPtr)>;
  using LaserScanCallback = std::function<void(const LaserScanPtr)>;
  using ImageCallback = std::function<void(const ImagePtr)>;
  using CameraInfoCallback = std::function<void(const CameraInfoPtr)>;
  using CompressedImageCallback = std::function<void(const CompressedImagePtr)>;
  using ImuCallback = std::function<void(const ImuPtr)>;

 public:
  /// Constructor: Create SensorController instance and initialize internal state
  SensorController();

  /// Destructor: Release resources and close all sensors
  virtual ~SensorController();

  /**
   * @brief Initialize the sensor controller, including resource allocation, driver loading, etc.
   * @return Returns true if initialization is successful, otherwise false.
   */
  bool Initialize();

  /**
   * @brief Close all sensor connections and release resources.
   */
  void Shutdown();

  // === Channel switch ===

  /**
   * @brief Open channel switch
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status
   */
  Status OpenChannelSwith(int timeout_ms = 5000);

  /**
   * @brief Close channel switch
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status
   */
  Status CloseChannelSwith(int timeout_ms = 5000);

  // === Laser Scan control ===

  /**
   * @brief Open Laser Scan.
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status.
   */
  Status OpenLaserScan(int timeout_ms = 5000);

  /**
   * @brief Close Laser Scan.
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status.
   */
  Status CloseLaserScan(int timeout_ms = 5000);

  // === RGBD camera control ===

  /**
   * @brief Open RGBD camera
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status.
   */
  Status OpenRgbdCamera(int timeout_ms = 5000);

  /**
   * @brief Close RGBD camera.
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status.
   */
  Status CloseRgbdCamera(int timeout_ms = 5000);

  // === Binocular camera control ===

  /**
   * @brief Open binocular camera.
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status.
   */
  Status OpenBinocularCamera(int timeout_ms = 5000);

  /**
   * @brief Close binocular camera.
   * @param timeout_ms Timeout in milliseconds
   * @return Operation status.
   */
  Status CloseBinocularCamera(int timeout_ms = 5000);

  // Subscription interfaces for various sensor data

  /**
   * @brief Subscribe to TOF data
   * @param callback Callback to process received TOF data
   */
  void SubscribeTof(const TofCallback callback);

  /**
   * @brief Subscribe to ultrasonic data
   * @param callback Callback to process received ultrasonic data
   */
  void SubscribeUltra(const UltraCallback callback);

  /**
   * @brief Subscribe to head touch data
   * @param callback Callback to process received head touch data
   */
  void SubscribeHeadTouch(const HeadTouchCallback callback);

  /**
   * @brief Subscribe to laser scan data
   * @param callback Callback to process received laser scan data
   */
  void SubscribeLaserScan(const LaserScanCallback callback);

  /**
   * @brief Subscribe to RGBD depth camera intrinsic data
   * @param callback Callback to process received RGBD depth camera intrinsic data
   */
  void SubscribeRgbDepthCameraInfo(const CameraInfoCallback callback);

  /**
   * @brief Subscribe to RGBD depth image data
   * @param callback Callback to process received RGBD depth image data
   */
  void SubscribeRgbdDepthImage(const ImageCallback callback);

  /**
   * @brief Subscribe to RGBD color camera intrinsic data
   * @param callback Callback to process received RGBD color camera intrinsic data
   */
  void SubscribeRgbdColorCameraInfo(const CameraInfoCallback callback);

  /**
   * @brief Subscribe to RGBD color image data
   * @param callback Callback to process received RGBD color image data
   */
  void SubscribeRgbdColorImage(const ImageCallback callback);

  /**
   * @brief Subscribe to IMU data
   * @param callback Callback to process received IMU data
   */
  void SubscribeImu(const ImuCallback callback);

  /**
   * @brief Subscribe to left high-quality binocular image data
   * @param callback Callback to process received left high-quality binocular image data
   */
  void SubscribeLeftBinocularHighImg(const CompressedImageCallback callback);

  /**
   * @brief Subscribe to left low-quality binocular image data
   * @param callback Callback to process received left low-quality binocular image data
   */
  void SubscribeLeftBinocularLowImg(const CompressedImageCallback callback);

  /**
   * @brief Subscribe to right low-quality binocular image data
   * @param callback Callback to process received right low-quality binocular image data
   */
  void SubscribeRightBinocularLowImg(const CompressedImageCallback callback);

  /**
   * @brief Subscribe to depth image
   * @param callback Callback to process received depth image
   */
  void SubscribeDepthImage(const ImageCallback callback);

 private:
  std::atomic_bool is_shutdown_{true};  // Indicates whether initialized
};

}  // namespace magic::dog::sensor
