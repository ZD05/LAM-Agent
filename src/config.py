from pydantic_settings import BaseSettings
from typing import Optional, List
from .utils.exceptions import APIKeyError


class Settings(BaseSettings):
    # DeepSeek API配置
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"
    
    # 兼容性配置（保持向后兼容）
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    
    # 其他配置
    langsmith_tracing: bool = False
    langsmith_api_key: Optional[str] = None
    lam_agent_model: str = "deepseek-chat"
    lam_browser_headless: bool = True
    use_deepseek: bool = True  # 是否使用DeepSeek

    # 对部分网站启用纯鼠标操作模式（不修改DOM、不注入脚本、不使用iframe方案）
    mouse_only_sites: List[str] = [
        "bilibili.com",
        "www.bilibili.com",
        "m.bilibili.com",
        # 可按需添加：优酷、爱奇艺等对脚本更敏感的网站
        "youku.com",
        "iqiyi.com",
    ]

    class Config:
        # 启用 .env 加载，使用 UTF-8 编码；空值忽略
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_ignore_empty = True


settings = Settings()


def validate_settings() -> None:
    """验证设置配置"""
    if settings.use_deepseek and not settings.deepseek_api_key:
        raise APIKeyError("DeepSeek")
    elif not settings.use_deepseek and not settings.openai_api_key:
        raise APIKeyError("OpenAI")

