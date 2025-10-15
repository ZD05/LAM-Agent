# LAM-Agent 工具手册

LAM-Agent 提供67个MCP工具，涵盖网页自动化、桌面管理、游戏集成、视频操作、凭据管理、网站集成、软件集成等各个方面。

## 📋 工具分类

### 🌐 网页自动化工具 (15个)

#### 基础网页操作
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `web_automate` | 在指定网页上执行自动化操作 | `url`, `steps` | 打开网页并执行点击、输入等操作 |
| `web_fetch` | 获取网页内容 | `url`, `wait_selector` | 获取网页HTML内容 |
| `web_click` | 点击网页元素 | `url`, `selector` | 点击指定按钮或链接 |
| `web_type` | 在网页输入框中输入文本 | `url`, `selector`, `text` | 在搜索框输入关键词 |
| `web_scroll` | 滚动网页 | `url`, `direction`, `amount` | 向下滚动页面 |
| `web_wait` | 等待网页元素出现 | `url`, `selector`, `timeout` | 等待页面加载完成 |

#### 高级网页操作
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `web_screenshot` | 截取网页截图 | `url`, `selector` | 截取整个页面或指定区域 |
| `web_extract_text` | 提取网页文本内容 | `url`, `selector` | 提取文章内容 |
| `web_extract_links` | 提取网页链接 | `url`, `filter` | 提取所有外部链接 |
| `web_form_fill` | 自动填充表单 | `url`, `form_data` | 自动填写登录表单 |
| `web_cookie_manage` | 管理网页Cookie | `url`, `action`, `cookies` | 设置或获取Cookie |
| `web_local_storage` | 管理本地存储 | `url`, `action`, `data` | 设置或获取本地存储数据 |

### 🖥️ 桌面管理工具 (12个)

#### 文件管理
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `desktop_scan` | 扫描桌面文件 | `file_types` | 扫描桌面上的所有文件 |
| `desktop_search` | 搜索桌面文件 | `keyword`, `file_types` | 搜索包含关键词的文件 |
| `desktop_launch` | 启动桌面应用 | `app_name` | 启动指定的桌面应用 |
| `desktop_file_info` | 获取文件信息 | `file_path` | 获取文件的详细信息 |
| `desktop_create_shortcut` | 创建桌面快捷方式 | `target_path`, `name` | 为程序创建桌面快捷方式 |
| `desktop_organize` | 整理桌面文件 | `organization_type` | 按类型整理桌面文件 |

#### 系统操作
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `system_info` | 获取系统信息 | - | 获取操作系统和硬件信息 |
| `process_list` | 列出运行进程 | `filter` | 列出所有运行中的进程 |
| `process_kill` | 终止进程 | `process_name` | 终止指定进程 |
| `system_restart` | 重启系统 | `delay` | 延迟重启系统 |
| `system_shutdown` | 关闭系统 | `delay` | 延迟关闭系统 |
| `clipboard_manage` | 管理剪贴板 | `action`, `content` | 设置或获取剪贴板内容 |

### 🎮 Steam游戏集成工具 (9个)

#### 游戏库管理
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `steam_get_library` | 获取游戏库 | - | 获取所有已安装游戏列表 |
| `steam_get_game_details` | 获取游戏详情 | `appid` | 获取指定游戏的详细信息 |
| `steam_get_recent_activity` | 获取最近活动 | - | 获取最近的游戏活动记录 |
| `steam_get_friend_comparison` | 获取好友对比 | - | 与好友的游戏库对比 |
| `steam_analyze_gaming_habits` | 分析游戏习惯 | - | 分析用户的游戏使用习惯 |
| `steam_get_recommendations` | 获取游戏推荐 | `genre` | 获取个性化游戏推荐 |

#### 游戏操作
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `steam_download_game` | 下载游戏 | `appid` | 下载指定的游戏 |
| `steam_uninstall_game` | 卸载游戏 | `appid` | 卸载指定的游戏 |
| `steam_open_store` | 打开Steam商店 | - | 打开Steam商店页面 |

### 📺 Bilibili视频操作工具 (10个)

#### 视频搜索和播放
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `bilibili_search_play` | 搜索并播放视频 | `up_name`, `keep_open_seconds` | 搜索UP主并播放第一个视频 |
| `bilibili_search_videos` | 搜索视频 | `keyword`, `page` | 搜索指定关键词的视频 |
| `bilibili_play_video` | 播放视频 | `video_url` | 直接播放指定视频 |
| `bilibili_get_video_info` | 获取视频信息 | `video_id` | 获取视频的详细信息 |
| `bilibili_get_comments` | 获取视频评论 | `video_id`, `page` | 获取视频的评论列表 |

#### 用户和频道
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `bilibili_open_up` | 打开UP主页面 | `up_name` | 打开指定UP主的主页 |
| `bilibili_get_user_profile` | 获取用户资料 | `user_id` | 获取用户的详细资料 |
| `bilibili_get_user_videos` | 获取用户视频 | `user_id`, `page` | 获取用户发布的视频列表 |
| `bilibili_follow_user` | 关注用户 | `user_id` | 关注指定的用户 |
| `bilibili_get_trending` | 获取热门视频 | `category` | 获取指定分类的热门视频 |

### 🔐 凭据管理工具 (10个)

#### 凭据存储
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `credential_add` | 添加凭据 | `website`, `username`, `password` | 添加网站登录凭据 |
| `credential_get` | 获取凭据 | `website` | 获取指定网站的凭据 |
| `credential_update` | 更新凭据 | `website`, `username`, `password` | 更新现有凭据 |
| `credential_delete` | 删除凭据 | `website` | 删除指定网站的凭据 |
| `credential_list` | 列出所有凭据 | - | 列出所有保存的凭据 |

#### 自动填充
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `credential_auto_fill` | 自动填充凭据 | `website` | 在指定网站自动填充登录信息 |
| `credential_export` | 导出凭据 | `format` | 导出凭据到文件 |
| `credential_import` | 导入凭据 | `file_path` | 从文件导入凭据 |
| `credential_backup` | 备份凭据 | `backup_path` | 创建凭据备份 |
| `credential_restore` | 恢复凭据 | `backup_path` | 从备份恢复凭据 |

### 🌐 网站集成工具 (15个)

#### 电商平台
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `jd_search_products` | 京东商品搜索 | `keyword`, `page` | 在京东搜索商品 |
| `jd_get_product_info` | 获取京东商品信息 | `product_id` | 获取商品详细信息 |
| `taobao_search_products` | 淘宝商品搜索 | `keyword`, `page` | 在淘宝搜索商品 |
| `taobao_get_product_info` | 获取淘宝商品信息 | `product_id` | 获取商品详细信息 |
| `pdd_search_products` | 拼多多商品搜索 | `keyword`, `page` | 在拼多多搜索商品 |
| `pdd_get_product_info` | 获取拼多多商品信息 | `product_id` | 获取商品详细信息 |

#### 地图服务
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `amap_search_location` | 高德地图位置搜索 | `keyword` | 搜索指定位置 |
| `amap_get_route` | 获取路线规划 | `start`, `end`, `mode` | 规划出行路线 |
| `amap_get_nearby` | 获取附近地点 | `location`, `type` | 查找附近的餐厅、商店等 |

#### 短视频平台
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `douyin_search_videos` | 抖音视频搜索 | `keyword` | 在抖音搜索视频 |
| `douyin_get_video_info` | 获取抖音视频信息 | `video_id` | 获取视频详细信息 |
| `kuaishou_search_videos` | 快手视频搜索 | `keyword` | 在快手搜索视频 |
| `kuaishou_get_video_info` | 获取快手视频信息 | `video_id` | 获取视频详细信息 |

#### 通用网站
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `website_open` | 打开网站 | `url` | 打开指定网站 |
| `website_summarize` | 网站内容总结 | `url` | 总结网站主要内容 |

### 💻 软件集成工具 (6个)

#### 办公软件
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `wps_launch` | 启动WPS Office | - | 启动WPS Office |
| `wps_open_document` | 打开WPS文档 | `file_path` | 打开指定文档 |
| `wps_create_document` | 创建WPS文档 | `doc_type` | 创建新的文档 |

#### 社交软件
| 工具名称 | 功能描述 | 参数 | 示例 |
|---------|---------|------|------|
| `wechat_launch` | 启动微信 | - | 启动微信应用 |
| `wechat_send_message` | 发送微信消息 | `contact`, `message` | 发送消息给指定联系人 |
| `qq_launch` | 启动QQ | - | 启动QQ应用 |

## 🛠️ 工具使用指南

### 1. 工具调用方式

#### 通过自然语言
```
用户: "帮我打开京东搜索手机"
系统: 自动识别并调用 jd_search_products 工具
```

#### 通过MCP协议
```python
# 直接调用MCP工具
result = await mcp_client.call_tool("jd_search_products", {
    "keyword": "手机",
    "page": 1
})
```

### 2. 参数说明

#### 通用参数
- `timeout`: 操作超时时间（秒）
- `retry_count`: 重试次数
- `headless`: 是否无头模式运行

#### 网站相关参数
- `url`: 目标网站URL
- `selector`: CSS选择器
- `wait_time`: 等待时间（秒）

#### 文件相关参数
- `file_path`: 文件路径
- `file_type`: 文件类型
- `encoding`: 文件编码

### 3. 返回值格式

所有工具都返回统一的JSON格式：

```json
{
    "success": true,
    "message": "操作成功",
    "data": {
        // 具体数据
    },
    "method": "tool_name",
    "timestamp": "2025-01-12T10:30:00Z"
}
```

### 4. 错误处理

#### 错误格式
```json
{
    "success": false,
    "error": "错误描述",
    "error_code": "ERROR_CODE",
    "details": {
        // 错误详情
    }
}
```

#### 常见错误码
- `TOOL_NOT_FOUND`: 工具不存在
- `INVALID_PARAMETERS`: 参数无效
- `EXECUTION_FAILED`: 执行失败
- `TIMEOUT`: 操作超时
- `PERMISSION_DENIED`: 权限不足

## 🔧 工具扩展

### 1. 创建自定义工具

```python
from src.mcp.core.base import BaseToolHandler

class CustomTool(BaseToolHandler):
    """自定义工具"""
    
    async def handle(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具逻辑"""
        try:
            # 工具逻辑
            result = await self._execute_logic(args)
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
```

### 2. 注册自定义工具

```python
# 在工具注册器中添加
def register_custom_tools(self):
    """注册自定义工具"""
    self.register_tool(MCPTool(
        name="custom_tool",
        description="自定义工具描述",
        input_schema={
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            }
        },
        handler=CustomTool().handle
    ))
```

### 3. 工具测试

```python
# 测试自定义工具
async def test_custom_tool():
    tool = CustomTool()
    result = await tool.handle({"param1": "value1"})
    assert result["success"] == True
```

## 📊 工具统计

### 按类别统计
- 网页自动化: 15个工具
- 桌面管理: 12个工具
- Steam游戏: 9个工具
- Bilibili视频: 10个工具
- 凭据管理: 10个工具
- 网站集成: 15个工具
- 软件集成: 6个工具

### 按功能统计
- 搜索功能: 25个工具
- 操作功能: 20个工具
- 信息获取: 15个工具
- 管理功能: 7个工具

## 🚀 最佳实践

### 1. 工具选择
- 优先使用专门的工具而不是通用工具
- 根据具体需求选择合适的工具
- 考虑工具的稳定性和成功率

### 2. 参数优化
- 提供足够的参数信息
- 使用合适的超时时间
- 设置合理的重试次数

### 3. 错误处理
- 检查返回值的success字段
- 处理常见的错误情况
- 提供用户友好的错误信息

### 4. 性能优化
- 避免频繁调用相同工具
- 使用缓存机制
- 合理设置并发数量

---

**LAM-Agent 的67个工具为您提供了强大的自动化能力，让桌面操作变得更加智能和高效！**


