# LAM-Agent (Language + Action Model)

一个智能的 Language + Action Model 代理，支持 DeepSeek 和 OpenAI 模型，能够直接执行用户指令而不是仅仅提供建议。

## 🎯 核心特性

- 🚀 **直接操作**: AI直接执行操作而不是仅仅建议
- 🧠 **多模型支持**: 支持 DeepSeek 和 OpenAI 模型
- 🔍 **智能搜索**: 自动在浏览器中打开多个搜索引擎
- 🌐 **网页抓取**: 使用 Playwright 抓取并解析网页内容
- 💻 **图形界面**: 提供友好的用户界面
- 🛡️ **安全验证**: 输入验证和安全性检查
- 📝 **详细日志**: 完整的操作日志记录
- 🚀 **API 接口**: RESTful API 和命令行接口

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd LAM-Agent

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env
```

编辑 `.env` 文件，填入必要的配置：

```env
# DeepSeek API配置（推荐）
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# OpenAI API配置（可选，用于兼容性）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# LangSmith配置（可选）
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=your_langsmith_api_key_here

# LAM Agent配置
LAM_AGENT_MODEL=deepseek-chat
LAM_BROWSER_HEADLESS=true
USE_DEEPSEEK=true
```

### 3. 使用方式

#### 命令行接口

```bash
# 基本使用（使用DeepSeek）
python cli.py "帮我查下Python 3.13 新特性并给出要点"

# 指定模型
python cli.py --model deepseek-chat "分析最新的AI发展趋势"

# 使用OpenAI模型
python cli.py --model gpt-4o-mini "生成一个包含步骤的网页自动化示例"

# 详细输出
python cli.py --verbose "生成一个包含步骤的网页自动化示例"
```

#### API 服务

```bash
# 启动 API 服务
uvicorn src.api.main:app --reload --port 8000

# 或使用提供的脚本
# Windows
scripts\run_api.ps1

# Linux/Mac
./scripts/run_api.sh
```

API 文档: http://localhost:8000/docs

#### API 使用示例

```bash
# 健康检查
curl http://localhost:8000/health

# 发送查询
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "帮我查下Python 3.13 新特性并给出要点"}'
```

## 项目结构

```
LAM-Agent/
├── src/
│   ├── agent/           # 核心代理逻辑
│   ├── api/            # FastAPI 接口
│   ├── tools/          # 工具模块（搜索、浏览器）
│   ├── utils/          # 工具函数（验证、安全）
│   └── config.py       # 配置管理
├── scripts/            # 运行脚本
├── cli.py             # 命令行接口
├── requirements.txt   # 依赖管理
└── README.md         # 项目文档
```

## 技术栈

- **LangChain**: 大语言模型集成
- **DeepSeek**: 国产大语言模型（默认）
- **OpenAI**: 大语言模型（兼容）
- **Playwright**: 网页自动化
- **FastAPI**: Web API 框架
- **DuckDuckGo**: 网络搜索
- **BeautifulSoup**: HTML 解析
- **Pydantic**: 数据验证

## 模型配置

### DeepSeek 模型（推荐）

DeepSeek 是国产大语言模型，具有以下优势：
- 成本更低
- 中文理解能力强
- 响应速度快
- 支持长文本处理

配置方法：
```env
USE_DEEPSEEK=true
DEEPSEEK_API_KEY=your_deepseek_api_key_here
LAM_AGENT_MODEL=deepseek-chat
```

### OpenAI 模型（兼容）

如果需要使用 OpenAI 模型：
```env
USE_DEEPSEEK=false
OPENAI_API_KEY=your_openai_api_key_here
LAM_AGENT_MODEL=gpt-4o-mini
```

## 安全特性

- 输入验证和清理
- URL 安全性检查
- 防止恶意内容注入
- 私有IP地址保护
- 内容长度限制
- 环境变量验证
- 自定义异常处理
- 配置安全性检查

## 开发

```bash
# 代码格式化
black src/

# 导入排序
isort src/

# 类型检查
mypy src/

# 代码检查
flake8 src/

# 运行测试
pytest tests/

# 安装开发依赖
pip install -r requirements.txt
```

## 许可证

MIT License

