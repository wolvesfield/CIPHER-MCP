from __future__ import annotations

import os
from fastapi import FastAPI

app = FastAPI(title="Cipher Consensus Arbiter", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "arbiter",
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
    }
