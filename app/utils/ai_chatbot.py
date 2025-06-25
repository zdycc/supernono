#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supernono AI聊天机器人
基于本地知识库 + MindSpore自然语言处理
"""

import logging
import threading
import time
from typing import Dict, List, Tuple, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化组件
try:
    from app.utils.knowledge_base import search_knowledge, get_emotional_support
    from app.utils.mindspore_nlp import MindSporeNLP
    
    # 初始化NLP处理器
    nlp_processor = MindSporeNLP()
    
    logger.info("✅ 本地知识库和MindSpore NLP模块加载成功")
    
except Exception as e:
    logger.error(f"❌ 模块加载失败: {e}")
    # 提供备用函数
    def search_knowledge(query): return "知识库未加载", 0.0
    def get_emotional_support(text): return "中性", "我会尽力帮助您"
    nlp_processor = None

class SupernonoBot:
    """Supernono AI助手 - 基于本地知识库和MindSpore NLP"""
    
    def __init__(self):
        self.name = "supernono"
        self.version = "4.0.0"
        self.description = "基于本地知识库和MindSpore自然语言处理的专业软件工程助手"
        self.nlp_processor = nlp_processor
        self.system_ready = nlp_processor is not None
        
        # 对话历史管理
        self.conversation_history = {}
        self.history_lock = threading.Lock()
        self.max_history_length = 10
        
        logger.info(f"🤖 Supernono AI助手初始化完成 - {'本地知识库模式' if self.system_ready else '基础模式'}")

    def chat(self, user_message: str, user_id: str = "default") -> str:
        """处理用户消息"""
        try:
            logger.info(f"💭 收到用户[{user_id}]消息: {user_message[:50]}...")
            start_time = time.time()
            
            if not self.system_ready:
                return "抱歉，AI系统正在初始化中，请稍后再试。"
            
            # MindSpore NLP分析
            nlp_result = self.nlp_processor.generate_response_metadata(user_message)
            logger.info(f"🧠 MindSpore NLP分析 - 意图:{nlp_result['intent']}, 情绪:{nlp_result['emotion']}, 技术话题:{len(nlp_result['technical_topics'])}")
            
            # 情绪支持检查
            if nlp_result['emotion'] in ['负面', '焦虑', '沮丧', '愤怒']:
                emotion_support = self._get_emotional_support(nlp_result['emotion'])
                if emotion_support:
                    return self._smart_text_wrap(emotion_support)
            
            # 知识库查询
            try:
                kb_answer, confidence = search_knowledge(user_message)
                if confidence > 0.6:
                    logger.info(f"📚 本地知识库命中 - 置信度:{confidence:.2f}")
                    return self._smart_text_wrap(kb_answer)
            except Exception as e:
                logger.warning(f"知识库查询失败: {e}")
            
            # 智能回退
            logger.info("⚡ 使用智能回退系统...")
            response = self._get_smart_fallback_response(user_message)
            
            # 更新对话历史
            self._update_conversation_history(user_id, user_message, response)
            
            # 记录响应时间
            response_time = time.time() - start_time
            logger.info(f"⚡ 响应完成 - 耗时: {response_time:.3f}秒")
            
            return response
            
        except Exception as e:
            logger.error(f"聊天处理失败: {e}")
            return "抱歉，我在处理您的消息时遇到了技术问题，请稍后再试。"
    
    def _smart_text_wrap(self, text: str, max_line_length: int = 30) -> str:
        """智能文本分行 - 针对中文优化，去掉装饰性内容"""
        if not text:
            return ""
        
        # 去掉所有装饰性内容
        text = self._clean_decorative_content(text)
        
        # 清理多余空格和换行
        text = ' '.join(text.split())
        
        lines = []
        current_line = ""
        
        # 简单按标点符号分行
        i = 0
        while i < len(text):
            char = text[i]
            current_line += char
            
            # 遇到句号或感叹号时分行
            if char in '。！？' and len(current_line) >= 15:
                lines.append(current_line.strip())
                current_line = ""
            # 当前行太长时，找逗号分行
            elif len(current_line) >= max_line_length:
                # 查找最近的逗号
                last_comma = current_line.rfind('，')
                if last_comma > len(current_line) // 2:  # 逗号在后半部分
                    lines.append(current_line[:last_comma + 1].strip())
                    current_line = current_line[last_comma + 1:].strip()
                else:
                    # 没有合适的逗号，直接换行
                    lines.append(current_line.strip())
                    current_line = ""
            
            i += 1
        
        # 添加最后一行
        if current_line.strip():
            lines.append(current_line.strip())
        
        return '\n'.join(line for line in lines if line.strip())
    
    def _clean_decorative_content(self, text: str) -> str:
        """清理装饰性内容"""
        import re
        
        # 去掉图标和装饰线
        text = re.sub(r'[🎯📋🔧📊🏷️💝🔍📚⚡🤖💭🧠]+', '', text)
        text = re.sub(r'[=\-]{3,}', '', text)
        text = re.sub(r'\*{2,}', '', text)
        
        # 去掉版本信息
        text = re.sub(r'Supernono v\d+\.\d+\.\d+.*?助手', '', text)
        text = re.sub(r'本地知识库.*?专业.*?助手', '', text)
        
        # 去掉多余的标题格式
        text = re.sub(r'专业知识解答', '', text)
        text = re.sub(r'知识库参考', '', text)
        
        # 清理多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _get_emotional_support(self, emotion: str) -> str:
        """获取情绪支持信息"""
        emotion_responses = {
            '负面': '我理解您现在的感受。每个人都会遇到挑战，重要的是保持积极的心态。有什么具体问题我可以帮您分析一下吗？',
            '焦虑': '感到焦虑是很正常的，特别是面对新的挑战时。让我们一步步来解决问题，这样会让您感觉更有掌控感。',
            '沮丧': '我能感受到您的沮丧。有时候事情确实不如预期，但这是成长过程的一部分。让我们看看有什么可以改进的地方。',
            '愤怒': '我理解您的愤怒。深呼吸一下，让我们冷静地分析一下情况，找到解决问题的最佳方式。'
        }
        return emotion_responses.get(emotion, '')

    def _get_smart_fallback_response(self, message: str) -> str:
        """获取智能回退回复"""
        return self._get_basic_fallback(message)
    
    def _get_basic_fallback(self, message: str) -> str:
        """基础回退回复"""
        fallback_responses = [
            "抱歉，我对这个问题还不够了解。",
            "您可以尝试询问软件工程或项目管理相关的问题。",
            "我擅长回答关于编程、测试、项目管理等技术话题。"
        ]
        
        response = '\n'.join(fallback_responses)
        return self._smart_text_wrap(response)
    
    def _get_conversation_history(self, user_id: str) -> List[Tuple[str, str]]:
        """获取对话历史"""
        with self.history_lock:
            return self.conversation_history.get(user_id, [])
    
    def _update_conversation_history(self, user_id: str, user_message: str, bot_response: str):
        """更新对话历史"""
        with self.history_lock:
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            self.conversation_history[user_id].append((user_message, bot_response))
            
            # 限制历史长度
            if len(self.conversation_history[user_id]) > self.max_history_length:
                self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history_length:]
    
    def clear_history(self, user_id: str):
        """清除指定用户的对话历史"""
        with self.history_lock:
            if user_id in self.conversation_history:
                del self.conversation_history[user_id]
                logger.info(f"已清除用户 {user_id} 的对话历史")
    
    def get_status(self) -> Dict[str, Any]:
        """获取机器人状态信息"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'system_type': '本地知识库 + MindSpore NLP',
            'system_ready': self.system_ready,
            'features': [
                '软件工程知识库',
                '项目管理知识库',
                'MindSpore自然语言处理',
                '情绪检测与支持',
                '意图识别',
                '技术话题提取'
            ],
            'capabilities': [
                '软件工程问答',
                '项目管理咨询', 
                '情绪安抚',
                '多轮对话',
                '上下文理解'
            ]
        }
    
    def get_info(self) -> Dict[str, str]:
        """获取机器人基本信息（兼容性方法）"""
        status = self.get_status()
        return {
            'name': status['name'],
            'version': status['version'],
            'description': status['description'],
            'system': status['system_type'],
            'features': '本地知识库 + MindSpore NLP'
        }
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        try:
            from app.utils.knowledge_base import _knowledge_base
            kb = _knowledge_base.qa_database
            
            total_categories = len(kb)
            total_items = len(kb)
            
            categories = [
                "代码质量管理", "测试策略", "项目管理", "敏捷开发", 
                "团队协作", "软件工程基础", "职业发展"
            ]
            
            return {
                "知识库类别数": 7,
                "知识点数量": total_items,
                "知识条目总数": total_items,
                "主要类别": categories,
                "系统状态": "运行正常"
            }
        except Exception as e:
            logger.error(f"获取知识库统计失败: {e}")
            return {"错误": str(e)}

# 全局实例（单例模式）
_supernono_bot_instance = None

def get_supernono_bot() -> SupernonoBot:
    """获取supernono机器人实例（单例模式）"""
    global _supernono_bot_instance
    if _supernono_bot_instance is None:
        _supernono_bot_instance = SupernonoBot()
    return _supernono_bot_instance

# 为了向后兼容，保留旧的函数名
def get_chatglm_bot() -> SupernonoBot:
    """兼容性函数，返回supernono机器人"""
    return get_supernono_bot() 