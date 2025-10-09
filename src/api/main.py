import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from ..agent.lam_agent import LamAgent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LAM Agent API",
    description="Language + Action Model Agent API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局代理实例
agent: Optional[LamAgent] = None


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="用户问题")
    model: Optional[str] = Field(None, description="指定使用的模型")


class QueryResponse(BaseModel):
    plan: str = Field(..., description="执行计划")
    evidence_count: int = Field(..., description="证据数量")
    answer: str = Field(..., description="最终答案")
    sources: list[str] = Field(..., description="来源链接")


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化代理"""
    global agent
    try:
        agent = LamAgent()
        logger.info("LAM Agent 初始化成功")
    except Exception as e:
        logger.error(f"LAM Agent 初始化失败: {e}")
        raise


@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "LAM Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "agent_ready": agent is not None}


@app.post("/ask", response_model=QueryResponse)
async def ask(request: QueryRequest):
    """处理用户查询"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        logger.info(f"收到查询请求: {request.question[:100]}...")
        result = agent.run(request.question)
        return QueryResponse(**result)
    except ValueError as e:
        logger.warning(f"输入验证错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"处理查询时发生错误: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

