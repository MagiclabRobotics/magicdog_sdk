#pragma once

#include <array>
#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace magic::dog {

/************************************************************
 *                        常量信息                           *
 ************************************************************/

constexpr uint8_t kLegJointNum = 12;  ///< 下肢关节数量

constexpr uint64_t kPeriodMs = 2;  ///< 控制器周期时间，单位为毫秒

/************************************************************
 *                        接口信息                           *
 ************************************************************/

enum ErrorCode {
  OK = 0,
  SERVICE_NOT_READY = 1,
  TIMEOUT = 2,
  INTERNAL_ERROR = 3,
  SERVICE_ERROR = 4,
};

struct Status {
  ErrorCode code;
  std::string message;
};

/************************************************************
 *                        状态信息                           *
 ************************************************************/
/**
 * @brief 错误信息结构体
 *
 * 用于表示系统中发生的错误信息，包括错误代码和错误消息。
 */
struct Fault {
  /**
   * @brief 错误代码
   *
   * 整型值，用于标识具体的异常类型。不同的错误代码可以对应不同的错误类型，便于错误管理和处理。
   */
  int32_t error_code;

  /**
   * @brief 错误信息
   *
   * 描述错误发生的具体信息，通常是对错误原因的详细描述，便于调试和定位问题。
   */
  std::string error_message;
};

/**
 * @brief 电池状态枚举类型
 *
 * 表示电池当前的状态，包含多个可能的电池状态选项，用于系统中电池状态的判断和处理。
 */
enum class BatteryState : int8_t {
  UNKNOWN = 0,                ///< 未知状态
  GOOD = 1,                   ///< 电池状态良好
  OVERHEAT = 2,               ///< 电池过热
  DEAD = 3,                   ///< 电池损坏
  OVERVOLTAGE = 4,            ///< 电池过电压
  UNSPEC_FAILURE = 5,         ///< 未知故障
  COLD = 6,                   ///< 电池过冷
  WATCHDOG_TIMER_EXPIRE = 7,  ///< 看门狗定时器超时
  SAFETY_TIMER_EXPIRE = 8,    ///< 安全定时器超时
};

/**
 * @brief 电池充放电状态
 */
enum class PowerSupplyStatus : int8_t {
  UNKNOWN = 0,      ///< 未知状态
  CHARGING = 1,     ///< 电池充电中
  DISCHARGING = 2,  ///< 电池放电中
  NOTCHARGING = 3,  ///< 电池未充放电
  FULL = 4,         ///< 电池充满
};

/**
 * @brief 电池管理系统数据结构体
 *
 * 用于存储电池的相关信息，包括电池的剩余电量、电池健康状况、电池状态和充电状态。
 */
typedef struct bms_data {
  /**
   * @brief 电池剩余电量
   *
   * 电池的当前电量百分比，范围从 0 到 100，表示电池的剩余电量。
   */
  float battery_percentage;

  /**
   * @brief 电池健康状态
   *
   * 电池的健康状况，通常是一个表示电池性能的浮动值。健康状况越高表示电池越好。
   */
  float battery_health;

  /**
   * @brief 电池状态
   *
   * 电池当前的状态，用来表示电池的不同状态。
   */
  BatteryState battery_state;

  /**
   * @brief 充电状态
   *
   * 一个布尔值，指示电池是否正在充电。`true` 表示电池正在充电，`false` 表示电池未充电。
   */
  PowerSupplyStatus power_supply_status;
} BmsData;

typedef struct robot_state {
  std::vector<Fault> faults;  ///< 故障信息列表
  BmsData bms_data;           ///< 电池管理系统数据
} RobotState;

/************************************************************
 *                        运动控制                           *
 ************************************************************/

/**
 * @brief 运动控制器的层级类型，用于区分不同的控制器职责。
 */
enum class ControllerLevel : int8_t {
  UNKKOWN = 0,
  HighLevel = 1,  ///< 高层级控制器
  LowLevel = 2    ///< 低层级控制器
};

/**
 * @brief 机器人状态枚举，适用于状态机控制
 */
enum class GaitMode : int32_t {
  GAIT_PASSIVE = 0,             // 掉落（关闭电机使能）
  GAIT_STAND_R = 2,             // 位控站立、RecoveryStand
  GAIT_STAND_B = 3,             // 力控站立、姿态展示、BalanceStand
  GAIT_RUN_FAST = 8,            // 快跑
  GAIT_DOWN_CLIMB_STAIRS = 9,   // 下爬楼梯=>盲走=>慢跑
  GAIT_TROT = 10,               // 小跑
  GAIT_PRONK = 11,              // 跳跃
  GAIT_BOUND = 12,              // 前后跳
  GAIT_AMBLE = 14,              // 交叉步
  GAIT_CRAWL = 29,              // 爬行
  GAIT_LOWLEVL_SDK = 30,        // 低层SDK步态
  GAIT_WALK = 39,               // 缓走
  GAIT_UP_CLIMB_STAIRS = 56,    // 上爬楼梯（全地形）
  GAIT_RL_TERRAIN = 110,        // 全地形
  GAIT_RL_FALL_RECOVERY = 111,  // 跌倒爬起
  GAIT_RL_HAND_STAND = 112,     // 倒立
  GAIT_RL_FOOT_STAND = 113,     // 正立
  GAIT_ENTER_RL = 1001,         // 进入RL
  GAIT_DEFAULT = 99,            // 默认
  GAIT_NONE = 9999,             // 无步态
};

/**
 * @brief 人形机器人动作指令枚举（对应动作ID）
 */
enum class TrickAction : int32_t {
  ACTION_NONE = 0,
  ACTION_WIGGLE_HIP = 26,             // 扭屁股
  ACTION_SWING_BODY = 27,             // 甩身
  ACTION_STRETCH = 28,                // 伸懒腰
  ACTION_STOMP = 29,                  // 跺脚
  ACTION_JUMP_JACK = 30,              // 开合跳
  ACTION_SPACE_WALK = 31,             // 太空步
  ACTION_IMITATE = 32,                // 模仿
  ACTION_SHAKE_HEAD = 33,             // 摇头
  ACTION_PUSH_UP = 34,                // 俯卧撑
  ACTION_CHEER_UP = 35,               // 加油
  ACTION_HIGH_FIVES = 36,             // 击掌
  ACTION_SCRATCH = 37,                // 挠痒
  ACTION_HIGH_JUMP = 38,              // 跳高
  ACTION_SWING_DANCE = 39,            // 摇摆舞
  ACTION_LEAP_FROG = 40,              // 蛙跳
  ACTION_BACK_FLIP = 41,              // 后空翻
  ACTION_FRONT_FLIP = 42,             // 前空翻
  ACTION_SPIN_JUMP_LEFT = 43,         // 旋转左跳70度
  ACTION_SPIN_JUMP_RIGHT = 44,        // 旋转右跳70度
  ACTION_JUMP_FRONT = 45,             // 前跳0.5米
  ACTION_ACT_CUTE = 46,               // 撒娇
  ACTION_BOXING = 47,                 // 打拳
  ACTION_SIDE_SOMERSAULT = 48,        // 侧空翻
  ACTION_RANDOM_DANCE = 49,           // 随机跳舞
  ACTION_LEFT_SIDE_SOMERSAULT = 84,   // 左侧侧空翻
  ACTION_RIGHT_SIDE_SOMERSAULT = 85,  // 右侧侧空翻
  ACTION_DANCE2 = 91,                 // 跳舞2
  ACTION_EMERGENCY_STOP = 101,        // 急停
  ACTION_LIE_DOWN = 102,              // 趴下
  ACTION_RECOVERY_STAND = 103,        // 起立
  ACTION_HAPPY_NEW_YEAR = 105,        // 拜年=作揖
  ACTION_SLOW_GO_FRONT = 108,         // 过来
  ACTION_SLOW_GO_BACK = 109,          // 后退
  ACTION_BACK_HOME = 110,             // 回窝
  ACTION_LEAVE_HOME = 111,            // 离窝
  ACTION_TURN_AROUND = 112,           // 转圈
  ACTION_DANCE = 115,                 // 跳舞
  ACTION_ROLL_ABOUT = 116,            // 打滚
  ACTION_SHAKE_RIGHT_HAND = 117,      // 握右手
  ACTION_SHAKE_LEFT_HAND = 118,       // 握左手
  ACTION_SIT_DOWN = 119,              // 坐下
};

/**
 * @brief 高层运动控制摇杆指令的数据结构
 */
struct JoystickCommand {
  /**
   * @brief 左侧摇杆的X轴方向值
   *
   * 该值表示左侧摇杆沿X轴方向的输入，范围从 -1.0 到 1.0。
   * -1.0 表示左移，1.0 表示右移，0 表示中立位置。
   */
  float left_x_axis;

  /**
   * @brief 左侧摇杆的Y轴方向值
   *
   * 该值表示左侧摇杆沿Y轴方向的输入，范围从 -1.0 到 1.0。
   * -1.0 表示下移，1.0 表示上移，0 表示中立位置。
   */
  float left_y_axis;

  /**
   * @brief 右侧摇杆的X轴方向值
   *
   * 该值表示右侧摇杆沿Z轴方向的旋转，范围从 -1.0 到 1.0。
   * -1.0 表示左旋转，1.0 表示右旋转，0 表示中立位置。
   */
  float right_x_axis;

  /**
   * @brief 右侧摇杆的Y轴方向值，待定
   */
  float right_y_axis;
};

/**
 * @brief 步态以及对应 前进、横移、旋转 速度比例
 */
struct GaitSpeedRatio {
  double straight_ratio;
  double turn_ratio;
  double lateral_ratio;
};

/**
 * @brief 所有步态以及对应 前进、横移、旋转 速度比例
 */
struct AllGaitSpeedRatio {
  std::map<GaitMode, GaitSpeedRatio> gait_speed_ratios;
};

/**
 * @brief 单个下肢关节的控制命令
 */
struct SingleLegJointCommand {
  float q_des = 0.0;    // desired joint position
  float dq_des = 0.0;   // desired joint velocity
  float tau_des = 0.0;  // desired feed-forward torque

  float kp = 0.0;  // P gain, must be positive
  float kd = 0.0;  // D gain, must be positive, must be positive
};

/**
 * @brief 整个下肢控制命令
 */
struct LegJointCommand {
  int64_t timestamp;                                    ///< 时间戳（单位：纳秒）
  std::array<SingleLegJointCommand, kLegJointNum> cmd;  ///< 控制命令数组，依次为左手和右手
};

/**
 * @brief 单个下肢关节的状态
 */
struct SingleLegJointState {
  float q = 0.0;
  float dq = 0.0;
  float tau_est = 0.0;
};

/**
 * @brief 整个下肢状态信息
 */
struct LegState {
  int64_t timestamp;                                    ///< 时间戳（单位：纳秒）
  std::array<SingleLegJointState, kLegJointNum> state;  ///< 所有下肢关节状态
};

/************************************************************
 *                        语音控制                           *
 ************************************************************/

/**
 * @brief TTS 播报优先级等级
 *
 * 用于控制不同TTS任务之间的中断行为。优先级越高的任务将中断当前低优先级任务的播放。
 */
enum class TtsPriority : int8_t {
  HIGH = 0,    ///< 最高优先级，例如：低电告警、紧急提醒
  MIDDLE = 1,  ///< 中优先级，例如：系统提示、状态播报
  LOW = 2      ///< 最低优先级，例如：日常语音对话、背景播报
};

/**
 * @brief 同一优先级下的任务调度策略
 *
 * 用于细化控制在相同优先级条件下多个TTS任务的播放顺序和清除逻辑。
 */
enum class TtsMode : int8_t {
  CLEARTOP = 0,    ///< 清空当前优先级所有任务（包括正在播放和等待队列），立即播放本次请求
  ADD = 1,         ///< 将本次请求追加到当前优先级队列尾部，顺序播放（不打断当前播放）
  CLEARBUFFER = 2  ///< 清空队列中未播放的请求，保留当前播放，之后播放本次请求
};

/**
 * @brief TTS（Text-To-Speech）播放命令结构体
 *
 * 用于描述一次TTS播放请求的完整信息，支持设置唯一标识、文本内容、优先级控制以及相同优先级下的调度模式。
 *
 * 场景举例：播放天气播报、电量提醒等语音内容时，根据优先级和模式决定播报顺序和中断行为。
 */
typedef struct tts_cmd {
  /**
   * @brief TTS任务唯一ID
   *
   * 用于标识一次TTS任务，在后续回调中追踪TTS状态（如开始播放、播放完成等）。
   * 例如："id_01"
   */
  std::string id;
  /**
   * @brief 要播放的文本内容
   *
   * 支持任意可朗读的UTF-8字符串，例如："你好，欢迎使用智能语音系统。"
   */
  std::string content;
  /**
   * @brief 播报优先级
   *
   * 控制不同TTS请求之间的中断关系，优先级越高的请求会打断正在播放的低优先级请求。
   */
  TtsPriority priority;
  /**
   * @brief 同优先级下的调度模式
   *
   * 控制在相同优先级情况下多个TTS请求的处理逻辑，避免无限扩展优先级值。
   */
  TtsMode mode;
} TtsCommand;

/************************************************************
 *                         传感器                            *
 ************************************************************/

/**
 * @brief IMU 数据结构体，包含时间戳、姿态、角速度、加速度和温度信息
 */
struct Imu {
  int64_t timestamp;                          ///< 时间戳（单位：纳秒），表示该IMU数据采集的时间点
  std::array<double, 4> orientation;          ///< 姿态四元数（w, x, y, z），用于表示空间姿态，避免欧拉角万向锁问题
  std::array<double, 3> angular_velocity;     ///< 角速度（单位：rad/s），绕X、Y、Z轴的角速度，通常来自陀螺仪
  std::array<double, 3> linear_acceleration;  ///< 线加速度（单位：m/s^2），X、Y、Z轴的线性加速度，通常来自加速度计
  float temperature;                          ///< 温度（单位：摄氏度或其他，应在使用时明确）
};

/**
 * @brief Header结构，包含时间戳与帧名
 */
struct Header {
  int64_t stamp;         ///< 时间戳，单位：纳秒
  std::string frame_id;  ///< 坐标系名称
};

/**
 * @brief 点云字段描述结构体，对应于ROS2中的sensor_msgs::msg::PointField。
 */
struct PointField {
  std::string name;  ///< 字段名，例如"x"、"y"、"z"、"intensity"等
  int32_t offset;    ///< 起始字节偏移
  int8_t datatype;   ///< 数据类型（对应常量）
  int32_t count;     ///< 该字段包含的元素数量
};

/**
 * @brief 通用点云数据结构，类似于 ROS2 的 sensor_msgs::msg::PointCloud2
 */
struct PointCloud2 {
  Header header;  ///< 标准消息头

  int32_t height;  ///< 行数
  int32_t width;   ///< 列数

  std::vector<PointField> fields;  ///< 点字段数组

  bool is_bigendian;   ///< 字节序
  int32_t point_step;  ///< 每个点占用的字节数
  int32_t row_step;    ///< 每行占用的字节数

  std::vector<uint8_t> data;  ///< 原始点云数据（按字段打包）

  bool is_dense;  ///< 是否为稠密点云（无无效点）
};

/**
 * @brief 图像数据结构，支持多种编码格式
 */
struct Image {
  Header header;

  int32_t height;  ///< 图像高度（像素）
  int32_t width;   ///< 图像宽度（像素）

  std::string encoding;  ///< 图像编码类型，如 "rgb8", "mono8", "bgr8"
  bool is_bigendian;     ///< 数据是否为大端模式
  int32_t step;          ///< 每行图像占用的字节数

  std::vector<uint8_t> data;  ///< 原始图像字节数据
};

/**
 * @brief 相机内参与畸变信息，通常与 Image 消息一起发布
 */
struct CameraInfo {
  Header header;

  int32_t height;  ///< 图像高度（行数）
  int32_t width;   ///< 图像宽度（列数）

  std::string distortion_model;  ///< 畸变模型，例如 "plumb_bob"

  std::vector<double> D;  ///< 畸变参数数组

  std::array<double, 9> K;   ///< 相机内参矩阵
  std::array<double, 9> R;   ///< 矫正矩阵
  std::array<double, 12> P;  ///< 投影矩阵

  int32_t binning_x;  ///< 水平binning系数
  int32_t binning_y;  ///< 垂直binning系数

  int32_t roi_x_offset;  ///< ROI起始x
  int32_t roi_y_offset;  ///< ROI起始y
  int32_t roi_height;    ///< ROI高度
  int32_t roi_width;     ///< ROI宽度
  bool roi_do_rectify;   ///< 是否进行矫正
};

/**
 * @brief 三目相机帧数据结构，包含采集/解码时间和三个图像帧
 */
struct TrinocularCameraFrame {
  Header header;  ///< 通用消息头（时间戳+frame_id）

  int64_t vin_time;     ///< 图像采集时间戳，单位：纳秒
  int64_t decode_time;  ///< 图像解码完成时间戳，单位：纳秒

  std::vector<uint8_t> imgfl_array;  ///< 左目图像数据
  std::vector<uint8_t> imgf_array;   ///< 中目图像数据
  std::vector<uint8_t> imgfr_array;  ///< 右目图像数据
};

/**
 * @brief 压缩图像数据结构，支持多种压缩格式
 */
struct CompressedImage {
  Header header;

  std::string format;
  std::vector<uint8_t> data;
};

/**
 * @brief 激光雷达数据结构，支持多种格式
 */
struct LaserScan {
  Header header;

  int32_t angle_min;
  int32_t angle_max;
  int32_t angle_increment;
  int32_t time_increment;
  int32_t scan_time;
  int32_t range_min;
  int32_t range_max;
  std::vector<double> ranges;
  std::vector<double> intensities;
};

/**
 * @brief 多维数组维度描述
 */
struct MultiArrayDimension {
  std::string label;
  int32_t size;
  int32_t stride;
};

/**
 * @brief 多维数组布局描述
 */
struct MultiArrayLayout {
  int32_t dim_size;
  std::vector<MultiArrayDimension> dim;
  int32_t data_offset;
};

/**
 * @brief 浮点数多维数组
 */
struct Float32MultiArray {
  MultiArrayLayout layout;
  std::vector<float> data;
};

/**
 * @brief 字节数组
 */
struct ByteMultiArray {
  MultiArrayLayout layout;
  std::vector<uint8_t> data;
};

/**
 * @brief 8位整数数据结构
 */
struct Int8 {
  int8_t data;
};

/**
 * @brief 头部触摸数据结构
 */
using HeadTouch = Int8;

class NonCopyable {
 protected:
  NonCopyable() = default;
  ~NonCopyable() = default;
  NonCopyable(NonCopyable&&) = default;
  NonCopyable& operator=(NonCopyable&&) = default;
  NonCopyable(const NonCopyable&) = delete;
  NonCopyable& operator=(const NonCopyable&) = delete;
};

/**
 * @brief 自定义智能体配置
 */
struct CustomBotInfo {
  std::string name;      // 智能体名称
  std::string workflow;  // 工作流id
  std::string token;     // 用户授权token
};

/**
 * @brief 自定义智能体映射表
 */
using CustomBotMap = std::map<std::string, CustomBotInfo>;

/**
 * @brief 语音配置参数
 */
struct SetSpeechConfig {
  std::string speaker_id;     // 音色id
  std::string region;         // 音色地区
  std::string bot_id;         // 模式id
  bool is_front_doa;          // 是否强制正常向识别
  bool is_fullduplex_enable;  // 自然对话
  bool is_enable;             // 语音开关
  bool is_doa_enable;         // 是否打开唤醒方位转头
  float speaker_speed;        // TTS播放语速范围[1,2]
  std::string wakeup_name;    // 唤醒名字
  CustomBotMap custom_bot;    // 自定义智能体
};

struct SpeakerConfigSelected {
  std::string region;      // 选中的地区
  std::string speaker_id;  // 选中的音色ID
};

/**
 * @brief 音色配置结构体
 */
struct SpeakerConfig {
  std::map<std::string, std::vector<std::array<std::string, 2>>> data;  // 音色数据：地区->音色ID->音色名称
  SpeakerConfigSelected selected;
  float speaker_speed;  // 语速
};

/**
 * @brief 智能体配置信息
 */
struct BotInfo {
  std::string name;      // 工作场景名称
  std::string workflow;  // 工作流ID
};

struct BotConfigSelected {
  std::string bot_id;  // 选中的智能体ID
};

/**
 * @brief 智能体配置结构体
 */
struct BotConfig {
  std::map<std::string, BotInfo> data;               // 标准智能体数据：智能体ID->智能体信息
  std::map<std::string, CustomBotInfo> custom_data;  // 自定义智能体数据：智能体ID->自定义智能体信息
  BotConfigSelected selected;
};

/**
 * @brief 唤醒配置结构体
 */
struct WakeupConfig {
  std::string name;                         // 唤醒名称
  std::map<std::string, std::string> data;  // 唤醒词数据：唤醒词->拼音
};

/**
 * @brief 对话配置结构体
 */
struct DialogConfig {
  bool is_front_doa;          // 是否强制正前方加强拾音
  bool is_fullduplex_enable;  // 是否打开全双工对话
  bool is_enable;             // 是否打开语音
  bool is_doa_enable;         // 是否打开唤醒方位转头
};

enum class TtsType {
  NONE = 0,
  DOUBAO = 1,
  GOOGLE = 2,
};

/**
 * @brief 语音系统完整配置结构体
 */
struct GetSpeechConfig {
  SpeakerConfig speaker_config;      // 音色配置
  BotConfig bot_config;              // 智能体配置
  WakeupConfig wakeup_config;        // 唤醒配置
  DialogConfig dialog_config;        // 对话配置
  TtsType tts_type = TtsType::NONE;  // 语音模型
};

inline SetSpeechConfig ToSetSpeechConfig(const GetSpeechConfig& get_speech_config) {
  SetSpeechConfig set_speech_config;
  set_speech_config.speaker_id = get_speech_config.speaker_config.selected.speaker_id;
  set_speech_config.region = get_speech_config.speaker_config.selected.region;
  set_speech_config.bot_id = get_speech_config.bot_config.selected.bot_id;
  set_speech_config.is_front_doa = get_speech_config.dialog_config.is_front_doa;
  set_speech_config.is_fullduplex_enable = get_speech_config.dialog_config.is_fullduplex_enable;
  set_speech_config.is_enable = get_speech_config.dialog_config.is_enable;
  set_speech_config.is_doa_enable = get_speech_config.dialog_config.is_doa_enable;
  set_speech_config.speaker_speed = get_speech_config.speaker_config.speaker_speed;
  set_speech_config.wakeup_name = get_speech_config.wakeup_config.name;
  set_speech_config.custom_bot = get_speech_config.bot_config.custom_data;
  return set_speech_config;
}
}  // namespace magic::dog
