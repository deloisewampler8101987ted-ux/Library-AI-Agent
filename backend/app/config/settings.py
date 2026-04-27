# -*- coding: utf-8 -*-
"""
API Key、知识库路径、超时配置
"""

import os


class Settings:
    """应用配置"""

    # ==================== 阿里云千问配置 ====================
    # API Key（生产环境应使用环境变量）
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "your-api-key-here")

    # 千问模型配置
    QIANWEN_MODEL: str = "qwen-turbo"  # 模型名称
    QIANWEN_TEMPERATURE: float = 0.7  # 温度参数
    QIANWEN_MAX_TOKENS: int = 2000  # 最大token数
    QIANWEN_TIMEOUT: int = 30  # 请求超时（秒）
    QIANWEN_RETRY_TIMES: int = 1  # 重试次数

    # ==================== LMS 图书馆系统配置 ====================
    LMS_API_URL: str = os.getenv("LMS_API_URL", "http://localhost:8080/api")
    LMS_API_KEY: str = os.getenv("LMS_API_KEY", "your-lms-api-key")

    # 借阅配置
    MAX_BORROW_COUNT: int = 5  # 最大借阅数量
    BORROW_DAYS: int = 30  # 借阅天数
    RENEW_TIMES: int = 1  # 续借次数
    RESERVE_DAYS: int = 3  # 预约保留天数
    OVERDUE_FEE_PER_DAY: float = 0.5  # 逾期费用（元/天）

    # ==================== 知识库配置 ====================
    # 知识库根目录
    KNOWLEDGE_BASE_PATH: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "docs"
    )

    # 向量数据库配置
    VECTOR_STORE_TYPE: str = "simple"  # simple/chroma/milvus
    VECTOR_DIMENSION: int = 1536  # 向量维度
    TOP_K: int = 5  # 检索返回数量

    # ==================== 会话配置 ====================
    # 会话上下文保留时长（分钟）
    SESSION_CONTEXT_TIMEOUT: int = 30

    # 对话历史保留天数
    HISTORY_RETENTION_DAYS: int = 30

    # ==================== 前端配置 ====================
    # CORS 配置
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # ==================== 系统配置 ====================
    # 日志级别
    LOG_LEVEL: str = "INFO"

    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./library_ai.db")

    # 缓存配置
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 缓存时间（秒）

    @classmethod
    def get_knowledge_base_path(cls) -> str:
        """获取知识库路径"""
        return cls.KNOWLEDGE_BASE_PATH

    @classmethod
    def get_dashscope_api_key(cls) -> str:
        """获取千问 API Key"""
        return cls.DASHSCOPE_API_KEY

    @classmethod
    def validate(cls) -> bool:
        """验证配置完整性"""
        if not cls.DASHSCOPE_API_KEY or cls.DASHSCOPE_API_KEY == "your-api-key-here":
            print("警告：未配置 DASHSCOPE_API_KEY")
            return False
        return True


# 全局配置实例
settings = Settings()
