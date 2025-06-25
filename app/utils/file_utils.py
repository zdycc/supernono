import os
import datetime
from typing import List, Optional
from werkzeug.utils import secure_filename
from PIL import Image

class FileManager:
    """文件管理工具类"""
    
    def __init__(self, upload_folder: str = 'static/img'):
        self.upload_folder = upload_folder
        self.allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        
    def allowed_file(self, filename: str) -> bool:
        """检查文件类型是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_avatar(self, file, filename: str, user_type: str) -> Optional[str]:
        """保存用户头像"""
        try:
            if file and self.allowed_file(file.filename):
                # 确定保存路径
                if user_type == 'admin':
                    save_dir = os.path.join(self.upload_folder, 'admin')
                else:
                    save_dir = os.path.join(self.upload_folder, 'user')
                
                # 确保目录存在
                os.makedirs(save_dir, exist_ok=True)
                
                # 保存文件
                save_path = os.path.join(save_dir, filename)
                file.save(save_path)
                
                # 压缩图片（可选）
                self._compress_image(save_path)
                
                return filename
                
        except Exception as e:
            print(f"保存头像时出错：{e}")
            return None
    
    def _compress_image(self, image_path: str, max_size: tuple = (200, 200)):
        """压缩图片"""
        try:
            with Image.open(image_path) as img:
                # 使用新版本Pillow兼容的重采样方法
                if hasattr(Image, 'Resampling'):
                    # Pillow >= 10.0.0
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                else:
                    # Pillow < 10.0.0
                    img.thumbnail(max_size, Image.LANCZOS)
                img.save(image_path, optimize=True, quality=85)
        except Exception as e:
            print(f"压缩图片时出错：{e}")
    
    def export_chat_history(self, chatroom_name: str, messages: List) -> str:
        """导出聊天记录为txt文件"""
        try:
            # 生成安全的文件名
            safe_chatroom_name = secure_filename(chatroom_name)
            current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_chatroom_name}_聊天记录_{current_date}.txt"
            
            # 确保exports目录存在（在项目根目录）
                project_root = os.getcwd()
            export_dir = os.path.join(project_root, "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            file_path = os.path.join(export_dir, filename)
            print(f"📁 导出文件路径: {file_path}")
            
            # 写入聊天记录
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"聊天室：{chatroom_name}\n")
                f.write(f"导出时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"消息总数：{len(messages)}\n")
                f.write("=" * 50 + "\n\n")
                
                for message in messages:
                    timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    sender = message.get_sender_name()
                    content = message.content
                    
                    f.write(f"[{timestamp}] {sender}：{content}\n")
                
                f.write("\n" + "=" * 50 + "\n")
                f.write("导出完成")
                
            print(f"✅ 聊天记录导出成功: {filename}")
            return file_path
            
        except Exception as e:
            print(f"❌ 导出聊天记录时出错：{e}")
            return None
    
    def get_avatar_url(self, user_type: str, avatar_filename: str) -> str:
        """获取头像URL"""
        if user_type == 'admin':
            return f"/static/img/admin/{avatar_filename}"
        elif user_type == 'user':
            return f"/static/img/user/{avatar_filename}"
        else:
            return f"/static/img/default.png"
    
    def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件时出错：{e}")
            return False
    
    def create_default_avatars(self):
        """创建默认头像目录和文件"""
        try:
            # 创建目录
            admin_dir = os.path.join(self.upload_folder, 'admin')
            user_dir = os.path.join(self.upload_folder, 'user')
            supernono_dir = os.path.join(self.upload_folder, 'supernono')
            
            os.makedirs(admin_dir, exist_ok=True)
            os.makedirs(user_dir, exist_ok=True)
            os.makedirs(supernono_dir, exist_ok=True)
            
            print("默认头像目录创建完成")
            
        except Exception as e:
            print(f"创建默认头像目录时出错：{e}") 