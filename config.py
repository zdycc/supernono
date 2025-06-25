import os
from datetime import timedelta

class Config:
    # Flask 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supernono-secret-key-2024'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:7235506@localhost/supernono?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session 配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # 开发环境设为False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 强制退出登录配置
    FORCE_LOGOUT_ON_RESTART = True
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'img')
    
    # 开发配置
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # 头像路径配置
    ADMIN_AVATAR_PATH = 'img/admin'
    USER_AVATAR_PATH = 'img/user'
    BOT_AVATAR_PATH = 'img/supernono/bot.png'
    
    # AI 系统配置
    AI_MODEL_NAME = 'supernono'
    AI_SYSTEM_TYPE = '本地知识库 + MindSpore NLP'
    AI_VERSION = '4.0.0'
    
    # 知识库配置
    KNOWLEDGE_BASE_CONFIDENCE_THRESHOLD = 0.3
    EMOTIONAL_SUPPORT_PRIORITY = True
    
    # MindSpore NLP配置
    MINDSPORE_NLP_ENABLED = True
    INTENT_RECOGNITION_ENABLED = True
    EMOTION_ANALYSIS_ENABLED = True
    TECHNICAL_TOPIC_EXTRACTION_ENABLED = True

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True

# 默认配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 