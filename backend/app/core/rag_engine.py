# -*- coding: utf-8 -*-
"""
知识库检索核心逻辑
基于向量数据库实现 RAG（检索增强生成）
"""

import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional


class DocumentType(Enum):
    """文档类型枚举"""

    BORROW_RULES = "borrow_rules"  # 借阅规则
    FAQ = "faq"  # 常见问题
    BOOK_METADATA = "book_metadata"  # 图书元数据
    ACTIVITY = "activity"  # 活动通知


class RAGEngine:
    """检索增强生成引擎"""

    def __init__(self, knowledge_base_path: str):
        """
        初始化 RAG 引擎

        Args:
            knowledge_base_path: 知识库根目录路径
        """
        self.knowledge_base_path = knowledge_base_path
        self.vector_store = {}  # 简化版向量存储（实际项目中应使用 Milvus/Chroma）
        self.documents = {}  # 原始文档存储
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """加载知识库文档"""
        # 加载借阅规则
        rules_path = os.path.join(
            self.knowledge_base_path, "knowledge_base", "rules", "borrowing_policy.json"
        )
        if os.path.exists(rules_path):
            with open(rules_path, "r", encoding="utf-8") as f:
                self.documents[DocumentType.BORROW_RULES] = json.load(f)

        # 加载 FAQ
        faq_path = os.path.join(
            self.knowledge_base_path, "knowledge_base", "FAQ", "historical_qa.json"
        )
        if os.path.exists(faq_path):
            with open(faq_path, "r", encoding="utf-8") as f:
                self.documents[DocumentType.FAQ] = json.load(f)

        # 加载图书元数据
        metadata_path = os.path.join(
            self.knowledge_base_path, "knowledge_base", "metadata", "book_summaries.csv"
        )
        if os.path.exists(metadata_path):
            self._load_book_metadata(metadata_path)

        # 加载意图样本
        samples_path = os.path.join(
            self.knowledge_base_path, "knowledge_base", "samples", "intent_samples.json"
        )
        if os.path.exists(samples_path):
            with open(samples_path, "r", encoding="utf-8") as f:
                self.documents["intent_samples"] = json.load(f)

    def _load_book_metadata(self, csv_path: str):
        """加载图书元数据"""
        import csv

        books = []
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    books.append(row)
            self.documents[DocumentType.BOOK_METADATA] = books
        except Exception as e:
            print(f"加载图书元数据失败: {e}")
            self.documents[DocumentType.BOOK_METADATA] = []

    def retrieve(
        self, query: str, top_k: int = 5, doc_type: Optional[DocumentType] = None
    ) -> List[Dict[str, Any]]:
        """
        检索相关文档

        Args:
            query: 查询文本
            top_k: 返回结果数量
            doc_type: 限定文档类型

        Returns:
            List: 检索结果列表
        """
        results = []

        # 简化版检索：基于关键词匹配
        # 实际项目中应使用向量相似度搜索

        if doc_type == DocumentType.BORROW_RULES or doc_type is None:
            results.extend(self._search_borrow_rules(query, top_k))

        if doc_type == DocumentType.FAQ or doc_type is None:
            results.extend(self._search_faq(query, top_k))

        if doc_type == DocumentType.BOOK_METADATA or doc_type is None:
            results.extend(self._search_books(query, top_k))

        # 按相关性排序
        results.sort(key=lambda x: x.get("score", 0), reverse=True)

        return results[:top_k]

    def _search_borrow_rules(self, query: str, top_k: int) -> List[Dict]:
        """搜索借阅规则"""
        results = []
        rules = self.documents.get(DocumentType.BORROW_RULES, {})

        if not rules:
            return results

        # 搜索规则内容
        for rule in rules.get("rules", []):
            score = self._calculate_similarity(query, rule.get("content", ""))
            if score > 0.1:
                results.append(
                    {
                        "type": "borrow_rule",
                        "title": rule.get("title", ""),
                        "content": rule.get("content", ""),
                        "score": score,
                        "source": "borrowing_policy.json",
                    }
                )

        return results[:top_k]

    def _search_faq(self, query: str, top_k: int) -> List[Dict]:
        """搜索 FAQ"""
        results = []
        faq_data = self.documents.get(DocumentType.FAQ, {})

        for faq in faq_data.get("faqs", []):
            # 计算与问题的相似度
            question = faq.get("question", "")
            score = self._calculate_similarity(query, question)

            if score > 0.1:
                results.append(
                    {
                        "type": "faq",
                        "question": question,
                        "answer": faq.get("answer", ""),
                        "score": score,
                        "source": "historical_qa.json",
                    }
                )

        return results[:top_k]

    def _search_books(self, query: str, top_k: int) -> List[Dict]:
        """搜索图书"""
        results = []
        books = self.documents.get(DocumentType.BOOK_METADATA, [])

        query_lower = query.lower()
        for book in books:
            # 计算与图书的相似度
            book_text = f"{book.get('title', '')} {book.get('author', '')} {book.get('description', '')}"
            score = self._calculate_similarity(query_lower, book_text.lower())

            if score > 0.1:
                results.append(
                    {
                        "type": "book",
                        "title": book.get("title", ""),
                        "author": book.get("author", ""),
                        "publisher": book.get("publisher", ""),
                        "description": book.get("description", ""),
                        "score": score,
                        "source": "book_summaries.csv",
                    }
                )

        return results[:top_k]

    def _calculate_similarity(self, query: str, text: str) -> float:
        """
        计算查询与文本的相似度
        简化版：基于关键词重叠
        """
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())

        if not query_words or not text_words:
            return 0.0

        # Jaccard 相似度
        intersection = query_words & text_words
        union = query_words | text_words

        return len(intersection) / len(union) if union else 0.0

    def generate_answer(
        self,
        query: str,
        retrieved_docs: List[Dict],
        qianwen_client,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        基于检索结果生成回答

        Args:
            query: 用户查询
            retrieved_docs: 检索到的文档列表
            qianwen_client: 千问客户端
            system_prompt: 系统提示词

        Returns:
            str: 生成的回答
        """
        if not retrieved_docs:
            return "抱歉，我暂时没有找到相关信息。请问可以换个问题吗？"

        # 构建上下文
        context = self._build_context(retrieved_docs)

        # 构建 prompt
        if system_prompt is None:
            system_prompt = """你是一个专业的图书馆AI管理员。请根据提供的知识库内容回答用户问题。
回答要求：
1. 准确引用知识库中的信息
2. 回答简洁明了
3. 如果知识库中没有相关信息，请如实告知"""

        prompt = f"""基于以下知识库内容回答用户问题。

知识库内容：
{context}

用户问题：{query}

请根据知识库内容回答："""

        result = qianwen_client.chat(
            message=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000,
        )

        if result.get("success"):
            return result["content"]
        else:
            return f"生成回答时出错: {result.get('error', '未知错误')}"

    def _build_context(self, retrieved_docs: List[Dict]) -> str:
        """构建检索上下文"""
        context_parts = []

        for i, doc in enumerate(retrieved_docs, 1):
            doc_type = doc.get("type", "unknown")

            if doc_type == "borrow_rule":
                context_parts.append(
                    f"{i}. 【借阅规则】{doc.get('title', '')}\n   {doc.get('content', '')}"
                )
            elif doc_type == "faq":
                context_parts.append(
                    f"{i}. 【常见问题】\n   问题：{doc.get('question', '')}\n   回答：{doc.get('answer', '')}"
                )
            elif doc_type == "book":
                context_parts.append(
                    f"{i}. 【图书】{doc.get('title', '')} - {doc.get('author', '')}\n   {doc.get('description', '')}"
                )

        return "\n\n".join(context_parts)

    def get_borrow_rules(self) -> Dict:
        """获取借阅规则"""
        return self.documents.get(DocumentType.BORROW_RULES, {})

    def get_faq(self) -> List[Dict]:
        """获取 FAQ 列表"""
        faq_data = self.documents.get(DocumentType.FAQ, {})
        return faq_data.get("faqs", [])

    def get_book_by_title(self, title: str) -> Optional[Dict]:
        """根据书名获取图书信息"""
        books = self.documents.get(DocumentType.BOOK_METADATA, [])

        for book in books:
            if title in book.get("title", ""):
                return book

        return None


# 全局 RAG 引擎实例
_rag_engine: Optional[RAGEngine] = None


def init_rag_engine(knowledge_base_path: str) -> RAGEngine:
    """初始化 RAG 引擎"""
    global _rag_engine
    _rag_engine = RAGEngine(knowledge_base_path)
    return _rag_engine


def get_rag_engine() -> RAGEngine:
    """获取 RAG 引擎实例"""
    if _rag_engine is None:
        raise RuntimeError("RAG引擎未初始化")
    return _rag_engine
