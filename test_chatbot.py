#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChatGLM3 + MindSpore 聊天系统测试脚本
"""

import sys
import os
import time
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mindspore_processor():
    """测试MindSpore文本处理器"""
    print("🔍 正在测试MindSpore文本处理器...")
    
    try:
        from app.utils.ai_chatbot import MindSporeTextProcessor
        
        processor = MindSporeTextProcessor()
        
        # 测试情感分析
        test_texts = [
            "我今天心情很好！",
            "这个产品真的很糟糕",
            "天气不错，适合出门"
        ]
        
        print("\n📊 情感分析测试:")
        for text in test_texts:
            sentiment = processor.analyze_sentiment(text)
            print(f"文本: {text}")
            print(f"情感: {sentiment}")
            print("-" * 50)
        
        # 测试意图识别
        test_intents = [
            "你好，很高兴认识你",
            "谢谢你的帮助",
            "请问现在几点了？",
            "再见，下次聊"
        ]
        
        print("\n🎯 意图识别测试:")
        for text in test_intents:
            intent = processor.process_intent(text)
            print(f"文本: {text}")
            print(f"意图: {intent}")
            print("-" * 50)
        
        # 测试关键词提取
        test_keywords = [
            "我想了解人工智能的发展历史和未来趋势",
            "请帮我制定一个健康的运动计划",
            "介绍一下Python编程语言的特点"
        ]
        
        print("\n🔑 关键词提取测试:")
        for text in test_keywords:
            keywords = processor.extract_keywords(text, top_k=3)
            print(f"文本: {text}")
            print(f"关键词: {keywords}")
            print("-" * 50)
        
        print("✅ MindSpore文本处理器测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ MindSpore文本处理器测试失败: {e}")
        return False

def test_supernono_bot():
    """测试supernono聊天机器人"""
    print("\n🤖 正在测试supernono聊天机器人...")
    
    try:
        from app.utils.ai_chatbot import get_supernono_bot
        
        # 获取机器人实例
        print("正在初始化supernono机器人...")
        bot = get_supernono_bot()
        
        # 显示系统信息
        info = bot.get_info()
        print("\n📋 系统信息:")
        for key, value in info.items():
            print(f"{key}: {value}")
        
        # 测试对话
        test_conversations = [
            "你好！我是新用户",
            "你能做什么？",
            "请介绍一下你自己",
            "我今天心情不好",
            "谢谢你的帮助",
            "再见！"
        ]
        
        print("\n💬 对话测试:")
        user_id = "test_user_" + str(int(time.time()))
        
        for i, message in enumerate(test_conversations, 1):
            print(f"\n[第{i}轮对话]")
            print(f"用户: {message}")
            
            start_time = time.time()
            response = bot.chat(message, user_id=user_id)
            end_time = time.time()
            
            print(f"机器人: {response}")
            print(f"响应时间: {end_time - start_time:.2f}秒")
            print("-" * 50)
        
        # 测试多用户对话
        print("\n👥 多用户对话测试:")
        user1_id = "user_1"
        user2_id = "user_2"
        
        # 用户1的对话
        response1 = bot.chat("我叫张三", user_id=user1_id)
        print(f"用户1: 我叫张三")
        print(f"回复: {response1}")
        
        # 用户2的对话
        response2 = bot.chat("我叫李四", user_id=user2_id)
        print(f"用户2: 我叫李四")
        print(f"回复: {response2}")
        
        # 测试记忆功能
        memory_test1 = bot.chat("我的名字是什么？", user_id=user1_id)
        memory_test2 = bot.chat("我的名字是什么？", user_id=user2_id)
        
        print(f"用户1问名字: {memory_test1}")
        print(f"用户2问名字: {memory_test2}")
        
        print("✅ supernono聊天机器人测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ supernono聊天机器人测试失败: {e}")
        print("💡 提示: 首次运行需要下载模型，可能需要较长时间")
        return False

def test_compatibility():
    """测试向后兼容性"""
    print("\n🔄 正在测试向后兼容性...")
    
    try:
        # 测试新的接口
        from app.utils.ai_chatbot import SupernonoBot, get_supernono_bot
        
        # 方式1：直接实例化
        bot1 = SupernonoBot()
        response1 = bot1.chat("你好，supernono！")
        print(f"直接实例化测试:")
        print(f"用户: 你好，supernono！")
        print(f"回复: {response1}")
        
        # 方式2：单例模式
        bot2 = get_supernono_bot()
        response2 = bot2.chat("测试单例模式")
        print(f"\n单例模式测试:")
        print(f"用户: 测试单例模式")
        print(f"回复: {response2}")
        
        # 获取信息
        info = bot1.get_info()
        print(f"\n机器人信息: {info}")
        
        print("✅ 向后兼容性测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 向后兼容性测试失败: {e}")
        return False

def performance_test():
    """性能压力测试"""
    print("\n⚡ 正在进行性能测试...")
    
    try:
        from app.utils.ai_chatbot import SupernonoBot
        
        bot = SupernonoBot()
        
        # 连续对话测试
        messages = ["你好"] * 10
        total_time = 0
        
        for i, message in enumerate(messages, 1):
            start_time = time.time()
            response = bot.chat(f"{message} - 第{i}次", user_id="perf_test")
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            print(f"第{i}次对话响应时间: {response_time:.2f}秒")
        
        avg_time = total_time / len(messages)
        print(f"\n📊 性能统计:")
        print(f"总对话次数: {len(messages)}")
        print(f"总用时: {total_time:.2f}秒")
        print(f"平均响应时间: {avg_time:.2f}秒")
        
        if avg_time < 5:
            print("✅ 性能表现优秀！")
        elif avg_time < 10:
            print("⚠️ 性能表现良好")
        else:
            print("❌ 性能需要优化")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 ChatGLM3 + MindSpore 聊天系统测试开始")
    print("=" * 80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(("MindSpore文本处理器", test_mindspore_processor()))
    test_results.append(("supernono聊天机器人", test_supernono_bot()))
    test_results.append(("向后兼容性", test_compatibility()))
    test_results.append(("性能测试", performance_test()))
    
    # 显示测试结果汇总
    print("\n" + "=" * 80)
    print("📋 测试结果汇总:")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("-" * 80)
    print(f"总测试项: {total}")
    print(f"通过测试: {passed}")
    print(f"失败测试: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！supernono智能聊天系统运行正常！")
    else:
        print("\n⚠️ 部分测试失败，请检查错误信息并修复问题。")
    
    print("\n💡 提示:")
    print("- 首次运行会自动下载ChatGLM3模型（约12GB）")
    print("- 如果GPU可用，supernono会自动使用GPU加速")
    print("- 如遇到内存不足，请尝试重启Python进程")
    print("- supernono现在是唯一的聊天机器人，集成了所有AI功能")

if __name__ == "__main__":
    main() 