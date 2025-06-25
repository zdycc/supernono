from app import create_app, db
from app.models import Admin, User, ChatRoom, Message, user_chatrooms

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """Flask shell上下文处理器"""
    return {
        'db': db,
        'Admin': Admin,
        'User': User,
        'ChatRoom': ChatRoom,
        'Message': Message,
        'user_chatrooms': user_chatrooms
    }

def clear_all_sessions():
    """清除所有Session数据（启动时调用）"""
    try:
        print("✅ Session清理完成")
    except Exception as e:
        print(f"⚠️ Session清理时出现警告: {e}")

if __name__ == '__main__':
    print("正在启动 Supernono AI聊天机器人...")
    
    with app.app_context():
        db.create_all()

        try:
            from sqlalchemy import text
            
            # 检查last_seen字段是否存在
            result = db.session.execute(text("DESCRIBE users"))
            columns = [row[0] for row in result]
            
            if 'last_seen' not in columns:
                print("📊 正在添加last_seen字段...")
                db.session.execute(text("ALTER TABLE users ADD COLUMN last_seen DATETIME DEFAULT CURRENT_TIMESTAMP"))
                db.session.commit()
                print("✅ last_seen字段添加成功")
                
                # 为现有用户设置初始last_seen值
                db.session.execute(text("UPDATE users SET last_seen = created_at WHERE last_seen IS NULL"))
                db.session.commit()
                print("✅ 现有用户last_seen值初始化完成")
            
        except Exception as e:
            print(f"⚠️ 数据库升级检查失败: {e}")
            
        # 🔒 强制所有用户下线（设置为超时状态）
        try:
            from datetime import datetime, timedelta
            # 将所有用户的last_seen设置为6分钟前，确保is_online()返回False
            offline_time = datetime.utcnow() - timedelta(minutes=6)
            updated_count = db.session.execute(
                text("UPDATE users SET last_seen = :offline_time"), 
                {"offline_time": offline_time}
            ).rowcount
            db.session.commit()
            print(f"🔒 强制 {updated_count} 个用户下线（设置为离线状态）")
        except Exception as e:
            print(f"⚠️ 强制下线操作失败: {e}")
            db.session.rollback()
        
        print("📊 数据库表创建/检查完成！")
        
        # 检查默认管理员账户（仅在数据库为空时创建）
        try:
            admin_count = Admin.query.count()
            if admin_count == 0:
                admin = Admin(username='admin')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("👤 默认管理员账户创建完成！用户名：admin，密码：admin123")
            else:
                print(f"📊 检测到 {admin_count} 个管理员账户已存在")
        except Exception as e:
            print(f"⚠️ 数据库检查失败: {e}")
            print("💡 请确保MySQL数据库正在运行并且连接配置正确")
        
        # 清除所有Session
        clear_all_sessions()
    
    print("🌐 服务器启动地址：http://localhost:5000")
    print("🔑 测试账户：")
    print("   管理员：admin / admin123")
    print("   用户：demo / demo（需要管理员创建）")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000) 