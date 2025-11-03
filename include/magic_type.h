#pragma once

#include <array>
#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace magic::dog {

/************************************************************
 *                        Constants                         *
 ************************************************************/

constexpr uint8_t kLegJointNum = 12;  ///< Number of leg joints

/************************************************************
 *                        Interface Info                    *
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
 *                        State Info                        *
 ************************************************************/
/**
 * @brief Fault information structure
 *
 * Used to represent error information that occurs in the system, including error code and error message.
 */
struct Fault {
  /**
   * @brief Error code
   *
   * Integer value used to identify the specific type of exception. Different error codes can correspond to different error types for error management and handling.
   */
  int32_t error_code;

  /**
   * @brief Error message
   *
   * Describes the specific information of the error, usually a detailed description of the cause of the error, which is convenient for debugging and locating problems.
   */
  std::string error_message;
};

/**
 * @brief Battery state enumeration type
 *
 * Indicates the current state of the battery, including multiple possible battery state options, used for battery state judgment and handling in the system.
 */
enum class BatteryState : int8_t {
  UNKNOWN = 0,                ///< Unknown state
  GOOD = 1,                   ///< Battery is good
  OVERHEAT = 2,               ///< Battery overheated
  DEAD = 3,                   ///< Battery damaged
  OVERVOLTAGE = 4,            ///< Battery overvoltage
  UNSPEC_FAILURE = 5,         ///< Unknown failure
  COLD = 6,                   ///< Battery too cold
  WATCHDOG_TIMER_EXPIRE = 7,  ///< Watchdog timer expired
  SAFETY_TIMER_EXPIRE = 8,    ///< Safety timer expired
};

/**
 * @brief Battery charge/discharge status
 */
enum class PowerSupplyStatus : int8_t {
  UNKNOWN = 0,      ///< Unknown state
  CHARGING = 1,     ///< Battery charging
  DISCHARGING = 2,  ///< Battery discharging
  NOTCHARGING = 3,  ///< Battery not charging/discharging
  FULL = 4,         ///< Battery full
};

/**
 * @brief Battery management system data structure
 *
 * Used to store battery-related information, including remaining battery percentage, battery health, battery state, and charge status.
 */
typedef struct bms_data {
  /**
   * @brief Remaining battery percentage
   *
   * The current battery percentage, ranging from 0 to 100, indicating the remaining battery.
   */
  double battery_percentage;

  /**
   * @brief Battery health
   *
   * The health status of the battery, usually a doubleing value representing battery performance. The higher the value, the better the battery.
   */
  double battery_health;

  /**
   * @brief Battery state
   *
   * The current state of the battery, used to indicate different battery states.
   */
  BatteryState battery_state;

  /**
   * @brief Charge status
   *
   * A boolean value indicating whether the battery is charging. `true` means charging, `false` means not charging.
   */
  PowerSupplyStatus power_supply_status;
} BmsData;

typedef struct robot_state {
  std::vector<Fault> faults;  ///< List of fault information
  BmsData bms_data;           ///< Battery management system data
} RobotState;

/************************************************************
 *                        Motion Control                    *
 ************************************************************/

/**
 * @brief Controller level type, used to distinguish different controller responsibilities.
 */
enum class ControllerLevel : int8_t {
  UNKKOWN = 0,
  HighLevel = 1,  ///< High-level controller
  LowLevel = 2    ///< Low-level controller
};

/**
 * @brief Robot gait mode enumeration, suitable for state machine control
 */
enum class GaitMode : int32_t {
  GAIT_PASSIVE = 0,             // Drop (disable motor enable)
  GAIT_STAND_R = 2,             // Position control stand, RecoveryStand
  GAIT_STAND_B = 3,             // Force control stand, pose show, BalanceStand
  GAIT_RUN_FAST = 8,            // Fast run
  GAIT_DOWN_CLIMB_STAIRS = 9,   // Down stairs => blind walk => slow run
  GAIT_TROT = 10,               // Trot
  GAIT_PRONK = 11,              // Jump
  GAIT_BOUND = 12,              // Bound (front-back jump)
  GAIT_AMBLE = 14,              // Amble (cross step)
  GAIT_CRAWL = 29,              // Crawl
  GAIT_LOWLEVL_SDK = 30,        // Low-level SDK gait
  GAIT_WALK = 39,               // Walk
  GAIT_UP_CLIMB_STAIRS = 56,    // Up stairs (all terrain)
  GAIT_RL_TERRAIN = 110,        // All terrain
  GAIT_RL_FALL_RECOVERY = 111,  // Fall recovery
  GAIT_RL_HAND_STAND = 112,     // Handstand
  GAIT_RL_FOOT_STAND = 113,     // Upright
  GAIT_ENTER_RL = 1001,         // Enter RL
  GAIT_DEFAULT = 99,            // Default
  GAIT_NONE = 9999,             // No gait
};

/**
 * @brief Humanoid robot trick action enumeration (corresponding to action ID)
 */
enum class TrickAction : int32_t {
  ACTION_NONE = 0,
  ACTION_WIGGLE_HIP = 26,             // Wiggle hip
  ACTION_SWING_BODY = 27,             // Swing body
  ACTION_STRETCH = 28,                // Stretch
  ACTION_STOMP = 29,                  // Stomp
  ACTION_JUMP_JACK = 30,              // Jump jack
  ACTION_SPACE_WALK = 31,             // Space walk
  ACTION_IMITATE = 32,                // Imitate
  ACTION_SHAKE_HEAD = 33,             // Shake head
  ACTION_PUSH_UP = 34,                // Push up
  ACTION_CHEER_UP = 35,               // Cheer up
  ACTION_HIGH_FIVES = 36,             // High fives
  ACTION_SCRATCH = 37,                // Scratch
  ACTION_HIGH_JUMP = 38,              // High jump
  ACTION_SWING_DANCE = 39,            // Swing dance
  ACTION_LEAP_FROG = 40,              // Leap frog
  ACTION_BACK_FLIP = 41,              // Back flip
  ACTION_FRONT_FLIP = 42,             // Front flip
  ACTION_SPIN_JUMP_LEFT = 43,         // Spin jump left 70 degrees
  ACTION_SPIN_JUMP_RIGHT = 44,        // Spin jump right 70 degrees
  ACTION_JUMP_FRONT = 45,             // Jump forward 0.5m
  ACTION_ACT_CUTE = 46,               // Act cute
  ACTION_BOXING = 47,                 // Boxing
  ACTION_SIDE_SOMERSAULT = 48,        // Side somersault
  ACTION_RANDOM_DANCE = 49,           // Random dance
  ACTION_LEFT_SIDE_SOMERSAULT = 84,   // Left side somersault
  ACTION_RIGHT_SIDE_SOMERSAULT = 85,  // Right side somersault
  ACTION_DANCE2 = 91,                 // Dance 2
  ACTION_EMERGENCY_STOP = 101,        // Emergency stop
  ACTION_LIE_DOWN = 102,              // Lie down
  ACTION_RECOVERY_STAND = 103,        // Stand up
  ACTION_HAPPY_NEW_YEAR = 105,        // New Year greeting
  ACTION_SLOW_GO_FRONT = 108,         // Come here
  ACTION_SLOW_GO_BACK = 109,          // Go back
  ACTION_BACK_HOME = 110,             // Go home
  ACTION_LEAVE_HOME = 111,            // Leave home
  ACTION_TURN_AROUND = 112,           // Turn around
  ACTION_DANCE = 115,                 // Dance
  ACTION_ROLL_ABOUT = 116,            // Roll about
  ACTION_SHAKE_RIGHT_HAND = 117,      // Shake right hand
  ACTION_SHAKE_LEFT_HAND = 118,       // Shake left hand
  ACTION_SIT_DOWN = 119,              // Sit down
};

/**
 * @brief High-level motion control joystick command data structure
 */
struct JoystickCommand {
  /**
   * @brief X-axis value of the left joystick
   *
   * This value represents the input of the left joystick along the X-axis, ranging from -1.0 to 1.0.
   * -1.0 means left, 1.0 means right, 0 means neutral.
   */
  double left_x_axis;

  /**
   * @brief Y-axis value of the left joystick
   *
   * This value represents the input of the left joystick along the Y-axis, ranging from -1.0 to 1.0.
   * -1.0 means down, 1.0 means up, 0 means neutral.
   */
  double left_y_axis;

  /**
   * @brief X-axis value of the right joystick
   *
   * This value represents the rotation of the right joystick along the Z-axis, ranging from -1.0 to 1.0.
   * -1.0 means rotate left, 1.0 means rotate right, 0 means neutral.
   */
  double right_x_axis;

  /**
   * @brief Y-axis value of the right joystick, TBD
   */
  double right_y_axis;
};

/**
 * @brief Gait and corresponding speed ratios for forward, lateral, and turning
 */
struct GaitSpeedRatio {
  double straight_ratio;
  double turn_ratio;
  double lateral_ratio;
};

/**
 * @brief All gaits and corresponding speed ratios for forward, lateral, and turning
 */
struct AllGaitSpeedRatio {
  std::map<GaitMode, GaitSpeedRatio> gait_speed_ratios;
};

/**
 * @brief Single leg joint control command
 */
struct SingleLegJointCommand {
  double q_des = 0.0;    // desired joint position
  double dq_des = 0.0;   // desired joint velocity
  double tau_des = 0.0;  // desired feed-forward torque

  double kp = 0.0;  // P gain, must be positive
  double kd = 0.0;  // D gain, must be positive
};

/**
 * @brief Whole leg joint control command
 */
struct LegJointCommand {
  int64_t timestamp;                                    ///< Timestamp (ns)
  std::array<SingleLegJointCommand, kLegJointNum> cmd;  ///< Command array, in order of left and right
};

/**
 * @brief Single leg joint state
 */
struct SingleLegJointState {
  double q = 0.0;
  double dq = 0.0;
  double tau_est = 0.0;
};

/**
 * @brief Whole leg state information
 */
struct LegState {
  int64_t timestamp;                                    ///< Timestamp (ns)
  std::array<SingleLegJointState, kLegJointNum> state;  ///< All leg joint states
};

/************************************************************
 *                        Speech Control                    *
 ************************************************************/

/**
 * @brief TTS playback priority level
 *
 * Used to control interruption behavior between different TTS tasks. Higher priority tasks will interrupt currently playing lower priority tasks.
 */
enum class TtsPriority : int8_t {
  HIGH = 0,    ///< Highest priority, e.g., low battery warning, emergency alert
  MIDDLE = 1,  ///< Medium priority, e.g., system prompt, status broadcast
  LOW = 2      ///< Lowest priority, e.g., daily voice chat, background broadcast
};

/**
 * @brief Task scheduling strategy under the same priority
 *
 * Used to refine the playback order and clearing logic of multiple TTS tasks under the same priority.
 */
enum class TtsMode : int8_t {
  CLEARTOP = 0,    ///< Clear all tasks of current priority (including playing and waiting queue), play this request immediately
  ADD = 1,         ///< Append this request to the end of the current priority queue, play in order (do not interrupt current playback)
  CLEARBUFFER = 2  ///< Clear unplayed requests in the queue, keep current playback, then play this request
};

/**
 * @brief TTS (Text-To-Speech) playback command structure
 *
 * Used to describe the complete information of a TTS playback request, supporting unique ID, text content, priority control, and scheduling mode under the same priority.
 *
 * Example: When playing weather broadcast, battery reminder, etc., the playback order and interruption behavior are determined according to priority and mode.
 */
typedef struct tts_cmd {
  /**
   * @brief Unique ID of TTS task
   *
   * Used to identify a TTS task, and track TTS status (such as start, finish, etc.) in subsequent callbacks.
   * For example: "id_01"
   */
  std::string id;
  /**
   * @brief Text content to play
   *
   * Supports any readable UTF-8 string, e.g., "Hello, welcome to the intelligent voice system."
   */
  std::string content;
  /**
   * @brief Playback priority
   *
   * Controls the interruption relationship between different TTS requests. Higher priority requests will interrupt currently playing lower priority requests.
   */
  TtsPriority priority;
  /**
   * @brief Scheduling mode under the same priority
   *
   * Controls the processing logic of multiple TTS requests under the same priority, avoiding unlimited expansion of priority values.
   */
  TtsMode mode;
} TtsCommand;

/************************************************************
 *                         Sensors                          *
 ************************************************************/

/**
 * @brief IMU data structure, including timestamp, orientation, angular velocity, acceleration, and temperature
 */
struct Imu {
  int64_t timestamp;                          ///< Timestamp (ns), indicates the time point of IMU data acquisition
  std::array<double, 4> orientation;          ///< Orientation quaternion (w, x, y, z), used to represent spatial orientation, avoiding gimbal lock of Euler angles
  std::array<double, 3> angular_velocity;     ///< Angular velocity (rad/s), angular velocity around X, Y, Z axes, usually from gyroscope
  std::array<double, 3> linear_acceleration;  ///< Linear acceleration (m/s^2), X, Y, Z axis linear acceleration, usually from accelerometer
  double temperature;                         ///< Temperature (Celsius or other, should be specified when used)
};

/**
 * @brief Header structure, including timestamp and frame name
 */
struct Header {
  int64_t stamp;         ///< Timestamp, unit: ns
  std::string frame_id;  ///< Coordinate frame name
};

/**
 * @brief Point cloud field description structure, corresponding to ROS2 sensor_msgs::msg::PointField.
 */
struct PointField {
  std::string name;  ///< Field name, e.g., "x", "y", "z", "intensity", etc.
  int32_t offset;    ///< Start byte offset
  int8_t datatype;   ///< Data type (corresponding constant)
  int32_t count;     ///< Number of elements in this field
};

/**
 * @brief Generic point cloud data structure, similar to ROS2 sensor_msgs::msg::PointCloud2
 */
struct PointCloud2 {
  Header header;  ///< Standard message header

  int32_t height;  ///< Number of rows
  int32_t width;   ///< Number of columns

  std::vector<PointField> fields;  ///< Point field array

  bool is_bigendian;   ///< Endianness
  int32_t point_step;  ///< Number of bytes per point
  int32_t row_step;    ///< Number of bytes per row

  std::vector<uint8_t> data;  ///< Raw point cloud data (packed by field)

  bool is_dense;  ///< Whether it is a dense point cloud (no invalid points)
};

/**
 * @brief Image data structure, supports multiple encoding formats
 */
struct Image {
  Header header;

  int32_t height;  ///< Image height (pixels)
  int32_t width;   ///< Image width (pixels)

  std::string encoding;  ///< Image encoding type, such as "rgb8", "mono8", "bgr8"
  bool is_bigendian;     ///< Whether the data is in big-endian mode
  int32_t step;          ///< Number of bytes per image row

  std::vector<uint8_t> data;  ///< Raw image byte data
};

/**
 * @brief Camera intrinsic and distortion information, usually published with Image message
 */
struct CameraInfo {
  Header header;

  int32_t height;  ///< Image height (rows)
  int32_t width;   ///< Image width (columns)

  std::string distortion_model;  ///< Distortion model, e.g., "plumb_bob"

  std::vector<double> D;  ///< Distortion parameter array

  std::array<double, 9> K;   ///< Camera intrinsic matrix
  std::array<double, 9> R;   ///< Rectification matrix
  std::array<double, 12> P;  ///< Projection matrix

  int32_t binning_x;  ///< Horizontal binning factor
  int32_t binning_y;  ///< Vertical binning factor

  int32_t roi_x_offset;  ///< ROI start x
  int32_t roi_y_offset;  ///< ROI start y
  int32_t roi_height;    ///< ROI height
  int32_t roi_width;     ///< ROI width
  bool roi_do_rectify;   ///< Whether to rectify
};

/**
 * @brief Trinocular camera frame data structure, including acquisition/decoding time and three image frames
 */
struct TrinocularCameraFrame {
  Header header;  ///< Common message header (timestamp + frame_id)

  int64_t vin_time;     ///< Image acquisition timestamp, unit: ns
  int64_t decode_time;  ///< Image decoding completion timestamp, unit: ns

  std::vector<uint8_t> imgfl_array;  ///< Left image data
  std::vector<uint8_t> imgf_array;   ///< Middle image data
  std::vector<uint8_t> imgfr_array;  ///< Right image data
};

/**
 * @brief Compressed image data structure, supports multiple compression formats
 */
struct CompressedImage {
  Header header;

  std::string format;
  std::vector<uint8_t> data;
};

/**
 * @brief Lidar data structure, supports multiple formats
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
 * @brief Multi-dimensional array dimension description
 */
struct MultiArrayDimension {
  std::string label;
  int32_t size;
  int32_t stride;
};

/**
 * @brief Multi-dimensional array layout description
 */
struct MultiArrayLayout {
  int32_t dim_size;
  std::vector<MultiArrayDimension> dim;
  int32_t data_offset;
};

/**
 * @brief Float multi-dimensional array
 */
struct Float32MultiArray {
  MultiArrayLayout layout;
  std::vector<double> data;
};

/**
 * @brief Byte array
 */
struct ByteMultiArray {
  MultiArrayLayout layout;
  std::vector<uint8_t> data;
};

/**
 * @brief 8-bit integer data structure
 */
struct Int8 {
  int8_t data;
};

/**
 * @brief Head touch data structure
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
 * @brief Custom bot configuration
 */
struct CustomBotInfo {
  std::string name;      // Bot name
  std::string workflow;  // Workflow id
  std::string token;     // User authorization token
};

/**
 * @brief Custom bot mapping table
 */
using CustomBotMap = std::map<std::string, CustomBotInfo>;

/**
 * @brief Speech configuration parameters
 */
struct SetSpeechConfig {
  std::string speaker_id;     // Speaker id
  std::string region;         // Speaker region
  std::string bot_id;         // Mode id
  bool is_front_doa;          // Whether to force front direction recognition
  bool is_fullduplex_enable;  // Natural conversation
  bool is_enable;             // Speech switch
  bool is_doa_enable;         // Whether to enable wakeup direction head turning
  double speaker_speed;       // TTS playback speed range [1,2]
  std::string wakeup_name;    // Wakeup name
  CustomBotMap custom_bot;    // Custom bot
};

struct SpeakerConfigSelected {
  std::string region;      // Selected region
  std::string speaker_id;  // Selected speaker ID
};

/**
 * @brief Speaker configuration structure
 */
struct SpeakerConfig {
  std::map<std::string, std::vector<std::vector<std::string>>> data;  // Speaker data: region->speaker ID->speaker name
  SpeakerConfigSelected selected;
  double speaker_speed;  // Speed
};

/**
 * @brief Bot configuration info
 */
struct BotInfo {
  std::string name;      // Work scene name
  std::string workflow;  // Workflow ID
};

struct BotConfigSelected {
  std::string bot_id;  // Selected bot ID
};

/**
 * @brief Bot configuration structure
 */
struct BotConfig {
  std::map<std::string, BotInfo> data;               // Standard bot data: bot ID->bot info
  std::map<std::string, CustomBotInfo> custom_data;  // Custom bot data: bot ID->custom bot info
  BotConfigSelected selected;
};

/**
 * @brief Wakeup configuration structure
 */
struct WakeupConfig {
  std::string name;                         // Wakeup name
  std::map<std::string, std::string> data;  // Wakeup word data: wakeup word->pinyin
};

/**
 * @brief Dialog configuration structure
 */
struct DialogConfig {
  bool is_front_doa;          // Whether to force front direction enhanced pickup
  bool is_fullduplex_enable;  // Whether to enable full-duplex dialog
  bool is_enable;             // Whether to enable speech
  bool is_doa_enable;         // Whether to enable wakeup direction head turning
};

enum class TtsType {
  NONE = 0,
  DOUBAO = 1,
  GOOGLE = 2,
};

/**
 * @brief Complete speech system configuration structure
 */
struct GetSpeechConfig {
  SpeakerConfig speaker_config;      // Speaker configuration
  BotConfig bot_config;              // Bot configuration
  WakeupConfig wakeup_config;        // Wakeup configuration
  DialogConfig dialog_config;        // Dialog configuration
  TtsType tts_type = TtsType::NONE;  // Speech model
};

/************************************************************
 *                     Slam and Navigation                  *
 ************************************************************/

/**
 * @brief Navigation mode enumeration type
 */
enum class NavMode {
  IDLE = 0,      // Idle mode
  GRID_MAP = 1,  // Grid map navigation mode
};

/**
 * @brief 3D pose structure
 */
struct Pose3DEuler {
  std::array<double, 3> position;     ///< Position (x, y, z), used to represent spatial position
  std::array<double, 3> orientation;  ///< Euler angles (roll, pitch, yaw), used to represent spatial attitude, avoiding Euler angle gimbal lock issues
};

/**
 * @brief Mapping image data structure, .pgm format
 */
struct MapImageData {
  std::string type;             // magic number, "P5": binary format
  uint32_t width = 0;           // image width
  uint32_t height = 0;          // image height
  uint32_t max_gray_value = 0;  // max gray value, 255
  std::vector<uint8_t> image;   // image data
};

/**
 * @brief Mapping map metadata structure
 */
struct MapMetaData {
  double resolution = 0.0;      // Map resolution, unit: m/pixel
  Pose3DEuler origin;           // Map origin, origin of the world coordinate system relative to the map’s lower-left corner
  MapImageData map_image_data;  // image data, .pgm format image data
};

/**
 * @brief Single map information structure
 */
struct MapInfo {
  std::string map_name;       // Map name
  MapMetaData map_meta_data;  // Map metadata
};

/**
 * @brief All map information structure
 */
struct AllMapInfo {
  std::string current_map_name;    // Current map name
  std::vector<MapInfo> map_infos;  // All map information
};

/**
 * @brief Current localization information structure
 */
struct LocalizationInfo {
  bool is_localization = false;  // Whether localized
  Pose3DEuler pose;              // Localization pose in euler angle(rad)
};

/**
 * @brief Global navigation target point structure
 */
struct NavTarget {
  int32_t id = -1;       // Target point ID
  std::string frame_id;  // Target point frame ID
  Pose3DEuler goal;      // Target point pose in quaternion
};

enum class NavStatusType {
  NONE = 0,         // None status
  RUNNING = 1,      // Running
  END_SUCCESS = 2,  // End success
  END_FAILED = 3,   // End failed
  PAUSE = 4,        // Pause
  CONTINUE = 5,     // Continue
  CANCEL = 6,       // Cancel
};

struct NavStatus {
  int32_t id = -1;       // Target point ID, -1 means no target point
  NavStatusType status;  // Navigation status
  std::string message;   // Navigation status message
};

/**
 * @brief Odometry data structure
 */
struct Odometry {
  Header header;                           ///< Generic message header (timestamp + frame_id)
  std::string child_frame_id;              ///< Child frame ID
  std::array<double, 3> position;          ///< Position (x, y, z)
  std::array<double, 4> orientation;       ///< Orientation (w, x, y, z)
  std::array<double, 3> linear_velocity;   ///< Linear velocity (x, y, z)
  std::array<double, 3> angular_velocity;  ///< Angular velocity (x, y, z)
};
}  // namespace magic::dog
