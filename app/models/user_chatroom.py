from app import db

# 用户聊天室关联表
user_chatrooms = db.Table('user_chatrooms',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('chatroom_id', db.Integer, db.ForeignKey('chatrooms.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=db.func.current_timestamp())
) 