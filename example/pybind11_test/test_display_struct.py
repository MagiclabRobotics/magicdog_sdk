#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MagicDog SDK Python 使用示例

这个文件展示了如何使用 MagicDog SDK 的 Python 绑定来控制机器人。
"""

import sys
import time
import magicdog_python as magicdog

print("\n=== 测试表情数据结构 ===")
face_expression = magicdog.FaceExpression()
face_expression.id = 30
face_expression.name = "happy"
face_expression.description = "开心"

print("\n=== 测试设置值读取和验证 ===")

# 验证表情数据结构
print("验证表情数据结构:")
print(
    f"  设置值 - ID='{face_expression.id}', 名称='{face_expression.name}', 描述='{face_expression.description}'"
)
print(
    f"  读取值 - ID='{face_expression.id}', 名称='{face_expression.name}', 描述='{face_expression.description}'"
)

# 执行一致性检查
print("\n=== 执行一致性检查 ===")
all_checks_passed = True


# 检查表情数据结构一致性
if face_expression.id != 30:
    print(
        f"❌ 表情ID不一致: 期望 '30', 实际 '{face_expression.id}'"
    )
    all_checks_passed = False
else:
    print("✅ 表情ID一致")

if face_expression.name != "happy":
    print(
        f"❌ 表情名称不一致: 期望 'happy', 实际 '{face_expression.name}'"
    )
    all_checks_passed = False
else:
    print("✅ 表情名称一致")

if face_expression.description != "开心":
    print(
        f"❌ 表情描述不一致: 期望 '开心', 实际 '{face_expression.description}'"
    )
    all_checks_passed = False
else:
    print("✅ 表情描述一致")


# 输出最终结果
print(f"\n=== 一致性检查结果 ===")
if all_checks_passed:
    print("🎉 所有设置值与读取值完全一致！测试通过！")
else:
    print("❌ 发现不一致的值，测试失败！")
    sys.exit(1)

print("\n=== 测试完成 ===")
