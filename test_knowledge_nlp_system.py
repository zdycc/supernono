#!/usr/bin/env python3
"""
测试知识库 + MindSpore NLP 集成系统
"""

import sys
import os
sys.path.append('.')

def test_knowledge_base():
    """测试知识库功能"""
    print("📚 测试知识库系统")
    print("=" * 50)
    
    from app.utils.knowledge_base import search_knowledge, get_emotional_support
    
    test_questions = [
        "什么是软件工程？",
        "敏捷开发的核心价值观是什么？",
        "设计模式有哪些类型？",
        "项目管理的生命周期包括哪些阶段？",
        "软件测试的方法有哪些？",
        "我感到很沮丧，项目进度太慢了",
        "职业发展路径有哪些选择？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 测试 {i}: {question}")
        answer, confidence = search_knowledge(question)
        print(f"📋 置信度: {confidence:.2f}")
        print(f"💬 回答: {answer[:200]}...")
        
        # 测试情绪支持
        if "沮丧" in question or "困难" in question:
            emotion, support = get_emotional_support(question)
            print(f"💝 情绪检测: {emotion}")
            print(f"💝 支持回复: {support}")
    
    print("\n✅ 知识库测试完成！")

def test_mindspore_nlp():
    """测试MindSpore NLP功能"""
    print("\n🧠 测试MindSpore NLP系统")
    print("=" * 50)
    
    from app.utils.mindspore_nlp import process_text, get_smart_routing, calculate_similarity
    
    test_texts = [
        "请问什么是软件工程？",
        "我需要学习Python编程",
        "项目管理太难了，我很困惑",
        "Java和Python有什么区别？",
        "帮我解决这个代码bug",
        "谢谢你的帮助！",
        "敏捷开发适合我们团队吗？"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n🔍 文本 {i}: {text}")
        
        # 基础分析
        analysis = process_text(text)
        print(f"🎯 关键词: {analysis['keywords'][:3]}")
        print(f"🎯 意图: {analysis['intent']} (置信度: {analysis['intent_confidence']:.2f})")
        print(f"😊 情绪: {analysis['emotion']} (置信度: {analysis['emotion_confidence']:.2f})")
        print(f"🔧 技术话题: {len(analysis['technical_topics'])} 个")
        
        # 智能路由
        routing = get_smart_routing(text)
        route_info = routing['routing']
        print(f"🚦 路由决策: 知识库={route_info['use_knowledge_base']}, "
              f"情绪支持={route_info['use_emotional_support']}")
        
        # 相似度测试
        if i > 1:
            similarity = calculate_similarity(text, test_texts[0])
            print(f"🔗 与第一个文本相似度: {similarity:.3f}")
    
    print("\n✅ MindSpore NLP测试完成！")

def test_integrated_system():
    """测试集成系统"""
    print("\n🤖 测试集成AI系统")
    print("=" * 50)
    
    try:
        from app.utils.ai_chatbot import SupernonoBot
        
        # 初始化机器人（但不等待ChatGLM3加载）
        bot = SupernonoBot()
        
        integration_tests = [
            "你好，请介绍一下自己",
            "什么是敏捷开发？",
            "我对项目管理感到很困惑，能帮助我吗？",
            "Python和Java在web开发中的区别",
            "设计模式在软件工程中的作用",
            "我最近工作压力很大，感到很疲惫",
            "如何规划软件工程师的职业发展？"
        ]
        
        for i, question in enumerate(integration_tests, 1):
            print(f"\n💬 对话 {i}: {question}")
            print("-" * 30)
            
            response = bot.chat(question, f"test_user_{i}")
            print(f"🤖 Supernono: {response}")
            
            # 显示状态
            status = bot.get_status()
            print(f"📊 状态: 模型加载={status['model_loaded']}, 设备={status['device']}")
        
        print("\n✅ 集成系统测试完成！")
        
    except ImportError as e:
        print(f"❌ 集成测试失败，模块导入错误: {e}")
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")

def test_performance():
    """测试系统性能"""
    print("\n⚡ 性能测试")
    print("=" * 50)
    
    import time
    from app.utils.knowledge_base import search_knowledge
    from app.utils.mindspore_nlp import process_text
    
    test_query = "什么是软件工程的核心原则？"
    iterations = 10
    
    # 知识库性能测试
    start_time = time.time()
    for _ in range(iterations):
        search_knowledge(test_query)
    kb_time = (time.time() - start_time) / iterations
    
    # NLP处理性能测试
    start_time = time.time()
    for _ in range(iterations):
        process_text(test_query)
    nlp_time = (time.time() - start_time) / iterations
    
    print(f"📚 知识库平均响应时间: {kb_time*1000:.2f} ms")
    print(f"🧠 NLP处理平均时间: {nlp_time*1000:.2f} ms")
    print(f"⚡ 总体平均响应时间: {(kb_time + nlp_time)*1000:.2f} ms")
    
    if (kb_time + nlp_time) < 0.1:
        print("✅ 性能优秀：<100ms响应")
    elif (kb_time + nlp_time) < 0.5:
        print("✅ 性能良好：<500ms响应")
    else:
        print("⚠️ 性能需要优化：>500ms响应")

def main():
    """主测试流程"""
    print("🧪 Supernono 知识库 + MindSpore NLP 系统测试")
    print("=" * 60)
    
    try:
        # 1. 测试知识库
        test_knowledge_base()
        
        # 2. 测试MindSpore NLP
        test_mindspore_nlp()
        
        # 3. 测试集成系统
        test_integrated_system()
        
        # 4. 性能测试
        test_performance()
        
        print(f"\n🎉 所有测试完成！")
        print("📋 系统特性总结：")
        print("   ✅ 本地软件工程知识库 (秒级响应)")
        print("   ✅ MindSpore自然语言处理 (意图识别、情感分析)")
        print("   ✅ 智能情绪支持系统")
        print("   ✅ 可选ChatGLM3深度分析")
        print("   ✅ 硬件适配 (CPU友好)")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 