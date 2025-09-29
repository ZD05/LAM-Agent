## LAM-Agent (LangChain + Playwright)

### 快速开始

1. 创建 `.env`

```
cp .env.example .env
```

填入 `OPENAI_API_KEY`，可调整 `LAM_BROWSER_HEADLESS`。

2. 激活虚拟环境

```
./.venv/Scripts/Activate.ps1
```

3. 运行 API

```
uvicorn src.api.main:app --reload --port 8000
```

POST `http://localhost:8000/ask`，Body：

```
{
  "question": "帮我查下Python 3.13 新特性并给出要点"
}
```

4. 命令行使用

```
python cli.py 生成一个包含步骤的网页自动化示例
```

### 说明
- LAM Agent 将决定是否进行搜索或浏览抓取，然后综合回答。
- 使用 DuckDuckGo 搜索与 Playwright 抓取页面，BS4 提取正文。

