#include "magic_robot.h"

#include <unistd.h>
#include <csignal>

#include <iostream>

using namespace magic::dog;

magic::dog::MagicRobot robot;

void signalHandler(int signum) {
  std::cout << "Interrupt signal (" << signum << ") received.\n";

  robot.Shutdown();
  // 退出进程
  exit(signum);
}

int main() {
  // 绑定 SIGINT（Ctrl+C）
  signal(SIGINT, signalHandler);

  std::string local_ip = "192.168.55.10";
  // 配置本机网线直连机器的IP地址，并进行SDK初始化
  if (!robot.Initialize(local_ip)) {
    std::cerr << "robot sdk initialize failed." << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 设置rpc超时时间为5s
  robot.SetTimeout(5000);

  // 连接机器人
  auto status = robot.Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "connect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 获取音频控制器
  auto& controller = robot.GetAudioController();

  // 获取机器人当前音量
  int get_volume = 0;
  status = controller.GetVolume(get_volume);
  if (status.code != ErrorCode::OK) {
    std::cerr << "get volume failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  std::cout << "get volume success, volume: " << std::to_string(get_volume) << std::endl;

  // 设置机器人音量
  status = controller.SetVolume(7);
  if (status.code != ErrorCode::OK) {
    std::cerr << "set volume failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 校验设置的音量是否正确
  status = controller.GetVolume(get_volume);
  if (status.code != ErrorCode::OK) {
    std::cerr << "get volume failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  std::cout << "get volume success, volume: " << std::to_string(get_volume) << std::endl;

  // 播放语音
  TtsCommand tts;
  tts.id = "100000000001";
  tts.content = "今天天气怎么样！";
  tts.priority = TtsPriority::HIGH;
  tts.mode = TtsMode::CLEARTOP;
  status = controller.Play(tts);
  if (status.code != ErrorCode::OK) {
    std::cerr << "play tts failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 等待2s
  usleep(5000000);

  // 停止播放语音
  status = controller.Stop();
  if (status.code != ErrorCode::OK) {
    std::cerr << "stop tts failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 等待5s
  usleep(2000000);

  // 获取语音配置
  GetSpeechConfig get_speech_config;
  status = controller.GetVoiceConfig(get_speech_config);
  if (status.code != ErrorCode::OK) {
    std::cerr << "get voice config failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  std::cout << "get voice config success, speaker_id: " << get_speech_config.speaker_config.selected.speaker_id
            << ", region: " << get_speech_config.speaker_config.selected.region
            << ", bot_id: " << get_speech_config.bot_config.selected.bot_id
            << ", is_front_doa: " << get_speech_config.dialog_config.is_front_doa
            << ", is_fullduplex_enable: " << get_speech_config.dialog_config.is_fullduplex_enable
            << ", is_enable: " << get_speech_config.dialog_config.is_enable
            << ", is_doa_enable: " << get_speech_config.dialog_config.is_doa_enable
            << ", speaker_speed: " << get_speech_config.speaker_config.speaker_speed
            << ", wakeup_name: " << get_speech_config.wakeup_config.name
            << ", custom_bot: " << get_speech_config.bot_config.custom_data.size() << std::endl;
  for (const auto& [key, value] : get_speech_config.bot_config.custom_data) {
    std::cout << "custom_bot_data: " << key << ", " << value.name << std::endl;
  }

  // 设置语音配置
  SetSpeechConfig set_speech_config = ToSetSpeechConfig(get_speech_config);
  set_speech_config.wakeup_name = "小麦";
  set_speech_config.is_doa_enable = false;
  set_speech_config.is_front_doa = false;
  set_speech_config.is_fullduplex_enable = false;
  set_speech_config.is_enable = true;

  status = controller.SetVoiceConfig(set_speech_config);
  if (status.code != ErrorCode::OK) {
    std::cerr << "set voice config failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // 订阅原始语音数据
  controller.SubscribeOriginVoiceData([](const std::shared_ptr<ByteMultiArray> data) {
    std::cout << "receive origin voice data, size: " << data->data.size() << std::endl;
  });
  // 订阅BF语音数据
  controller.SubscribeBfVoiceData([](const std::shared_ptr<ByteMultiArray> data) {
    std::cout << "receive bf voice data, size: " << data->data.size() << std::endl;
  });

  // 控制语音数据流
  status = controller.ControlVoiceStream(true, true);
  if (status.code != ErrorCode::OK) {
    std::cerr << "control voice stream failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
  }

  // 等待10s
  usleep(10000000);

  std::cout << "close voice stream" << std::endl;

  // 停止订阅语音数据
  // status = sensor.ControlVoiceStream(false, false);
  // if (status.code != ErrorCode::OK) {
  //   std::cerr << "control voice stream failed"
  //             << ", code: " << status.code
  //             << ", message: " << status.message << std::endl;
  // }

  // // 等待10s
  // usleep(10000000);

  std::cout << "disconnect robot" << std::endl;

  // 断开与机器人的链接
  status = robot.Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "disconnect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  robot.Shutdown();

  return 0;
}