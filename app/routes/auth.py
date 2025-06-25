from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.admin import Admin
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面 - 自动判断用户身份"""
    # 强制清除任何现有的登录状态
    if current_user.is_authenticated:
        logout_user()
        session.clear()
        flash('检测到之前的登录状态，已自动退出，请重新登录', 'info')
        return redirect(url_for('auth.login'))
    
    # 确保Session是干净的
    if session.get('user_type') or '_user_id' in session:
        session.clear()
        print("🔄 清除残留的Session数据")
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请填写用户名和密码', 'error')
            return render_template('auth/login.html')
        
        # 先尝试管理员登录
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            # 管理员登录成功
            session.clear()
            login_user(admin, remember=False)
            session['user_type'] = 'admin'
            session['login_time'] = str(True)
            session.permanent = True
            
            flash(f'欢迎管理员：{username}！', 'success')
            print(f"✅ 管理员 {username} 成功登录")
            return redirect(url_for('admin.dashboard'))
        
        # 再尝试普通用户登录
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # 普通用户登录成功
            session.clear()
            login_user(user, remember=False)
            session['user_type'] = 'user'
            session['login_time'] = str(True)
            session.permanent = True
            
            # 更新用户最后活跃时间
            user.ping()
            
            flash(f'欢迎用户：{username}！', 'success')
            print(f"✅ 用户 {username} 成功登录")
            return redirect(url_for('user.dashboard'))
        
        # 登录失败
        flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """登出"""
    username = current_user.username if current_user.is_authenticated else '用户'
    
    # 在登出前将用户标记为离线
    if current_user.is_authenticated and hasattr(current_user, 'set_offline'):
        current_user.set_offline()
    
    logout_user()
    session.clear()
    flash(f'再见，{username}！您已安全退出', 'info')
    print(f"🚪 用户 {username} 已退出登录并设为离线状态")
    return redirect(url_for('auth.login'))

@auth_bp.route('/force_logout')
def force_logout():
    """强制退出登录（用于应用重启时的清理）"""
    if current_user.is_authenticated:
        logout_user()
    session.clear()
    flash('您的登录状态已过期，请重新登录', 'warning')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册（仅供管理员使用，可通过管理界面创建用户）"""
    # 这个路由可以用于未来扩展
    flash('注册功能暂未开放，请联系管理员', 'info')
    return redirect(url_for('auth.login')) 