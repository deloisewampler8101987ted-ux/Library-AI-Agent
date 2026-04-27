# -*- coding: utf-8 -*-
"""
推荐服务模块
联动千问理由生成的推荐算法
"""

import random
from typing import Any, Dict, List, Optional


class RecommendService:
    """推荐服务"""

    def __init__(self, library_service, qianwen_client):
        """
        初始化推荐服务

        Args:
            library_service: 图书馆服务实例
            qianwen_client: 千问客户端实例
        """
        self.library_service = library_service
        self.qianwen_client = qianwen_client

        # 推荐分类配置
        self.categories = [
            {"id": "recommend_for_you", "name": "为你推荐", "icon": "star"},
            {"id": "major_related", "name": "专业相关", "icon": "book"},
            {"id": "hot_borrow", "name": "热门借阅", "icon": "fire"},
            {"id": "new_books", "name": "新书上架", "icon": "new"},
            {"id": "fiction", "name": "小说", "icon": "novel"},
            {"id": "tech", "name": "技术", "icon": "code"},
            {"id": "science", "name": "科普", "icon": "science"},
            {"id": "history", "name": "历史", "icon": "history"},
        ]

    def get_recommend_categories(self) -> List[Dict]:
        """获取推荐分类列表"""
        return self.categories

    def get_recommend_books(
        self,
        category_id: str,
        user_profile: Optional[Dict] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        获取推荐图书

        Args:
            category_id: 分类ID
            user_profile: 用户画像
            page: 页码
            page_size: 每页数量

        Returns:
            Dict: 推荐结果
        """
        books = []

        if category_id == "recommend_for_you":
            # 为你推荐（个性化）
            books = self._get_personal_recommend(user_profile)
        elif category_id == "major_related":
            # 专业相关
            books = self._get_major_recommend(user_profile)
        elif category_id == "hot_borrow":
            # 热门借阅
            books = self.library_service.get_hot_books()
        elif category_id == "new_books":
            # 新书上架
            books = self.library_service.get_new_books()
        else:
            # 按分类获取
            category_map = {
                "fiction": "科幻小说",
                "tech": "编程",
                "science": "科普",
                "history": "历史",
            }
            category_name = category_map.get(category_id, "")
            if category_name:
                result = self.library_service.get_books_by_category(
                    category_name, page, page_size
                )
                books = result.get("data", {}).get("list", [])

        # 生成推荐理由
        for book in books:
            book["recommend_reason"] = self._generate_recommend_reason(
                book, user_profile
            )

        return {
            "success": True,
            "data": {"category_id": category_id, "list": books, "total": len(books)},
        }

    def _get_personal_recommend(self, user_profile: Optional[Dict]) -> List[Dict]:
        """获取个性化推荐"""
        all_books = self.library_service._mock_data["books"]

        if not user_profile:
            # 无用户画像，返回随机推荐
            return random.sample(all_books, min(5, len(all_books)))

        # 基于用户画像推荐
        recommended = []
        major = user_profile.get("major", "")
        interests = user_profile.get("interests", [])

        for book in all_books:
            score = 0

            # 专业匹配加分
            if major and major in book.get("description", ""):
                score += 2

            # 兴趣匹配加分
            for interest in interests:
                if interest in book.get("category", ""):
                    score += 1

            if score > 0:
                book["_score"] = score
                recommended.append(book)

        # 按分数排序
        recommended.sort(key=lambda x: x.get("_score", 0), reverse=True)

        return recommended[:10]

    def _get_major_recommend(self, user_profile: Optional[Dict]) -> List[Dict]:
        """获取专业相关推荐"""
        if not user_profile:
            return self.library_service.get_hot_books()

        major = user_profile.get("major", "")
        major_books = []

        all_books = self.library_service._mock_data["books"]
        for book in all_books:
            if major and major in book.get("description", ""):
                major_books.append(book)

        return major_books[:10] if major_books else all_books[:5]

    def _generate_recommend_reason(
        self, book: Dict, user_profile: Optional[Dict]
    ) -> str:
        """
        生成推荐理由

        Args:
            book: 图书信息
            user_profile: 用户画像

        Returns:
            str: 推荐理由
        """
        if not self.qianwen_client:
            return self._simple_reason(book)

        try:
            result = self.qianwen_client.generate_recommendation_reason(
                book_info=book, user_profile=user_profile or {}
            )
            return result
        except Exception as e:
            print(f"生成推荐理由失败: {e}")
            return self._simple_reason(book)

    def _simple_reason(self, book: Dict) -> str:
        """简单推荐理由（无千问时使用）"""
        reasons = [
            "热门借阅图书，值得一读",
            "经典之作，不容错过",
            "内容丰富，评价很高",
            "适合入门学习",
            "深受读者喜爱",
        ]
        return random.choice(reasons)

    def custom_recommend(
        self, query: str, user_profile: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        自定义推荐（用户输入需求）

        Args:
            query: 用户需求描述
            user_profile: 用户画像

        Returns:
            Dict: 推荐结果
        """
        # 解析用户需求
        keywords = self._parse_user_query(query)

        # 搜索匹配图书
        all_books = self.library_service._mock_data["books"]
        matched_books = []

        for book in all_books:
            book_text = f"{book.get('title', '')} {book.get('author', '')} {book.get('description', '')} {book.get('category', '')}"

            match_count = 0
            for keyword in keywords:
                if keyword in book_text:
                    match_count += 1

            if match_count > 0:
                book["_match_score"] = match_count
                matched_books.append(book)

        # 排序
        matched_books.sort(key=lambda x: x.get("_match_score", 0), reverse=True)

        # 生成推荐理由
        for book in matched_books[:10]:
            book["recommend_reason"] = self._generate_recommend_reason(
                book, user_profile
            )

        # 生成临时分类名
        category_name = self._generate_category_name(query)

        return {
            "success": True,
            "data": {
                "category_id": "custom",
                "category_name": category_name,
                "query": query,
                "list": matched_books[:10],
                "total": len(matched_books),
            },
        }

    def _parse_user_query(self, query: str) -> List[str]:
        """解析用户查询关键词"""
        # 简单分词
        keywords = []

        # 专业/类别关键词
        majors = [
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
            "人工智能",
            "机器学习",
        ]
        categories = ["小说", "科幻", "悬疑", "编程", "技术", "科普", "历史", "哲学"]
        purposes = ["考研", "备考", "入门", "进阶", "冲刺"]

        for word in majors + categories + purposes:
            if word in query:
                keywords.append(word)

        if not keywords:
            keywords = [query]

        return keywords

    def _generate_category_name(self, query: str) -> str:
        """生成临时分类名"""
        if not self.qianwen_client:
            # 简单处理
            return f"关于「{query}」的推荐"

        try:
            result = self.qianwen_client.chat(
                message=f"请为以下用户需求生成一个简洁的分类名称（3-6个字）：{query}",
                temperature=0.7,
                max_tokens=50,
            )
            if result.get("success"):
                return result["content"].strip()
        except:
            pass

        return f"关于「{query}」的推荐"

    def refresh_recommend(
        self,
        category_id: str,
        user_profile: Optional[Dict] = None,
        exclude_book_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        刷新推荐（换一批）

        Args:
            category_id: 分类ID
            user_profile: 用户画像
            exclude_book_ids: 排除的图书ID

        Returns:
            Dict: 新的推荐结果
        """
        result = self.get_recommend_books(category_id, user_profile)

        if exclude_book_ids:
            # 过滤已推荐的图书
            books = result["data"]["list"]
            result["data"]["list"] = [
                b for b in books if b.get("id") not in exclude_book_ids
            ]
            result["data"]["total"] = len(result["data"]["list"])

        return result


# 全局服务实例
_recommend_service: Optional[RecommendService] = None


def init_recommend_service(library_service, qianwen_client) -> RecommendService:
    """初始化推荐服务"""
    global _recommend_service
    _recommend_service = RecommendService(library_service, qianwen_client)
    return _recommend_service


def get_recommend_service() -> RecommendService:
    """获取推荐服务实例"""
    if _recommend_service is None:
        raise RuntimeError("推荐服务未初始化")
    return _recommend_service
