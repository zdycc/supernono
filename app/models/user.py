from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), default='default.png')
    last_seen = db.Column(db.DateTime, default=db.func.current_timestamp())  # 启用最后活跃时间
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # 关系 - 修复关系定义，确保双向都是dynamic
    messages = db.relationship('Message', backref='user', lazy='dynamic')
    chatrooms = db.relationship('ChatRoom', secondary='user_chatrooms', 
                               backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Flask-Login 需要的方法"""
        return f"user_{self.id}"
    
    def get_avatar_path(self):
        """获取头像路径"""
        if self.avatar and self.avatar != 'default.png':
        return f"img/user/{self.avatar}"
        return "img/user/default.png"
    
    def get_chatroom_count(self):
        """获取用户参与的聊天室数量"""
        return self.chatrooms.count()
    
    def ping(self):
        """更新用户最后活跃时间"""
        self.last_seen = datetime.utcnow()
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ 更新用户活跃时间失败: {e}")
    
    def set_offline(self):
        """将用户设置为离线状态"""
        # 将last_seen设置为6分钟前，确保is_online()返回False
        self.last_seen = datetime.utcnow() - timedelta(minutes=6)
        try:
            db.session.commit()
            print(f"🔒 用户 {self.username} 已设置为离线状态")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ 设置用户离线状态失败: {e}")
    
    def is_online(self, timeout_minutes=5):
        """检查用户是否在线（5分钟内活跃）"""
        if not hasattr(self, 'last_seen') or self.last_seen is None:
            return False
        return (datetime.utcnow() - self.last_seen).total_seconds() < timeout_minutes * 60
    
    def get_online_status(self):
        """获取在线状态文本"""
        return "在线" if self.is_online() else "离线"
    
    def get_online_status_class(self):
        """获取在线状态CSS类"""
        return "text-success" if self.is_online() else "text-muted"
    
    def __repr__(self):
        return f'<User {self.username}>' 