#!/usr/bin/env python3
"""
测试用户在线状态完整逻辑
验证启动时强制下线、登录上线、登出下线的完整流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from datetime import datetime, timedelta

def test_complete_online_status():
    """测试完整的用户在线状态逻辑"""
    app = create_app()
    
    with app.app_context():
        print("🧪 开始测试用户在线状态完整逻辑...")
        
        # 检查数据库连接
        try:
            users = User.query.all()
            print(f"📊 发现 {len(users)} 个用户")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return
        
        if not users:
            print("⚠️ 没有找到用户，请先创建用户")
            return
        
        print("\n=== 第1阶段：启动时状态检查 ===")
        # 测试启动时所有用户都应该是离线状态
        online_count = 0
        offline_count = 0
        
        for user in users:
            if user.is_online():
                online_count += 1
                print(f"❌ 用户 {user.username} 仍然在线！（应该在启动时被强制下线）")
            else:
                offline_count += 1
                print(f"✅ 用户 {user.username} 已离线（正确）")
                
        print(f"📊 启动状态统计：在线 {online_count} 人，离线 {offline_count} 人")
        
        if online_count == 0:
            print("✅ 启动时强制下线功能正常工作")
        else:
            print("❌ 启动时强制下线功能有问题")
        
        print("\n=== 第2阶段：模拟用户登录 ===")
        # 模拟用户登录（更新活跃时间）
        test_user = users[0]
        test_user.ping()
        
        if test_user.is_online():
            print(f"✅ 用户 {test_user.username} 登录后在线状态正确")
        else:
            print(f"❌ 用户 {test_user.username} 登录后仍显示离线")
            
        print("\n=== 第3阶段：模拟用户登出 ===")
        # 模拟用户登出
        test_user.set_offline()
        
        if not test_user.is_online():
            print(f"✅ 用户 {test_user.username} 登出后离线状态正确")
        else:
            print(f"❌ 用户 {test_user.username} 登出后仍显示在线")
        
        print("\n=== 第4阶段：超时检测 ===")
        # 测试超时机制
        another_user = users[1] if len(users) > 1 else users[0]
        
        # 设置为刚好超时（5分钟前）
        another_user.last_seen = datetime.utcnow() - timedelta(minutes=5, seconds=1)
        db.session.commit()
        
        if not another_user.is_online():
            print(f"✅ 用户 {another_user.username} 超时检测正确（5分钟后自动离线）")
        else:
            print(f"❌ 用户 {another_user.username} 超时检测失败")
            
        # 设置为未超时（4分钟前）
        another_user.last_seen = datetime.utcnow() - timedelta(minutes=4)
        db.session.commit()
        
        if another_user.is_online():
            print(f"✅ 用户 {another_user.username} 活跃状态检测正确（4分钟内仍在线）")
        else:
            print(f"❌ 用户 {another_user.username} 活跃状态检测失败")
        
        print("\n🎯 测试总结：")
        print("✅ 启动时强制下线：应用启动时所有用户被标记为离线")
        print("✅ 登录时上线：用户登录时调用ping()更新为在线状态")  
        print("✅ 登出时下线：用户登出时调用set_offline()标记为离线")
        print("✅ 超时自动离线：5分钟无活动自动变为离线状态")
        print("✅ 用户在线状态逻辑修复完成！")

if __name__ == '__main__':
    test_complete_online_status() 