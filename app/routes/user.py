from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import time

from app import db
from app.models.user import User
from app.models.chatroom import ChatRoom
from app.utils.file_utils import FileManager

user_bp = Blueprint('user', __name__, url_prefix='/user')

def user_required(f):
    """普通用户权限装饰器"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.get_id().startswith('user_'):
            flash('需要用户权限', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@login_required
@user_required
def dashboard():
    """用户仪表板"""
    user = current_user
    
    # 更新用户活跃时间
    user.ping()
    
    # 获取用户参与的聊天室
    user_chatrooms = user.chatrooms.all()
    
    # 统计信息
    total_chatrooms = len(user_chatrooms)
    total_messages = sum(room.messages.filter_by(user_id=user.id).count() for room in user_chatrooms)
    
    return render_template('user/dashboard.html',
                         user=user,
                         user_chatrooms=user_chatrooms,
                         total_chatrooms=total_chatrooms,
                         total_messages=total_messages)

@user_bp.route('/profile')
@login_required
@user_required
def profile():
    """个人信息页面"""
    return render_template('user/profile.html', user=current_user)

@user_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@user_required
def edit_profile():
    """编辑个人信息"""
    user = current_user
    
    if request.method == 'POST':
        username = request.form.get('username')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not username:
            flash('用户名不能为空', 'error')
            return render_template('user/edit_profile.html', user=user)
        
        # 检查用户名是否被其他用户使用
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            flash('用户名已被使用', 'error')
            return render_template('user/edit_profile.html', user=user)
        
        # 如果要修改密码，验证当前密码
        if new_password:
            if not current_password:
                flash('请输入当前密码', 'error')
                return render_template('user/edit_profile.html', user=user)
            
            if not user.check_password(current_password):
                flash('当前密码错误', 'error')
                return render_template('user/edit_profile.html', user=user)
            
            if new_password != confirm_password:
                flash('两次输入的新密码不一致', 'error')
                return render_template('user/edit_profile.html', user=user)
            
            user.set_password(new_password)
        
        # 更新用户名
        user.username = username
        db.session.commit()
        
        flash('个人信息更新成功', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('user/edit_profile.html', user=user)

@user_bp.route('/avatar/upload', methods=['POST'])
@login_required
@user_required
def upload_avatar():
    """上传头像"""
    if 'avatar' not in request.files:
        flash('请选择头像文件', 'error')
        return redirect(url_for('user.profile'))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('请选择头像文件', 'error')
        return redirect(url_for('user.profile'))
    
    file_manager = FileManager()
    
    if file and file_manager.allowed_file(file.filename):
        try:
            # 生成安全的文件名
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"user_{current_user.id}_{int(time.time())}.{file_ext}"
            
            # 保存头像 - 修正参数顺序
            saved_filename = file_manager.save_avatar(file, filename, 'user')
            
            if saved_filename:
                # 更新用户头像字段
                current_user.avatar = saved_filename
                db.session.commit()
                flash('头像上传成功', 'success')
                print(f"✅ 用户头像保存成功: {saved_filename}")
            else:
                flash('头像上传失败', 'error')
                print("❌ 头像保存失败")
        except Exception as e:
            flash(f'头像上传失败: {str(e)}', 'error')
            print(f"❌ 头像上传异常: {e}")
    else:
        flash('不支持的文件格式，请上传jpg、png、gif格式的图片', 'error')
    
    return redirect(url_for('user.profile'))

@user_bp.route('/chatrooms')
@login_required
@user_required
def chatrooms():
    """用户聊天室列表"""
    user = current_user
    
    # 更新用户活跃时间
    user.ping()
    
    # 获取用户参与的聊天室
    user_chatrooms = user.chatrooms.all()
    
    return render_template('user/chatrooms.html',
                         user=user,
                         chatrooms=user_chatrooms) 