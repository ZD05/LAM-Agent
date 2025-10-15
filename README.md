# LAM-Agent 智能桌面助手

一个基于大语言模型的智能桌面助手，支持自然语言交互、网页自动化、Steam游戏操作、Bilibili视频操作、凭据管理等功能。现已完成 MCP (Model Context Protocol) 协议集成。

## 🚀 核心功能

- **智能对话**: 支持多种大语言模型，自然语言交互
- **网页自动化**: 基于Playwright的浏览器自动化操作
- **Steam集成**: 游戏库管理、下载、卸载、智能启动
- **Bilibili操作**: 视频搜索、播放、UP主页面访问
- **桌面管理**: 文件扫描、搜索、应用程序启动
- **凭据管理**: 密码存储、自动填充、安全加密
- **网站集成**: 京东、淘宝、拼多多、高德地图等
- **桌面软件**: WPS Office、微信、QQ等软件集成
- **统一UI**: ChatGPT风格现代化界面，侧边栏导航设计

## 📊 功能统计

- **总工具数量**: 67个MCP工具
- **支持网站**: 10+个主流网站
- **桌面软件**: 3个常用软件
- **技术特性**: MCP协议、异步处理、错误处理、日志记录
- **代码架构**: 模块化设计、基类继承、统一接口

## 🚀 快速开始

### 1. 环境配置
```bash
# 克隆项目
git clone <repository-url>
cd LAM-Agent

# 安装依赖
pip install -r requirements.txt

# 设置环境变量（可放入 .env 文件）
export DEEPSEEK_API_KEY="your_api_key"          # 或 OPENAI_API_KEY
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export LAM_AGENT_MODEL="deepseek-chat"
export USE_DEEPSEEK="true"                       # false 则使用 OpenAI
export LAM_BROWSER_CHANNEL="msedge"              # 默认通过 Playwright 驱动系统 Edge
export LAM_BROWSER_EXECUTABLE="C:/Path/to/msedge.exe"  # 可选：强制指定 Edge 路径
```

### 2. 启动应用
```bash
# 启动图形界面（默认）
python main.py

# 命令行模式
python main.py --cli "你的问题"

# 启动API服务（FastAPI + Uvicorn）
python main.py --api

# 显示帮助
python main.py --help
```

### 3. 基本使用
1. **智能对话**: 在底部输入框中输入自然语言指令
2. **工具面板**: 使用侧边栏的"工具面板"按钮
3. **凭据管理**: 点击侧边栏的"凭据管理"按钮
4. **对话历史**: 在侧边栏查看和管理对话历史

## 📋 主要工具

### Steam集成 (9个工具)
- `steam_get_library` - 获取游戏库
- `steam_download_game` - 下载游戏
- `steam_uninstall_game` - 卸载游戏
- `steam_open_store` - 打开Steam商店
- 更多Steam相关工具...

### Bilibili操作 (10个工具)
- `bilibili_search_play` - 搜索并播放视频
- `bilibili_open_up` - 打开UP主页面
- `bilibili_get_user_profile` - 获取用户资料
- 更多Bilibili相关工具...

### 凭据管理 (10个工具)
- `credential_add` - 添加凭据
- `credential_get` - 获取凭据
- `credential_auto_fill` - 自动填充
- 更多凭据管理工具...

### 网站集成 (15个工具)
- `website_open` - 打开网站
- `jd_search_products` - 京东搜索商品
- `taobao_search_products` - 淘宝搜索商品
- 更多网站集成工具...

## 🏗️ 代码架构

### 模块化设计
- **基础集成类**: `BaseIntegration`、`ECommerceIntegration`、`VideoPlatformIntegration`
- **软件集成基类**: `BaseSoftwareIntegration`、`OfficeSoftwareIntegration`、`SocialSoftwareIntegration`
- **MCP处理器基类**: `BaseToolHandler`、`BaseIntegrationHandler`
- **统一错误处理**: 标准化的异常处理和日志记录

### 代码组织
```
src/
├── tools/                    # 工具模块
│   ├── base_integration.py   # 网站集成基类
│   ├── base_software_integration.py  # 软件集成基类
│   ├── website_integration.py        # 网站集成实现
│   └── desktop_software_integration.py  # 软件集成实现
├── mcp/                      # MCP协议模块
│   ├── core/                 # 核心基础类
│   ├── handlers/             # 处理器模块
│   │   └── base_handler.py   # 处理器基类
│   └── registry/             # 工具注册
└── ui/                       # 用户界面
```

## 🎨 用户界面

### 统一UI设计
- **深色主题**: ChatGPT风格的现代化界面
- **双界面集成**: 主界面和凭据管理器
- **顶部导航**: 便捷的界面切换
- **响应式布局**: 自适应窗口大小

## 🔧 高级配置

### Steam配置
```bash
export STEAM_API_KEY="your_steam_api_key"
export STEAM_USER_ID="your_steam_user_id"
```

### 数据库配置
- **凭据数据库**: 自动创建SQLite数据库
- **数据位置**: `src/database/credentials.db`
- **备份恢复**: 支持导入导出功能

## 📚 详细文档

- **[完整指南](LAM_AGENT_FINAL_GUIDE.md)**: 详细的功能说明和使用指南，包含所有67个工具的完整说明

## 🛡️ 安全特性

- **密码安全**: Base64编码存储，按需解密
- **数据保护**: 本地SQLite存储，用户控制
- **隐私保护**: 无网络传输，透明操作

## 🔮 未来规划

- **功能增强**: 更多网站支持、移动端适配
- **技术优化**: 性能优化、内存优化、启动优化
- **用户体验**: 主题系统、快捷键、语音控制

## 📞 技术支持

- **问题反馈**: GitHub Issues
- **文档更新**: 持续更新使用文档
- **社区支持**: 用户社区交流

---

**LAM-Agent** - 让智能助手更智能，让桌面操作更简单！

*最后更新: 2025-01-12*