# LAM-Agent 智能桌面助手

一个基于大语言模型的智能桌面助手，支持自然语言交互、网页自动化、Bilibili操作和桌面文件管理。

## 🚀 功能特性

### 1. 自然语言交互
- 支持多种大语言模型（DeepSeek、OpenAI等）
- 智能命令识别和参数提取
- 实时建议和自动补全

### 2. 网页自动化
- 基于Playwright的浏览器自动化
- 支持搜索、点击、输入等操作
- 智能等待和错误处理

### 3. Bilibili操作
- 搜索UP主和视频
- 自动播放视频
- 进入UP主主页
- 支持鼠标点击操作（避免反爬检测）

### 4. 桌面文件管理
- 扫描桌面文件和快捷方式
- 智能搜索桌面文件
- 启动桌面应用程序
- 支持多种文件类型识别

### 5. 图形用户界面
- 基于Tkinter的现代化UI
- 多标签页桌面管理对话框
- 侧边栏快速操作按钮
- 实时命令建议系统

## 📁 项目结构

```
LAM-Agent/
├── src/                          # 源代码目录
│   ├── agent/                    # 智能代理
│   │   └── lam_agent.py         # 主代理类
│   ├── api/                      # API服务
│   │   └── main.py              # FastAPI服务器
│   ├── tools/                    # 工具模块
│   │   ├── bilibili.py          # Bilibili操作
│   │   ├── browser.py           # 浏览器自动化
│   │   ├── command_recognizer.py # 命令识别
│   │   ├── desktop_integration.py # 桌面集成
│   │   ├── desktop_launcher.py  # 桌面启动器
│   │   ├── search.py            # 搜索功能
│   │   └── ...                  # 其他工具
│   ├── ui/                       # 用户界面
│   │   └── main_window.py       # 主窗口
│   ├── utils/                    # 工具函数
│   └── config.py                # 配置文件
├── scripts/                      # 启动脚本
├── logs/                         # 日志文件
├── cli.py                        # 命令行接口
├── start_ui.py                   # UI启动器
├── run_with_deepseek.py         # DeepSeek启动器
└── requirements.txt              # 依赖包
```

## 🛠️ 安装和配置

### 1. 环境要求
- Python 3.8+
- Windows 10/11
- 现代浏览器（Chrome/Edge）

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置API密钥
创建 `.env` 文件并配置：
```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
LAM_AGENT_MODEL=deepseek-chat
USE_DEEPSEEK=true
```

## 🎯 使用方法

### 1. 启动UI界面
```bash
python start_ui.py
```

### 2. 命令行模式
```bash
python cli.py
```

### 3. API服务模式
```bash
python -m src.api.main
```

### 4. 使用DeepSeek模型
```bash
python run_with_deepseek.py
```

## 💡 使用示例

### 桌面管理
- "扫描桌面文件" - 扫描桌面所有文件
- "搜索桌面文件 python" - 搜索包含python的文件
- "启动桌面文件 notepad.exe" - 启动记事本

### Bilibili操作
- "搜索影视飓风" - 搜索UP主
- "播放影视飓风第一个视频" - 播放视频
- "打开影视飓风主页" - 进入UP主主页

### 网页自动化
- "搜索滕王阁序" - 在浏览器中搜索
- "点击第一个搜索结果" - 点击链接

## 🔧 配置选项

### 浏览器配置
- `HEADLESS_MODE`: 是否无头模式
- `BROWSER_TYPE`: 浏览器类型（chrome/edge）
- `TIMEOUT`: 操作超时时间

### 桌面配置
- `DESKTOP_PATH`: 桌面路径
- `SUPPORTED_EXTENSIONS`: 支持的文件扩展名

### 命令识别
- `COMMAND_PATTERNS`: 命令匹配模式
- `PARAMETER_EXTRACTION`: 参数提取规则

## 🚨 注意事项

1. **Bilibili操作**: 使用鼠标点击避免反爬检测
2. **桌面管理**: 需要管理员权限启动某些应用程序
3. **API限制**: 注意大语言模型的API调用限制
4. **浏览器兼容**: 建议使用Chrome或Edge浏览器

## 📝 开发说明

### 添加新功能
1. 在 `src/tools/` 中创建新工具模块
2. 在 `src/agent/lam_agent.py` 中集成新功能
3. 在 `src/ui/main_window.py` 中添加UI支持
4. 更新命令识别器以支持新命令

### 调试模式
设置环境变量启用详细日志：
```bash
set LAM_AGENT_DEBUG=true
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 发起 Pull Request

## 📄 许可证

MIT License

## 📞 支持

如有问题或建议，请创建 Issue 或联系开发者。

---

**LAM-Agent** - 让AI助手更智能，让桌面操作更简单！