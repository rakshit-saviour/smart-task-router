"""
FastAPI backend exposing a single /route endpoint.
Handles the request -> classify -> call model -> log -> respond flow.
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

try:
    from .router import route_request
    from .db import init_db, log_request, get_all_requests
except ImportError:
    from router import route_request
    from db import init_db, log_request, get_all_requests

app = FastAPI(title="Smart Task Router")

init_db()


class PromptRequest(BaseModel):
    prompt: str


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Smart Task Router API is running"}


@app.post("/route")
def route(request: PromptRequest):
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        result = route_request(request.prompt)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    log_request(request.prompt, result)
    return result


@app.get("/history")
def history(limit: int = 50):
    rows = get_all_requests(limit)
    return [
        {
            "timestamp": r[0],
            "prompt": r[1],
            "model_used": r[2],
            "complexity": r[3],
            "latency_seconds": r[4],
            "total_tokens": r[5],
            "estimated_cost_usd": r[6],
        }
        for r in rows
    ]
