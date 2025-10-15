# LAM-Agent 最终完整指南

## 🎯 项目概述

LAM-Agent 是一个基于大语言模型的智能桌面助手，支持自然语言交互、网页自动化、桌面文件管理、Steam游戏操作、Bilibili视频操作、凭据管理、网站集成、桌面软件集成等功能。现已完成 MCP (Model Context Protocol) 协议集成，提供标准化的工具接口。

## 🚀 核心功能

### 1. 智能对话系统
- **多模型支持**: DeepSeek、OpenAI等大语言模型
- **自然语言理解**: 智能命令识别和参数提取
- **实时建议**: 命令建议和自动补全
- **对话历史**: 完整的对话记录管理

### 2. 网页自动化
- **浏览器控制**: 基于Playwright的自动化操作
- **智能操作**: 搜索、点击、输入、滚动等
- **错误处理**: 智能等待和异常处理
- **多网站支持**: 京东、淘宝、拼多多、高德地图等

### 3. 桌面文件管理
- **文件扫描**: 扫描桌面文件和快捷方式
- **智能搜索**: 快速定位桌面文件
- **应用启动**: 启动桌面应用程序
- **文件类型识别**: 支持多种文件格式

### 4. Steam游戏集成
- **游戏库管理**: 获取游戏库和统计信息
- **游戏操作**: 下载、卸载、启动游戏
- **智能启动**: 安全启动Steam，避免黑屏
- **路径检测**: 全面查找Steam安装路径

### 5. Bilibili视频操作
- **视频搜索**: 搜索UP主和视频内容
- **自动播放**: 智能播放视频
- **用户页面**: 进入UP主主页
- **反爬检测**: 支持鼠标点击操作

### 6. 凭据管理系统
- **密码存储**: SQLite数据库加密存储
- **自动填充**: 网站和应用自动填充
- **UI管理**: 图形化凭据管理界面
- **安全特性**: 密码加密和访问控制

### 7. 网站集成
- **通用网站**: 支持任意网站访问和信息总结
- **电商平台**: 京东、淘宝、拼多多商品搜索
- **地图服务**: 高德地图位置搜索和路线规划
- **短视频平台**: 抖音、快手视频搜索

### 8. 桌面软件集成
- **WPS Office**: 文档打开和创建
- **微信/QQ**: 消息发送和聊天管理
- **通用启动**: 支持各种桌面软件

## 🛠️ 技术架构

### MCP协议集成
- **标准化接口**: 遵循MCP协议标准
- **工具转换**: 67个工具全部MCP化
- **向后兼容**: 保持原有功能不变
- **异步支持**: 支持异步工具调用

### 统一UI系统
- **现代化设计**: ChatGPT风格深色主题
- **双界面集成**: 主界面和凭据管理器
- **响应式布局**: 自适应窗口大小
- **顶部导航**: 便捷的界面切换

### 模块化架构
```
LAM-Agent
├── src/
│   ├── agent/           # 智能代理核心
│   ├── tools/           # 工具模块
│   │   ├── browser.py   # 网页自动化
│   │   ├── bilibili.py  # B站操作
│   │   ├── steam_integration.py  # Steam集成
│   │   ├── desktop_launcher.py   # 桌面启动
│   │   ├── website_integration.py # 网站集成
│   │   ├── desktop_software_integration.py # 桌面软件
│   │   └── auto_fill_integration.py # 自动填充
│   ├── mcp/             # MCP协议实现
│   ├── database/        # 数据库模块
│   └── ui/              # 用户界面
├── requirements.txt     # 依赖包
└── README.md           # 项目说明
```

## 📋 完整工具列表 (67个)

### 网页操作类 (7个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `web_automate` | 网页自动化操作 | url, steps |
| `web_search` | 网页搜索 | query, max_results |
| `page_fetch` | 获取网页内容 | url |
| `site_search` | 网站内搜索 | url, keyword |
| `browse_product` | 浏览商品 | product_url |
| `play_video_generic` | 播放视频 | video_url |
| `add_to_cart` | 添加到购物车 | product_url |

### Steam集成类 (9个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `steam_get_library` | 获取游戏库 | 无 |
| `steam_get_recent_activity` | 获取最近活动 | 无 |
| `steam_get_game_details` | 获取游戏详情 | appid |
| `steam_get_friend_comparison` | 朋友比较 | 无 |
| `steam_open_store` | 打开Steam商店 | game_name (可选) |
| `steam_analyze_habits` | 分析游戏习惯 | 无 |
| `steam_get_recommendations` | 获取游戏推荐 | 无 |
| `steam_download_game` | 下载游戏 | appid |
| `steam_uninstall_game` | 卸载游戏 | appid |

### Bilibili操作类 (10个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `bilibili_search_play` | 搜索并播放视频 | up_name, keep_open_seconds |
| `bilibili_open_up` | 打开UP主页面 | up_name |
| `bilibili_get_user_profile` | 获取用户资料 | uid |
| `bilibili_search_videos` | 搜索视频 | keyword, page |
| `bilibili_get_video_details` | 获取视频详情 | bvid |
| `bilibili_get_user_videos` | 获取用户视频 | uid, page |
| `bilibili_get_following_list` | 获取关注列表 | uid, page |
| `bilibili_get_favorites` | 获取收藏 | uid, page |
| `bilibili_get_watch_later` | 获取稍后再看 | uid, page |
| `bilibili_get_user_statistics` | 获取用户统计 | uid |

### 桌面管理类 (2个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `desktop_scan` | 扫描桌面文件 | file_type |
| `desktop_launch` | 启动桌面文件 | file_name |

### 凭据管理类 (10个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `credential_add` | 添加凭据 | username, account, password, application |
| `credential_get` | 获取凭据 | credential_id |
| `credential_list` | 列出凭据 | category (可选) |
| `credential_update` | 更新凭据 | credential_id, ... |
| `credential_delete` | 删除凭据 | credential_id |
| `credential_search` | 搜索凭据 | keyword |
| `credential_auto_fill` | 自动填充 | application, website_url |
| `credential_export` | 导出凭据 | file_path (可选) |
| `credential_import` | 导入凭据 | file_path |
| `credential_categories` | 获取分类 | 无 |

### 自动填充类 (6个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `auto_fill_website` | 网站自动填充 | url |
| `auto_fill_application` | 应用自动填充 | application |
| `smart_auto_fill` | 智能自动填充 | identifier, identifier_type |
| `get_suggested_credentials` | 获取建议凭据 | application, limit |
| `validate_credential_format` | 验证凭据格式 | username, password, application |
| `get_auto_fill_statistics` | 获取统计信息 | 无 |

### 网站集成类 (15个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `website_open` | 打开网站 | url |
| `website_search` | 搜索网站 | url, keyword |
| `website_summary` | 网站摘要 | url |
| `jd_search_products` | 京东搜索商品 | keyword |
| `jd_get_product_info` | 获取京东商品信息 | product_id |
| `taobao_search_products` | 淘宝搜索商品 | keyword |
| `taobao_get_product_info` | 获取淘宝商品信息 | product_id |
| `amap_search_location` | 高德搜索地点 | keyword |
| `amap_get_route` | 高德获取路线 | start, end |
| `pdd_search_products` | 拼多多搜索商品 | keyword |
| `pdd_get_product_info` | 获取拼多多商品信息 | product_id |
| `douyin_search_videos` | 抖音搜索视频 | keyword |
| `douyin_get_video_info` | 获取抖音视频信息 | video_id |
| `kuaishou_search_videos` | 快手搜索视频 | keyword |
| `kuaishou_get_video_info` | 获取快手视频信息 | video_id |

### 桌面软件类 (9个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `software_launch` | 启动软件 | software_name |
| `software_info` | 获取软件信息 | software_name |
| `software_list` | 列出软件 | 无 |
| `wps_open_document` | WPS打开文档 | document_path |
| `wps_create_document` | WPS创建文档 | document_name |
| `wechat_send_message` | 微信发送消息 | contact, message |
| `wechat_open_chat` | 微信打开聊天 | contact |
| `qq_send_message` | QQ发送消息 | contact, message |
| `qq_open_chat` | QQ打开聊天 | contact |

### 通用工具类 (5个)
| 工具名称 | 描述 | 参数 |
|---------|------|------|
| `nl_step_execute` | 自然语言步骤执行 | steps |
| `nl_automate` | 自然语言自动化 | instruction |
| `get_weather` | 获取天气 | city |
| `calculate` | 数学计算 | expression |
| `translate` | 翻译文本 | text, target_lang, source_lang |

## 🎮 Steam集成详细说明

### Steam功能特点
- **游戏库管理**: 获取所有游戏信息和游戏时长统计
- **活动追踪**: 查看最近游戏活动和当前正在玩的游戏
- **成就系统**: 获取游戏详细信息和成就数据
- **朋友比较**: 与朋友比较游戏库并获得推荐
- **习惯分析**: 分析游戏习惯和偏好
- **智能推荐**: 基于游戏库生成个性化推荐

### Steam配置
```bash
# Steam API配置
export STEAM_API_KEY="your_steam_api_key"
export STEAM_USER_ID="your_steam_user_id"
```

### Steam智能启动逻辑
1. **桌面快捷方式**: 优先尝试打开桌面Steam快捷方式
2. **注册表检测**: 从Windows注册表获取Steam安装路径
3. **常见路径**: 尝试常见的Steam安装路径（C、D、E盘）
4. **客户端启动**: 使用`-silent`参数启动Steam客户端
5. **浏览器备用**: 如果客户端启动失败，在浏览器中打开Steam商店
6. **游戏搜索**: 支持搜索特定游戏功能

### Steam使用示例
```python
# 获取游戏库
result = await server.call_tool("steam_get_library", {})

# 分析游戏习惯
result = await server.call_tool("steam_analyze_habits", {})

# 下载游戏
result = await server.call_tool("steam_download_game", {"appid": "730"})

# 卸载游戏
result = await server.call_tool("steam_uninstall_game", {"appid": "730"})
```

## 📺 Bilibili集成详细说明

### Bilibili功能特点
- **用户资料**: 获取用户详细资料和统计数据
- **视频搜索**: 搜索视频并获取详细信息
- **个人数据**: 访问观看历史、收藏、点赞视频、投币历史
- **关注管理**: 获取关注列表和用户上传的视频
- **收藏管理**: 浏览个人收藏和稍后再看列表
- **统计分析**: 获取用户详细统计数据

### Bilibili使用示例
```python
# 搜索视频
result = await server.call_tool("bilibili_search_videos", {
    "keyword": "Python编程",
    "pagesize": 10
})

# 获取视频详情
result = await server.call_tool("bilibili_get_video_details", {
    "bvid": "BV1xx411c7mD"
})

# 获取用户资料
result = await server.call_tool("bilibili_get_user_profile", {
    "uid": "123456"
})
```

## 🔐 凭据管理系统详细说明

### 系统架构
```
用户凭据管理系统
├── 数据库层 (credential_db.py)
│   ├── SQLite数据库存储
│   ├── 密码加密/解密
│   └── 数据操作接口
├── UI界面层 (credential_manager.py)
│   ├── Tkinter图形界面
│   ├── 凭据管理功能
│   └── 导入/导出功能
├── 自动填充层 (auto_fill_integration.py)
│   ├── 网站自动填充
│   ├── 应用自动填充
│   └── 智能识别
└── MCP集成层
    ├── 凭据数据库工具
    └── 自动填充工具
```

### 数据库设计
#### 用户凭据表 (credentials)
```sql
CREATE TABLE credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    account TEXT NOT NULL,
    password TEXT NOT NULL,
    contact TEXT,
    application TEXT NOT NULL,
    website_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    UNIQUE(account, application)
)
```

#### 应用分类表 (application_categories)
```sql
CREATE TABLE application_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 默认应用分类
| 分类名称 | 描述 | 图标 |
|----------|------|------|
| 社交软件 | 微信、QQ、微博等社交应用 | 社交 |
| 办公软件 | WPS、Office、钉钉等办公应用 | 办公 |
| 电商平台 | 淘宝、京东、拼多多等购物平台 | 电商 |
| 娱乐平台 | 抖音、快手、B站等娱乐应用 | 娱乐 |
| 金融服务 | 银行、支付、理财等金融应用 | 金融 |
| 学习平台 | 教育、培训、在线学习平台 | 学习 |
| 游戏平台 | Steam、Epic、手游等游戏平台 | 游戏 |
| 其他 | 其他类型的应用 | 其他 |

### 凭据管理使用示例
```python
# 添加凭据
result = await server.call_tool("credential_add", {
    "username": "测试用户",
    "account": "test@example.com",
    "password": "password123",
    "application": "测试应用"
})

# 自动填充
result = await server.call_tool("smart_auto_fill", {
    "identifier": "https://baidu.com",
    "identifier_type": "url"
})
```

## 🌐 网站集成详细说明

### 支持的网站
| 网站 | 域名 | 分类 | 特殊功能 |
|------|------|------|----------|
| 京东 | jd.com | 电商 | 商品搜索、商品信息 |
| 淘宝 | taobao.com | 电商 | 商品搜索、商品信息 |
| 天猫 | tmall.com | 电商 | 商品搜索、商品信息 |
| 拼多多 | pinduoduo.com | 电商 | 商品搜索、商品信息 |
| 高德地图 | amap.com | 地图 | 位置搜索、路线规划 |
| 百度 | baidu.com | 搜索 | 网页搜索、新闻搜索 |
| 知乎 | zhihu.com | 问答 | 问题搜索、答案获取 |
| 哔哩哔哩 | bilibili.com | 视频 | 视频搜索、视频信息 |
| 抖音 | douyin.com | 短视频 | 视频搜索、视频信息 |
| 快手 | kuaishou.com | 短视频 | 视频搜索、视频信息 |

### 网站集成使用示例
```python
# 打开网站
result = await server.call_tool("website_open", {
    "url": "https://www.baidu.com"
})

# 在京东搜索商品
result = await server.call_tool("jd_search_products", {
    "keyword": "iPhone 15",
    "page": 1
})

# 高德地图搜索位置
result = await server.call_tool("amap_search_location", {
    "keyword": "北京天安门"
})

# 抖音搜索视频
result = await server.call_tool("douyin_search_videos", {
    "keyword": "美食制作"
})
```

## 💻 桌面软件集成详细说明

### 支持的软件
| 软件 | 名称 | 分类 | 特殊功能 |
|------|------|------|----------|
| wps | WPS Office | 办公软件 | 文档打开、文档创建 |
| wechat | 微信 | 社交软件 | 消息发送、聊天打开 |
| qq | QQ | 社交软件 | 消息发送、聊天打开 |

### 软件启动优先级
1. **注册表路径**：从 Windows 注册表获取安装路径
2. **常见安装路径**：检查常见的安装目录
3. **桌面快捷方式**：查找桌面快捷方式
4. **可执行文件**：直接启动可执行文件
5. **start 命令**：使用 Windows start 命令

### 桌面软件使用示例
```python
# 启动WPS Office
result = await server.call_tool("software_launch", {
    "software_name": "wps"
})

# 打开WPS文档
result = await server.call_tool("wps_open_document", {
    "file_path": "C:/Users/Documents/test.docx"
})

# 发送微信消息
result = await server.call_tool("wechat_send_message", {
    "contact": "张三",
    "message": "你好，这是一条测试消息"
})

# 发送QQ消息
result = await server.call_tool("qq_send_message", {
    "contact": "李四",
    "message": "你好，这是一条测试消息"
})
```

## 🎨 用户界面

### 统一UI设计
- **深色主题**: ChatGPT风格的现代化界面
- **双界面集成**: 主界面和凭据管理器
- **顶部导航**: 便捷的界面切换
- **响应式布局**: 自适应窗口大小

### 主界面功能
- **智能对话**: 与AI助手自然语言交互
- **桌面操作**: 文件扫描、搜索、启动
- **网页自动化**: 浏览器操作和网站访问
- **系统集成**: MCP协议和命令识别

### 凭据管理器功能
- **凭据管理**: 添加、修改、删除、搜索
- **自动填充**: 网站和应用自动填充
- **安全存储**: 密码加密和访问控制
- **导入导出**: 数据备份和恢复

## 🚀 快速开始

### 1. 环境配置
```bash
# 克隆项目
git clone <repository-url>
cd LAM-Agent

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export DEEPSEEK_API_KEY="your_api_key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export LAM_AGENT_MODEL="deepseek-chat"
export USE_DEEPSEEK="true"
```

### 2. 启动应用
```bash
# 启动统一UI
python launch_unified_ui.py

# 或直接运行
python src/ui/unified_app.py
```

### 3. 基本使用
1. **智能对话**: 在输入框中输入自然语言指令
2. **桌面操作**: 使用侧边栏的桌面操作按钮
3. **凭据管理**: 点击顶部导航栏的"凭据管理"按钮
4. **功能切换**: 使用顶部导航栏切换界面

## 🔧 高级配置

### Steam配置
```bash
# Steam API配置
export STEAM_API_KEY="your_steam_api_key"
export STEAM_USER_ID="your_steam_user_id"
```

### 数据库配置
- **凭据数据库**: 自动创建SQLite数据库
- **数据位置**: `src/database/credentials.db`
- **备份恢复**: 支持导入导出功能

### MCP协议配置
- **服务器**: 自动启动MCP服务器
- **客户端**: 自动连接和工具发现
- **回退机制**: 自动回退到原有实现

## 📊 功能统计

### 工具数量统计
- **总工具数量**: 67个
- **网页操作类**: 7个
- **Steam集成类**: 9个
- **Bilibili操作类**: 10个
- **桌面管理类**: 2个
- **凭据管理类**: 10个
- **自动填充类**: 6个
- **网站集成类**: 15个
- **桌面软件类**: 9个
- **通用工具类**: 5个

### 技术特性
- **MCP协议**: 100%支持
- **异步处理**: 支持异步工具调用
- **错误处理**: 完善的异常处理机制
- **日志记录**: 详细的操作日志
- **类型提示**: 完整的类型注解

## 🛡️ 安全特性

### 密码安全
- **加密存储**: Base64编码存储
- **按需解密**: 仅在需要时解密
- **避免明文**: 不在日志中记录明文密码

### 数据保护
- **本地存储**: SQLite数据库本地存储
- **访问控制**: 用户权限管理
- **备份恢复**: 数据导入导出功能

### 隐私保护
- **无网络传输**: 凭据数据不传输到网络
- **用户控制**: 用户完全控制数据
- **透明操作**: 所有操作都有日志记录

## 🔮 未来规划

### 功能增强
- **更多网站支持**: 扩展网站集成功能
- **移动端适配**: 支持移动设备
- **云端同步**: 凭据数据云端同步
- **插件系统**: 支持第三方插件

### 技术优化
- **性能优化**: 提升响应速度
- **内存优化**: 减少内存使用
- **启动优化**: 加快启动时间
- **稳定性提升**: 增强系统稳定性

### 用户体验
- **主题系统**: 支持多种主题
- **快捷键**: 键盘快捷键支持
- **语音控制**: 语音指令支持
- **手势操作**: 触摸手势支持

## 📞 技术支持

### 问题反馈
- **GitHub Issues**: 提交问题和建议
- **文档更新**: 持续更新使用文档
- **社区支持**: 用户社区交流

### 开发贡献
- **代码贡献**: 欢迎提交代码
- **功能建议**: 提出新功能想法
- **文档改进**: 完善项目文档

## ⚠️ 注意事项

### Steam注意事项
1. **API 密钥**: 需要有效的 Steam API 密钥
2. **用户 ID**: 需要正确的 Steam 用户 ID
3. **隐私设置**: 某些功能需要公开的游戏库
4. **API 限制**: 遵守 Steam API 使用限制

### Bilibili注意事项
1. **登录状态**: 某些功能需要登录状态
2. **API 限制**: 遵守 Bilibili API 使用限制
3. **反爬虫**: 避免频繁请求
4. **数据隐私**: 保护用户隐私数据

### 凭据管理注意事项
1. **数据安全**: 定期备份凭据数据
2. **密码强度**: 使用强密码保护
3. **访问控制**: 限制数据访问权限
4. **更新维护**: 定期更新密码和凭据

### 网站集成注意事项
1. **网络连接**: 需要稳定的网络连接访问网站
2. **浏览器支持**: 依赖系统默认浏览器
3. **反爬虫**: 某些网站可能有反爬虫机制
4. **内容更新**: 网站内容可能随时更新

### 桌面软件注意事项
1. **软件安装**: 需要先安装相应的软件
2. **权限要求**: 某些操作可能需要管理员权限
3. **路径依赖**: 软件路径可能因安装方式而异
4. **消息发送**: 消息发送功能需要手动操作

## 🎯 使用场景

### Steam使用场景
- **游戏库管理**: 查看和管理游戏收藏
- **游戏推荐**: 获取个性化游戏推荐
- **朋友比较**: 与朋友比较游戏库
- **习惯分析**: 分析游戏使用习惯

### Bilibili使用场景
- **视频搜索**: 搜索感兴趣的视频内容
- **用户关注**: 管理关注的UP主
- **收藏管理**: 整理收藏的视频内容
- **统计分析**: 查看观看统计数据

### 凭据管理使用场景
- **密码存储**: 安全存储各种账号密码
- **自动填充**: 网站和应用自动登录
- **数据备份**: 凭据数据备份和恢复
- **分类管理**: 按应用分类管理凭据

### 网站集成使用场景
- **电商购物**: 搜索和比较商品价格
- **地图导航**: 查找位置和规划路线
- **信息搜索**: 在各大搜索引擎中查找信息
- **内容浏览**: 访问和总结网站内容

### 桌面软件使用场景
- **办公自动化**: 自动打开和创建文档
- **社交管理**: 快速启动社交软件
- **系统集成**: 与其他功能模块集成
- **工作流程**: 自动化工作流程

## 🎉 总结

LAM-Agent 现已支持完整的功能集成：

### ✅ 核心功能
- 67个MCP工具，覆盖所有主要功能
- 智能对话系统，支持自然语言交互
- 统一UI界面，现代化用户体验

### ✅ Steam集成
- 9个Steam相关工具
- 游戏库管理和统计分析
- 朋友比较和游戏推荐
- 游戏习惯分析

### ✅ Bilibili集成
- 10个Bilibili相关工具
- 用户资料和视频搜索
- 个人数据管理
- 关注和收藏管理

### ✅ 凭据管理
- 10个凭据管理工具
- 6个自动填充工具
- 安全密码存储
- 图形化界面管理

### ✅ 网站集成
- 15个网站集成工具
- 支持10+个主流网站
- 电商、地图、短视频平台
- 智能网站识别和信息提取

### ✅ 桌面软件集成
- 9个桌面软件工具
- WPS Office、微信、QQ支持
- 智能路径检测和启动
- 多种启动方式支持

### 🚀 技术优势
- **标准化接口**: 遵循 MCP 协议
- **完整集成**: 覆盖主要功能
- **错误处理**: 完善的错误处理机制
- **易于使用**: 支持自然语言指令

现在 LAM-Agent 具备了强大的智能助手能力，为用户提供全面的桌面操作和自动化功能体验！

---

**LAM-Agent** - 让智能助手更智能，让桌面操作更简单！

*最后更新: 2025-01-12*


