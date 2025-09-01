#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来控制机器人。
"""

import sys
import time


try:
    import magicdog_python as magicdog
    from magicdog_python import TtsCommand, TtsPriority, TtsMode, GetSpeechConfig, ErrorCode
    print("Successfully imported MagicDog Python module!")
    print(f"Imported magicdog_python path: {sys.path}")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

print("=== 测试 TTS 优先级枚举 ===")
tts_priority = magicdog.TtsPriority.HIGH
print(f"TTS优先级: {tts_priority} (HIGH - 最高优先级，用于紧急提醒)")

tts_mode = magicdog.TtsMode.ADD
print(f"TTS模式: {tts_mode} (ADD - 追加到队列尾部，不打断当前播放)")

print("\n=== 测试 TTS 命令结构体 ===")
tts_cmd = magicdog.TtsCommand()
tts_cmd.id = "weather_alert_001"
tts_cmd.content = "今日天气晴朗，温度25度，适合户外活动"
tts_cmd.priority = tts_priority
tts_cmd.mode = tts_mode
print(f"TTS命令: ID={tts_cmd.id}, 内容='{tts_cmd.content}', 优先级={tts_cmd.priority}, 模式={tts_cmd.mode}")

print("\n=== 测试自定义机器人信息 ===")
custom_bot_info = magicdog.CustomBotInfo()
custom_bot_info.name = "智能客服助手"
custom_bot_info.workflow = "customer_service_workflow_v2.1"
custom_bot_info.token = "cs_token_2024_001"
print(f"自定义机器人: 名称='{custom_bot_info.name}', 工作流='{custom_bot_info.workflow}', 令牌='{custom_bot_info.token}'")

custom_bot_map = magicdog.StringCustomBotMap()
custom_bot_map["cs_bot_001"] = custom_bot_info
for key, value in custom_bot_map.items():
    print(f"机器人映射: {key} -> {value.name}")

print("\n=== 测试语音设置配置 ===")
set_speech_config = magicdog.SetSpeechConfig()
set_speech_config.speaker_id = "xiaoyun_female"
set_speech_config.region = "zh-CN"
set_speech_config.bot_id = "main_assistant"
set_speech_config.is_front_doa = True
set_speech_config.is_fullduplex_enable = True
set_speech_config.is_enable = True
set_speech_config.is_doa_enable = True
set_speech_config.speaker_speed = 1.2
set_speech_config.wakeup_name = "小云"
set_speech_config.custom_bot = custom_bot_map
print(f"语音设置: 音色ID='{set_speech_config.speaker_id}', 地区='{set_speech_config.region}', 机器人ID='{set_speech_config.bot_id}'")
print(f"语音设置: 语速={set_speech_config.speaker_speed}, 唤醒词='{set_speech_config.wakeup_name}'")

print("\n=== 测试音色配置选择 ===")
speaker_config_selected = magicdog.SpeakerConfigSelected()
speaker_config_selected.region = "zh-CN"
speaker_config_selected.speaker_id = "xiaoyun_female"
print(f"选中的音色配置: 地区='{speaker_config_selected.region}', 音色ID='{speaker_config_selected.speaker_id}'")

print("\n=== 测试音色配置数据结构 ===")
speaker_config_data = magicdog.String2DStringVectorMap()

# 创建中文音色数据
array1 = magicdog.S2DString()
array1[0] = "xiaoyun_female"
array1[1] = "小云女声"

array2 = magicdog.S2DString()
array2[0] = "xiaogang_male"
array2[1] = "小刚男声"

array3 = magicdog.S2DString()
array3[0] = "xiaomei_female"
array3[1] = "小美女声"

# 创建向量并添加音色数组
vector_data = magicdog.S2DStringVector()
vector_data.append(array1)
vector_data.append(array2)
vector_data.append(array3)

# 设置中文地区音色数据
speaker_config_data["zh-CN"] = vector_data

# 创建英文音色数据
array_en1 = magicdog.S2DString()
array_en1[0] = "john_male"
array_en1[1] = "John Male Voice"

array_en2 = magicdog.S2DString()
array_en2[0] = "sarah_female"
array_en2[1] = "Sarah Female Voice"

vector_en_data = magicdog.S2DStringVector()
vector_en_data.append(array_en1)
vector_en_data.append(array_en2)

# 设置英文地区音色数据
speaker_config_data["en-US"] = vector_en_data

print("音色配置数据:")
for region, speakers in speaker_config_data.items():
    print(f"  地区: {region}")
    for speaker in speakers:
        print(f"    音色ID: {speaker[0]}, 音色名称: {speaker[1]}")

speaker_config = magicdog.SpeakerConfig()
speaker_config.data = speaker_config_data
speaker_config.selected = speaker_config_selected
speaker_config.speaker_speed = 1.2
print(f"音色配置: 语速={speaker_config.speaker_speed}")

print("\n=== 测试机器人配置 ===")
bot_info = magicdog.BotInfo()
bot_info.name = "智能家居控制"
bot_info.workflow = "smart_home_control_v1.0"

bot_config_selected = magicdog.BotConfigSelected()
bot_config_selected.bot_id = "home_bot_001"

bot_config_data = magicdog.StringBotInfoMap()
bot_config_data["home_bot_001"] = bot_info

# 创建另一个机器人
bot_info2 = magicdog.BotInfo()
bot_info2.name = "天气查询助手"
bot_info2.workflow = "weather_query_v2.1"
bot_config_data["weather_bot_002"] = bot_info2

print("标准机器人配置:")
for bot_id, info in bot_config_data.items():
    print(f"  机器人ID: {bot_id}, 名称: {info.name}, 工作流: {info.workflow}")

custom_bot_info = magicdog.CustomBotInfo()
custom_bot_info.name = "智能客服助手"
custom_bot_info.workflow = "customer_service_workflow_v2.1"
custom_bot_info.token = "cs_token_2024_001"

custom_bot_map = magicdog.StringCustomBotMap()
custom_bot_map["cs_bot_001"] = custom_bot_info

bot_config = magicdog.BotConfig()
bot_config.data = bot_config_data
bot_config.custom_data = custom_bot_map
bot_config.selected = bot_config_selected
print(f"机器人配置: 选中的机器人ID='{bot_config.selected.bot_id}'")

print("\n=== 测试唤醒配置 ===")
wakeup_config_data = magicdog.StringStringMap()
wakeup_config_data["小云"] = "xiao yun"
wakeup_config_data["小刚"] = "xiao gang"
wakeup_config_data["小美"] = "xiao mei"
wakeup_config_data["Hello"] = "he llo"

wakeup_config = magicdog.WakeupConfig()
wakeup_config.name = "小云"
wakeup_config.data = wakeup_config_data

print("唤醒配置:")
print(f"  唤醒名称: {wakeup_config.name}")
for wakeup_word, pinyin in wakeup_config.data.items():
    print(f"  唤醒词: '{wakeup_word}' -> 拼音: '{pinyin}'")

print("\n=== 测试对话配置 ===")
dialog_config = magicdog.DialogConfig()
dialog_config.is_front_doa = True
dialog_config.is_fullduplex_enable = True
dialog_config.is_enable = True
dialog_config.is_doa_enable = True

print("对话配置:")
print(f"  强制正前方拾音: {dialog_config.is_front_doa}")
print(f"  全双工对话: {dialog_config.is_fullduplex_enable}")
print(f"  语音开关: {dialog_config.is_enable}")
print(f"  唤醒方位转头: {dialog_config.is_doa_enable}")

print("\n=== 测试完整语音配置 ===")
get_speech_config = magicdog.GetSpeechConfig()
get_speech_config.speaker_config = speaker_config
get_speech_config.bot_config = bot_config
get_speech_config.wakeup_config = wakeup_config
get_speech_config.dialog_config = dialog_config

print("完整语音配置已创建，包含:")
print(f"  - 音色配置: {len(speaker_config.data)} 个地区")
print(f"  - 机器人配置: {len(bot_config.data)} 个标准机器人 + {len(bot_config.custom_data)} 个自定义机器人")
print(f"  - 唤醒配置: {len(wakeup_config.data)} 个唤醒词")
print(f"  - 对话配置: 语音{'启用' if dialog_config.is_enable else '禁用'}")

print("\n=== 测试完成 ===")