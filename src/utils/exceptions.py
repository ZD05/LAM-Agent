"""
自定义异常类
提供更详细的错误分类和处理
"""
from typing import Optional, Dict, Any


class LAMAgentError(Exception):
    """LAM Agent 基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}


class ConfigurationError(LAMAgentError):
    """配置错误"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key


class APIKeyError(ConfigurationError):
    """API密钥错误"""
    
    def __init__(self, api_provider: str):
        super().__init__(
            f"缺少 {api_provider} API 密钥",
            f"{api_provider.upper()}_API_KEY"
        )
        self.api_provider = api_provider


class ValidationError(LAMAgentError):
    """输入验证错误"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class BrowserError(LAMAgentError):
    """浏览器操作错误"""
    
    def __init__(self, message: str, operation: Optional[str] = None, url: Optional[str] = None):
        super().__init__(message, "BROWSER_ERROR")
        self.operation = operation
        self.url = url


class NetworkError(LAMAgentError):
    """网络相关错误"""
    
    def __init__(self, message: str, url: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message, "NETWORK_ERROR")
        self.url = url
        self.status_code = status_code


class SearchError(LAMAgentError):
    """搜索相关错误"""
    
    def __init__(self, message: str, query: Optional[str] = None, provider: Optional[str] = None):
        super().__init__(message, "SEARCH_ERROR")
        self.query = query
        self.provider = provider


class AutomationError(LAMAgentError):
    """自动化操作错误"""
    
    def __init__(self, message: str, step: Optional[str] = None, selector: Optional[str] = None):
        super().__init__(message, "AUTOMATION_ERROR")
        self.step = step
        self.selector = selector


class TimeoutError(LAMAgentError):
    """超时错误"""
    
    def __init__(self, message: str, timeout_seconds: Optional[float] = None, operation: Optional[str] = None):
        super().__init__(message, "TIMEOUT_ERROR")
        self.timeout_seconds = timeout_seconds
        self.operation = operation




















