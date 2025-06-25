#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地软件工程知识库 - 精准问答系统
每个问题对应具体的答案，避免宽泛回复
"""

import re
import random
from typing import Dict, List, Tuple, Optional

class SoftwareEngineeringKnowledgeBase:
    """软件工程专业知识库 - 精准问答版"""
    
    def __init__(self):
        self.qa_database = self._build_qa_database()
        self.emotion_keywords = self._build_emotion_keywords()
        
    def _build_qa_database(self) -> Dict[str, str]:
        """构建精准的问答数据库"""
        return {
            # ===== 代码质量相关 =====
            "代码质量": "代码质量保障的核心方法包括：\n1. 代码审查：建立强制性代码审查，每个PR至少需要一人审核通过\n2. 编码规范：制定团队统一的代码风格和命名规范，使用工具自动检查\n3. 单元测试：覆盖率达到80%以上，确保核心逻辑的正确性\n4. 技术债管理：定期安排技术债清理时间，不要让技术债累积影响开发效率",
            
            "代码审查": "代码审查最佳实践：\n1. 审查范围：检查代码逻辑、性能、安全性和可维护性\n2. 审查时机：每个功能分支合并前必须经过审查\n3. 审查标准：代码符合团队规范，逻辑清晰，有适当注释\n4. 审查工具：使用GitHub PR、GitLab MR等工具进行线上审查",
            
            "编码规范": "编码规范制定要点：\n1. 命名规范：变量名、函数名要有意义，避免缩写\n2. 代码格式：统一缩进、空格、换行风格\n3. 注释规范：复杂逻辑必须有注释说明\n4. 自动化检查：配置ESLint、SonarQube等工具自动检查",
            
            # ===== 测试策略相关 =====
            "测试策略": "测试策略制定方法：\n1. 测试金字塔：70%单元测试+20%集成测试+10%端到端测试\n2. 测试左移：在需求阶段就考虑测试用例，开发时同步编写测试\n3. 风险评估：针对高风险模块加强测试覆盖\n4. 自动化优先：核心功能必须有自动化测试，确保回归质量",
            
            "测试计划": "测试计划包含内容：\n1. 测试范围：明确哪些功能需要测试，哪些可以跳过\n2. 测试方法：单元测试、集成测试、系统测试的分工\n3. 测试环境：准备测试数据和测试环境\n4. 验收标准：定义每个功能的通过标准",
            
            "单元测试": "单元测试编写要点：\n1. 测试覆盖率：核心业务逻辑覆盖率80%以上\n2. 测试独立性：每个测试用例应该独立运行\n3. 测试命名：测试方法名要清楚表达测试意图\n4. 断言明确：每个测试只验证一个功能点",
            
            "集成测试": "集成测试重点关注：\n1. 接口测试：验证模块间接口的正确性\n2. 数据流测试：验证数据在系统中的流转\n3. 端到端测试：模拟用户真实操作流程\n4. 环境一致性：测试环境要尽量接近生产环境",
            
            # ===== 项目管理相关 =====
            "项目管理": "项目管理核心要素：\n1. 范围管理：明确项目边界，控制需求变更\n2. 时间管理：制定合理进度计划，识别关键路径\n3. 资源管理：合理分配人员和技术资源\n4. 风险管理：识别项目风险并制定应对策略",
            
            "需求管理": "需求管理最佳实践：\n1. 需求收集：通过用户访谈、原型演示等方法深入了解真实需求\n2. 需求分析：将业务需求转化为具体的功能需求\n3. 需求变更：建立变更委员会，评估变更影响\n4. 需求追踪：确保每个需求都能追踪到具体实现",
            
            "进度管理": "进度管理有效方法：\n1. 任务分解：使用WBS将项目分解为可管理的任务\n2. 时间估算：结合历史数据和专家判断进行估算\n3. 关键路径：识别影响项目总工期的关键任务\n4. 进度跟踪：定期更新进度，及时发现偏差",
            
            # ===== 敏捷开发相关 =====
            "敏捷开发": "敏捷开发核心实践：\n1. 迭代开发：2-4周的短周期开发\n2. 持续反馈：频繁交付，及时获得用户反馈\n3. 拥抱变化：快速响应需求变更\n4. 团队协作：跨功能团队紧密合作",
            
            "Sprint计划": "Sprint计划制定步骤：\n1. 需求梳理：从Product Backlog中选择本轮要开发的需求\n2. 任务分解：将需求分解为具体的开发任务\n3. 工作量估算：团队共同估算每个任务的工作量\n4. 承诺确认：团队承诺在Sprint期间完成选定的任务",
            
            "站会": "每日站会运营要点：\n1. 时间控制：严格控制在15分钟内\n2. 三个问题：昨天做了什么、今天计划什么、遇到什么障碍\n3. 问题跟进：记录障碍和问题，会后专门解决\n4. 团队同步：让团队成员了解彼此的工作进展",
            
            "回顾会议": "Sprint回顾会议要点：\n1. 总结成果：回顾本轮Sprint的完成情况\n2. 问题分析：分析遇到的问题和原因\n3. 改进措施：提出下轮Sprint的改进计划\n4. 团队建设：增进团队成员间的理解和信任",
            
            # ===== 团队协作相关 =====
            "团队协作": "团队协作提升方法：\n1. 沟通机制：建立定期沟通机制，包括周会、月会等\n2. 协作工具：使用Slack、Teams等工具提高沟通效率\n3. 知识共享：建立团队知识库，分享最佳实践\n4. 团队文化：营造开放、互助的团队氛围",
            
            "冲突处理": "团队冲突处理策略：\n1. 及时沟通：发现冲突苗头要及时介入\n2. 倾听各方：公平听取各方观点和诉求\n3. 寻找共识：找到各方都能接受的解决方案\n4. 跟踪效果：确保解决方案得到有效执行",
            
            "会议管理": "高效会议管理技巧：\n1. 明确目标：会前确定会议目标和议程\n2. 控制时间：严格按时开始和结束\n3. 记录决定：记录会议决定和行动项\n4. 跟进执行：确保会议决定得到执行",
            
            # ===== 软件工程基础 =====
            "软件工程": "软件工程是应用工程化方法开发软件的学科。\n核心包括：需求分析、系统设计、编码实现、测试验证、部署维护等阶段。\n目标是在预算和时间约束下，开发出满足用户需求的高质量软件产品。",
            
            "软件测试": "软件测试是通过运行程序来检测软件缺陷的过程。\n主要包括单元测试、集成测试、系统测试等类型。\n测试方法有黑盒测试、白盒测试和灰盒测试。\n目标是确保软件质量，降低上线风险。",
            
            "设计模式": "设计模式是软件设计中常见问题的可复用解决方案。\n主要分为创建型、结构型、行为型三大类。\n常用模式包括单例、工厂、观察者、策略模式等。\n能提高代码的可维护性和可扩展性。",
            
            # ===== 职业发展相关 =====
            "职业规划": "程序员职业发展路径：\n1. 技术路线：初级→中级→高级→架构师→技术专家\n2. 管理路线：开发→技术主管→项目经理→技术总监\n3. 产品路线：开发→产品助理→产品经理→产品总监\n4. 创业路线：积累技术和管理经验后自主创业",
            
            "技能提升": "程序员技能提升建议：\n1. 技术深度：深入掌握1-2门编程语言和相关技术栈\n2. 技术广度：了解多种技术领域，具备全栈开发能力\n3. 软技能：提升沟通、团队协作、项目管理能力\n4. 学习能力：保持持续学习，关注技术发展趋势",
        }
    
    def _build_emotion_keywords(self) -> Dict[str, List[str]]:
        """构建情绪关键词库"""
        return {
            "焦虑": ["焦虑", "紧张", "压力", "担心", "不安", "忧虑"],
            "沮丧": ["沮丧", "失望", "挫折", "绝望", "无助", "难过"],
            "愤怒": ["愤怒", "生气", "恼火", "烦躁", "气愤", "愤恨"],
            "疲惫": ["累", "疲惫", "疲劳", "筋疲力尽", "身心俱疲"],
            "困惑": ["困惑", "迷茫", "不知道", "不明白", "搞不懂"]
        }
    
    def search_knowledge(self, query: str) -> Tuple[str, float]:
        """精准搜索知识库答案"""
        query_clean = query.strip().lower()
        best_match = ""
        best_score = 0.0
        
        # 1. 精确匹配核心关键词
        keyword_matches = {
            "代码质量": ["代码质量", "代码规范", "代码审查", "code review", "质量保障", "如何保障代码质量"],
            "测试策略": ["测试策略", "测试计划", "测试方法", "怎么测试", "测试怎么", "策略制定"],
            "软件测试": ["软件测试", "测试是什么", "测试方法", "测试类型"],
            "单元测试": ["单元测试", "unit test", "单测"],
            "集成测试": ["集成测试", "integration test"],
            "项目管理": ["项目管理", "project management", "项目怎么管"],
            "需求管理": ["需求管理", "需求变更", "需求收集", "需求分析"],
            "进度管理": ["进度管理", "进度控制", "时间管理", "延期"],
            "敏捷开发": ["敏捷开发", "agile", "scrum"],
            "Sprint计划": ["sprint计划", "sprint", "冲刺计划", "sprint怎么"],
            "站会": ["站会", "daily", "每日会议", "晨会", "站会怎么开"],
            "回顾会议": ["回顾会议", "retrospective", "复盘"],
            "团队协作": ["团队协作", "团队合作", "协作"],
            "冲突处理": ["冲突处理", "团队冲突", "处理冲突"],
            "会议管理": ["会议管理", "开会", "会议效率"],
            "软件工程": ["软件工程", "software engineering"],
            "设计模式": ["设计模式", "design pattern"],
            "职业规划": ["职业规划", "职业发展", "career"],
            "技能提升": ["技能提升", "学习建议", "怎么学习"]
        }
        
        # 查找最佳匹配
        for qa_key, keywords in keyword_matches.items():
            for keyword in keywords:
                if keyword in query_clean:
                    if qa_key in self.qa_database:
                        best_match = self.qa_database[qa_key]
                        best_score = 0.9
                        break
            if best_score > 0.8:
                break
        
        # 2. 如果没有精确匹配，尝试部分匹配
        if best_score < 0.5:
            for qa_key, answer in self.qa_database.items():
                if qa_key.lower() in query_clean:
                    best_match = answer
                    best_score = 0.7
                    break
        
        # 3. 最后尝试模糊匹配
        if best_score < 0.5:
            query_words = query_clean.split()
            for qa_key, answer in self.qa_database.items():
                key_words = qa_key.lower().split()
                matches = sum(1 for word in query_words if any(w in word or word in w for w in key_words))
                if matches > 0 and matches / len(query_words) > 0.3:
                    best_match = answer
                    best_score = 0.5
                    break
        
        return best_match or "抱歉，我对这个问题还不够了解。您可以尝试询问软件工程、项目管理、测试策略等相关问题。", best_score
    
    def detect_emotion(self, text: str) -> Tuple[str, List[str]]:
        """检测文本中的情绪"""
        detected_emotions = []
        matched_keywords = []
        
        text_lower = text.lower()
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_emotions.append(emotion)
                    matched_keywords.append(keyword)
        
        primary_emotion = detected_emotions[0] if detected_emotions else "中性"
        return primary_emotion, matched_keywords
    
    def get_emotional_support(self, emotion: str, context: str = "") -> str:
        """根据情绪提供支持"""
        support_responses = {
            "焦虑": "我理解您现在的焦虑感受。深呼吸一下，让我们一步步来解决问题。",
            "沮丧": "遇到挫折是很正常的，这是成长过程的一部分。让我们看看有什么可以改进的地方。",
            "愤怒": "我能感受到您的愤怒。让我们冷静地分析一下情况，找到解决问题的最佳方式。",
            "疲惫": "您辛苦了！适当的休息很重要，劳逸结合才能保持长期的工作效率。",
            "困惑": "遇到困惑是学习过程中的正常现象。让我们一起来梳理一下思路。"
        }
        
        return support_responses.get(emotion, "我理解您的感受，让我们一起来解决这个问题。")

# 全局知识库实例
_knowledge_base = SoftwareEngineeringKnowledgeBase()

def search_knowledge(query: str) -> Tuple[str, float]:
    """搜索知识库"""
    return _knowledge_base.search_knowledge(query)

def get_emotional_support(text: str) -> Tuple[str, str]:
    """获取情绪支持"""
    emotion, keywords = _knowledge_base.detect_emotion(text)
    support = _knowledge_base.get_emotional_support(emotion, text)
    return emotion, support 