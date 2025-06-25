from app import db

class ChatRoom(db.Model):
    __tablename__ = 'chatrooms'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # 关系定义
    messages = db.relationship('Message', backref='chatroom', lazy='dynamic', cascade='all, delete-orphan')
    # users关系由User模型中的chatrooms关系自动创建（通过backref='users'）
    
    def get_user_count(self):
        """获取聊天室用户数量"""
        return self.users.count()
    
    def get_message_count(self):
        """获取聊天室消息数量"""
        return self.messages.count()
    
    def __repr__(self):
        return f'<ChatRoom {self.name}>' 