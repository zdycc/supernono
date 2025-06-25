from app import db

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # AI消息为空
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chatrooms.id'), nullable=False)
    is_ai_message = db.Column(db.Boolean, default=False)  # 是否为AI消息
    ai_name = db.Column(db.String(50), default='supernono')  # AI机器人名称
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def get_sender_name(self):
        """获取发送者名称"""
        if self.is_ai_message:
            return f"supernono"  # AI机器人显示名称
        elif self.user:
            return self.user.username
        else:
            return "未知用户"
    
    def get_sender_avatar(self):
        """获取发送者头像路径"""
        if self.is_ai_message:
            return "img/supernono/bot.png"
        elif self.user:
            return self.user.get_avatar_path()
        else:
            return "img/user/default.png"
    
    def get_sender_type(self):
        """获取发送者类型"""
        if self.is_ai_message:
            return "ai"
        elif self.user:
            return "user"
        else:
            return "unknown"
    
    def format_for_export(self):
        """格式化消息用于导出"""
        sender = self.get_sender_name()
        return f"{sender}：{self.content}"
    
    def __repr__(self):
        return f'<Message {self.id}>' 