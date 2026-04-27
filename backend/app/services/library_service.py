# -*- coding: utf-8 -*-
"""
图书馆服务模块
封装 LMS 系统接口（借阅记录、图书查询、预约等）
"""

import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class BorrowStatus(Enum):
    """借阅状态"""
    BORROWED = "borrowed"      # 已借出
    AVAILABLE = "available"    # 可借
    RESERVED = "reserved"      # 已预约
    OVERDUE = "overdue"       # 已逾期


class LibraryService:
    """图书馆服务"""
    
    def __init__(self, lms_api_url: str = "", lms_api_key: str = ""):
        """
        初始化图书馆服务
        
        Args:
            lms_api_url: LMS 系统 API 地址
            lms_api_key: LMS API 密钥
        """
        self.lms_api_url = lms_api_url
        self.lms_api_key = lms_api_key
        self._mock_data = self._load_mock_data()
    
    def _load_mock_data(self) -> Dict:
        """加载模拟数据（实际项目中替换为真实API调用）"""
        return {
            "books": [
                {
                    "id": "B001",
                    "title": "三体",
                    "author": "刘慈欣",
                    "publisher": "重庆出版社",
                    "isbn": "978-7-5366-8624-5",
                    "description": "地球文明与三体文明的星际战争",
                    "category": "科幻小说",
                    "total": 5,
                    "available": 3,
                    "location": "一楼科幻区A-12"
                },
                {
                    "id": "B002",
                    "title": "Python编程：从入门到实践",
                    "author": "埃里克·马瑟斯",
                    "publisher": "人民邮电出版社",
                    "isbn": "978-7-115-42866-4",
                    "description": "Python入门经典教材",
                    "category": "编程",
                    "total": 8,
                    "available": 5,
                    "location": "二楼技术区B-05"
                },
                {
                    "id": "B003",
                    "title": "活着",
                    "author": "余华",
                    "publisher": "作家出版社",
                    "isbn": "978-7-5063-2543-9",
                    "description": "讲述农民福贵的人生悲剧",
                    "category": "文学",
                    "total": 6,
                    "available": 4,
                    "location": "三楼文学区C-18"
                },
                {
                    "id": "B004",
                    "title": "人工智能导论",
                    "author": "王晓晔",
                    "publisher": "高等教育出版社",
                    "isbn": "978-7-04-044638-5",
                    "description": "AI入门教材，涵盖机器学习、深度学习基础",
                    "category": "人工智能",
                    "total": 10,
                    "available": 2,
                    "location": "二楼技术区B-22"
                },
                {
                    "id": "B005",
                    "title": "盗墓笔记",
                    "author": "南派三叔",
                    "publisher": "中国友谊出版公司",
                    "isbn": "978-7-5057-2271-9",
                    "description": "盗墓题材悬疑小说",
                    "category": "悬疑小说",
                    "total": 4,
                    "available": 2,
                    "location": "一楼悬疑区D-03"
                },
            ],
            "borrow_records": [
                {
                    "id": "BR001",
                    "book_id": "B002",
                    "book_title": "Python编程：从入门到实践",
                    "borrow_date": "2026-04-01",
                    "due_date": "2026-04-30",
                    "status": "borrowed"
                },
                {
                    "id": "BR002",
                    "book_id": "B003",
                    "book_title": "活着",
                    "borrow_date": "2026-04-15",
                    "due_date": "2026-05-15",
                    "status": "borrowed"
                },
            ],
            "reservations": [
                {
                    "id": "R001",
                    "book_id": "B001",
                    "book_title": "三体",
                    "reserve_date": "2026-04-25",
                    "expire_date": "2026-04-28",
                    "status": "available"
                }
            ]
        }
    
    # ==================== 图书查询 ====================
    
    def search_books(
        self, 
        keyword: str, 
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """
        搜索图书
        
        Args:
            keyword: 搜索关键词
            category: 图书分类
            page: 页码
            page_size: 每页数量
            
        Returns:
            Dict: 搜索结果
        """
        books = self._mock_data["books"]
        
        # 过滤
        results = []
        keyword_lower = keyword.lower()
        for book in books:
            # 关键词匹配
            if (keyword_lower in book.get("title", "").lower() or
                keyword_lower in book.get("author", "").lower() or
                keyword_lower in book.get("description", "").lower()):
                
                # 分类过滤
                if category is None or book.get("category") == category:
                    results.append(book)
        
        # 分页
        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        page_data = results[start:end]
        
        return {
            "success": True,
            "data": {
                "list": page_data,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    
    def get_book_by_id(self, book_id: str) -> Optional[Dict]:
        """根据ID获取图书详情"""
        for book in self._mock_data["books"]:
            if book.get("id") == book_id:
                return book
        return None
    
    def get_book_by_title(self, title: str) -> Optional[Dict]:
        """根据书名获取图书"""
        for book in self._mock_data["books"]:
            if title in book.get("title", ""):
                return book
        return None
    
    def get_books_by_category(
        self, 
        category: str, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """根据分类获取图书列表"""
        books = self._mock_data["books"]
        
        # 过滤分类
        results = [b for b in books if b.get("category") == category]
        
        # 分页
        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        page_data = results[start:end]
        
        return {
            "success": True,
            "data": {
                "list": page_data,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
    
    def get_all_categories(self) -> List[str]:
        """获取所有图书分类"""
        categories = set()
        for book in self._mock_data["books"]:
            if book.get("category"):
                categories.add(book["category"])
        return sorted(list(categories))
    
    def get_hot_books(self, limit: int = 10) -> List[Dict]:
        """获取热门图书（模拟：按借阅热度）"""
        return self._mock_data["books"][:limit]
    
    def get_new_books(self, limit: int = 10) -> List[Dict]:
        """获取新书（模拟：返回前N本）"""
        return self._mock_data["books"][:limit]
    
    # ==================== 借阅管理 ====================
    
    def get_borrow_status(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户借阅状态
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 借阅状态信息
        """
        records = self._mock_data["borrow_records"]
        
        # 计算逾期数量
        overdue_count = 0
        today = datetime.now().date()
        
        for record in records:
            due_date = datetime.strptime(record["due_date"], "%Y-%m-%d").date()
            if due_date < today:
                record["is_overdue"] = True
                overdue_count += 1
            else:
                record["is_overdue"] = False
        
        return {
            "success": True,
            "data": {
                "borrowing_count": len(records),
                "overdue_count": overdue_count,
                "records": records
            }
        }
    
    def borrow_book(self, user_id: str, book_id: str) -> Dict[str, Any]:
        """
        借书
        
        Args:
            user_id: 用户ID
            book_id: 图书ID
            
        Returns:
            Dict: 借书结果
        """
        # 检查图书是否可借
        book = self.get_book_by_id(book_id)
        if not book:
            return {"success": False, "message": "图书不存在"}
        
        if book.get("available", 0) <= 0:
            return {"success": False, "message": "图书已全部借出"}
        
        # 检查用户借阅数量
        borrow_status = self.get_borrow_status(user_id)
        if borrow_status["data"]["borrowing_count"] >= 5:
            return {"success": False, "message": "已达到最大借阅数量(5本)"}
        
        # 创建借阅记录
        new_record = {
            "id": f"BR{len(self._mock_data['borrow_records']) + 1:03d}",
            "book_id": book_id,
            "book_title": book["title"],
            "borrow_date": datetime.now().strftime("%Y-%m-%d"),
            "due_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "status": "borrowed"
        }
        
        self._mock_data["borrow_records"].append(new_record)
        
        # 更新图书可借数量
        book["available"] -= 1
        
        return {
            "success": True,
            "message": "借书成功",
            "data": new_record
        }
    
    def return_book(self, user_id: str, record_id: str) -> Dict[str, Any]:
        """
        还书
        
        Args:
            user_id: 用户ID
            record_id: 借阅记录ID
            
        Returns:
            Dict: 还书结果
        """
        records = self._mock_data["borrow_records"]
        
        for record in records:
            if record.get("id") == record_id:
                # 归还图书
                book = self.get_book_by_id(record["book_id"])
                if book:
                    book["available"] += 1
                
                # 更新记录状态
                record["status"] = "returned"
                record["return_date"] = datetime.now().strftime("%Y-%m-%d")
                
                return {
                    "success": True,
                    "message": "还书成功",
                    "data": record
                }
        
        return {"success": False, "message": "借阅记录不存在"}
    
    def renew_book(self, user_id: str, record_id: str) -> Dict[str, Any]:
        """
        续借
        
        Args:
            user_id: 用户ID
            record_id: 借阅记录ID
            
        Returns:
            Dict: 续借结果
        """
        records = self._mock_data["borrow_records"]
        
        for record in records:
            if record.get("id") == record_id:
                # 检查是否已逾期
                due_date = datetime.strptime(record["due_date"], "%Y-%m-%d")
                if due_date.date() < datetime.now().date():
                    return {"success": False, "message": "已逾期，无法续借"}
                
                # 续借30天
                new_due_date = due_date + timedelta(days=30)
                record["due_date"] = new_due_date.strftime("%Y-%m-%d")
                record["renew_count"] = record.get("renew_count", 0) + 1
                
                return {
                    "success": True,
                    "message": "续借成功",
                    "data": record
                }
        
        return {"success": False, "message": "借阅记录不存在"}
    
    # ==================== 预约管理 ====================
    
    def reserve_book(self, user_id: str, book_id: str) -> Dict[str, Any]:
        """
        预约图书
        
        Args:
            user_id: 用户ID
            book_id: 图书ID
            
        Returns:
            Dict: 预约结果
        """
        book = self.get_book_by_id(book_id)
        if not book:
            return {"success": False, "message": "图书不存在"}
        
        # 检查是否已预约
        for res in self._mock_data["reservations"]:
            if res.get("book_id") == book_id and res.get("status") != "expired":
                return {"success": False, "message": "该图书已有人预约"}
        
        # 创建预约记录
        new_reservation = {
            "id": f"R{len(self._mock_data['reservations']) + 1:03d}",
            "book_id": book_id,
            "book_title": book["title"],
            "reserve_date": datetime.now().strftime("%Y-%m-%d"),
            "expire_date": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "status": "reserved"
        }
        
        self._mock_data["reservations"].append(new_reservation)
        
        return {
            "success": True,
            "message": "预约成功",
            "data": new_reservation
        }
    
    def cancel_reservation(self, user_id: str, reservation_id: str) -> Dict[str, Any]:
        """取消预约"""
        reservations = self._mock_data["reservations"]
        
        for res in reservations:
            if res.get("id") == reservation_id:
                res["status"] = "cancelled"
                return {"success": True, "message": "取消预约成功"}
        
        return {"success": False, "message": "预约记录不存在"}
    
    def get_user_reservations(self, user_id: str) -> List[Dict]:
        """获取用户预约列表"""
        return self._mock_data["reservations"]
    
    # ==================== 通知 ====================
    
    def get_notifications(self, user_id: str) -> List[Dict]:
        """获取用户通知"""
        notifications = []
        
        # 检查即将到期的图书
        records = self._mock_data["borrow_records"]
        today = datetime.now().date()
        
        for record in records:
            due_date = datetime.strptime(record["due_date"], "%Y-%m-%d").date()
            days_left = (due_date - today).days
            
            if 0 < days_left <= 3:
                notifications.append({
                    "type": "due_reminder",
                    "title": "图书到期提醒",
                    "message": f"《{record['book_title']}》还有{days_left}天到期，请及时归还",
                    "book_id": record["book_id"],
                    "record_id": record["id"]
                })
            elif days_left < 0:
                notifications.append({
                    "type": "overdue_warning",
                    "title": "图书逾期提醒",
                    "message": f"《{record['book_title']》已逾期{-days_left}天，请尽快归还",}
                    "book_id": record["book_id"],
                    "record_id": record["id"]
                })
        
        # 检查预约到书
        for res in self._mock_data["reservations"]:
            if res.get("status") == "available":
                notifications.append({
                    "type": "reservation_available",
                    "title": "预约到书",
                    "message": f"《{res['book_title']}》已到馆，请在3天内借阅",
                    "book_id": res["book_id"],
                    "reservation_id": res["id"]
                })
        
        return notifications


# 全局服务实例
_library_service: Optional[LibraryService] = None


def init_library_service(lms_api_url: str = "", lms_api_key: str = "") -> LibraryService:
    """初始化图书馆服务"""
    global _library_service
    _library_service = LibraryService(lms_api_url, lms_api_key)
    return _library_service


def get_library_service() -> LibraryService:
    """获取图书馆服务实例"""
    if _library_service is None:
        return LibraryService()
    return _library_service