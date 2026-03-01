"""
CIPHER OPS — MCP → A2A Bridge
================================
Wraps every existing MCP tool as an A2A-compatible skill.
Each MCP server becomes a callable A2A skill that can be
invoked by any General through the Arbiter.

This is the "Southbound" bridge:
  A2A (General talks to Arbiter) → MCP (Agent uses tools)

Architecture:
  General Alpha/Bravo/Charlie
       ↓ A2A Protocol (Northbound)
  Consensus Arbiter
       ↓ MCP Protocol (Southbound)  
  MCP Tool Servers (filesystem, blockchain, browser, etc.)

Author: Cipher Legacy Foundation — for Littli
"""

from __future__ import annotations
import json
import subprocess
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

log = logging.getLogger("mcp-a2a-bridge")

# ─── MCP Tool Registry ────────────────────────────────────
# Maps A2A skill IDs to their MCP server configs
# Loaded from the compiled MCP config at startup

@dataclass
class MCPToolConfig:
    """Configuration for a single MCP tool server."""
    skill_id: str           # A2A skill ID (e.g., "mcp-playwright")
    mcp_server: str         # MCP server name (e.g., "playwright") 
    command: str            # Binary path
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    domain: str = "core"    # hacking | trading | dev | core
    description: str = ""


class ToolInvocation(BaseModel):
    """A2A skill invocation request."""
    skill_id: str
    method: str             # MCP method name (e.g., "tools/call")
    params: dict = {}
    timeout_sec: int = 30


class ToolResult(BaseModel):
    """A2A skill invocation result."""
    skill_id: str
    success: bool
    result: Any = None
    error: Optional[str] = None
    latency_ms: int = 0


# ─── Tool Registry ─────────────────────────────────────────

TOOL_REGISTRY: dict[str, MCPToolConfig] = {}


def load_mcp_config(config_path: str = "mcp-compiled.json") -> dict[str, MCPToolConfig]:
    """Load compiled MCP config and register all tools."""
    path = Path(config_path)
    if not path.exists():
        log.warning(f"MCP config not found: {config_path}")
        return {}

    with open(path) as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    registry = {}

    # Domain classification
    DOMAIN_MAP = {
        "playwright": "hacking", "puppeteer": "hacking", "chrome-devtools": "hacking",
        "browser-devtools-generic": "hacking", "antigravity-browser": "hacking",
        "fetch": "hacking", "hostinger-api": "hacking",
        "evm-blockchain": "trading", "solana-blockchain": "trading",
        "tatum-blockchain": "trading", "supabase-postgres": "trading", "dbhub-io": "trading",
        "docker-executor": "dev", "kubernetes-cluster": "dev", "google-cloud": "dev",
        "python-secure-sandbox": "dev", "generic-openapi": "dev",
        "figma-remote": "dev", "github-enterprise-cloud": "dev",
    }

    for name, server in servers.items():
        skill_id = f"mcp-{name}"
        tool = MCPToolConfig(
            skill_id=skill_id,
            mcp_server=name,
            command=server.get("command", ""),
            args=server.get("args", []),
            env=server.get("env", {}),
            domain=DOMAIN_MAP.get(name, "core"),
            description=f"MCP server: {name}",
        )
        registry[skill_id] = tool

    log.info(f"Loaded {len(registry)} MCP tools into A2A bridge")
    return registry


async def invoke_mcp_tool(tool: MCPToolConfig, method: str, params: dict, timeout: int = 30) -> dict:
    """
    Invoke an MCP tool server via stdio transport.

    MCP uses JSON-RPC 2.0 over stdio:
    1. Start the MCP server process
    2. Send JSON-RPC request via stdin
    3. Read JSON-RPC response from stdout
    """
    import time
    import os

    start = time.monotonic()

    # Build environment with resolved variables
    env = os.environ.copy()
    for key, val in tool.env.items():
        if val.startswith("${") and val.endswith("}"):
            var_name = val[2:-1]
            env[key] = os.getenv(var_name, "")
        else:
            env[key] = val

    # JSON-RPC 2.0 request
    request = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params,
    })

    try:
        cmd = [tool.command] + tool.args
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(input=request.encode()),
            timeout=timeout,
        )

        elapsed_ms = int((time.monotonic() - start) * 1000)

        if proc.returncode != 0:
            return {
                "success": False,
                "error": f"MCP server exited with code {proc.returncode}: {stderr.decode()[:500]}",
                "latency_ms": elapsed_ms,
            }

        # Parse JSON-RPC response
        response = json.loads(stdout.decode())

        if "error" in response:
            return {
                "success": False,
                "error": response["error"].get("message", "Unknown MCP error"),
                "latency_ms": elapsed_ms,
            }

        return {
            "success": True,
            "result": response.get("result"),
            "latency_ms": elapsed_ms,
        }

    except asyncio.TimeoutError:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return {
            "success": False,
            "error": f"MCP tool {tool.mcp_server} timed out after {timeout}s",
            "latency_ms": elapsed_ms,
        }
    except Exception as e:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        return {
            "success": False,
            "error": str(e),
            "latency_ms": elapsed_ms,
        }


# ─── FastAPI Bridge Endpoints ──────────────────────────────

bridge_app = FastAPI(
    title="CIPHER OPS — MCP→A2A Bridge",
    description="Wraps MCP tool servers as A2A-callable skills",
    version="1.0.0",
)


@bridge_app.on_event("startup")
async def startup():
    global TOOL_REGISTRY
    TOOL_REGISTRY = load_mcp_config()


@bridge_app.get("/.well-known/agent.json")
async def bridge_agent_card():
    """A2A Agent Card for the MCP Bridge itself."""
    skills = []
    for skill_id, tool in TOOL_REGISTRY.items():
        skills.append({
            "id": skill_id,
            "name": f"{tool.mcp_server} ({tool.domain})",
            "description": tool.description,
            "tags": [tool.domain, "mcp", tool.mcp_server],
        })

    return {
        "name": "Cipher Ops MCP-A2A Bridge",
        "description": "Bridges MCP tool servers to A2A protocol for General consumption",
        "version": "1.0.0",
        "supportedInterfaces": [{"url": "http://localhost:8001", "protocolBinding": "HTTP+JSON", "protocolVersion": "1.0"}],
        "capabilities": {"streaming": False, "pushNotifications": False},
        "skills": skills,
    }


@bridge_app.post("/tools/invoke", response_model=ToolResult)
async def invoke_tool(invocation: ToolInvocation):
    """Invoke an MCP tool via its A2A skill ID."""
    if invocation.skill_id not in TOOL_REGISTRY:
        raise HTTPException(404, f"Unknown skill: {invocation.skill_id}")

    tool = TOOL_REGISTRY[invocation.skill_id]
    result = await invoke_mcp_tool(tool, invocation.method, invocation.params, invocation.timeout_sec)

    return ToolResult(
        skill_id=invocation.skill_id,
        success=result["success"],
        result=result.get("result"),
        error=result.get("error"),
        latency_ms=result.get("latency_ms", 0),
    )


@bridge_app.get("/tools")
async def list_tools():
    """List all available MCP tools with their A2A skill mappings."""
    return {
        skill_id: {
            "mcp_server": t.mcp_server,
            "domain": t.domain,
            "command": t.command,
            "description": t.description,
        }
        for skill_id, t in TOOL_REGISTRY.items()
    }


@bridge_app.get("/tools/by-domain/{domain}")
async def tools_by_domain(domain: str):
    """Filter tools by domain (hacking/trading/dev/core)."""
    return {
        skill_id: {
            "mcp_server": t.mcp_server,
            "description": t.description,
        }
        for skill_id, t in TOOL_REGISTRY.items()
        if t.domain == domain
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("mcp_a2a_bridge:bridge_app", host="0.0.0.0", port=8001, reload=True)
