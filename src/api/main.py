from fastapi import FastAPI
from pydantic import BaseModel
from ..agent.lam_agent import LamAgent


app = FastAPI(title="LAM Agent API")
agent = LamAgent()


class Query(BaseModel):
    question: str


@app.post("/ask")
def ask(q: Query):
    return agent.run(q.question)

