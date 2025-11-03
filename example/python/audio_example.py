#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import signal
import termios
import tty
import logging
from typing import Optional
import magicdog_python as magicdog
from magicdog_python import TtsCommand, TtsPriority, TtsMode, GetSpeechConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Global robot instance
robot = None


def signal_handler(signum, frame):
    """Handle Ctrl+C signal"""
    logging.info(f"\nInterrupt signal ({signum}) received.")
    if robot:
        robot.shutdown()
    sys.exit(signum)


def print_help():
    """Print help information"""
    logging.info("Key Function Description:")
    logging.info("")
    logging.info("Audio Functions:")
    logging.info("  1        Function 1: Get volume")
    logging.info("  2        Function 2: Set volume")
    logging.info("  3        Function 3: Play TTS")
    logging.info("  4        Function 4: Stop playback")
    logging.info("  5        Function 5: Get voice config")
    logging.info("")
    logging.info("Audio stream Functions:")
    logging.info("  6        Function 6: Open audio stream")
    logging.info("  7        Function 7: Close audio stream")
    logging.info("  8        Function 8: Subscribe to audio stream")
    logging.info("  9        Function 9: Unsubscribe from audio stream")
    logging.info("")
    logging.info("  ?        Function ?: Print help")
    logging.info("  ESC      Exit program")


def getch():
    """Get a single character from standard input"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_volume(audio_controller):
    """Get current volume"""
    status, volume = audio_controller.get_volume()
    if status.code != magicdog.ErrorCode.OK:
        logging.error("get volume failed")
        return
    logging.info(f"get volume success, volume: {volume}")


def set_volume(audio_controller):
    """Set volume"""
    status = audio_controller.set_volume(50)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            f"set volume failed, code: {status.code}, message: {status.message}"
        )
        return
    logging.info("set volume success")


def play_tts(audio_controller):
    """Play TTS"""
    tts = TtsCommand()
    tts.id = "100000000001"
    tts.content = "How's the weather today!"
    tts.priority = TtsPriority.HIGH
    tts.mode = TtsMode.CLEARTOP
    status = audio_controller.play(tts)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            f"play tts failed, code: {status.code}, message: {status.message}"
        )
        return
    logging.info("play tts success")


def stop_tts(audio_controller):
    """Stop TTS playback"""
    status = audio_controller.stop()
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            f"stop tts failed, code: {status.code}, message: {status.message}"
        )
        return
    logging.info("stop tts success")


def open_audio_stream(audio_controller):
    """Open audio stream"""
    status = audio_controller.control_voice_stream(True, True)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            f"open audio stream failed, code: {status.code}, message: {status.message}"
        )
        return
    logging.info("open audio stream success")


def close_audio_stream(audio_controller):
    """Close audio stream"""
    status = audio_controller.control_voice_stream(False, False)
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            f"close audio stream failed, code: {status.code}, message: {status.message}"
        )
        return
    logging.info("close audio stream success")


# Global counter for audio stream callbacks
origin_counter = [0]
bf_counter = [0]


def subscribe_audio_stream(audio_controller):
    """Subscribe to audio streams"""

    def origin_callback(data):
        if origin_counter[0] % 30 == 0:
            logging.info(f"Received origin voice data, size: {len(data.data)}")
            sys.stdout.write("\r")
            sys.stdout.flush()
        origin_counter[0] += 1

    def bf_callback(data):
        if bf_counter[0] % 30 == 0:
            logging.info(f"Received bf voice data, size: {len(data.data)}")
            sys.stdout.write("\r")
            sys.stdout.flush()
        bf_counter[0] += 1

    audio_controller.subscribe_origin_voice_data(origin_callback)
    audio_controller.subscribe_bf_voice_data(bf_callback)
    logging.info("Subscribed to audio streams")


def unsubscribe_audio_stream(audio_controller):
    """Unsubscribe from audio streams"""
    audio_controller.unsubscribe_origin_voice_data()
    audio_controller.unsubscribe_bf_voice_data()
    logging.info("Unsubscribed from audio streams")


def get_voice_config(audio_controller):
    """Get voice configuration"""
    status, voice_config = audio_controller.get_voice_config()
    if status.code != magicdog.ErrorCode.OK:
        logging.error("get voice config failed")
        return

    logging.info("Get voice config success")
    logging.info(f"voice config tts type: {int(voice_config.tts_type)}")
    logging.info(
        f"voice config speaker config: {voice_config.speaker_config.selected.speaker_id}"
    )
    logging.info(f"voice config bot config: {voice_config.bot_config.selected.bot_id}")
    logging.info(f"voice config wakeup config: {voice_config.wakeup_config.name}")
    logging.info(
        f"voice config dialog config: {voice_config.dialog_config.is_front_doa}"
    )
    logging.info(
        f"voice config dialog config: {voice_config.dialog_config.is_fullduplex_enable}"
    )
    logging.info(f"voice config dialog config: {voice_config.dialog_config.is_enable}")
    logging.info(
        f"voice config dialog config: {voice_config.dialog_config.is_doa_enable}"
    )


def main():
    """Main function"""
    global robot

    # Bind SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)

    print_help()

    local_ip = "192.168.55.10"
    robot = magicdog.MagicRobot()

    # Configure local IP address for direct network connection and initialize SDK
    if not robot.initialize(local_ip):
        logging.error("robot sdk initialize failed.")
        robot.shutdown()
        return -1

    # Connect to robot
    status = robot.connect()
    if status.code != magicdog.ErrorCode.OK:
        logging.error(
            f"connect robot failed, code: {status.code}, message: {status.message}"
        )
        robot.shutdown()
        return -1

    logging.info("Press any key to continue (ESC to exit)...")

    audio_controller = robot.get_audio_controller()

    # Wait for user input
    while True:
        key = getch()
        if key == "\x1b":  # ESC key
            break

        key_ascii = ord(key)
        logging.info(f"Key ASCII: {key_ascii}, Character: {key}")

        # 1. Audio Functions
        # 1.1 Get volume
        if key == "1":
            get_volume(audio_controller)
        # 1.2 Set volume
        elif key == "2":
            set_volume(audio_controller)
        # 1.3 Play TTS
        elif key == "3":
            play_tts(audio_controller)
        # 1.4 Stop TTS
        elif key == "4":
            stop_tts(audio_controller)
        # 1.5 Get voice config
        elif key == "5":
            get_voice_config(audio_controller)
        # 2. Audio stream Functions
        # 2.1 Open audio stream
        elif key == "6":
            open_audio_stream(audio_controller)
        # 2.2 Close audio stream
        elif key == "7":
            close_audio_stream(audio_controller)
        # 2.3 Subscribe to audio stream
        elif key == "8":
            subscribe_audio_stream(audio_controller)
        # 2.4 Unsubscribe from audio stream
        elif key == "9":
            unsubscribe_audio_stream(audio_controller)
        # Help
        elif key == "?":
            print_help()
        else:
            logging.info(f"Unknown key: {key_ascii}")

        # Sleep 10ms, equivalent to usleep(10000)
        time.sleep(0.01)

    audio_controller.shutdown()
    logging.info("audio controller shutdown")

    # Disconnect from robot
    robot.disconnect()
    logging.info("disconnect robot success")

    robot.shutdown()
    logging.info("robot shutdown")

    return 0


if __name__ == "__main__":
    sys.exit(main())
