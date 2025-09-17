#include "magic_robot.h"

#include <unistd.h>
#include <csignal>

#include <iostream>

using namespace magic::dog;

magic::dog::MagicRobot robot;

void signalHandler(int signum) {
  std::cout << "Interrupt signal (" << signum << ") received.\n";

  robot.Shutdown();
  // Exit process
  exit(signum);
}

int main() {
  // Bind SIGINT (Ctrl+C)
  signal(SIGINT, signalHandler);

  std::string local_ip = "192.168.55.10";
  // Configure local IP address for direct network connection to machine and initialize SDK
  if (!robot.Initialize(local_ip)) {
    std::cerr << "Robot SDK initialization failed." << std::endl;
    robot.Shutdown();
    return -1;
  }

  // Connect to robot
  auto status = robot.Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Connect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // Get audio controller
  auto& controller = robot.GetAudioController();

  // Get robot's current volume
  int get_volume = 0;
  status = controller.GetVolume(get_volume);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Get volume failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  std::cout << "Get volume success, volume: " << std::to_string(get_volume) << std::endl;

  // Set robot volume
  status = controller.SetVolume(70);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Set volume failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // Verify if the set volume is correct
  status = controller.GetVolume(get_volume);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Get volume failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  std::cout << "Get volume success, volume: " << std::to_string(get_volume) << std::endl;

  // Play voice
  TtsCommand tts;
  tts.id = "100000000001";
  tts.content = "How's the weather today!";
  tts.priority = TtsPriority::HIGH;
  tts.mode = TtsMode::CLEARTOP;
  status = controller.Play(tts);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Play TTS failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // Wait 2s
  usleep(5000000);

  // Stop voice playback
  status = controller.Stop();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Stop TTS failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // Wait 5s
  usleep(2000000);

  std::cout << "Play music" << std::endl;
  std::string music_file_path = "local_music:/opt/eame/dreame_manager/share/dreame_manager/configures/music_files/dance_xsgy.mp3";
  tts.content = music_file_path;
  status = controller.Play(tts);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Play music failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  // Wait 5s
  usleep(5000000);

  // Get voice configuration
  GetSpeechConfig get_speech_config;
  status = controller.GetVoiceConfig(get_speech_config);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Get voice config failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  std::cout << "Get voice config success, speaker_id: " << get_speech_config.speaker_config.selected.speaker_id
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
    std::cout << "Custom bot data: " << key << ", " << value.name << std::endl;
  }

  // Subscribe to raw voice data
  controller.SubscribeOriginVoiceData([](const std::shared_ptr<ByteMultiArray> data) {
    std::cout << "Received raw voice data, size: " << data->data.size() << std::endl;
  });
  // Subscribe to BF voice data
  controller.SubscribeBfVoiceData([](const std::shared_ptr<ByteMultiArray> data) {
    std::cout << "Received BF voice data, size: " << data->data.size() << std::endl;
  });

  // Control voice data stream
  status = controller.ControlVoiceStream(true, true);
  if (status.code != ErrorCode::OK) {
    std::cerr << "Control voice stream failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
  }

  // Wait 10s
  usleep(10000000);

  std::cout << "Close voice stream" << std::endl;

  // status = sensor.ControlVoiceStream(false, false);
  // if (status.code != ErrorCode::OK) {
  //   std::cerr << "control voice stream failed"
  //             << ", code: " << status.code
  //             << ", message: " << status.message << std::endl;
  // }

  // usleep(10000000);

  std::cout << "Disconnect robot" << std::endl;

  // Disconnect from robot
  status = robot.Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "Disconnect robot failed"
              << ", code: " << status.code
              << ", message: " << status.message << std::endl;
    robot.Shutdown();
    return -1;
  }

  robot.Shutdown();

  return 0;
}