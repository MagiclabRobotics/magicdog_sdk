#pragma once
#include "magic_export.h"
#include "magic_type.h"

#include <atomic>
#include <functional>
#include <memory>
#include <string>

namespace magic::dog::audio {

class AudioController;
using AudioControllerPtr = std::unique_ptr<AudioController>;

/**
 * @class AudioController
 * @brief A class encapsulating audio control functions, providing interfaces for audio playback, stop, volume adjustment, etc.
 *
 * This class is typically used to control audio output in robots or smart devices, supporting text-to-speech (TTS) playback,
 * volume setting and query, and providing initialization and resource release mechanisms.
 */
class MAGIC_EXPORT_API AudioController final : public NonCopyable {
  // Message pointer type definition (smart pointer for memory management)
  using ByteMultiArrayPtr = std::shared_ptr<ByteMultiArray>;  // Byte array data pointer

  // Callback function type definitions for various audio data
  using ByteMultiArrayCallback = std::function<void(const ByteMultiArrayPtr)>;

 public:
  /**
   * @brief Constructor, initializes the audio controller object.
   *        Can be used to construct internal state, allocate resources, etc.
   */
  AudioController();

  /**
   * @brief Destructor, releases audio controller resources.
   *        Ensures playback is stopped and underlying resources are cleaned up.
   */
  ~AudioController();

  /**
   * @brief Initialize the audio control module.
   * @return Returns true on success, false on failure.
   */
  bool Initialize();

  /**
   * @brief Shutdown the audio controller and release resources.
   *        Used together with Initialize to ensure safe exit.
   */
  void Shutdown();

  /**
   * @brief Switch TTS voice model.
   * @param tts_type TTS voice model type.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status SwitchTtsVoiceModel(TtsType tts_type, int timeout_ms = 5000);

  /**
   * @brief Get speech configuration.
   * @param config Speech configuration.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status GetVoiceConfig(GetSpeechConfig& config, int timeout_ms = 5000);

  /**
   * @brief Set speech configuration.
   * @param config Speech configuration to set.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status SetVoiceConfig(const SetSpeechConfig& config, int timeout_ms = 5000);

  /**
   * @brief Play TTS command.
   * @param cmd TTS command, including text content, speed, pitch, etc.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status Play(const TtsCommand& cmd, int timeout_ms = 5000);

  /**
   * @brief Stop current audio playback.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status Stop(int timeout_ms = 5000);

  /**
   * @brief Set the output volume.
   * @param volume Volume value (usually 0-100 or as defined by protocol).
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status SetVolume(int volume, int timeout_ms = 5000);

  /**
   * @brief Get the current output volume.
   * @param[out] volume Current volume value (returned by reference).
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status, returns Status::OK on success.
   */
  Status GetVolume(int& volume, int timeout_ms = 5000);

  /**
   * @brief Control voice data stream.
   * @param enable_raw_data enable raw data stream.
   * @param enable_bf_data enable bf data stream.
   * @param timeout_ms Timeout in milliseconds.
   * @return Operation status.
   */
  Status ControlVoiceStream(bool enable_raw_data, bool enable_bf_data, int timeout_ms = 5000);

  /**
   * @brief Subscribe to original voice data.
   * @param callback Callback to handle received original voice data.
   */
  void SubscribeOriginVoiceData(const ByteMultiArrayCallback callback);

  /**
   * @brief Unsubscribe from original voice data.
   */
  void UnsubscribeOriginVoiceData();

  /**
   * @brief Subscribe to BF voice data.
   * @param callback Callback to handle received BF voice data.
   */
  void SubscribeBfVoiceData(const ByteMultiArrayCallback callback);

  /**
   * @brief Unsubscribe from BF voice data.
   */
  void UnsubscribeBfVoiceData();

 private:
  std::atomic_bool is_shutdown_{true};  // Flag indicating whether initialized
};

}  // namespace magic::dog::audio