from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app import db
from app.models.admin import Admin
from app.models.user import User
from app.models.chatroom import ChatRoom
from app.models.message import Message
from app.utils.file_utils import FileManager

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """管理员权限装饰器"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.get_id().startswith('admin_'):
            flash('需要管理员权限', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """管理员仪表板"""
    # 统计数据
    total_users = User.query.count()
    total_admins = Admin.query.count()
    total_chatrooms = ChatRoom.query.count()
    total_messages = Message.query.count()
    
    # 最近的用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # 最活跃的聊天室
    active_chatrooms = ChatRoom.query.order_by(ChatRoom.updated_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_admins=total_admins,
                         total_chatrooms=total_chatrooms,
                         total_messages=total_messages,
                         recent_users=recent_users,
                         active_chatrooms=active_chatrooms)

# ========== 管理员管理 ==========
@admin_bp.route('/admins')
@login_required
@admin_required
def manage_admins():
    """管理员信息管理"""
    admins = Admin.query.order_by(Admin.created_at.desc()).all()
    return render_template('admin/manage_admins.html', admins=admins)

@admin_bp.route('/admins/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_admin():
    """添加管理员"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请填写所有字段', 'error')
            return render_template('admin/add_admin.html')
        
        # 检查用户名是否已存在
        if Admin.query.filter_by(username=username).first():
            flash('管理员用户名已存在', 'error')
            return render_template('admin/add_admin.html')
        
        # 创建新管理员
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        
        flash(f'管理员 {username} 创建成功', 'success')
        return redirect(url_for('admin.manage_admins'))
    
    return render_template('admin/add_admin.html')

@admin_bp.route('/admins/delete/<int:admin_id>')
@login_required
@admin_required
def delete_admin(admin_id):
    """删除管理员"""
    if current_user.id == admin_id:
        flash('不能删除自己', 'error')
        return redirect(url_for('admin.manage_admins'))
    
    admin = Admin.query.get_or_404(admin_id)
    username = admin.username
    db.session.delete(admin)
    db.session.commit()
    
    flash(f'管理员 {username} 删除成功', 'success')
    return redirect(url_for('admin.manage_admins'))

# ========== 用户管理 ==========
@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """用户信息管理"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """添加用户"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请填写所有字段', 'error')
            return render_template('admin/add_user.html')
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('admin/add_user.html')
        
        # 创建新用户
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash(f'用户 {username} 创建成功', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username:
            flash('用户名不能为空', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # 检查用户名是否被其他用户使用
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            flash('用户名已被使用', 'error')
            return render_template('admin/edit_user.html', user=user)
        
        # 更新用户信息
        user.username = username
        if password:  # 只有提供密码时才更新
            user.set_password(password)
        
        db.session.commit()
        flash(f'用户 {username} 更新成功', 'success')
        return redirect(url_for('admin.manage_users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    username = user.username
    
    # 删除用户的所有消息
    Message.query.filter_by(user_id=user_id).delete()
    
    # 删除用户
    db.session.delete(user)
    db.session.commit()
    
    flash(f'用户 {username} 删除成功', 'success')
    return redirect(url_for('admin.manage_users'))

# ========== 聊天室管理 ==========
@admin_bp.route('/chatrooms')
@login_required
@admin_required
def manage_chatrooms():
    """聊天室管理"""
    chatrooms = ChatRoom.query.order_by(ChatRoom.created_at.desc()).all()
    return render_template('admin/manage_chatrooms.html', chatrooms=chatrooms)

@admin_bp.route('/chatrooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_chatroom():
    """添加聊天室"""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('聊天室名称不能为空', 'error')
            return render_template('admin/add_chatroom.html')
        
        # 检查聊天室名称是否已存在
        if ChatRoom.query.filter_by(name=name).first():
            flash('聊天室名称已存在', 'error')
            return render_template('admin/add_chatroom.html')
        
        # 创建新聊天室
        chatroom = ChatRoom(name=name, description=description)
        db.session.add(chatroom)
        db.session.commit()
        
        flash(f'聊天室 {name} 创建成功', 'success')
        return redirect(url_for('admin.manage_chatrooms'))
    
    return render_template('admin/add_chatroom.html')

@admin_bp.route('/chatrooms/edit/<int:chatroom_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_chatroom(chatroom_id):
    """编辑聊天室"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            flash('聊天室名称不能为空', 'error')
            return render_template('admin/edit_chatroom.html', chatroom=chatroom)
        
        # 检查名称是否被其他聊天室使用
        existing_room = ChatRoom.query.filter_by(name=name).first()
        if existing_room and existing_room.id != chatroom.id:
            flash('聊天室名称已被使用', 'error')
            return render_template('admin/edit_chatroom.html', chatroom=chatroom)
        
        # 更新聊天室信息
        chatroom.name = name
        chatroom.description = description
        db.session.commit()
        
        flash(f'聊天室 {name} 更新成功', 'success')
        return redirect(url_for('admin.manage_chatrooms'))
    
    return render_template('admin/edit_chatroom.html', chatroom=chatroom)

@admin_bp.route('/chatrooms/delete/<int:chatroom_id>')
@login_required
@admin_required
def delete_chatroom(chatroom_id):
    """删除聊天室"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    name = chatroom.name
    
    # 删除聊天室会自动删除相关消息（cascade='all, delete-orphan'）
    db.session.delete(chatroom)
    db.session.commit()
    
    flash(f'聊天室 {name} 删除成功', 'success')
    return redirect(url_for('admin.manage_chatrooms'))

@admin_bp.route('/chatrooms/<int:chatroom_id>/clear_messages', methods=['POST'])
@login_required
@admin_required
def clear_chatroom_messages(chatroom_id):
    """清空聊天室的所有对话"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    
    # 删除聊天室中的所有消息
    message_count = Message.query.filter_by(chatroom_id=chatroom_id).count()
    Message.query.filter_by(chatroom_id=chatroom_id).delete()
    
    # 更新聊天室的更新时间
    chatroom.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'已清空聊天室 "{chatroom.name}" 的 {message_count} 条对话记录', 'success')
    return redirect(url_for('admin.manage_chatrooms'))

# ========== 用户聊天室分配 ==========
@admin_bp.route('/chatrooms/<int:chatroom_id>/manage_users')
@login_required
@admin_required
def manage_chatroom_users(chatroom_id):
    """管理聊天室用户"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    all_users = User.query.all()
    chatroom_users = chatroom.users.all()  # 转换为列表
    
    return render_template('admin/manage_chatroom_users.html',
                         chatroom=chatroom,
                         all_users=all_users,
                         chatroom_users=chatroom_users)

@admin_bp.route('/chatrooms/<int:chatroom_id>/add_user/<int:user_id>')
@login_required
@admin_required
def add_user_to_chatroom(chatroom_id, user_id):
    """将用户添加到聊天室"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    user = User.query.get_or_404(user_id)
    
    if not chatroom.users.filter_by(id=user.id).first():
        chatroom.users.append(user)
        db.session.commit()
        flash(f'用户 {user.username} 已添加到聊天室 {chatroom.name}', 'success')
    else:
        flash(f'用户 {user.username} 已经在聊天室中', 'info')
    
    return redirect(url_for('admin.manage_chatroom_users', chatroom_id=chatroom_id))

@admin_bp.route('/chatrooms/<int:chatroom_id>/remove_user/<int:user_id>')
@login_required
@admin_required
def remove_user_from_chatroom(chatroom_id, user_id):
    """从聊天室移除用户"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    user = User.query.get_or_404(user_id)
    
    if chatroom.users.filter_by(id=user.id).first():
        chatroom.users.remove(user)
        db.session.commit()
        flash(f'用户 {user.username} 已从聊天室 {chatroom.name} 移除', 'success')
    else:
        flash(f'用户 {user.username} 不在该聊天室中', 'info')
    
    return redirect(url_for('admin.manage_chatroom_users', chatroom_id=chatroom_id))

# ========== 聊天记录导出 ==========
@admin_bp.route('/export')
@login_required
@admin_required
def export_page():
    """聊天记录导出页面"""
    chatrooms = ChatRoom.query.all()
    return render_template('admin/export.html', chatrooms=chatrooms)

@admin_bp.route('/export/<int:chatroom_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def export_chatroom(chatroom_id):
    """导出聊天室记录（支持时间范围筛选）"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    
    if request.method == 'POST':
        # 获取时间范围参数
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # 构建查询
        query = Message.query.filter_by(chatroom_id=chatroom_id)
        
        # 应用时间筛选
        if start_date:
            try:
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Message.created_at >= start_datetime)
            except ValueError:
                flash('开始日期格式错误', 'error')
                return redirect(url_for('admin.export_chatroom', chatroom_id=chatroom_id))
        
        if end_date:
            try:
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                # 设置为当天的23:59:59
                end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                query = query.filter(Message.created_at <= end_datetime)
            except ValueError:
                flash('结束日期格式错误', 'error')
                return redirect(url_for('admin.export_chatroom', chatroom_id=chatroom_id))
        
        # 获取筛选后的消息
        messages = query.order_by(Message.created_at.asc()).all()
        
        if not messages:
            flash('指定时间范围内没有找到聊天记录', 'warning')
            return redirect(url_for('admin.export_chatroom', chatroom_id=chatroom_id))
        
        # 生成文件名
        filename_parts = [chatroom.name]
        if start_date:
            filename_parts.append(f"from_{start_date}")
        if end_date:
            filename_parts.append(f"to_{end_date}")
        
        filename_suffix = "_".join(filename_parts)
        
        # 导出文件
        file_manager = FileManager()
        file_path = file_manager.export_chat_history(filename_suffix, messages)
        
        if file_path:
            return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
        else:
            flash('导出失败', 'error')
            return redirect(url_for('admin.export_chatroom', chatroom_id=chatroom_id))
    
    # GET请求，显示导出配置页面
    # 获取聊天室的第一条和最后一条消息的时间，用于设置日期范围
    first_message = Message.query.filter_by(chatroom_id=chatroom_id).order_by(Message.created_at.asc()).first()
    last_message = Message.query.filter_by(chatroom_id=chatroom_id).order_by(Message.created_at.desc()).first()
    
    min_date = first_message.created_at.strftime('%Y-%m-%d') if first_message else None
    max_date = last_message.created_at.strftime('%Y-%m-%d') if last_message else None
    
    return render_template('admin/export_chatroom.html', 
                         chatroom=chatroom,
                         min_date=min_date,
                         max_date=max_date)

# ========== 管理员个人信息管理 ==========
@admin_bp.route('/profile')
@login_required
@admin_required
def profile():
    """管理员个人信息页面"""
    # 获取统计数据
    total_users = User.query.count()
    total_chatrooms = ChatRoom.query.count()
    total_messages = Message.query.count()
    
    return render_template('admin/profile.html',
                         total_users=total_users,
                         total_chatrooms=total_chatrooms,
                         total_messages=total_messages)

@admin_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile():
    """编辑管理员个人信息"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username:
            flash('用户名不能为空', 'error')
            return render_template('admin/edit_profile.html')
        
        # 检查用户名是否被其他管理员使用
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin and existing_admin.id != current_user.id:
            flash('用户名已被使用', 'error')
            return render_template('admin/edit_profile.html')
        
        # 更新管理员信息
        current_user.username = username
        if password:  # 只有提供密码时才更新
            current_user.set_password(password)
        
        db.session.commit()
        flash('个人信息更新成功', 'success')
        return redirect(url_for('admin.profile'))
    
    return render_template('admin/edit_profile.html')

@admin_bp.route('/profile/upload_avatar', methods=['POST'])
@login_required
@admin_required
def upload_avatar():
    """上传管理员头像"""
    if 'avatar' not in request.files:
        flash('请选择头像文件', 'error')
        return redirect(url_for('admin.profile'))
    
    file = request.files['avatar']
    if file.filename == '':
        flash('请选择头像文件', 'error')
        return redirect(url_for('admin.profile'))
    
    if file:
        try:
            # 使用FileManager处理头像上传
            file_manager = FileManager()
            
            # 为管理员创建唯一的文件名
            filename = f"admin_{current_user.id}_{secure_filename(file.filename)}"
            avatar_path = file_manager.save_avatar(file, filename, 'admin')
            
            # 更新管理员头像字段
            current_user.avatar = avatar_path
            db.session.commit()
            
            flash('头像更新成功', 'success')
        except Exception as e:
            flash(f'头像上传失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.profile')) 