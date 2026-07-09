# viz_nav.py — MagicDog 导航可视化 GUI

基于 **MagicDog Python SDK** 的桌面工具，通过 **gRPC（GrpcOnly）** 连接机载 `eame_app`，在 WiFi / 机器人 AP 网络下完成：

- 高层运动（步态、步态速度比例、特技、虚拟摇杆 20 Hz）
- SLAM 建图与地图管理
- 栅格地图导航（初始位姿、目标点、任务控制）
- 语音 / TTS（Audio，gRPC）
- LCD 表情（Display，gRPC）
- 硬件传感器开关（Sensor，gRPC）
- RTSP 相机预览 + 可选 OpenCV / YOLO 图像检测（不经过 SDK）

---

## 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [界面概览](#界面概览)
- [推荐使用流程](#推荐使用流程)
- [连接时 SDK 初始化](#连接时-sdk-初始化)
- [各页功能与 API 对照](#各页功能与-api-对照)
- [Video 图像检测与模型文件](#video-图像检测与模型文件)
- [操作反馈与日志](#操作反馈与日志)
- [命令行参数](#命令行参数)
- [常见问题](#常见问题)
- [相关文件](#相关文件)

---

## 环境要求

| 项目 | 说明 |
|------|------|
| Python | 3.8+ |
| 系统包 | `python3-tk`（Tkinter） |
| Python 依赖 | 见 `requirements.txt`：`numpy`、`matplotlib`（地图）；`opencv-python`、`Pillow`（Video RTSP）；`ultralytics`（YOLO）；`easyocr`（OCR，可选） |
| SDK | 已编译 `magicdog_python`，产物在 `magicdog_sdk/build/` |
| 网络 | PC 与机器人在同一网段；默认机器人 gRPC `192.168.55.200:50051`，PC 示例 `192.168.55.10` |
| 中文字体（推荐） | `fonts-noto-cjk` 或 `fonts-wqy-microhei`，避免界面与地图中文为方框 |
| Linux RTSP | 系统安装 FFmpeg（OpenCV 拉流），例如 `sudo apt install ffmpeg` |

```bash
# Ubuntu 示例
sudo apt install python3-tk fonts-noto-cjk ffmpeg
pip install -r requirements.txt
```

未安装 OpenCV / Pillow 时仍可启动 GUI，**Video** 页会提示安装依赖，其余 Tab 正常。  
未安装 `ultralytics` 时，Video 页 OpenCV 检测（颜色 / 人脸 / 运动 / ArUco / DNN 等）仍可用，YOLO 相关模式不可用。

---

## 快速开始

```bash
# 1. 编译 SDK（在 magicdog_sdk 根目录）
mkdir -p build && cd build
cmake .. && make -j

# 2. 运行 GUI
cd ../example/python/viz_nav
export PYTHONPATH=/path/to/magicdog_sdk/build:$PYTHONPATH
python3 viz_nav.py --local-ip 192.168.55.10 --robot-ip 192.168.55.200
```

1. 在 **Connection** 栏确认 **Local IP** / **Robot gRPC**，点击 **Connect**。
2. 建图或导航前，在 **Motion** 将步态设为 **Down climb stairs (nav)**。
3. 按下方 [推荐使用流程](#推荐使用流程) 在 **SLAM** → **Nav** 页操作。
4. 底部 **Log · 操作反馈** 查看结果；可拖动分隔条调整日志区高度。

---

## 界面概览

主窗口默认约 **1160×780**（最小 880×560），自上而下：

| 区域 | 内容 |
|------|------|
| 标题栏 | 产品名 + 功能摘要（gRPC · Motion · SLAM · Nav · Audio · Display · Sensor · Video） |
| Connection | Local IP、Robot gRPC、Connect / Disconnect、连接状态 |
| Tab 区 | 八个标签页（可滚动页用右侧滚动条 / 滚轮） |
| Log · 操作反馈 | 可拖动分隔条；全局状态徽章 + 滚动日志 |

| Tab | 作用 |
|-----|------|
| **Motion** | 步态 / 步态速度比例 / 特技 / 虚拟摇杆推流 |
| **SLAM** | 流程 A 建图、流程 B 加载与定位、地图维护 |
| **Nav** | 流程 C 导航、位姿参数、占用栅格地图交互 |
| **Audio** | 音量、TTS、语音配置（gRPC） |
| **Display** | 表情列表、设置 / 查询当前表情（gRPC） |
| **Sensor** | 硬件传感器开关（gRPC） |
| **Video** | RTSP 预览 + 图像检测 + 摇杆（与 Motion 共用一条推流） |

**摇杆推流**：Motion 与 Video 各有一套摇杆 UI，但同一时刻只有一路 20 Hz `send_joystick_command`；在某一页点击 **Start stream** 后，读数来自该页摇杆，另一页摇杆会同步显示状态（推流中 / 已停止）。

---

## 推荐使用流程

建图 / 导航前，在 **Motion** 将步态设为 **Down climb stairs (nav)**（`GaitMode.GAIT_DOWN_CLIMB_STAIRS`）。

```mermaid
flowchart LR
  M[Motion 步态 / 摇杆探索]
  A[SLAM 流程 A 建图 ①②③]
  B[SLAM 流程 B 加载定位 ④⑤⑥]
  C[Nav 流程 C 导航 ⑦～⑩]
  M --> A --> B --> C
```

| 阶段 | 页面 | 要点 |
|------|------|------|
| 探索 / 步态 | Motion | `Set gait` → 建图用摇杆巡逻需 **Start stream** |
| 新环境建图 | SLAM · 流程 A | ① 开始建图 → ② Motion 探索 → ③ 保存地图 |
| 已有地图 | SLAM · 流程 B | ④ 刷新列表 → ⑤ 加载 → ⑥ 切换定位 |
| 导航 | Nav · 流程 C | ⑦ 刷新地图 → ⑧ Nav mode ON → ⑨ 初始位姿 → ⑩ 目标与导航 |

流程 B 完成后在 **Nav** 页继续。

---

## 连接时 SDK 初始化

点击 **Connect** 后，`RobotSession` 内部顺序：

| 步骤 | Python API | 说明 |
|------|------------|------|
| 1 | `MagicRobot()` | 创建实例 |
| 2 | `initialize_grpc_only(local_ip, HIGH_LEVEL_MOTION \| SLAM_NAVIGATION, robot_ip)` | GrpcOnly，仅高层运动 + SLAM/导航 |
| 3 | `connect()` | gRPC 连接 `eame_app` |
| 4 | `set_motion_control_level(ControllerLevel.HIGH_LEVEL)` | 高层控制 |
| 5 | `get_high_level_motion_controller()` / `get_slam_nav_controller()` | 运动与 SLAM 控制器 |
| 6 | `high.enable_joy_stick()` | 允许摇杆指令 |
| 7 | `get_audio_controller()` | Audio 页 gRPC（音量 / TTS / 配置） |
| 后台 | `get_current_localization_info()` / `get_nav_task_status()` | 约 0.5 s 轮询，更新 Nav 状态与地图机器人位姿 |

**Disconnect**：停止摇杆线程 → `disable_joy_stick()` → 关闭 Audio 订阅与 `audio.shutdown()` → `disconnect()` → `shutdown()`。

与完整 `robot.initialize()` 的区别：不启 LCM 传感器/低层运动；GrpcOnly 下里程计订阅不可用（与 SDK 一致）。**Video** 使用 OpenCV 直连 RTSP，不经过 SDK。

---

## 各页功能与 API 对照

### Connection

| GUI | Python API | C++ 对应 |
|-----|------------|----------|
| Connect | 见上表 | `Initialize` / `Connect` 等 |
| Disconnect | `disconnect()`、`shutdown()` | `Disconnect` / `Shutdown` |

---

### Motion

| GUI | Python API | C++ `HighLevelMotionController` |
|-----|------------|----------------------------------|
| Set gait | `high.set_gait(GaitMode)` | `SetGait` |
| Get gait | `high.get_gait()` → `(Status, GaitMode)` | `GetGait` |
| 当前步态（状态行） | Connect / Get / Set 后刷新；见下方说明 | — |
| Get all ratios | `high.get_all_gait_speed_ratio()` | `GetAllGaitSpeedRatio` |
| Set ratio | `high.set_gait_speed_ratio(GaitMode, GaitSpeedRatio)` | `SetGaitSpeedRatio` |
| Execute | `high.execute_trick(TrickAction)` | `ExecuteTrick` |
| Start stream | 20 Hz `high.send_joystick_command(JoystickCommand)` | `SendJoyStickCommand` |
| Stop | 停止线程，摇杆回中发零 | — |

**Get gait 与界面显示（GrpcOnly）**

- SDK 侧 `GetGait` 常读 gRPC 状态流缓存，未同步时可能返回 **`id=9999`（GAIT_NONE）** 或 `-1`，与机器人实际步态不一致。
- GUI 将 `9999` / `-1` 视为无效；**Set gait 成功**后以所设步态更新界面，并记住「上次 Set」。
- **Get gait** 若仍为无效值，状态行显示参考步态（默认 `GAIT_STAND_R` 或上次 Set），Log 中会注明 `not synced`。
- 下拉框内步态与 `magic_type.h` 中 `GaitMode` 对应；特技列表见 `TrickAction`。

**Gait speed ratio（步态速度比例）**

- 支持调整 **Straight（前进）**、**Turn（转向）**、**Lateral（侧移）** 三项比例（0–1）。
- 仅以下步态支持 Get / Set（与 `magic_grpc_client.cpp` 一致）：
  - Run fast · 快跑
  - Down climb stairs (nav) · 导航盲走
  - RL terrain · 全地形
  - RL hand stand · 倒立
  - RL foot stand · 正立
- **Get all ratios** 查询全部支持步态的比例；**Set ratio** 写入当前选中步态。
- `GaitSpeedRatio` 字段：`straight_ratio`、`turn_ratio`、`lateral_ratio`。

**摇杆轴**（`JoystickCommand`）：

| 摇杆 | 字段 | 含义 |
|------|------|------|
| 左 | `left_x_axis`, `left_y_axis` | 横向、前进（Y 向上为正） |
| 右 | `right_x_axis` | 偏航 / 转向（Video 页右摇杆仅水平） |

---

### SLAM

| 步骤 | GUI | Python API | C++ `SlamNavController` |
|------|-----|------------|-------------------------|
| ① | 开始 / 取消建图 | `start_mapping()` / `cancel_mapping()` | `StartMapping` / `CancelMapping` |
| ③ | 保存地图 | `save_map(name)` | `SaveMap` |
| ④ | 刷新列表 | `get_all_map_info()` | `GetAllMapInfo` |
| ⑤ | 加载选中 | `load_map(name)` | `LoadMap` |
| ⑥ | 切换定位 | `switch_to_location()` | `SwitchToLocation` |
| — | 删除选中 | `delete_map(name)` | `DeleteMap` |
| — | 关闭 SLAM（Idle） | `switch_to_idle()` | `SwitchToIdle` |

页面内容较多，使用**垂直滚动**查看流程 B 与底部「维护」区。

---

### Nav（地图导航）

| 步骤 | GUI | Python API | 说明 |
|------|-----|------------|------|
| ⑦ | 刷新地图 | `get_all_map_info()` | 刷新右侧占用栅格 |
| ⑧ | Nav mode ON | `activate_nav_mode(NavMode.GRID_MAP)` | 开启栅格导航 |
| ⑨ | 提交 Init pose | `init_pose(Pose3DEuler)` | position [X,Y,0] + orientation [Roll,Pitch,Yaw]（rad） |
| ⑨ | 填入定位位姿 | — | 从 `get_current_localization_info()` 写入「初始位姿」行 |
| ⑩ | 导航到目标点 | 见下「发起导航」 | `set_nav_target` |
| ⑩ | 暂停 / 继续 / 取消 | `pause_nav_task()` / `resume_nav_task()` / `cancel_nav_task()` | |
| — | 查询导航状态 | `get_nav_task_status()` | 更新 Nav 状态文案 |

**发起导航**（工具栏 / 左键双击，模式为「导航目标」）：

1. `set_gait(GAIT_DOWN_CLIMB_STAIRS)`
2. `disable_joy_stick()`
3. 构造 `NavTarget`（`frame_id="map"`，目标来自「导航目标」行 X/Y/Yaw）
4. `set_nav_target(tgt)`
5. `enable_joy_stick()`

**地图鼠标**（需先选「地图点击」模式）：

| 操作 | 导航目标模式 | 初始位姿模式 |
|------|----------------|----------------|
| 左键单击 | 设置目标 X/Y | 设置初始 X/Y |
| 右键按住拖动 | 以当前 X/Y 为圆心设 Yaw（箭头预览） | 同左 |
| 左键双击 | `set_nav_target` | `init_pose` |

**位姿参数**（左栏「位姿参数」）：

- **初始位姿**：X、Y、Yaw、Roll、Pitch（弧度）
- **导航目标**：X、Y、Yaw；可用「目标 Yaw ← 定位」从定位结果拷贝偏航

**图例**：绿箭头 = 当前定位；黄箭头 = 初始位姿预览；红叉 + 短箭头 = 导航目标。

---

### Audio

对应 `AudioController`（`sdk/include/magic_audio.h`）的 **gRPC** 接口；交互可参考 `example/python/audio_example.py`（本 GUI 不含 LCM 语音流 / Speech IO）。

| 区域 | GUI | Python API |
|------|-----|------------|
| 音量 | 滑块 0–100，Get / Set | `get_volume()` / `set_volume()` |
| TTS | ID、Priority、Mode、文本，Play / Stop | `play(TtsCommand)` / `stop()` |
| 语音配置 | Get config、Switch 模型 | `get_voice_config()` / `switch_tts_voice_model()` |

Connect 后获取 `get_audio_controller()`，无需 `audio.initialize()`（不启 LCM）。

---

### Display（LCD 表情）

对应 `DisplayController`（`sdk/include/magic_display.h`），参考 `example/python/display_example.py`。

| GUI | Python API | gRPC |
|-----|------------|------|
| Refresh list | `get_all_face_expressions()` | `getAllFaceExpressions` |
| Get current | `get_current_face_expression()` | `getFaceExpression` |
| Set face | `set_face_expression(id)` | `setFaceExpression` |

Connect 后 `get_display_controller()` 即可，无需 LCM。

---

### Sensor

对应 `SensorController`（gRPC），用于开关机载硬件传感器（如相机、激光等，以机载配置为准）。

| GUI | 说明 |
|-----|------|
| 传感器列表 | Connect 后刷新可用项 |
| Open / Close | 通过 gRPC 打开或关闭指定传感器 |

---

### Video（RTSP）

不经过 MagicDog SDK；**OpenCV + Pillow** 解码，`ImageTk` 显示。

| GUI | 说明 |
|-----|------|
| URL | 默认 `rtsp://<机器人IP>:<rtsp-port>`，默认端口 **8082** |
| 同步机器人 IP | 从 Connection 的 Robot 主机名重写 URL |
| Start / Stop | 后台线程 `VideoCapture` 读帧 |
| 图像检测 | 下拉选择检测模式，叠加框 / 标记于预览画面 |
| 统计栏 | 近 1 s 接收 FPS、流标注 FPS、帧数、读失败次数、源/显示分辨率、时长、检测摘要 |
| 摇杆 | 与 Motion 共用推流；适合边看画面边控狗 |

- 切换检测模式会自动重置检测器状态；切换 Tab、Disconnect 或关闭窗口会自动 Stop RTSP。
- 若相机路径非根路径，请写全 URL 或使用 `--rtsp-path`，例如 `rtsp://192.168.55.200:8082/stream`。

---

## Video 图像检测与模型文件

### 检测模式一览

| 模式 | 依赖 | 说明 |
|------|------|------|
| 关闭 | — | 仅预览 |
| 颜色(红/绿/蓝) | OpenCV | HSV 色块检测 |
| 人脸 | OpenCV FaceDetectorYN | YuNet ONNX（OpenCV 5+）；OpenCV 4 可回退 Haar |
| 运动区域 | OpenCV | 背景差分 |
| YOLO 通用物品 | ultralytics | COCO 80 类，`yolov8n.pt` |
| YOLO 行人 | ultralytics | 仅 COCO `person` |
| YOLO 人体姿态 | ultralytics | 骨架 + 人体框，`yolov8n-pose.pt` |
| ArUco 标记 | OpenCV aruco | `DICT_4X4_50`，显示 `ArUco#ID` |
| 轮廓/边缘 | OpenCV | Canny + 大轮廓框 |
| 人体(DNN) | OpenCV DNN | MediaPipe 行人 ONNX（OpenCV 5 兼容）；旧版 OpenCV 可回退 Caffe MobileNet-SSD；失败时 HOG |
| OCR 文字 | easyocr | 中英文文字框 + 识别结果（默认 `ch_sim` + `en`） |

YOLO 模式每 4 帧推理一次；**OCR 在后台线程运行**（不阻塞 RTSP），每 6 帧提交一帧；**画面移动时自动清除旧框**，结果默认显示 1.5 秒。

**ArUco 标记**：黑白方形 fiducial 码（外黑框 + 内部 4×4 网格），可打印贴墙用于定位 demo。可用 OpenCV `generateImageMarker` 生成 ID 0–49 测试图。

**切换 YOLO 模式**：通用 / 行人 / 姿态使用**独立模型实例**，避免 ultralytics 内部 `classes` 过滤在模式切换后残留。

### 模型目录 `models/`

权重文件**不纳入 Git**（见 `models/.gitignore`），需本地放置或首次运行时自动下载：

| 文件 | 用途 | 获取方式 |
|------|------|----------|
| `yolov8n.pt` | YOLO 通用 / 行人 | ultralytics 首次自动下载，或 `--yolo-model` |
| `yolov8n-pose.pt` | YOLO 姿态 | 首次自动下载，或 `--yolo-pose-model` |
| `person_detection_mediapipe_2023mar.onnx` | 人体 DNN（约 12 MB，OpenCV 5+） | 首次自动下载到 `models/` |
| `face_detection_yunet_2023mar.onnx` | 人脸检测（约 0.3 MB，OpenCV 5+） | 首次自动下载到 `models/` |
| `MobileNetSSD_deploy.prototxt` | 人体 DNN（OpenCV 4 Caffe 回退） | 可选，首次自动下载 |
| `MobileNetSSD.caffemodel` | 人体 DNN Caffe 权重（约 23 MB） | 可选，首次自动下载 |
| `models/easyocr/` | OCR 模型缓存 | EasyOCR 首次运行时自动下载 |

环境变量（可选）：

| 变量 | 说明 |
|------|------|
| `VIZ_NAV_YOLO_MODEL` | 通用/行人 YOLO 权重路径 |
| `VIZ_NAV_YOLO_POSE_MODEL` | 姿态 YOLO 权重路径 |
| `VIZ_NAV_DNN_ONNX` | 人体 DNN ONNX 路径（默认 `models/person_detection_mediapipe_2023mar.onnx`） |
| `VIZ_NAV_FACE_YUNET` | 人脸 YuNet ONNX 路径（默认 `models/face_detection_yunet_2023mar.onnx`） |
| `VIZ_NAV_DNN_PROTOTXT` | MobileNet-SSD prototxt（OpenCV 4 Caffe 回退） |
| `VIZ_NAV_DNN_CAFFEMODEL` | MobileNet-SSD caffemodel（OpenCV 4 Caffe 回退） |
| `VIZ_NAV_OCR_LANGS` | OCR 语言，逗号分隔，默认 `ch_sim,en` |
| `VIZ_NAV_OCR_CONF` | OCR 置信度阈值，默认 `0.25`（小字可适当降低） |
| `VIZ_NAV_OCR_UPSCALE_MIN` | OCR 前将画面长边放大到至少该像素，默认 `960` |
| `VIZ_NAV_OCR_RESULT_TTL` | OCR 结果最长保留秒数，默认 `1.5` |
| `VIZ_NAV_OCR_MOVE_THRESHOLD` | 画面变化超过该阈值时清除旧框（默认 `10`，越小越敏感） |
| `VIZ_NAV_OCR_MODEL_DIR` | EasyOCR 模型缓存目录，默认 `models/easyocr` |

手动下载 DNN / 人脸模型（自动下载失败时）：

- [face_detection_yunet_2023mar.onnx](https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx)（OpenCV 5+ 人脸）
- [person_detection_mediapipe_2023mar.onnx](https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/person_detection_mediapipe/person_detection_mediapipe_2023mar.onnx)（OpenCV 5+ 人体）
- [MobileNetSSD_deploy.prototxt](https://raw.githubusercontent.com/chuanqi305/MobileNet-SSD/master/MobileNetSSD_deploy.prototxt)（OpenCV 4 Caffe 回退）
- [MobileNetSSD_deploy.caffemodel](https://github.com/Sujan-Roy/Real-Time-Object-detection-with-MobileNet-and-SSD/raw/main/MobileNetSSD_deploy.caffemodel)（OpenCV 4 Caffe 回退）

---

## 操作反馈与日志

Tab 区与 **Log · 操作反馈** 之间有**可拖动分隔条**。

| 徽章 | 含义 |
|------|------|
| `IDLE` 灰 | 等待操作 |
| `···` 黄 | 已点击，执行中 |
| `OK` 绿 | 成功 |
| `FAIL` 红 | 失败 |

说明文案显示在徽章右侧，并同步写入 Log；约 **10 秒**后恢复 idle。Connect、各 Tab 主要按钮、SLAM 流程步骤、地图工具栏等均接入反馈。

---

## 命令行参数

```bash
python3 viz_nav.py --help
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--local-ip` | `192.168.55.10` | 本机在与机器人同一局域网内的 IP |
| `--robot-ip` | `192.168.55.200` | `eame_app` gRPC 主机名或 IP |
| `--rtsp-port` | `8082` | Video 页默认 RTSP 端口（与 IP 组成 `rtsp://IP:PORT`） |
| `--rtsp-path` | `""` | RTSP 路径后缀，如 `/stream` |
| `--yolo-model` | `""` | YOLO 检测权重（默认 `models/yolov8n.pt` 或自动下载） |
| `--yolo-pose-model` | `""` | YOLO 姿态权重（默认 `models/yolov8n-pose.pt`） |

---

## 常见问题

| 现象 | 处理 |
|------|------|
| `Cannot import magicdog_python` | 编译 SDK，`export PYTHONPATH=.../build:$PYTHONPATH` |
| 中文方框 / Matplotlib 缺字 | 安装 `fonts-noto-cjk`；检测框中文需 CJK 字体，否则自动用英文标签 |
| 地图空白 | SLAM 页 **加载选中** 后，Nav 页点 **刷新地图** |
| 导航失败 | 完成 SLAM ⑥ 定位、Nav ⑧ 开导航、⑨ 初始位姿；步态为 `GAIT_DOWN_CLIMB_STAIRS` |
| Get gait 显示 9999 / 与真机不一致 | GrpcOnly 缓存未同步属正常；以 **Set gait** 为准，或看 Log 中的 `not synced` 说明 |
| Get all gait speed ratios 失败 | 确认 Connect；仅支持步态见 [Gait speed ratio](#motion) |
| RTSP 黑屏 / 无法连接 | 核对 URL、端口与路径；安装 `opencv-python`、`ffmpeg`；看 Log 中 `RTSP:` 行 |
| Video 页缺失 | 未装 OpenCV/Pillow：`pip install opencv-python Pillow` |
| YOLO 不可用 | `pip install ultralytics`；通用模式需 **detect** 模型 `yolov8n.pt`，勿与 `yolov8n-pose.pt` 混用 |
| YOLO 通用只检出人 | 切换模式后应已修复；确认权重为 detect 模型；通用模式 conf 较低(0.25) |
| 人脸模式画面卡住 / OpenCV 5 | OpenCV 5 已移除 Haar `CascadeClassifier`；已改用 YuNet；首次自动下载 `face_detection_yunet_2023mar.onnx`；检测失败时仍继续显示画面 |
| 人体(DNN) 无检测 / OpenCV 5 报 `readNetFromCaffe` | OpenCV 5 已移除 Caffe；使用 ONNX（约 12 MB，首次自动下载）；失败时会显示 `[HOG]` 降级 |
| OCR 检测框不跟画面移动 | 已加入**移动检测自动清框** + 结果 TTL；若仍滞后可调低 `VIZ_NAV_OCR_MOVE_THRESHOLD=6` |
| OCR 导致 RTSP 卡住 | 已改为**后台 OCR 线程**，预览不应再冻结 |
| OCR 不可用 / 很慢 / 小字检不出 | `pip install easyocr`；**靠近文字、让字占画面 1/4 以上**；包装编号建议 `export VIZ_NAV_OCR_LANGS=en`；仍失败试 `export VIZ_NAV_OCR_CONF=0.15 VIZ_NAV_OCR_UPSCALE_MIN=1280` |
| ArUco 无反应 | 需 OpenCV contrib aruco；使用 DICT_4X4_50 打印标记，保持平整、足够大 |
| 摇杆无响应 | 需 **Connect** 且 **Start stream**；导航发目标时会短暂 `disable_joy_stick`，需重新 Start stream |
| Log 区太小 | 向上拖动 Tab 与 Log 之间的分隔条 |

---

## 相关文件

| 路径 | 说明 |
|------|------|
| `viz_nav.py` | GUI 主程序 |
| `requirements.txt` | Python 第三方依赖 |
| `models/` | 检测模型本地目录（Git 忽略权重，保留 `.gitkeep`） |
| `../python/slam_example.py` | 键盘版 SLAM / 导航示例 |
| `../python/navigation_example.py` | 导航示例 |
| `../python/audio_example.py` | Audio API 示例 |
| `../python/high_level_motion_example.py` | 高层运动（含步态速度比例）示例 |
| `sdk/include/magic_motion.h` | 高层运动 API |
| `sdk/include/magic_slam_navigation.h` | SLAM / 导航 API |
| `sdk/include/magic_audio.h` | 语音 / TTS API |
| `sdk/include/magic_type.h` | `GaitMode`、`GaitSpeedRatio`、`TrickAction`、`NavTarget` 等 |
