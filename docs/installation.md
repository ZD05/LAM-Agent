# LAM-Agent 安装指南

## 📋 系统要求

### 操作系统
- **Windows**: Windows 10/11 (推荐)
- **Linux**: Ubuntu 18.04+ / CentOS 7+ / 其他主流发行版
- **macOS**: macOS 10.15+ (部分功能可能受限)

### 硬件要求
- **内存**: 最少 4GB RAM，推荐 8GB+
- **存储**: 至少 2GB 可用空间
- **网络**: 稳定的互联网连接（用于AI模型调用）

### 软件依赖
- **Python**: 3.8+ (推荐 3.9+)
- **pip**: 最新版本
- **Git**: 用于克隆项目

## 🚀 安装步骤

### 1. 克隆项目
```bash
# 克隆项目到本地
git clone https://github.com/your-username/LAM-Agent.git
cd LAM-Agent
```

### 2. 创建虚拟环境（推荐）
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. 安装依赖
```bash
# 安装所有依赖包
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install
```

### 4. 配置环境变量
创建 `.env` 文件：
```bash
# AI模型配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
LAM_AGENT_MODEL=deepseek-chat
USE_DEEPSEEK=true

# 浏览器配置
LAM_BROWSER_HEADLESS=false

# Steam配置（可选）
STEAM_API_KEY=your_steam_api_key
STEAM_USER_ID=your_steam_user_id
```

### 5. 验证安装
```bash
# 检查依赖是否正确安装
python -c "import src.agent.lam_agent; print('安装成功！')"

# 运行测试
python main.py --help
```

## 🔧 高级配置

### 数据库配置
项目会自动创建SQLite数据库，位置：`src/database/credentials.db`

### 日志配置
日志文件位置：`logs/app.log`
- 自动轮转，最大2MB
- 保留3个备份文件
- UTF-8编码

### 浏览器配置
- **默认浏览器**: Chromium (Playwright)
- **无头模式**: 可通过环境变量控制
- **用户数据**: 保存在临时目录

## 🐛 常见问题

### 安装失败
**问题**: `pip install` 失败
**解决方案**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### Playwright安装问题
**问题**: `playwright install` 失败
**解决方案**:
```bash
# 手动安装浏览器
playwright install chromium

# 或者跳过浏览器安装（某些功能可能不可用）
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
```

### 权限问题
**问题**: Windows下权限不足
**解决方案**:
- 以管理员身份运行命令提示符
- 或者使用用户目录安装

### 网络问题
**问题**: 无法下载依赖
**解决方案**:
```bash
# 使用代理
pip install -r requirements.txt --proxy http://proxy:port

# 或使用国内镜像
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

## 🔍 验证安装

### 1. 基本功能测试
```bash
# 启动图形界面
python main.py

# 命令行测试
python main.py --cli "你好"
```

### 2. 功能模块测试
```python
# 测试各个模块导入
python -c "
import src.agent.lam_agent
import src.tools.browser
import src.tools.steam_integration
import src.tools.bilibili_integration
import src.database.credential_db
print('所有模块导入成功！')
"
```

### 3. 依赖检查
```bash
# 检查关键依赖
python -c "
import playwright
import requests
import sqlalchemy
import pydantic
print('关键依赖检查通过！')
"
```

## 📦 可选组件

### 开发工具
```bash
# 安装开发依赖
pip install pytest black flake8 mypy isort

# 代码格式化
black src/
isort src/
```

### 额外功能
```bash
# 安装额外工具
pip install jupyter  # 用于交互式开发
pip install pytest-cov  # 代码覆盖率测试
```

## 🔄 更新安装

### 更新项目
```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 更新浏览器
playwright install --force
```

### 清理安装
```bash
# 清理缓存
pip cache purge

# 重新安装
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

## 📞 获取帮助

如果安装过程中遇到问题：

1. **查看日志**: 检查 `logs/app.log` 文件
2. **社区支持**: 在GitHub Issues中搜索相关问题
3. **提交问题**: 创建新的Issue并提供详细信息

---

**安装完成后，请查看 [快速入门指南](quickstart.md) 开始使用 LAM-Agent！**


