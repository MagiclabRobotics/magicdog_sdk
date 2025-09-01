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
 * @brief 传感器控制器类，封装机器人各类传感器的初始化、开启/关闭和数据获取接口。
 *
 * 支持获取tof、imu、rgbd、ultra、laser_scan、 双目相机、 鱼眼相机等信息，提供统一的访问方式，
 * 用于上层控制器或状态融合模块调用。
 */
class MAGIC_EXPORT_API SensorController final : public NonCopyable {
  // 消息指针类型定义（智能指针，便于内存管理）
  using TofPtr = std::shared_ptr<Float32MultiArray>;            // TOF 数据指针
  using UltraPtr = std::shared_ptr<Float32MultiArray>;          // 超声波数据指针
  using HeadTouchPtr = std::shared_ptr<HeadTouch>;              // 头部触摸数据指针
  using LaserScanPtr = std::shared_ptr<LaserScan>;              // 激光雷达数据指针
  using ImagePtr = std::shared_ptr<Image>;                      // 图像数据指针
  using CameraInfoPtr = std::shared_ptr<CameraInfo>;            // 相机内参数据指针
  using CompressedImagePtr = std::shared_ptr<CompressedImage>;  // 压缩图像数据指针
  using ImuPtr = std::shared_ptr<Imu>;                          // IMU 惯性测量单元消息指针

  // 各类传感器数据的回调函数类型定义
  using TofCallback = std::function<void(const TofPtr)>;
  using UltraCallback = std::function<void(const UltraPtr)>;
  using HeadTouchCallback = std::function<void(const HeadTouchPtr)>;
  using LaserScanCallback = std::function<void(const LaserScanPtr)>;
  using ImageCallback = std::function<void(const ImagePtr)>;
  using CameraInfoCallback = std::function<void(const CameraInfoPtr)>;
  using CompressedImageCallback = std::function<void(const CompressedImagePtr)>;
  using ImuCallback = std::function<void(const ImuPtr)>;

 public:
  /// 构造函数：创建 SensorController 实例，初始化内部状态
  SensorController();

  /// 析构函数：释放资源，关闭所有传感器
  virtual ~SensorController();

  /**
   * @brief 初始化传感器控制器，包括资源申请、驱动加载等。
   * @return 初始化成功返回 true，否则返回 false。
   */
  bool Initialize();

  /**
   * @brief 关闭所有传感器连接并释放资源。
   */
  void Shutdown();

  // === 话题转换开关 ===

  /**
   * @brief 打开话题转换开关
   * @return 操作状态
   */
  Status OpenChannelSwith();

  /**
   * @brief 关闭话题转换开关
   * @return 操作状态
   */
  Status CloseChannelSwith();

  // === Laser Scan控制 ===

  /**
   * @brief 打开 Laser Scan。
   * @return 操作状态。
   */
  Status OpenLaserScan();

  /**
   * @brief 关闭 Laser Scan。
   * @return 操作状态。
   */
  Status CloseLaserScan();

  // === RGBD 相机控制 ===

  /**
   * @brief 打开 RGBD 相机
   * @return 操作状态。
   */
  Status OpenRgbdCamera();

  /**
   * @brief 关闭 RGBD 相机。
   * @return 操作状态。
   */
  Status CloseRgbdCamera();

  // === 双目相机控制 ===

  /**
   * @brief 打开双目相机。
   * @return 操作状态。
   */
  Status OpenBinocularCamera();

  /**
   * @brief 关闭双目相机。
   * @return 操作状态。
   */
  Status CloseBinocularCamera();

  // 订阅各类传感器数据的函数接口

  /**
   * @brief 订阅TOF数据
   * @param callback 接收到TOF数据后的处理回调
   */
  void SubscribeTof(const TofCallback callback);

  /**
   * @brief 订阅超声波数据
   * @param callback 接收到超声波数据后的处理回调
   */
  void SubscribeUltra(const UltraCallback callback);

  /**
   * @brief 订阅头部触摸数据
   * @param callback 接收到头部触摸数据后的处理回调
   */
  void SubscribeHeadTouch(const HeadTouchCallback callback);

  /**
   * @brief 订阅激光雷达数据
   * @param callback 接收到激光雷达数据后的处理回调
   */
  void SubscribeLaserScan(const LaserScanCallback callback);

  /**
   * @brief 订阅RGBD深度相机内参数据
   * @param callback 接收到RGBD深度相机内参数据后的处理回调
   */
  void SubscribeRgbDepthCameraInfo(const CameraInfoCallback callback);

  /**
   * @brief 订阅RGBD深度图像数据
   * @param callback 接收到RGBD深度图像数据后的处理回调
   */
  void SubscribeRgbdDepthImage(const ImageCallback callback);

  /**
   * @brief 订阅RGBD彩色图像内参数据
   * @param callback 接收到RGBD彩色图像内参数据后的处理回调
   */
  void SubscribeRgbdColorCameraInfo(const CameraInfoCallback callback);

  /**
   * @brief 订阅RGBD彩色图像数据
   * @param callback 接收到RGBD彩色图像数据后的处理回调
   */
  void SubscribeRgbdColorImage(const ImageCallback callback);

  /**
   * @brief 订阅IMU数据
   * @param callback 接收到IMU数据后的处理回调
   */
  void SubscribeImu(const ImuCallback callback);

  /**
   * @brief 订阅左侧高质量双目数据
   * @param callback 接收到左侧高质量双目数据后的处理回调
   */
  void SubscribeLeftBinocularHighImg(const CompressedImageCallback callback);

  /**
   * @brief 订阅左侧低质量双目数据
   * @param callback 接收到左侧低质量双目数据后的处理回调
   */
  void SubscribeLeftBinocularLowImg(const CompressedImageCallback callback);

  /**
   * @brief 订阅右侧低质量双目数据
   * @param callback 接收到右侧低质量双目数据后的处理回调
   */
  void SubscribeRightBinocularLowImg(const CompressedImageCallback callback);

  /**
   * @brief 订阅深度图像
   * @param callback 接收到深度图像后的处理回调
   */
  void SubscribeDepthImage(const ImageCallback callback);

 private:
  std::atomic_bool is_shutdown_{true};  // 标记是否已初始化
};

}  // namespace magic::dog::sensor
