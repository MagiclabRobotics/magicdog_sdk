#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python Usage Example

This file demonstrates how to use MagicDog SDK Python bindings to control the robot.
"""

import sys
import time
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,  # Minimum log level
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

try:
    import magicdog_python as magicdog
    from magicdog_python import TtsCommand, TtsPriority, TtsMode, GetSpeechConfig
    logging.info("Successfully imported MagicDog Python module!")
    # Print the path of imported magicdog_python
    logging.info(f"Imported magicdog_python path: {sys.path}")
except ImportError as e:
    logging.error(f"Import failed: {e}")
    sys.exit(1)

def main():
    """Main function"""
    logging.info("MagicDog SDK Audio Python Example Program")
    
    local_ip = "192.168.55.10"
    robot = magicdog.MagicRobot()
    if not robot.initialize(local_ip):
        logging.error("Robot initialization failed")
        return

    if not robot.connect():
        logging.error("Robot connection failed")
        robot.shutdown()
        return
    
    logging.info("Robot connected successfully")
    
    audio_controller = robot.get_audio_controller()

    # Get current volume
    volume = audio_controller.get_volume()
    if volume != -1:
        logging.info(f"Current volume: {volume}")
    else:
        logging.error("Failed to get volume")

    # Set volume
    status = audio_controller.set_volume(50)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(f"Failed to set volume: {status.message}")
        robot.shutdown()
        return
    
    # Get volume again to confirm successful setting
    volume = audio_controller.get_volume()
    if volume != -1:
        logging.info(f"Volume set successfully, current volume: {volume}")
    else:
        logging.error("Failed to get volume after setting")
    
    tts_command = TtsCommand()
    tts_command.id = "100000000002"
    tts_command.content = "How's the weather today!"
    tts_command.priority = TtsPriority.HIGH
    tts_command.mode = TtsMode.CLEARTOP
    status = audio_controller.play(tts_command)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(f"Failed to play voice: {status.message}")
        robot.shutdown()
        return
    
    time.sleep(5)
    
    status = audio_controller.stop()
    if status.code != magicdog.ErrorCode.OK:
        logging.error(f"Failed to stop voice playback: {status.message}")
        robot.shutdown()
        return

    # Get voice configuration
    speech_config = audio_controller.get_voice_config()
    if speech_config:
        logging.info("Successfully got voice configuration:")
        logging.info(f"  TTS Type: {speech_config.tts_type}")
        # Print configuration details
        logging.info(f"  Configuration details:")
        
        if speech_config.speaker_config:
            speaker = speech_config.speaker_config
            logging.info(f"    Speaker configuration:")
            logging.info(f"      Data: {speaker.data}")
            logging.info(f"      Selected: {speaker.selected.speaker_id} {speaker.selected.region}")
            logging.info(f"      Speed: {speaker.speaker_speed}")
        
        if speech_config.bot_config:
            bot = speech_config.bot_config
            logging.info(f"    Bot configuration:")
            logging.info(f"      Data: ")
            # bot.data is a dictionary with string keys and values containing [id, name] lists
            for bot_id, bot_info in bot.data.items():
                logging.info(f"        Bot ID: {bot_id}")
                logging.info(f"          Name: {bot_info.name}")
                logging.info(f"          Workflow ID: {bot_info.workflow}")
                
            logging.info(f"      Custom data: {bot.custom_data}")
            logging.info(f"      Selected: {bot.selected.bot_id}")
        
        if speech_config.wakeup_config:
            wakeup = speech_config.wakeup_config
            logging.info(f"    Wakeup configuration:")
            logging.info(f"      Name: {wakeup.name}")
            logging.info(f"      Data: {wakeup.data}")
        
        if speech_config.dialog_config:
            dialog = speech_config.dialog_config
            logging.info(f"    Dialog configuration:")
            logging.info(f"      Front DOA: {dialog.is_front_doa}")
            logging.info(f"      Full duplex enabled: {dialog.is_fullduplex_enable}")
            logging.info(f"      Enabled: {dialog.is_enable}")
            logging.info(f"      DOA enabled: {dialog.is_doa_enable}")
    else:
        logging.error("Failed to get voice configuration")   

    def subscribe_origin_voice_data(data):
        logging.info(f"Received raw voice data: {len(data.data)}")
    def subscribe_bf_voice_data(data):
        logging.info(f"Received BF voice data: {len(data.data)}")

    audio_controller.subscribe_origin_voice_data(subscribe_origin_voice_data)
    audio_controller.subscribe_bf_voice_data(subscribe_bf_voice_data)

    audio_controller.control_voice_stream(True, True)

    time.sleep(10)

    audio_controller.control_voice_stream(False, False)

    # Avoid unprocessed buffered data in lcm
    time.sleep(10)

    robot.disconnect()
    robot.shutdown()
    logging.info("\nExample program execution completed!")

if __name__ == "__main__":
    main() 