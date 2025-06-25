from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from app import db
from app.models.user import User
from app.models.chatroom import ChatRoom
from app.models.message import Message
from app.utils.ai_chatbot import get_supernono_bot

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# 获取AI机器人实例（单例模式）
def get_ai_bot():
    return get_supernono_bot()

def user_required(f):
    """用户权限装饰器"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.get_id().startswith('user_'):
            flash('需要用户权限', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@chat_bp.route('/room/<int:chatroom_id>')
@login_required
@user_required
def chatroom(chatroom_id):
    """聊天室页面"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    
    # 检查用户是否有权限进入该聊天室
    if not chatroom.users.filter_by(id=current_user.id).first():
        flash('您没有权限进入该聊天室', 'error')
        return redirect(url_for('user.chatrooms'))
    
    # 更新用户活跃时间
    current_user.ping()
    
    # 获取聊天记录
    messages = Message.query.filter_by(chatroom_id=chatroom_id).order_by(Message.created_at.asc()).all()
    
    # 获取聊天室成员
    chatroom_users = chatroom.users.all()
    
    return render_template('chat/chatroom.html',
                         chatroom=chatroom,
                         messages=messages,
                         chatroom_users=chatroom_users)

@chat_bp.route('/send_message', methods=['POST'])
@login_required
@user_required
def send_message():
    """发送消息"""
    # 支持表单提交
    chatroom_id = request.form.get('chatroom_id')
    content = request.form.get('content')
    use_ai = request.form.get('use_ai') == 'true'
    
    if not chatroom_id or not content:
        flash('缺少必要参数', 'error')
        return redirect(url_for('user.chatrooms'))
    
    chatroom = ChatRoom.query.get(chatroom_id)
    if not chatroom:
        flash('聊天室不存在', 'error')
        return redirect(url_for('user.chatrooms'))
    
    # 检查用户权限
    if not chatroom.users.filter_by(id=current_user.id).first():
        flash('您没有权限在该聊天室发言', 'error')
        return redirect(url_for('user.chatrooms'))
    
    # 更新用户活跃时间
    current_user.ping()
    
    try:
        # 保存用户消息
        user_message = Message(
            content=content,
            user_id=current_user.id,
            chatroom_id=chatroom_id,
            is_ai_message=False
        )
        db.session.add(user_message)
        db.session.commit()
        
        # 如果选择AI回答，生成AI回复
        if use_ai:
            try:
                ai_bot = get_ai_bot()
                ai_response = ai_bot.chat(content, str(current_user.id))
                
                # 保存AI回复
                ai_message = Message(
                    content=ai_response,
                    user_id=None,  # AI消息不关联用户
                    chatroom_id=chatroom_id,
                    is_ai_message=True,
                    ai_name='supernono'
                )
                db.session.add(ai_message)
                db.session.commit()
                
                flash('消息发送成功，supernono已回复', 'success')
            except Exception as e:
                flash(f'AI回复失败：{str(e)}', 'warning')
        else:
            flash('消息发送成功', 'success')
        
        return redirect(url_for('chat.chatroom', chatroom_id=chatroom_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'发送失败：{str(e)}', 'error')
        return redirect(url_for('chat.chatroom', chatroom_id=chatroom_id))

@chat_bp.route('/get_messages/<int:chatroom_id>')
@login_required
@user_required
def get_messages(chatroom_id):
    """获取聊天室消息（用于实时更新）"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    
    # 检查用户权限
    if not chatroom.users.filter_by(id=current_user.id).first():
        return jsonify({'success': False, 'message': '没有权限'})
    
    # 获取最新消息
    last_message_id = request.args.get('last_message_id', 0, type=int)
    messages = Message.query.filter(
        Message.chatroom_id == chatroom_id,
        Message.id > last_message_id
    ).order_by(Message.created_at.asc()).all()
    
    messages_data = []
    for message in messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender_name': message.get_sender_name(),
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_ai_message': message.is_ai_message
        })
    
    return jsonify({
        'success': True,
        'messages': messages_data
    })

@chat_bp.route('/chatroom_info/<int:chatroom_id>')
@login_required
@user_required
def chatroom_info(chatroom_id):
    """获取聊天室信息"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    
    # 检查用户权限
    if not chatroom.users.filter_by(id=current_user.id).first():
        return jsonify({'success': False, 'message': '没有权限'})
    
    # 获取聊天室成员信息
    users_data = []
    for user in chatroom.users.all():
        users_data.append({
            'id': user.id,
            'username': user.username,
            'avatar': user.get_avatar_path()
        })
    
    return jsonify({
        'success': True,
        'chatroom': {
            'id': chatroom.id,
            'name': chatroom.name,
            'description': chatroom.description,
            'users': users_data,
            'user_count': len(users_data),
            'message_count': chatroom.get_message_count()
        }
    })

@chat_bp.route('/ai_info')
@login_required
@user_required
def ai_info():
    """获取AI机器人信息"""
    try:
        ai_bot = get_ai_bot()
        bot_info = ai_bot.get_info()
        return jsonify({
            'success': True,
            'bot_info': bot_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@chat_bp.route('/send_message_ajax', methods=['POST'])
@login_required
@user_required
def send_message_ajax():
    """AJAX方式发送消息"""
    try:
        data = request.get_json()
        chatroom_id = data.get('chatroom_id')
        content = data.get('content')
        use_ai = data.get('use_ai', False)
        
        if not chatroom_id or not content:
            return jsonify({'success': False, 'message': '缺少必要参数'})
        
        chatroom = ChatRoom.query.get(chatroom_id)
        if not chatroom:
            return jsonify({'success': False, 'message': '聊天室不存在'})
        
        # 检查用户权限
        if not chatroom.users.filter_by(id=current_user.id).first():
            return jsonify({'success': False, 'message': '没有权限在该聊天室发言'})
        
        # 更新用户活跃时间
        current_user.ping()
        
        # 保存用户消息
        user_message = Message(
            content=content,
            user_id=current_user.id,
            chatroom_id=chatroom_id,
            is_ai_message=False
        )
        db.session.add(user_message)
        db.session.commit()
        
        response_data = {
            'success': True,
            'user_message': {
                'id': user_message.id,
                'content': user_message.content,
                'sender_name': user_message.get_sender_name(),
                'sender_avatar': user_message.get_sender_avatar(),
                'created_at': user_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_ai_message': False
            }
        }
        
        # 如果选择AI回答，生成AI回复
        if use_ai:
            try:
                ai_bot = get_ai_bot()
                ai_response = ai_bot.chat(content, str(current_user.id))
                
                # 保存AI回复
                ai_message = Message(
                    content=ai_response,
                    user_id=None,
                    chatroom_id=chatroom_id,
                    is_ai_message=True,
                    ai_name='supernono'
                )
                db.session.add(ai_message)
                db.session.commit()
                
                response_data['ai_message'] = {
                    'id': ai_message.id,
                    'content': ai_message.content,
                    'sender_name': ai_message.get_sender_name(),
                    'sender_avatar': ai_message.get_sender_avatar(),
                    'created_at': ai_message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_ai_message': True
                }
                response_data['message'] = 'supernono已回复'
            except Exception as e:
                response_data['ai_error'] = f'AI回复失败：{str(e)}'
        
        return jsonify(response_data)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'发送失败：{str(e)}'})

@chat_bp.route('/clear_ai_history/<int:user_id>')
@login_required
@user_required  
def clear_ai_history(user_id):
    """清除AI对话历史"""
    if current_user.id != user_id:
        return jsonify({'success': False, 'message': '只能清除自己的对话历史'})
    
    try:
        ai_bot = get_ai_bot()
        ai_bot.clear_history(str(user_id))
        return jsonify({'success': True, 'message': 'AI对话历史已清除'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'清除失败：{str(e)}'})

@chat_bp.route('/users_status/<int:chatroom_id>')
@login_required
@user_required
def users_status(chatroom_id):
    """获取聊天室用户在线状态"""
    chatroom = ChatRoom.query.get_or_404(chatroom_id)
    
    # 检查用户权限
    if not chatroom.users.filter_by(id=current_user.id).first():
        return jsonify({'success': False, 'message': '没有权限'})
    
    # 更新当前用户活跃时间
    current_user.ping()
    
    # 获取聊天室所有用户的在线状态
    users_status = []
    for user in chatroom.users.all():
        users_status.append({
            'id': user.id,
            'username': user.username,
            'avatar': user.get_avatar_path(),
            'online_status': user.get_online_status(),
            'online_status_class': user.get_online_status_class(),
            'is_online': user.is_online()
        })
    
    return jsonify({
        'success': True,
        'users': users_status
    }) 