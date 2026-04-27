# -*- coding: utf-8 -*-
"""
意图识别模块
基于 Few-Shot 样本处理，实现推荐、搜索、咨询三大意图识别
"""

from enum import Enum
from typing import Dict, Optional, Tuple


class IntentType(Enum):
    """意图类型枚举"""

    RECOMMEND = "recommend"  # 推荐意图：推荐图书、推荐类别
    SEARCH = "search"  # 搜索意图：搜索特定图书
    CONSULT = "consult"  # 咨询意图：咨询规则、问题解答
    BORROW_STATUS = "borrow_status"  # 借阅状态查询
    RESERVE = "reserve"  # 预约图书
    UNKNOWN = "unknown"  # 未知意图


# Few-Shot 训练样本
INTENT_SAMPLES = {
    IntentType.RECOMMEND: [
        "推荐一本计算机专业的书",
        "给我推荐一些科幻小说",
        "有什么好看的历史书吗",
        "推荐考研英语真题",
        "按我的专业推荐一些书",
        "我想看一些悬疑小说",
        "推荐几本入门的编程书",
        "有什么适合大一新生的书",
        "推荐公务员备考资料",
        "按兴趣推荐一些读物",
    ],
    IntentType.SEARCH: [
        "搜索《三体》",
        "查一下《Python编程》在哪里",
        "我想找《活着》这本书",
        "查找《盗墓笔记》",
        "搜索鲁迅的作品",
        "查《数据结构》这本书",
        "帮我找《百年孤独》",
        "搜索关于机器学习的书",
        "查找《平凡的世界》",
        "搜索金庸的武侠小说",
    ],
    IntentType.CONSULT: [
        "图书馆开放时间",
        "最多能借几本书",
        "续借规则是什么",
        "怎么预约图书",
        "借书要收费吗",
        "图书馆在哪",
        "怎么办理借书证",
        "逾期罚款多少",
        "可以委托代借吗",
        "闭馆时间",
    ],
    IntentType.BORROW_STATUS: [
        "我借了几本书",
        "查看我的借阅状态",
        "我有哪些书要还",
        "我的书什么时候到期",
        "还有多久还书",
        "当前借阅情况",
        "查询借书记录",
        "我借的书有哪些",
    ],
    IntentType.RESERVE: [
        "预约《三体》",
        "我想预约这本书",
        "预约《Python编程》",
        "帮我预约",
        "预定这本书",
        "预约下周一",
        "预约《盗墓笔记》",
    ],
}


class IntentDetector:
    """意图识别器"""

    def __init__(self, qianwen_client=None):
        """
        初始化意图识别器

        Args:
            qianwen_client: 千问客户端实例
        """
        self.qianwen_client = qianwen_client
        self.samples = INTENT_SAMPLES

    def detect(self, query: str) -> Tuple[IntentType, float, Dict]:
        """
        检测用户意图

        Args:
            query: 用户输入查询

        Returns:
            Tuple[IntentType, confidence, entities]:
                - IntentType: 识别出的意图类型
                - confidence: 置信度 (0-1)
                - entities: 提取的实体信息
        """
        # 1. 规则匹配（快速匹配）
        intent, confidence, entities = self._rule_match(query)
        if confidence > 0.9:
            return intent, confidence, entities

        # 2. 千问模型匹配（精确匹配）
        if self.qianwen_client:
            intent, confidence, entities = self._model_match(query)

        return intent, confidence, entities

    def _rule_match(self, query: str) -> Tuple[IntentType, float, Dict]:
        """
        基于规则的意图匹配
        快速筛选高频意图
        """
        query = query.lower()
        entities = {}

        # 借阅状态关键词
        borrow_keywords = [
            "借了几本",
            "借阅状态",
            "借了什么",
            "要还",
            "到期",
            "借书记录",
        ]
        if any(kw in query for kw in borrow_keywords):
            return IntentType.BORROW_STATUS, 0.95, entities

        # 预约关键词
        reserve_keywords = ["预约", "预定", "预订", "预约图书"]
        if any(kw in query for kw in reserve_keywords):
            return IntentType.RESERVE, 0.9, entities

        # 搜索关键词
        search_keywords = ["搜索", "查找", "找", "在哪", "查一下"]
        if any(kw in query for kw in search_keywords):
            return IntentType.SEARCH, 0.85, entities

        # 推荐关键词
        recommend_keywords = ["推荐", "给我", "有什么", "好看的", "适合"]
        if any(kw in query for kw in recommend_keywords):
            return IntentType.RECOMMEND, 0.85, entities

        # 咨询关键词
        consult_keywords = ["开放时间", "规则", "怎么办", "多少", "在哪", "如何"]
        if any(kw in query for kw in consult_keywords):
            return IntentType.CONSULT, 0.8, entities

        return IntentType.UNKNOWN, 0.0, entities

    def _model_match(self, query: str) -> Tuple[IntentType, float, Dict]:
        """
        基于千问模型的意图识别
        使用 Few-Shot 样本提升准确率
        """
        # 构建 Few-Shot prompt
        prompt = self._build_few_shot_prompt(query)

        result = self.qianwen_client.chat(
            message=prompt, temperature=0.3, max_tokens=500
        )

        if not result.get("success"):
            return IntentType.UNKNOWN, 0.0, {}

        # 解析模型返回结果
        return self._parse_intent_result(result["content"], query)

    def _build_few_shot_prompt(self, query: str) -> str:
        """构建 Few-Shot 提示词"""
        examples = []
        for intent_type, samples in self.samples.items():
            examples.append(f"意图类型: {intent_type.value}")
            for sample in samples[:3]:  # 每类取3个样本
                examples.append(f"  - {sample}")
            examples.append("")

        prompt = f"""你是一个意图识别助手。请根据用户输入判断其意图类型。

已知意图类型：
- recommend: 推荐意图（想要推荐图书、类别）
- search: 搜索意图（想要查找特定图书）
- consult: 咨询意图（想要咨询规则、问题）
- borrow_status: 借阅状态查询
- reserve: 预约意图（想要预约图书）
- unknown: 未知意图

示例：
{chr(10).join(examples)}

用户输入: {query}

请以JSON格式返回识别结果：
{{
    "intent": "意图类型",
    "confidence": 置信度(0-1),
    "entities": {{"实体键": "实体值"}}
}}

只返回JSON，不要其他内容。"""

        return prompt

    def _parse_intent_result(
        self, content: str, query: str
    ) -> Tuple[IntentType, float, Dict]:
        """解析意图识别结果"""
        try:
            import json
            import re

            # 提取JSON部分
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                intent_str = result.get("intent", "unknown")
                confidence = float(result.get("confidence", 0))
                entities = result.get("entities", {})

                # 转换为枚举类型
                for intent_type in IntentType:
                    if intent_type.value == intent_str:
                        return intent_type, confidence, entities

        except Exception as e:
            print(f"解析意图结果失败: {e}")

        # 解析失败，回退到规则匹配
        return self._rule_match(query)

    def extract_entities(self, query: str, intent: IntentType) -> Dict:
        """
        从查询中提取实体信息

        Args:
            query: 用户查询
            intent: 已识别的意图类型

        Returns:
            Dict: 提取的实体信息
        """
        entities = {}

        if intent == IntentType.SEARCH or intent == IntentType.RESERVE:
            # 提取书名
            import re

            book_patterns = [
                r"《([^》]+)》",
                r'"([^"]+)"',
                r"《([^》]+)》",
                r"书名[是为]?([^，。,\n]+)",
            ]
            for pattern in book_patterns:
                match = re.search(pattern, query)
                if match:
                    entities["book_title"] = match.group(1)
                    break

        elif intent == IntentType.RECOMMEND:
            # 提取推荐类别/专业
            category_keywords = ["专业", "类别", "类型", "方面"]
            for keyword in category_keywords:
                if keyword in query:
                    idx = query.find(keyword)
                    if idx > 0:
                        entities["category"] = query[:idx].strip()

            # 提取专业信息
            major_keywords = [
                "计算机",
                "数学",
                "物理",
                "化学",
                "生物",
                "历史",
                "文学",
                "经济",
                "管理",
                "法律",
            ]
            for major in major_keywords:
                if major in query:
                    entities["major"] = major

        return entities


# 全局意图检测器实例
_intent_detector: Optional[IntentDetector] = None


def init_intent_detector(qianwen_client) -> IntentDetector:
    """初始化意图检测器"""
    global _intent_detector
    _intent_detector = IntentDetector(qianwen_client)
    return _intent_detector


def get_intent_detector() -> IntentDetector:
    """获取意图检测器实例"""
    if _intent_detector is None:
        raise RuntimeError("意图检测器未初始化")
    return _intent_detector
