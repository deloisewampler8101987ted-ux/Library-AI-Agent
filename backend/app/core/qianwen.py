# -*- coding: utf-8 -*-
"""
阿里云千问 SDK 初始化与调用封装
基于 DashScope API 实现流式响应
"""

from typing import Any, AsyncGenerator, Dict, Optional

from dashscope import Generation
from dashscope.core.streaming import StreamingChatCompletion


class QianwenClient:
    """千问模型客户端"""

    def __init__(self, api_key: str, model: str = "qwen-turbo"):
        """
        初始化千问客户端

        Args:
            api_key: 阿里云 DashScope API Key
            model: 模型名称，默认 qwen-turbo
        """
        self.api_key = api_key
        self.model = model
        self._client = Generation()

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: Optional[list] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> Dict[str, Any]:
        """
        同步调用千问模型（非流式）

        Args:
            message: 用户消息
            system_prompt: 系统提示词
            history: 对话历史 [[role, content], ...]
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            Dict: 包含 response 和 usage 信息
        """
        messages = self._build_messages(message, system_prompt, history)

        response = self._client.call(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format="message",
        )

        if response.status_code == 200:
            return {
                "success": True,
                "content": response.output.choices[0].message.content,
                "usage": response.usage,
                "request_id": response.request_id,
            }
        else:
            return {
                "success": False,
                "error": response.message,
                "code": response.status_code,
            }

    async def chat_stream(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: Optional[list] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncGenerator[str, None]:
        """
        流式调用千问模型

        Args:
            message: 用户消息
            system_prompt: 系统提示词
            history: 对话历史
            temperature: 温度参数
            max_tokens: 最大生成token数

        Yields:
            str: 流式输出的文本片段
        """
        messages = self._build_messages(message, system_prompt, history)

        response = self._client.call(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            result_format="message",
            stream=True,
        )

        if isinstance(response, StreamingChatCompletion):
            for chunk in response:
                if chunk.status_code == 200:
                    content = chunk.output.choices[0].message.content
                    if content:
                        yield content
                else:
                    yield f"[ERROR] {chunk.message}"

    def chat_with_function(
        self,
        message: str,
        functions: list,
        system_prompt: Optional[str] = None,
        history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        带函数调用的千问模型调用
        用于执行特定操作（如查借阅、预约图书）

        Args:
            message: 用户消息
            functions: 函数定义列表
            system_prompt: 系统提示词
            history: 对话历史

        Returns:
            Dict: 包含 function_call 信息
        """
        messages = self._build_messages(message, system_prompt, history)

        response = self._client.call(
            model=self.model,
            messages=messages,
            functions=functions,
            result_format="message",
        )

        if response.status_code == 200:
            result = response.output.choices[0].message
            return {
                "success": True,
                "content": result.content,
                "function_call": result.function_call,
                "usage": response.usage,
            }
        else:
            return {"success": False, "error": response.message}

    def _build_messages(
        self, message: str, system_prompt: Optional[str], history: Optional[list]
    ) -> list:
        """构建消息列表"""
        messages = []

        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 添加历史对话
        if history:
            for role, content in history:
                messages.append({"role": role, "content": content})

        # 添加当前消息
        messages.append({"role": "user", "content": message})

        return messages

    def generate_recommendation_reason(
        self, book_info: Dict[str, Any], user_profile: Dict[str, Any]
    ) -> str:
        """
        生成图书推荐理由

        Args:
            book_info: 图书信息（书名、作者、出版社、简介等）
            user_profile: 用户画像（专业、年级、兴趣、借阅历史）

        Returns:
            str: 个性化推荐理由
        """
        prompt = f"""你是一个专业的图书推荐助手。请根据以下信息生成推荐理由。
        
图书信息：
- 书名：{book_info.get("title", "")}
- 作者：{book_info.get("author", "")}
- 出版社：{book_info.get("publisher", "")}
- 简介：{book_info.get("description", "")}

用户画像：
- 专业：{user_profile.get("major", "未知")}
- 年级：{user_profile.get("grade", "未知")}
- 兴趣：{", ".join(user_profile.get("interests", []))}
- 已读图书：{", ".join(user_profile.get("read_books", []))}

请生成一段简洁有力的推荐理由（50-100字），突出图书与用户需求的匹配点。"""

        result = self.chat(prompt, temperature=0.8, max_tokens=200)
        if result.get("success"):
            return result["content"]
        return "这本书值得一读"


# 全局客户端实例（单例模式）
_qianwen_client: Optional[QianwenClient] = None


def init_qianwen(api_key: str, model: str = "qwen-turbo") -> QianwenClient:
    """初始化千问客户端"""
    global _qianwen_client
    _qianwen_client = QianwenClient(api_key=api_key, model=model)
    return _qianwen_client


def get_qianwen_client() -> QianwenClient:
    """获取千问客户端实例"""
    if _qianwen_client is None:
        raise RuntimeError("千问客户端未初始化，请先调用 init_qianwen()")
    return _qianwen_client
