# -*- coding: utf-8 -*-
"""
本地对话缓存与用户偏好表
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class MessageRole(str, Enum):
    """消息角色"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """消息模型"""

    role: MessageRole
    content: str
    timestamp: datetime = datetime.now()
    intent: Optional[str] = None  # 意图类型
    entities: Optional[Dict] = None  # 实体信息


class Session(BaseModel):
    """会话模型"""

    session_id: str
    user_id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    messages: List[Message] = []
    context: Dict = {}  # 会话上下文


class UserProfile(BaseModel):
    """用户画像"""

    user_id: str
    major: Optional[str] = None  # 专业
    grade: Optional[str] = None  # 年级
    interests: List[str] = []  # 兴趣标签
    read_books: List[str] = []  # 已读图书
    preferences: Dict = {}  # 其他偏好


class BorrowRecord(BaseModel):
    """借阅记录"""

    record_id: str
    user_id: str
    book_id: str
    book_title: str
    borrow_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    status: str = "borrowed"  # borrowed/returned/overdue


class Reservation(BaseModel):
    """预约记录"""

    reservation_id: str
    user_id: str
    book_id: str
    book_title: str
    reserve_date: datetime
    expire_date: datetime
    status: str = "reserved"  # reserved/available/completed/cancelled


# 内存存储（实际项目中应使用数据库）
_session_store: Dict[str, Session] = {}
_user_profile_store: Dict[str, UserProfile] = {}


def create_session(user_id: str, session_id: Optional[str] = None) -> Session:
    """创建新会话"""
    import uuid

    if session_id is None:
        session_id = str(uuid.uuid4())

    session = Session(
        session_id=session_id,
        user_id=user_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    _session_store[session_id] = session
    return session


def get_session(session_id: str) -> Optional[Session]:
    """获取会话"""
    return _session_store.get(session_id)


def add_message_to_session(
    session_id: str,
    role: MessageRole,
    content: str,
    intent: Optional[str] = None,
    entities: Optional[Dict] = None,
) -> Session:
    """添加消息到会话"""
    session = _session_store.get(session_id)
    if session is None:
        raise ValueError(f"会话 {session_id} 不存在")

    message = Message(
        role=role,
        content=content,
        timestamp=datetime.now(),
        intent=intent,
        entities=entities,
    )

    session.messages.append(message)
    session.updated_at = datetime.now()

    # 限制消息数量
    if len(session.messages) > 100:
        session.messages = session.messages[-100:]

    return session


def get_session_history(session_id: str, limit: int = 50) -> List[Message]:
    """获取会话历史"""
    session = _session_store.get(session_id)
    if session is None:
        return []

    return session.messages[-limit:]


def clear_session(session_id: str):
    """清除会话"""
    if session_id in _session_store:
        del _session_store[session_id]


def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """获取用户画像"""
    return _user_profile_store.get(user_id)


def update_user_profile(user_id: str, profile: UserProfile):
    """更新用户画像"""
    _user_profile_store[user_id] = profile


def create_user_profile(
    user_id: str,
    major: Optional[str] = None,
    grade: Optional[str] = None,
    interests: Optional[List[str]] = None,
) -> UserProfile:
    """创建用户画像"""
    profile = UserProfile(
        user_id=user_id,
        major=major,
        grade=grade,
        interests=interests or [],
        read_books=[],
        preferences={},
    )

    _user_profile_store[user_id] = profile
    return profile


def add_read_book(user_id: str, book_id: str):
    """添加已读图书"""
    profile = _user_profile_store.get(user_id)
    if profile:
        if book_id not in profile.read_books:
            profile.read_books.append(book_id)


def add_interest(user_id: str, interest: str):
    """添加兴趣标签"""
    profile = _user_profile_store.get(user_id)
    if profile and interest not in profile.interests:
        profile.interests.append(interest)


# 导出
__all__ = [
    "Message",
    "Session",
    "UserProfile",
    "BorrowRecord",
    "Reservation",
    "MessageRole",
    "create_session",
    "get_session",
    "add_message_to_session",
    "get_session_history",
    "clear_session",
    "get_user_profile",
    "update_user_profile",
    "create_user_profile",
    "add_read_book",
    "add_interest",
]
