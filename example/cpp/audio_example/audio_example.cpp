#include "magic_robot.h"
#include "magic_sdk_version.h"

#include <termios.h>
#include <unistd.h>
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <thread>

using namespace magic::dog;

// Global robot instance
std::unique_ptr<MagicRobot> robot = nullptr;

void signalHandler(int signum) {
  std::cout << "\nInterrupt signal (" << signum << ") received." << std::endl;
  if (robot) {
    robot->Shutdown();
  }
  exit(signum);
}

void print_help() {
  std::cout << "Key Function Demo Program\n"
            << std::endl;
  std::cout << "Key Function Description:" << std::endl;
  std::cout << "Audio Functions:" << std::endl;
  std::cout << "  1        Function 1: Get volume" << std::endl;
  std::cout << "  2        Function 2: Set volume" << std::endl;
  std::cout << "  3        Function 3: Play TTS" << std::endl;
  std::cout << "  4        Function 4: Stop playback" << std::endl;
  std::cout << "  5        Function 5: Get voice config" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "Audio stream Functions:" << std::endl;
  std::cout << "  6        Function 6: Open audio stream" << std::endl;
  std::cout << "  7        Function 7: Close audio stream" << std::endl;
  std::cout << "  8        Function 8: Subscribe to audio stream" << std::endl;
  std::cout << "  9        Function 9: Unsubscribe from audio stream" << std::endl;
  std::cout << "" << std::endl;
  std::cout << "  ?        Function ?: Print help" << std::endl;
  std::cout << "  ESC      Exit program" << std::endl;
}

int getch() {
  struct termios oldt, newt;
  int ch;
  tcgetattr(STDIN_FILENO, &oldt);  // Get current terminal settings
  newt = oldt;
  newt.c_lflag &= ~(ICANON | ECHO);  // Disable buffering and echo
  tcsetattr(STDIN_FILENO, TCSANOW, &newt);
  ch = getchar();                           // Read key press
  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);  // Restore settings
  return ch;
}

void get_volume() {
  auto& audio_controller = robot->GetAudioController();

  int volume = 0;
  auto status = audio_controller.GetVolume(volume);
  if (status.code != ErrorCode::OK) {
    std::cerr << "get volume failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "get volume success, volume: " << volume << std::endl;
}

void set_volume(int volume) {
  auto& audio_controller = robot->GetAudioController();

  auto status = audio_controller.SetVolume(volume);
  if (status.code != ErrorCode::OK) {
    std::cerr << "set volume failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "set volume success" << std::endl;
}

void play_tts() {
  auto& audio_controller = robot->GetAudioController();

  TtsCommand tts;
  tts.id = "100000000001";
  tts.content = "How's the weather today!";
  tts.priority = TtsPriority::HIGH;
  tts.mode = TtsMode::CLEARTOP;

  auto status = audio_controller.Play(tts);
  if (status.code != ErrorCode::OK) {
    std::cerr << "play tts failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "play tts success" << std::endl;
}

void stop_tts() {
  auto& audio_controller = robot->GetAudioController();

  auto status = audio_controller.Stop();
  if (status.code != ErrorCode::OK) {
    std::cerr << "stop tts failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "stop tts success" << std::endl;
}

void open_audio_stream() {
  auto& audio_controller = robot->GetAudioController();

  auto status = audio_controller.ControlVoiceStream(true, true);
  if (status.code != ErrorCode::OK) {
    std::cerr << "open audio stream failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "open audio stream success" << std::endl;
}

void close_audio_stream() {
  auto& audio_controller = robot->GetAudioController();

  auto status = audio_controller.ControlVoiceStream(false, false);
  if (status.code != ErrorCode::OK) {
    std::cerr << "close audio stream failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }
  std::cout << "close audio stream success" << std::endl;
}

// Global counters for audio stream callbacks
static int origin_counter = 0;
static int bf_counter = 0;

void subscribe_audio_stream() {
  auto& audio_controller = robot->GetAudioController();

  // Subscribe to origin voice data
  audio_controller.SubscribeOriginVoiceData([](const std::shared_ptr<ByteMultiArray> data) {
    if (origin_counter % 30 == 0) {
      std::cout << "Received origin voice data, size: " << data->data.size() << std::endl;
      std::cout << "\r";
      std::cout.flush();
    }
    origin_counter++;
  });

  // Subscribe to bf voice data
  audio_controller.SubscribeBfVoiceData([](const std::shared_ptr<ByteMultiArray> data) {
    if (bf_counter % 30 == 0) {
      std::cout << "Received bf voice data, size: " << data->data.size() << std::endl;
      std::cout << "\r";
      std::cout.flush();
    }
    bf_counter++;
  });

  std::cout << "Subscribed to audio streams" << std::endl;
}

void unsubscribe_audio_stream() {
  auto& audio_controller = robot->GetAudioController();

  audio_controller.UnsubscribeOriginVoiceData();
  audio_controller.UnsubscribeBfVoiceData();
  std::cout << "Unsubscribed from audio streams" << std::endl;
}

void get_voice_config() {
  auto& audio_controller = robot->GetAudioController();

  GetSpeechConfig voice_config;
  auto status = audio_controller.GetVoiceConfig(voice_config);
  if (status.code != ErrorCode::OK) {
    std::cerr << "get voice config failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    return;
  }

  std::cout << "Get voice config success" << std::endl;
  std::cout << "TTS type: " << static_cast<int>(voice_config.tts_type) << std::endl;
  std::cout << "Speaker: " << voice_config.speaker_config.selected.speaker_id << std::endl;
  std::cout << "Bot config: " << voice_config.bot_config.selected.bot_id << std::endl;
  std::cout << "Wake word: " << voice_config.wakeup_config.name << std::endl;
  std::cout << "Dialog config - Front DOA: " << voice_config.dialog_config.is_front_doa << std::endl;
  std::cout << "Dialog config - Full duplex: " << voice_config.dialog_config.is_fullduplex_enable << std::endl;
  std::cout << "Dialog config - Voice enable: " << voice_config.dialog_config.is_enable << std::endl;
  std::cout << "Dialog config - DOA enable: " << voice_config.dialog_config.is_doa_enable << std::endl;
}

int main(int argc, char* argv[]) {
  // Bind SIGINT (Ctrl+C)
  signal(SIGINT, signalHandler);

  print_help();

  std::string local_ip = "192.168.54.111";
  robot = std::make_unique<MagicRobot>();

  // Configure local IP address for direct network connection and initialize SDK
  if (!robot->Initialize(local_ip)) {
    std::cerr << "robot sdk initialize failed." << std::endl;
    robot->Shutdown();
    return -1;
  }

  // Connect to robot
  auto status = robot->Connect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "connect robot failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    robot->Shutdown();
    return -1;
  }

  std::cout << "Press any key to continue (ESC to exit)..." << std::endl;

  // Wait for user input
  while (true) {
    int key = getch();
    if (key == 27) {  // ESC key
      break;
    }

    std::cout << "Key ASCII: " << key << ", Character: " << static_cast<char>(key) << std::endl;

    switch (key) {
      case '1':
        get_volume();
        break;
      case '2': {
        int volume = 50;
        std::cout << "Please input volume: ";
        std::cin >> volume;
        set_volume(volume);
        std::cin.ignore();
      } break;
      case '3':
        play_tts();
        break;
      case '4':
        stop_tts();
        break;
      case '5':
        get_voice_config();
        break;
      case '6':
        open_audio_stream();
        break;
      case '7':
        close_audio_stream();
        break;
      case '8':
        subscribe_audio_stream();
        break;
      case '9':
        unsubscribe_audio_stream();
        break;
      case '?':
        print_help();
        break;
      default:
        std::cout << "Unknown key: " << key << std::endl;
        break;
    }

    // Sleep 10ms, equivalent to usleep(10000)
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
  }

  // Disconnect from robot
  status = robot->Disconnect();
  if (status.code != ErrorCode::OK) {
    std::cerr << "disconnect robot failed, code: " << status.code
              << ", message: " << status.message << std::endl;
    robot->Shutdown();
    return -1;
  }

  std::cout << "disconnect robot success" << std::endl;

  robot->Shutdown();
  std::cout << "robot shutdown" << std::endl;

  return 0;
}