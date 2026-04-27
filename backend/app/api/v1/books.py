# -*- coding: utf-8 -*-
"""
图书推荐与查询路由
提供图书搜索、推荐、预约等功能
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

# 将 Service 获取方法统一提取到顶部
# 注意：确保这些路径在你的项目中是正确的
from backend.app.services.library_service import get_library_service
from backend.app.services.recommend_service import get_recommend_service

router = APIRouter(prefix="/books", tags=["图书管理"])


# ==================== 请求模型 ====================


class BookReserveRequest(BaseModel):
    """预约请求"""
    book_id: str
    user_id: str = "default_user"


class BookBorrowRequest(BaseModel):
    """借书请求"""
    book_id: str
    user_id: str = "default_user"


# ==================== 图书查询接口 ====================


@router.get("/search")
async def search_books(
    keyword: str = Query(..., description="搜索关键词"),
    category: Optional[str] = Query(None, description="图书分类"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """
    搜索图书
    支持按书名、作者、出版社、ISBN搜索
    """
    try:
        library_service = get_library_service()
        result = library_service.search_books(keyword, category, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category")
async def get_categories():
    """获取图书分类列表"""
    try:
        library_service = get_library_service()
        categories = library_service.get_all_categories()
        return {"success": True, "data": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/{category}")
async def get_books_by_category(
    category: str,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """根据分类获取图书"""
    try:
        library_service = get_library_service()
        result = library_service.get_books_by_category(category, page, page_size)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hot")
async def get_hot_books(limit: int = Query(10, description="返回数量")):
    """获取热门图书"""
    try:
        library_service = get_library_service()
        books = library_service.get_hot_books(limit)
        return {"success": True, "data": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/new")
async def get_new_books(limit: int = Query(10, description="返回数量")):
    """获取新书"""
    try:
        library_service = get_library_service()
        books = library_service.get_new_books(limit)
        return {"success": True, "data": books}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{book_id}")
async def get_book_detail(book_id: str):
    """获取图书详情"""
    try:
        library_service = get_library_service()
        book = library_service.get_book_by_id(book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="图书不存在")
        return {"success": True, "data": book}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 图书预约接口 ====================


@router.post("/reserve")
async def reserve_book(request: BookReserveRequest):
    """预约图书"""
    try:
        library_service = get_library_service()
        result = library_service.reserve_book(request.user_id, request.book_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reserve/cancel")
async def cancel_reservation(
    user_id: str = Query(...), reservation_id: str = Query(...)
):
    """取消预约"""
    try:
        library_service = get_library_service()
        result = library_service.cancel_reservation(user_id, reservation_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 图书借阅接口 ====================


@router.post("/borrow")
async def borrow_book(request: BookBorrowRequest):
    """借书"""
    try:
        library_service = get_library_service()
        result = library_service.borrow_book(request.user_id, request.book_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/return")
async def return_book(user_id: str = Query(...), record_id: str = Query(...)):
    """还书"""
    try:
        library_service = get_library_service()
        result = library_service.return_book(user_id, record_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/renew")
async def renew_book(user_id: str = Query(...), record_id: str = Query(...)):
    """续借"""
    try:
        library_service = get_library_service()
        result = library_service.renew_book(user_id, record_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 推荐接口 ====================


@router.get("/recommend/categories")
async def get_recommend_categories():
    """获取推荐分类"""
    try:
        recommend_service = get_recommend_service()
        categories = recommend_service.get_recommend_categories()
        return {"success": True, "data": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommend/{category_id}")
async def get_recommend_books(
    category_id: str,
    user_id: str = Query("default_user"),
    page: int = Query(1),
    page_size: int = Query(10),
):
    """获取推荐图书"""
    try:
        recommend_service = get_recommend_service()
        # 获取用户画像（实际应从数据库获取）
        user_profile = {
            "major": "计算机",
            "grade": "大一",
            "interests": ["技术", "科幻"],
            "read_books": [],
        }
        result = recommend_service.get_recommend_books(
            category_id, user_profile, page, page_size
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/refresh")
async def refresh_recommend(
    category_id: str = Query(...),
    exclude_ids: str = Query("", description="排除的图书ID，逗号分隔"),
):
    """刷新推荐（换一批）"""
    try:
        recommend_service = get_recommend_service()
        exclude_list = exclude_ids.split(",") if exclude_ids else None
        result = recommend_service.refresh_recommend(
            category_id, exclude_book_ids=exclude_list
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/custom")
async def custom_recommend(
    query: str = Query(..., description="用户需求描述"),
    user_id: str = Query("default_user"),
):
    """自定义推荐"""
    try:
        recommend_service = get_recommend_service()
        # 获取用户画像
        user_profile = {
            "major": "计算机",
            "grade": "大一",
            "interests": ["技术", "科幻"],
            "read_books": [],
        }
        result = recommend_service.custom_recommend(query, user_profile)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))