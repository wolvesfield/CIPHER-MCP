from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from starlette.responses import JSONResponse

CIPHER_OPS_PATH = Path(os.getenv("CIPHER_OPS_PATH", "/opt/cipher-ops")).resolve()

SOLDIER_SPECS = [
    {"agent_id": "A-01", "module": "cipher_ops.soldiers.alpha.a01_cia", "class_name": "CIAAgent"},
    {"agent_id": "A-02", "module": "cipher_ops.soldiers.alpha.a02_nsa", "class_name": "NSAAgent"},
    {"agent_id": "A-03", "module": "cipher_ops.soldiers.alpha.a03_nro", "class_name": "NROAgent"},
    {"agent_id": "A-04", "module": "cipher_ops.soldiers.alpha.a04_dia", "class_name": "DIAAgent"},
    {"agent_id": "A-05", "module": "cipher_ops.soldiers.alpha.a05_fbi", "class_name": "FBIAgent"},
    {"agent_id": "B-01", "module": "cipher_ops.soldiers.bravo.b01_corps", "class_name": "CorpsAgent"},
    {"agent_id": "B-02", "module": "cipher_ops.soldiers.bravo.b02_darpa", "class_name": "DARPAAgent"},
    {"agent_id": "B-03", "module": "cipher_ops.soldiers.bravo.b03_logist", "class_name": "LogistAgent"},
    {"agent_id": "B-04", "module": "cipher_ops.soldiers.bravo.b04_signal", "class_name": "SignalAgent"},
    {"agent_id": "C-01", "module": "cipher_ops.soldiers.charlie.c01_pentagon", "class_name": "PentagonAgent"},
    {"agent_id": "C-02", "module": "cipher_ops.soldiers.charlie.c02_homeland", "class_name": "HomelandAgent"},
    {"agent_id": "C-03", "module": "cipher_ops.soldiers.charlie.c03_secretsv", "class_name": "SecretSvAgent"},
    {"agent_id": "C-04", "module": "cipher_ops.soldiers.charlie.c04_nsc", "class_name": "NSCAgent"},
    {"agent_id": "D-01", "module": "cipher_ops.soldiers.delta.d01_treasury", "class_name": "TreasuryAgent"},
    {"agent_id": "D-02", "module": "cipher_ops.soldiers.delta.d02_wallst", "class_name": "WallStAgent"},
    {"agent_id": "D-03", "module": "cipher_ops.soldiers.delta.d03_fedres", "class_name": "FedResAgent"},
    {"agent_id": "D-04", "module": "cipher_ops.soldiers.delta.d04_secretsv", "class_name": "WatchdogAgent"},
    {"agent_id": "D-05", "module": "cipher_ops.soldiers.delta.d05_mint", "class_name": "MintAgent"},
]

def _cipher_ops_python() -> str:
    venv_python = CIPHER_OPS_PATH / ".venv" / "bin" / "python"
    return str(venv_python) if venv_python.exists() else sys.executable


def _run_cipher_ops_helper(action: str, payload: dict[str, Any], timeout_sec: int = 60) -> dict[str, Any]:
    helper = f"""
import asyncio
import importlib
import json
import sys
from pathlib import Path

action = sys.argv[1]
payload = json.loads(sys.argv[2])
cipher_ops_path = Path(sys.argv[3])
sys.path.insert(0, str(cipher_ops_path))
soldier_specs = json.loads({json.dumps(json.dumps(SOLDIER_SPECS))})

class BridgeMemory:
    async def retrieve(self, **kwargs):
        return []

    async def store(self, **kwargs):
        return None

loaded = {{}}
for spec in soldier_specs:
    module = importlib.import_module(spec["module"])
    cls = getattr(module, spec["class_name"])
    loaded[spec["agent_id"]] = (spec, cls)

if action == "list":
    agents = []
    for agent_id in sorted(loaded):
        spec, cls = loaded[agent_id]
        agents.append({{
            "agent_id": agent_id,
            "name": getattr(cls, "agent_name", spec["class_name"]),
            "wing": getattr(cls, "wing", ""),
            "general_id": getattr(cls, "general_id", ""),
            "module": spec["module"],
        }})
    print(json.dumps({{"count": len(agents), "agents": agents}}))
elif action == "invoke":
    from cipher_ops.base_agent import AgentTask
    agent_id = payload.get("agent_id")
    if agent_id not in loaded:
        raise ValueError(f"Unknown soldier agent_id: {{agent_id}}")
    _, cls = loaded[agent_id]
    agent = cls(memory=BridgeMemory())
    task = AgentTask(
        instruction=payload.get("instruction", ""),
        context=payload.get("context") or {{}},
    )
    result = asyncio.run(agent.run(task))
    print(json.dumps({{
        "task_id": result.task_id,
        "agent_id": result.agent_id,
        "success": result.success,
        "output": result.output,
        "error": result.error,
        "duration_ms": result.duration_ms,
        "model": result.model_used,
    }}))
else:
    raise ValueError(f"Unknown action: {{action}}")
"""
    proc = subprocess.run(
        [_cipher_ops_python(), "-c", helper, action, json.dumps(payload), str(CIPHER_OPS_PATH)],
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "unknown error"
        raise RuntimeError(f"cipher-ops helper failed: {detail}")
    output = proc.stdout.strip()
    if not output:
        raise RuntimeError("cipher-ops helper returned empty output")
    return json.loads(output)


mcp = FastMCP(name="Cipher MCP Bridge")


@mcp.tool
def list_cipher_ops_soldiers() -> dict[str, Any]:
    """List all 18 Cipher Ops soldier agents from /opt/cipher-ops."""
    result = _run_cipher_ops_helper("list", {})
    result["cipher_ops_path"] = str(CIPHER_OPS_PATH)
    return result


@mcp.tool
def invoke_cipher_ops_soldier(
    agent_id: str,
    instruction: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Invoke a specific Cipher Ops soldier by agent ID."""
    return _run_cipher_ops_helper(
        "invoke",
        {
            "agent_id": agent_id,
            "instruction": instruction,
            "context": context or {},
        },
    )


def _health_payload() -> dict[str, str | bool | int]:
    cfg = Path(os.getenv("MCP_CONFIG_PATH", "/app/bridge/mcp-compiled.json"))
    return {
        "status": "ok",
        "service": "mcp-bridge",
        "config_path": str(cfg),
        "config_exists": cfg.exists(),
        "cipher_ops_path": str(CIPHER_OPS_PATH),
        "soldier_agents": len(SOLDIER_SPECS),
    }


def _openapi_payload() -> dict[str, Any]:
    return {
        "openapi": "3.1.0",
        "info": {"title": "Cipher MCP Bridge", "version": "1.1.1"},
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health",
                    "responses": {
                        "200": {
                            "description": "Successful Response",
                            "content": {"application/json": {}},
                        }
                    },
                }
            },
            "/sse": {
                "get": {
                    "summary": "MCP SSE stream endpoint",
                    "description": "MCP SSE endpoint provided by FastMCP transport.",
                    "responses": {"200": {"description": "SSE stream established"}},
                }
            },
            "/messages": {
                "post": {
                    "summary": "MCP SSE message endpoint",
                    "description": "MCP message ingress endpoint paired with /sse.",
                    "responses": {"200": {"description": "Message accepted"}},
                }
            },
        }
    }

app = mcp.http_app(transport="sse")
app.add_route("/health", lambda request: JSONResponse(_health_payload()), methods=["GET"])
app.add_route("/openapi.json", lambda request: JSONResponse(_openapi_payload()), methods=["GET"])
