from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="Cipher MCP Bridge", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str | bool]:
    cfg = Path(os.getenv("MCP_CONFIG_PATH", "/app/bridge/mcp-compiled.json"))
    return {
        "status": "ok",
        "service": "mcp-bridge",
        "config_path": str(cfg),
        "config_exists": cfg.exists(),
    }
