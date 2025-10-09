"""输入验证和安全检查工具"""
import re
from typing import Optional
from urllib.parse import urlparse
from .exceptions import ValidationError, ConfigurationError


def validate_query(query: str) -> str:
    """验证用户查询"""
    if not query or not query.strip():
        raise ValidationError("查询不能为空", field="query")
    
    query = query.strip()
    
    # 检查长度
    if len(query) > 1000:
        raise ValidationError("查询长度不能超过1000个字符", field="query")
    
    # 检查是否包含恶意内容（简单检查）
    malicious_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'onload\s*=',
        r'onerror\s*=',
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            raise ValidationError("查询包含不安全的内容", field="query")
    
    return query


def validate_url(url: str) -> str:
    """验证URL格式和安全性"""
    if not url or not url.strip():
        raise ValidationError("URL不能为空", field="url")
    
    url = url.strip()
    
    # 解析URL
    parsed = urlparse(url)
    
    # 检查协议
    if not parsed.scheme:
        url = 'https://' + url
        parsed = urlparse(url)
    
    if parsed.scheme not in ['http', 'https']:
        raise ValidationError("只支持HTTP和HTTPS协议", field="url")
    
    # 检查域名
    if not parsed.netloc:
        raise ValidationError("无效的URL格式", field="url")
    
    # 检查是否为本地地址（安全考虑）
    if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
        raise ValidationError("不允许访问本地地址", field="url")
    
    # 检查是否为私有IP地址
    if parsed.hostname and is_private_ip(parsed.hostname):
        raise ValidationError("不允许访问私有IP地址", field="url")
    
    return url


def is_private_ip(hostname: str) -> bool:
    """检查是否为私有IP地址"""
    try:
        import ipaddress
        ip = ipaddress.ip_address(hostname)
        return ip.is_private
    except ValueError:
        # 不是IP地址，可能是域名
        return False


def sanitize_text(text: str, max_length: int = 10000) -> str:
    """清理文本内容"""
    if not text:
        return ""
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    # 移除潜在的恶意内容
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'vbscript:', '', text, flags=re.IGNORECASE)
    
    return text.strip()






