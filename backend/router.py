"""
Routing logic: decides which "agent" (model) should handle a request
based on a simple complexity heuristic, then calls the Groq API.
"""

import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Two tiers of models -> cheap/fast for simple tasks, bigger for complex ones
SIMPLE_MODEL = "llama-3.1-8b-instant"
COMPLEX_MODEL = "llama-3.3-70b-versatile"

# Rough per-1K-token cost estimates (USD) -- for demo purposes only
COST_PER_1K_TOKENS = {
    SIMPLE_MODEL: 0.00005,
    COMPLEX_MODEL: 0.00059,
}


def classify_complexity(prompt: str) -> str:
    """
    Very lightweight heuristic classifier.
    In a real system this could itself be a small model call,
    but a rule-based classifier is faster, free, and transparent.
    """
    word_count = len(prompt.split())
    complex_keywords = [
        "analyze", "compare", "design", "architecture", "explain in depth",
        "write code", "debug", "optimize", "summarize the following report",
        "step by step", "pros and cons"
    ]

    if word_count > 40:
        return "complex"

    lowered = prompt.lower()
    if any(keyword in lowered for keyword in complex_keywords):
        return "complex"

    return "simple"


def route_request(prompt: str) -> dict:
    """
    Classifies the prompt, calls the appropriate model via Groq,
    and returns the response plus routing metadata.
    """
    complexity = classify_complexity(prompt)
    model = COMPLEX_MODEL if complexity == "complex" else SIMPLE_MODEL

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set. Add it to your .env file.")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    start_time = time.time()
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    latency = round(time.time() - start_time, 2)

    if response.status_code != 200:
        raise RuntimeError(f"Groq API error {response.status_code}: {response.text}")

    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    total_tokens = usage.get("total_tokens", 0)
    cost = round((total_tokens / 1000) * COST_PER_1K_TOKENS[model], 6)

    return {
        "answer": answer,
        "model_used": model,
        "complexity": complexity,
        "latency_seconds": latency,
        "total_tokens": total_tokens,
        "estimated_cost_usd": cost,
    }
