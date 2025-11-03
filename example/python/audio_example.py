#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来控制机器人。
"""

import sys
import time

# 添加构建目录到 Python 路径，插入到最前面
sys.path.insert(0, '../../build')

try:
    import magicdog_python as magicdog
    from magicdog_python import TtsCommand, TtsPriority, TtsMode, GetSpeechConfig
    print("成功导入 MagicDog Python 模块！")
    # 打印导入的 magicdog_python 的路径
    print(f"导入的 magicdog_python 的路径: {sys.path}")
except ImportError as e:
    print(f"导入失败: {e}")
    print("请先运行 build_python.sh 构建 Python 绑定")
    sys.exit(1)

def main():
    """主函数"""
    print("MagicDog SDK Audio Python 示例程序")
    
    local_ip = "192.168.55.10"
    robot = magicdog.MagicRobot()
    if not robot.initialize(local_ip):
        print("机器人初始化失败")
        return

    robot.set_timeout(5000)
    if not robot.connect():
        print("机器人连接失败")
        robot.shutdown()
        return
    
    print("机器人连接成功")
    
    audio_controller = robot.get_audio_controller()

    # 获取当前音量
    volume = audio_controller.get_volume()
    if volume != -1:
        print(f"当前音量为: {volume}")
    else:
        print("获取音量失败")

    # 设置音量
    status = audio_controller.set_volume(50)
    if status.code != magicdog.ErrorCode.OK:
        print(f"设置音量失败: {status.message}")
        robot.shutdown()
        return
    
    # 再次获取音量确认设置成功
    volume = audio_controller.get_volume()
    if volume != -1:
        print(f"设置音量成功, 当前音量为: {volume}")
    else:
        print("设置音量后获取音量失败")
    
    tts_command = TtsCommand()
    tts_command.id = "100000000002"
    tts_command.content = "今天天气怎么样！"
    tts_command.priority = TtsPriority.HIGH
    tts_command.mode = TtsMode.CLEARTOP
    status = audio_controller.play(tts_command)
    if status.code != magicdog.ErrorCode.OK:
        print(f"播放语音失败: {status.message}")
        robot.shutdown()
        return
    
    time.sleep(5)
    
    status = audio_controller.stop()
    if status.code != magicdog.ErrorCode.OK:
        print(f"停止播放语音失败: {status.message}")
        robot.shutdown()
        return

    # 获取语音配置
    speech_config = audio_controller.get_voice_config()
    if speech_config:
        print("获取语音配置成功:")
        print(f"  TTS类型: {speech_config.tts_type}")
        # 打印配置内容
        print(f"  配置详情:")
        
        if speech_config.speaker_config:
            speaker = speech_config.speaker_config
            print(f"    扬声器配置:")
            print(f"      数据: {speaker.data}")
            print(f"      选中: {speaker.selected.speaker_id} {speaker.selected.region}")
            print(f"      语速: {speaker.speaker_speed}")
        
        if speech_config.bot_config:
            bot = speech_config.bot_config
            print(f"    机器人配置:")
            print(f"      数据: ")
            # bot.data 是一个字典，键为字符串，值为包含 [id, 名称] 的列表
            for bot_id, bot_info in bot.data.items():
                print(f"        智能体ID: {bot_id}")
                print(f"          名称: {bot_info.name}")
                print(f"          工作流ID: {bot_info.workflow}")
                
            print(f"      自定义数据: {bot.custom_data}")
            print(f"      选中: {bot.selected.bot_id}")
        
        if speech_config.wakeup_config:
            wakeup = speech_config.wakeup_config
            print(f"    唤醒配置:")
            print(f"      名称: {wakeup.name}")
            print(f"      数据: {wakeup.data}")
        
        if speech_config.dialog_config:
            dialog = speech_config.dialog_config
            print(f"    对话配置:")
            print(f"      前置DOA: {dialog.is_front_doa}")
            print(f"      全双工启用: {dialog.is_fullduplex_enable}")
            print(f"      启用: {dialog.is_enable}")
            print(f"      DOA启用: {dialog.is_doa_enable}")
    else:
        print("获取语音配置失败")   

    def subscribe_origin_voice_data(data):
        print(f"收到原始语音数据: {data.data}")
    def subscribe_bf_voice_data(data):
        print(f"收到BF语音数据: {data.data}")

    audio_controller.subscribe_origin_voice_data(subscribe_origin_voice_data)
    audio_controller.subscribe_bf_voice_data(subscribe_bf_voice_data)

    audio_controller.control_voice_stream(True, True)

    time.sleep(10)

    audio_controller.control_voice_stream(False, False)

    # 避免 lcm 中有缓冲数据未处理完
    time.sleep(10)

    robot.disconnect()
    robot.shutdown()
    print("\n示例程序执行完成！")

if __name__ == "__main__":
    main() 