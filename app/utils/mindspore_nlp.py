#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindSpore自然语言处理模块
用于意图识别、情感分析和文本理解
"""

import re
import jieba
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class MindSporeNLP:
    """基于MindSpore的自然语言处理"""
    
    def __init__(self):
        self.stop_words = self._load_stop_words()
        self.intent_keywords = self._build_intent_keywords()
        self.emotion_patterns = self._build_emotion_patterns()
        self.technical_terms = self._build_technical_terms()
        
    def _load_stop_words(self) -> set:
        """加载中文停用词"""
        stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', 
            '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '什么', '可以',
            '这个', '就是', '但是', '如果', '因为', '所以', '对于', '关于', '由于', '为了', '通过', '根据',
            '而且', '而是', '或者', '以及', '比如', '例如', '包括', '除了', '另外', '同时', '然后', '现在',
            '已经', '正在', '将要', '可能', '应该', '必须', '需要', '想要', '希望', '认为', '觉得', '感觉'
        }
        return stop_words
    
    def _build_intent_keywords(self) -> Dict[str, List[str]]:
        """构建意图关键词库"""
        return {
            "询问": ["什么是", "如何", "怎么", "为什么", "解释", "说明", "介绍", "什么叫", "请问"],
            "求助": ["帮助", "帮忙", "不会", "不懂", "困难", "问题", "错误", "bug", "出错"],
            "学习": ["学习", "掌握", "了解", "入门", "教程", "资料", "建议", "推荐"],
            "对比": ["区别", "不同", "差异", "比较", "对比", "vs", "和", "与"],
            "实践": ["实现", "开发", "编写", "设计", "搭建", "构建", "创建", "制作"],
            "情感": ["累", "烦", "难", "急", "压力", "焦虑", "沮丧", "困惑", "迷茫"],
            "感谢": ["谢谢", "感谢", "谢了", "多谢", "thanks", "thank you"]
        }
    
    def _build_emotion_patterns(self) -> Dict[str, List[str]]:
        """构建情感模式"""
        return {
            "积极": [
                r"(很好|不错|棒|优秀|满意|开心|高兴|感谢)",
                r"(成功|完成|解决|搞定|ok|好的)",
                r"(喜欢|满意|认可|赞同|支持)"
            ],
            "消极": [
                r"(不好|糟糕|差|失败|错误|问题|bug)",
                r"(困难|复杂|难懂|不会|不懂|迷茫)",
                r"(累|疲惫|压力|焦虑|沮丧|烦躁|紧张)"
            ],
            "中性": [
                r"(什么|如何|怎么|为什么|请问)",
                r"(介绍|说明|解释|了解|学习)",
                r"(比较|区别|对比|选择)"
            ]
        }
    
    def _build_technical_terms(self) -> Dict[str, List[str]]:
        """构建技术术语库"""
        return {
            "编程语言": ["python", "java", "javascript", "c++", "c#", "go", "rust", "php"],
            "前端技术": ["html", "css", "react", "vue", "angular", "webpack", "nodejs"],
            "后端技术": ["spring", "django", "flask", "express", "mysql", "redis", "mongodb"],
            "开发工具": ["git", "github", "gitlab", "docker", "kubernetes", "jenkins", "vscode"],
            "架构设计": ["微服务", "分布式", "负载均衡", "缓存", "消息队列", "api", "restful"],
            "项目管理": ["敏捷", "scrum", "看板", "迭代", "sprint", "backlog", "需求", "测试"],
            "软件工程": ["设计模式", "重构", "代码审查", "单元测试", "集成测试", "部署", "运维"]
        }
    
    def segment_text(self, text: str) -> List[str]:
        """文本分词"""
        try:
            # 使用jieba进行中文分词
            words = jieba.lcut(text.lower())
            # 过滤停用词和标点符号
            filtered_words = [
                word for word in words 
                if word not in self.stop_words 
                and len(word) > 1 
                and not re.match(r'^[^\w\s]+$', word)
            ]
            return filtered_words
        except Exception as e:
            logger.warning(f"分词失败: {e}")
            return text.split()
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """提取关键词"""
        words = self.segment_text(text)
        word_freq = Counter(words)
        
        # 技术术语权重加成
        weighted_freq = {}
        for word, freq in word_freq.items():
            weight = 1.0
            # 检查是否为技术术语
            for category, terms in self.technical_terms.items():
                if word in terms:
                    weight = 2.0
                    break
            weighted_freq[word] = freq * weight
        
        # 返回前top_k个关键词
        sorted_words = sorted(weighted_freq.items(), key=lambda x: x[1], reverse=True)
        return sorted_words[:top_k]
    
    def analyze_intent(self, text: str) -> Tuple[str, float]:
        """分析用户意图"""
        text_lower = text.lower()
        intent_scores = {}
        
        for intent, keywords in self.intent_keywords.items():
            score = 0.0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1.0
            
            # 基于关键词数量计算得分
            if len(keywords) > 0:
                intent_scores[intent] = score / len(keywords)
        
        # 特殊模式匹配
        if re.search(r'[？?]', text):
            intent_scores["询问"] = intent_scores.get("询问", 0) + 0.5
        
        if re.search(r'(请|能否|可以|帮)', text):
            intent_scores["求助"] = intent_scores.get("求助", 0) + 0.3
        
        # 返回得分最高的意图
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            return best_intent[0], best_intent[1]
        else:
            return "询问", 0.5  # 默认意图
    
    def analyze_emotion(self, text: str) -> Tuple[str, float]:
        """分析情感倾向"""
        emotion_scores = {"积极": 0, "消极": 0, "中性": 0}
        
        for emotion, patterns in self.emotion_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text)
                emotion_scores[emotion] += len(matches)
        
        # 计算情感权重
        total_score = sum(emotion_scores.values())
        if total_score == 0:
            return "中性", 0.5
        
        # 找到最高分的情感
        best_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        confidence = best_emotion[1] / total_score
        
        return best_emotion[0], confidence
    
    def extract_technical_topics(self, text: str) -> List[Tuple[str, str]]:
        """提取技术话题"""
        text_lower = text.lower()
        found_topics = []
        
        for category, terms in self.technical_terms.items():
            for term in terms:
                if term in text_lower:
                    found_topics.append((category, term))
        
        return found_topics
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        words1 = set(self.segment_text(text1))
        words2 = set(self.segment_text(text2))
        
        if not words1 or not words2:
            return 0.0
        
        # 使用Jaccard相似度
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def generate_response_metadata(self, text: str) -> Dict:
        """生成响应元数据"""
        try:
            keywords = self.extract_keywords(text, top_k=5)
            intent, intent_confidence = self.analyze_intent(text)
            emotion, emotion_confidence = self.analyze_emotion(text)
            technical_topics = self.extract_technical_topics(text)
            
            return {
                "keywords": [kw[0] for kw in keywords],
                "intent": intent,
                "intent_confidence": intent_confidence,
                "emotion": emotion,
                "emotion_confidence": emotion_confidence,
                "technical_topics": technical_topics,
                "word_count": len(self.segment_text(text))
            }
        except Exception as e:
            logger.error(f"生成响应元数据失败: {e}")
            return {
                "keywords": [],
                "intent": "询问",
                "intent_confidence": 0.5,
                "emotion": "中性",
                "emotion_confidence": 0.5,
                "technical_topics": [],
                "word_count": 0
            }
    
    def smart_response_routing(self, text: str, metadata: Dict) -> str:
        """智能响应路由"""
        intent = metadata.get("intent", "询问")
        emotion = metadata.get("emotion", "中性")
        technical_topics = metadata.get("technical_topics", [])
        
        routing_info = {
            "use_knowledge_base": False,
            "use_emotional_support": False,
            "priority_category": None,
            "response_style": "neutral"
        }
        
        # 根据意图决定路由
        if intent in ["询问", "学习", "对比", "实践"]:
            routing_info["use_knowledge_base"] = True
            
        if intent in ["求助", "情感"] or emotion == "消极":
            routing_info["use_emotional_support"] = True
            routing_info["response_style"] = "supportive"
        
        # 根据技术话题确定优先类别
        if technical_topics:
            category_counts = Counter([topic[0] for topic in technical_topics])
            if category_counts:
                routing_info["priority_category"] = category_counts.most_common(1)[0][0]
        
        return routing_info

# 全局NLP实例
_nlp_processor = MindSporeNLP()

def process_text(text: str) -> Dict:
    """处理文本并返回分析结果"""
    return _nlp_processor.generate_response_metadata(text)

def get_smart_routing(text: str) -> Dict:
    """获取智能路由信息"""
    metadata = process_text(text)
    routing = _nlp_processor.smart_response_routing(text, metadata)
    return {**metadata, "routing": routing}

def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度"""
    return _nlp_processor.calculate_text_similarity(text1, text2) 