#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supernono Web界面测试脚本
验证纯本地知识库+MindSpore NLP系统的Web功能
"""

import requests
import json
import time

def test_web_server():
    """测试Web服务器是否响应"""
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Web服务器响应正常")
            print(f"   状态码: {response.status_code}")
            print(f"   响应时间: {response.elapsed.total_seconds():.3f}秒")
            return True
        else:
            print(f"❌ Web服务器响应异常，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到Web服务器: {e}")
        return False

def test_login_page():
    """测试登录页面"""
    try:
        response = requests.get("http://localhost:5000/auth/login", timeout=5)
        if response.status_code == 200 and "登录" in response.text:
            print("✅ 登录页面加载正常")
            return True
        else:
            print("❌ 登录页面加载失败")
            return False
    except Exception as e:
        print(f"❌ 登录页面测试失败: {e}")
        return False

def test_chat_system():
    """测试聊天系统（需要登录后才能测试）"""
    try:
        # 这里只是测试API端点是否存在
        response = requests.get("http://localhost:5000/chat", timeout=5)
        # 302重定向到登录页面是正常的（未登录状态）
        if response.status_code in [200, 302]:
            print("✅ 聊天系统端点响应正常")
            return True
        else:
            print(f"❌ 聊天系统端点异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 聊天系统测试失败: {e}")
        return False

def test_supernono_api():
    """模拟测试supernono AI功能（直接调用后端）"""
    try:
        # 这里我们直接导入模块测试，因为API需要登录
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app.utils.ai_chatbot import get_supernono_bot
        
        bot = get_supernono_bot()
        
        # 测试几个问题
        test_questions = [
            "什么是软件工程",
            "我感到困惑",
            "敏捷开发的优势"
        ]
        
        print("🤖 测试Supernono AI功能:")
        for i, question in enumerate(test_questions):
            start_time = time.time()
            response = bot.chat(question, f"web_test_{i}")
            end_time = time.time()
            
            print(f"  问题 {i+1}: {question}")
            print(f"  回答: {response[:100]}...")
            print(f"  响应时间: {end_time - start_time:.3f}秒")
            print("-" * 50)
        
        print("✅ Supernono AI功能测试完成")
        return True
        
    except Exception as e:
        print(f"❌ Supernono AI功能测试失败: {e}")
        return False

def test_system_status():
    """测试系统状态"""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app.utils.ai_chatbot import get_supernono_bot
        
        bot = get_supernono_bot()
        status = bot.get_status()
        kb_stats = bot.get_knowledge_stats()
        
        print("📊 系统状态:")
        print(f"  系统名称: {status['name']}")
        print(f"  版本: {status['version']}")
        print(f"  系统类型: {status['system_type']}")
        print(f"  系统就绪: {status['system_ready']}")
        
        print("\n📚 知识库统计:")
        for key, value in kb_stats.items():
            print(f"  {key}: {value}")
        
        print("✅ 系统状态检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 系统状态检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🌐 Supernono Web界面功能测试")
    print("=" * 60)
    
    tests = [
        ("Web服务器连接", test_web_server),
        ("登录页面", test_login_page),
        ("聊天系统端点", test_chat_system),
        ("Supernono AI功能", test_supernono_api),
        ("系统状态检查", test_system_status)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 测试: {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 Web测试结果汇总:")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总结: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 Web系统完全正常！")
        print("💡 访问地址: http://localhost:5000")
        print("🔑 测试账户:")
        print("   管理员: admin / admin123")
        print("   用户: demo / demo123")
        print("\n🚀 系统特性:")
        print("   - 纯本地知识库运行")
        print("   - MindSpore NLP智能分析")
        print("   - 毫秒级响应速度")
        print("   - 专业软件工程知识")
        print("   - 情绪支持功能")
    else:
        print("\n⚠️ 部分Web功能可能存在问题")
        print("💡 建议检查:")
        print("   - Flask应用是否正常启动")
        print("   - 数据库连接是否正常")
        print("   - 所有依赖是否安装完整")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    print(f"\n{'🎉 测试成功' if success else '❌ 测试失败'}") 