"""
mcp_enterprise_compiler.py
==========================
Ahead-Of-Time (AOT) compiler for the CIPHER-MCP 24-server ecosystem.

What it does
------------
1. Reads mcp-enterprise.json (the canonical server manifest).
2. Downloads all npx / uvx dependencies into an isolated .mcp_env/ directory
   so that servers start in <150 ms without touching npm/PyPI at runtime.
3. Rewrites every server entry to use the local binary path instead of npx/uvx.
4. Writes the ready-to-use config to mcp-compiled.json.

Usage
-----
    python mcp_enterprise_compiler.py [--input mcp-enterprise.json] [--output mcp-compiled.json]
    python mcp_enterprise_compiler.py --validate-env

The .env file (copied from .env.example) must be present so that env-var
placeholders are validated before compilation.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ENV_DIR = Path(".mcp_env").resolve()
NODE_DIR = ENV_DIR / "node"
PY_DIR = ENV_DIR / "python"
IS_WIN = sys.platform == "win32"

# Values that indicate a variable has not been filled in from the template
_PLACEHOLDER_PATTERNS = (
    "REPLACE_ME",
    "sbp_REPLACE_ME",
    "tvly-REPLACE_ME",
    "m0-REPLACE_ME",
    "github_pat_REPLACE_ME",
    "xoxb-REPLACE_ME",
    "T0REPLACE_ME",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    """Run a subprocess, streaming its output to the terminal."""
    print(f"    $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, check=True, **kwargs)


def _node_bin(pkg: str) -> Path:
    """Return the expected local binary path for an npm package."""
    name = pkg.split("/")[-1]
    if IS_WIN:
        return NODE_DIR / "node_modules" / ".bin" / f"{name}.cmd"
    return NODE_DIR / "node_modules" / ".bin" / name


def _py_bin(pkg: str) -> Path:
    """Return the expected local binary path for a Python package."""
    name = pkg.split("[")[0]  # strip extras, e.g. package[extra]
    scripts = "Scripts" if IS_WIN else "bin"
    suffix = ".exe" if IS_WIN else ""
    return PY_DIR / scripts / f"{name}{suffix}"


# ---------------------------------------------------------------------------
# Environment bootstrap
# ---------------------------------------------------------------------------

def bootstrap_environments() -> None:
    """Create isolated Node and Python environments if they don't exist."""
    print("[1/3] Bootstrapping isolated environments …")
    NODE_DIR.mkdir(parents=True, exist_ok=True)
    PY_DIR.mkdir(parents=True, exist_ok=True)

    if not (NODE_DIR / "package.json").exists():
        _run(["npm", "init", "-y"], cwd=NODE_DIR,
             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not (PY_DIR / "pyvenv.cfg").exists():
        _run([sys.executable, "-m", "venv", str(PY_DIR)],
             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ---------------------------------------------------------------------------
# Dependency collection
# ---------------------------------------------------------------------------

def collect_dependencies(
    servers: dict,
) -> tuple[set[str], set[str], dict]:
    """
    Walk the server manifest and collect npm / pip packages to pre-install.

    Also rewrites each server entry in-place:
    - Replaces 'npx -y <pkg>' with the local binary path.
    - Replaces 'uvx <pkg>' with the local binary path.
    - Replaces literal secret values inside 'env' with ${VAR_NAME} placeholders.

    Returns (node_packages, python_packages, mutated_servers_dict).
    """
    node_pkgs: set[str] = set()
    py_pkgs: set[str] = set()

    for name, server in servers.items():
        cmd = server.get("command", "")
        args: list = server.get("args", [])

        # ------------------------------------------------------------------
        # Sanitize env block: replace literal values with ${VAR} references
        # ------------------------------------------------------------------
        if "env" in server:
            server["env"] = {k: f"${{{k}}}" for k in server["env"]}

        # ------------------------------------------------------------------
        # npx -y <package> [extra-args…]
        # ------------------------------------------------------------------
        if cmd == "npx" and len(args) >= 2 and args[0] == "-y":
            pkg = args[1]
            node_pkgs.add(pkg)
            server["command"] = str(_node_bin(pkg))
            server["args"] = args[2:]

        # ------------------------------------------------------------------
        # uvx <package> [extra-args…]
        # ------------------------------------------------------------------
        elif cmd == "uvx" and args:
            pkg = args[0]
            py_pkgs.add(pkg)
            server["command"] = str(_py_bin(pkg))
            server["args"] = args[1:]

    return node_pkgs, py_pkgs, servers


# ---------------------------------------------------------------------------
# Installation
# ---------------------------------------------------------------------------

def install_node_packages(pkgs: set[str]) -> None:
    if not pkgs:
        return
    print(f"[2/3] Installing {len(pkgs)} Node package(s) …")
    _run(["npm", "install", "--prefix", str(NODE_DIR)] + sorted(pkgs))


def install_python_packages(pkgs: set[str]) -> None:
    if not pkgs:
        return
    print(f"[2/3] Installing {len(pkgs)} Python package(s) …")
    pip = PY_DIR / ("Scripts" if IS_WIN else "bin") / ("pip.exe" if IS_WIN else "pip")
    _run([str(pip), "install", "--upgrade"] + sorted(pkgs))


# ---------------------------------------------------------------------------
# .env validation
# ---------------------------------------------------------------------------

def validate_env_vars(servers: dict) -> list[str]:
    """
    Return a list of env-var names referenced in the manifest that are NOT
    set in the current process environment.  Warnings only – compilation
    continues so the compiled config can still be used after the vars are set.
    """
    missing: list[str] = []
    for server in servers.values():
        for val in server.get("env", {}).values():
            if val.startswith("${") and val.endswith("}"):
                var = val[2:-1]
                if not os.environ.get(var):
                    missing.append(var)
    return missing


def validate_env_strict(input_path: Path) -> None:
    """
    --validate-env mode: load .env, then check that every ${VAR} placeholder
    referenced in the manifest is set AND does not still contain a REPLACE_ME
    or placeholder-style value.  Exits 0 on success, 1 on any failure.
    """
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
        print("[*] Loaded .env via python-dotenv")
    except ImportError:
        print("[*] python-dotenv not installed -- reading os.environ only")

    if not input_path.exists():
        print(f"[!] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with input_path.open() as fh:
        config: dict = json.load(fh)

    servers: dict = config.get("mcpServers", {})
    errors: list[str] = []

    for server_name, server in servers.items():
        for env_key, val in server.get("env", {}).items():
            if not (val.startswith("${") and val.endswith("}")):
                continue
            var = val[2:-1]
            actual = os.environ.get(var, "")
            if not actual:
                errors.append(f"  [{server_name}] {var} -- NOT SET")
            elif any(p in actual for p in _PLACEHOLDER_PATTERNS):
                errors.append(f"  [{server_name}] {var} -- still a placeholder ({actual!r})")

    if errors:
        print(f"\n[x] validate-env FAILED -- {len(errors)} issue(s):\n" + "\n".join(errors))
        print("\n    Fill in all values in your .env file and re-run.")
        sys.exit(1)
    else:
        print(f"\n[+] validate-env PASSED -- all {len(servers)} server env vars are set and non-placeholder.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="AOT compiler for the CIPHER-MCP 24-server ecosystem."
    )
    parser.add_argument(
        "--input", default="mcp-enterprise.json",
        help="Source manifest (default: mcp-enterprise.json)"
    )
    parser.add_argument(
        "--output", default="mcp-compiled.json",
        help="Compiled output (default: mcp-compiled.json)"
    )
    parser.add_argument(
        "--validate-env", action="store_true",
        help=(
            "Load .env and verify every ${VAR} placeholder in the manifest "
            "is set and is not still a REPLACE_ME value. Exits 0 on success."
        )
    )
    args = parser.parse_args()

    input_path = Path(args.input)

    # ---------------------------------------------------------------------- #
    # --validate-env: standalone pre-flight check, does not compile
    # ---------------------------------------------------------------------- #
    if args.validate_env:
        validate_env_strict(input_path)
        return

    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[!] Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[*] CIPHER-MCP AOT Compiler — reading {input_path} …")
    with input_path.open() as fh:
        config: dict = json.load(fh)

    servers: dict = config.get("mcpServers", {})

    # ------------------------------------------------------------------ #
    bootstrap_environments()

    node_pkgs, py_pkgs, servers = collect_dependencies(servers)

    install_node_packages(node_pkgs)
    install_python_packages(py_pkgs)

    # ------------------------------------------------------------------ #
    # Warn about unset env vars (load .env first if dotenv is available)
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except ImportError:
        pass  # dotenv is optional

    missing = validate_env_vars(servers)
    if missing:
        unique_missing = sorted(set(missing))
        print(
            f"\n[!] WARNING: {len(unique_missing)} environment variable(s) are not set. "
            "Set them in .env before deploying:\n"
            + "\n".join(f"    - {v}" for v in unique_missing)
        )

    # ------------------------------------------------------------------ #
    config["mcpServers"] = servers
    with output_path.open("w") as fh:
        json.dump(config, fh, indent=2)

    print(
        f"\n[+] Compiled {len(servers)} servers → {output_path}\n"
        "    Boot latency target: <150 ms per server.\n"
        "    Point your MCP host at mcp-compiled.json to launch the ecosystem."
    )


if __name__ == "__main__":
    main()
