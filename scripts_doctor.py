#!/usr/bin/env python3
"""Repository health checks for CIPHER-MCP."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "bridge" / "mcp-enterprise.json"


def fail(msg: str) -> None:
    print(f"[x] {msg}")
    raise SystemExit(1)


def main() -> None:
    if not MANIFEST.exists():
        fail("bridge/mcp-enterprise.json is missing")

    with MANIFEST.open(encoding="utf-8") as fh:
        data = json.load(fh)

    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        fail("mcpServers must be a non-empty object")

    problems: list[str] = []
    uses_npx_or_uvx = 0

    for name, server in servers.items():
        if not isinstance(server, dict):
            problems.append(f"{name}: entry must be an object")
            continue

        has_command = "command" in server
        has_url = "url" in server

        if has_command == has_url:
            problems.append(f"{name}: must define exactly one of command or url")
            continue

        if has_command:
            command = server.get("command")
            args = server.get("args", [])
            if not isinstance(command, str) or not command.strip():
                problems.append(f"{name}: command must be a non-empty string")
            if not isinstance(args, list):
                problems.append(f"{name}: args must be a list")
            if command in {"npx", "uvx"}:
                uses_npx_or_uvx += 1

        env = server.get("env", {})
        if env and not isinstance(env, dict):
            problems.append(f"{name}: env must be an object when provided")
        elif isinstance(env, dict):
            for key, value in env.items():
                if not isinstance(value, str):
                    problems.append(f"{name}: env var {key} must be a string")

    if problems:
        for p in problems:
            print(f"[x] {p}")
        raise SystemExit(1)

    print(f"[+] manifest OK: {len(servers)} server definitions")
    print(f"[+] runtime launchers to precompile: {uses_npx_or_uvx}")


if __name__ == "__main__":
    try:
        main()
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in manifest: {exc}")
