# -*- coding: utf-8 -*-
"""
AI 聊天与咨询路由
提供流式对话、意图识别、知识库检索功能
"""

import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["聊天咨询"])


# ==================== 请求模型 ====================


class ChatRequest(BaseModel):
    """聊天请求"""

    message: str  # 用户消息
    user_id: str = "default_user"  # 用户ID
    session_id: Optional[str] = None  # 会话ID
    use_stream: bool = True  # 是否使用流式响应


class RegenerateRequest(BaseModel):
    """重新生成请求"""

    session_id: str  # 会话ID
    message: str  # 原始消息


# ==================== 聊天接口 ====================


@router.post("/send")
async def send_message(request: ChatRequest) -> Dict[str, Any]:
    """
    发送消息（非流式）

    用于简单对话场景
    """
    from backend.app.core.intent_detector import get_intent_detector
    from backend.app.core.qianwen import get_qianwen_client
    from backend.app.core.rag_engine import get_rag_engine
    from backend.app.services.library_service import get_library_service

    try:
        qianwen_client = get_qianwen_client()
        intent_detector = get_intent_detector()
        rag_engine = get_rag_engine()
        library_service = get_library_service()

        # 1. 意图识别
        intent, confidence, entities = intent_detector.detect(request.message)

        # 2. 根据意图处理请求
        response_content = ""

        if intent.value == "borrow_status":
            # 借阅状态查询
            status = library_service.get_borrow_status(request.user_id)
            response_content = _format_borrow_status(status)

        elif intent.value == "search":
            # 图书搜索
            book_title = entities.get("book_title", request.message)
            result = library_service.search_books(book_title)
            response_content = _format_search_result(result)

        elif intent.value == "reserve":
            # 预约图书
            book_title = entities.get("book_title", request.message)
            book = library_service.get_book_by_title(book_title)
            if book:
                result = library_service.reserve_book(request.user_id, book["id"])
                response_content = _format_reserve_result(result)
            else:
                response_content = f"未找到图书「{book_title}」，请确认书名是否正确"

        elif intent.value == "recommend":
            # 图书推荐
            from backend.app.services.recommend_service import get_recommend_service

            recommend_service = get_recommend_service()
            result = recommend_service.custom_recommend(request.message)
            response_content = _format_recommend_result(result)

        elif intent.value == "consult":
            # 咨询问题（知识库检索）
            retrieved_docs = rag_engine.retrieve(request.message, top_k=3)
            response_content = rag_engine.generate_answer(
                request.message, retrieved_docs, qianwen_client
            )

        else:
            # 通用对话（千问模型）
            # 检索知识库
            retrieved_docs = rag_engine.retrieve(request.message, top_k=3)

            if retrieved_docs:
                # 有相关知识库内容
                response_content = rag_engine.generate_answer(
                    request.message, retrieved_docs, qianwen_client
                )
            else:
                # 无相关知识库，直接对话
                result = qianwen_client.chat(request.message)
                if result.get("success"):
                    response_content = result["content"]
                else:
                    response_content = f"抱歉，服务暂时不可用：{result.get('error')}"

        return {
            "success": True,
            "data": {
                "message": response_content,
                "intent": intent.value,
                "confidence": confidence,
                "entities": entities,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def send_message_stream(request: ChatRequest):
    """
    发送消息（流式响应）

    用于 AI 对话场景，支持实时流式输出
    """
    from backend.app.core.intent_detector import get_intent_detector
    from backend.app.core.qianwen import get_qianwen_client
    from backend.app.core.rag_engine import get_rag_engine

    async def generate():
        try:
            qianwen_client = get_qianwen_client()
            intent_detector = get_intent_detector()
            rag_engine = get_rag_engine()

            # 1. 意图识别
            intent, confidence, entities = intent_detector.detect(request.message)

            # 2. 根据意图处理
            if intent.value in ["search", "reserve", "recommend", "borrow_status"]:
                # 非对话意图，返回结构化结果
                result = await handle_structured_intent(
                    intent, request.message, entities, request.user_id
                )
                yield f"data: {json.dumps(result, ensure_ascii=False)}\n\n"

            else:
                # 对话意图，流式输出
                retrieved_docs = rag_engine.retrieve(request.message, top_k=3)

                if retrieved_docs:
                    # 有知识库内容
                    context = rag_engine._build_context(retrieved_docs)
                    prompt = f"""基于以下知识库内容回答用户问题。

知识库内容：
{context}

用户问题：{request.message}

请根据知识库内容回答："""
                else:
                    prompt = request.message

                # 流式调用千问
                async for chunk in qianwen_client.chat_stream(
                    message=prompt, temperature=0.7, max_tokens=2000
                ):
                    yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def handle_structured_intent(
    intent, message: str, entities: Dict, user_id: str
) -> Dict:
    """处理结构化意图"""
    from backend.app.services.library_service import get_library_service
    from backend.app.services.recommend_service import get_recommend_service

    library_service = get_library_service()

    if intent.value == "borrow_status":
        status = library_service.get_borrow_status(user_id)
        return {"type": "borrow_status", "content": _format_borrow_status(status)}

    elif intent.value == "search":
        book_title = entities.get("book_title", message)
        result = library_service.search_books(book_title)
        return {"type": "book_list", "content": _format_search_result(result)}

    elif intent.value == "reserve":
        book_title = entities.get("book_title", message)
        book = library_service.get_book_by_title(book_title)
        if book:
            result = library_service.reserve_book(user_id, book["id"])
            return {"type": "reserve", "content": _format_reserve_result(result)}
        return {"type": "error", "content": f"未找到图书「{book_title}」"}

    elif intent.value == "recommend":
        recommend_service = get_recommend_service()
        result = recommend_service.custom_recommend(message)
        return {"type": "recommend", "content": _format_recommend_result(result)}

    return {"type": "text", "content": "无法处理该请求"}


# ==================== 辅助函数 ====================


def _format_borrow_status(status: Dict) -> str:
    """格式化借阅状态"""
    data = status.get("data", {})
    count = data.get("borrowing_count", 0)
    overdue = data.get("overdue_count", 0)
    records = data.get("records", [])

    if count == 0:
        return "你当前没有借阅图书，快去借几本喜欢的书吧！"

    msg = f"你当前有 {count} 本未归还图书"
    if overdue > 0:
        msg += f"，其中 {overdue} 本已逾期，请尽快归还！\n\n"
    else:
        msg += "。\n\n"

    msg += "借阅明细：\n"
    for record in records:
        title = record.get("book_title", "")
        due = record.get("due_date", "")
        is_overdue = record.get("is_overdue", False)
        status_mark = "⚠️已逾期" if is_overdue else f"到期日：{due}"
        msg += f"• 《{title}》 - {status_mark}\n"

    return msg


def _format_search_result(result: Dict) -> str:
    """格式化搜索结果"""
    data = result.get("data", {})
    books = data.get("list", [])

    if not books:
        return "未找到相关图书，请尝试其他关键词"

    msg = f"找到 {len(books)} 本相关图书：\n\n"
    for book in books:
        msg += f"《{book.get('title', '')}》\n"
        msg += (
            f"  作者：{book.get('author', '')} | 出版社：{book.get('publisher', '')}\n"
        )
        msg += f"  馆藏：{book.get('location', '')} | 可借：{book.get('available', 0)}/{book.get('total', 0)}\n"
        msg += f"  简介：{book.get('description', '')}\n\n"

    return msg


def _format_reserve_result(result: Dict) -> str:
    """格式化预约结果"""
    if result.get("success"):
        data = result.get("data", {})
        return f"预约成功！《{data.get('book_title', '')}》已为你预留，请在3天内前往图书馆借阅。"
    else:
        return f"预约失败：{result.get('message', '未知错误')}"


def _format_recommend_result(result: Dict) -> str:
    """格式化推荐结果"""
    data = result.get("data", {})
    books = data.get("list", [])
    category_name = data.get("category_name", "推荐")

    if not books:
        return "暂无推荐图书"

    msg = f"为你推荐「{category_name}」相关图书：\n\n"
    for book in books[:5]:
        msg += f"《{book.get('title', '')}》 - {book.get('author', '')}\n"
        msg += f"  推荐理由：{book.get('recommend_reason', '')}\n\n"

    return msg


# ==================== FAQ 接口 ====================


@router.get("/faq")
async def get_faq():
    """获取常见问题列表"""
    from backend.app.core.rag_engine import get_rag_engine

    try:
        rag_engine = get_rag_engine()
        faqs = rag_engine.get_faq()

        return {"success": True, "data": faqs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/faq/{faq_id}")
async def get_faq_detail(faq_id: int):
    """获取FAQ详情"""
    from backend.app.core.rag_engine import get_rag_engine

    try:
        rag_engine = get_rag_engine()
        faqs = rag_engine.get_faq()

        for faq in faqs:
            if faq.get("id") == faq_id:
                return {"success": True, "data": faq}

        raise HTTPException(status_code=404, detail="FAQ不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 会话管理 ====================


@router.post("/session/create")
async def create_session(user_id: str = "default_user"):
    """创建新会话"""
    import uuid

    session_id = str(uuid.uuid4())

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": None,  # 可添加时间戳
        },
    }


@router.get("/history/{session_id}")
async def get_session_history(session_id: str):
    """获取会话历史"""
    # 实际实现中应从数据库读取
    return {"success": True, "data": {"session_id": session_id, "messages": []}}
