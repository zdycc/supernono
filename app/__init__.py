from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import atexit
import os

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()

# 全局变量用于跟踪应用启动状态
app_startup_flag = True

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login用户加载回调"""
    if user_id.startswith('admin_'):
        from app.models.admin import Admin
        admin_id = user_id.replace('admin_', '')
        return Admin.query.get(int(admin_id))
    elif user_id.startswith('user_'):
        from app.models.user import User
        real_user_id = user_id.replace('user_', '')
        return User.query.get(int(real_user_id))
    return None

def create_app():
    global app_startup_flag
    
    # 指定static文件夹为项目根目录的static
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(Config)
    
    # 强制退出登录配置
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1小时后自动过期
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为False
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.session_protection = 'strong'  # 强Session保护
    
    # 使用before_request来处理应用启动时的Session清理
    @app.before_request
    def check_app_restart():
        """检查应用是否重新启动，如果是则强制退出登录"""
        global app_startup_flag
        
        if app_startup_flag:
            # 清除启动标记
            app_startup_flag = False
            # 如果用户已登录，强制清除Session
            if 'user_id' in session or '_user_id' in session or session.get('user_type'):
                session.clear()
                print("🚪 检测到应用重启，已强制清除用户登录状态")
    
    @app.route('/')
    def index():
        """根路径重定向到登录页面"""
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # 在应用上下文中初始化启动标记
    with app.app_context():
        print("🔒 应用启动：强制清除所有登录状态")
        app_startup_flag = True
    
    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.user import user_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(chat_bp)
    
    return app 