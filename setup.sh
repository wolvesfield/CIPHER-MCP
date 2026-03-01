#!/bin/bash
# =============================================================================
# CIPHER-MCP — Universal Bootstrap Script (Linux / macOS / KVM8)
# One command onboards any machine: agents, skills, MCP tools, arbiter deps.
# Usage: bash setup.sh
# One-liner from scratch: bash <(curl -sSL https://raw.githubusercontent.com/wolvesfield/CIPHER-MCP/main/setup.sh)
# =============================================================================
set -e

echo -e "\033[1;36m🚀 Initializing CIPHER-MCP Master Environment...\033[0m"

# 1. Dependency Check
echo "Checking prerequisites..."
for cmd in node npm python3 pip3 git; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "\033[1;31m❌ Error: $cmd is not installed. Please install it first.\033[0m"
        exit 1
    fi
done

# Install uv if missing (high-speed Python package runner for MCP tools)
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env || true
fi

pip3 install python-dotenv --quiet

# Define paths
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COPILOT_GLOBAL_DIR="$HOME/.copilot"
COPILOT_CONFIG_DIR="$HOME/.config/copilot"

# 2. Create target directories
echo "Preparing workspace directories..."
mkdir -p "$COPILOT_CONFIG_DIR/agents"
mkdir -p "$COPILOT_GLOBAL_DIR/skills"
mkdir -p "$HOME/vs-code-agents/.github/prompts"
mkdir -p "$HOME/agent-output"
mkdir -p "$REPO_ROOT/work-logs"

# 3. Setup Global Instructions
echo "Linking instructions..."
SOURCE_INSTRUCTIONS="$REPO_ROOT/core/instructions/copilot-instructions.md"
TARGET_INSTRUCTIONS="$COPILOT_GLOBAL_DIR/copilot-instructions.md"
rm -f "$TARGET_INSTRUCTIONS"
if [ -f "$SOURCE_INSTRUCTIONS" ]; then
    ln -s "$SOURCE_INSTRUCTIONS" "$TARGET_INSTRUCTIONS"
fi

# 4. Setup Agents
echo "Linking Specialist Agents..."
for AGENT_FILE in "$REPO_ROOT/core/agents/"*.md; do
    if [ -f "$AGENT_FILE" ]; then
        ln -sf "$AGENT_FILE" "$COPILOT_CONFIG_DIR/agents/$(basename "$AGENT_FILE")"
    fi
done

# 5. Setup Skills
echo "Linking Core Skills..."
for SKILL_DIR in "$REPO_ROOT/core/skills/"*; do
    if [ -d "$SKILL_DIR" ]; then
        rm -rf "$COPILOT_GLOBAL_DIR/skills/$(basename "$SKILL_DIR")"
        ln -sf "$SKILL_DIR" "$COPILOT_GLOBAL_DIR/skills/$(basename "$SKILL_DIR")"
    fi
done

# 6. Setup Prompts
echo "Linking Prompt Templates..."
for PROMPT_FILE in "$REPO_ROOT/prompts/"*.md; do
    if [ -f "$PROMPT_FILE" ]; then
        ln -sf "$PROMPT_FILE" "$HOME/vs-code-agents/.github/prompts/$(basename "$PROMPT_FILE")"
    fi
done

# 7. Compile MCP Ecosystem
echo -e "\033[1;33m🛠️ Compiling MCP Ecosystem (AOT Mode)...\033[0m"
cd "$REPO_ROOT"
if [ ! -f ".env" ]; then
    echo "Creating .env from template (fill in your API keys)..."
    cp .env.example .env
fi

python3 mcp_enterprise_compiler.py

# 8. Install Arbiter / Bridge Python dependencies
echo -e "\033[1;33m🤖 Installing Consensus Arbiter dependencies...\033[0m"
pip3 install fastapi uvicorn httpx pydantic --quiet

# 9. Register mcp-compiled.json with VS Code (if installed)
VSCODE_MCP_CONFIG="$HOME/.config/Code/User/settings.json"
if [ -f "$VSCODE_MCP_CONFIG" ]; then
    echo "Registering MCP tools with VS Code..."
    python3 - <<PYEOF
import json, os
cfg_path = os.path.expanduser("$VSCODE_MCP_CONFIG")
mcp_path = "$REPO_ROOT/mcp-compiled.json"
with open(cfg_path) as f:
    cfg = json.load(f)
if "mcp" not in cfg:
    cfg["mcp"] = {}
cfg["mcp"]["servers-file"] = mcp_path
with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)
print("  ✅ VS Code settings.json updated with mcp.servers-file")
PYEOF
else
    echo "  VS Code settings not found — skipping (register manually if needed)"
fi

# 10. Register with Claude Desktop (if installed)
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
[ -d "$HOME/.config/Claude" ] && CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
CLAUDE_CONFIG="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"
if [ -d "$CLAUDE_CONFIG_DIR" ]; then
    echo "Registering MCP tools with Claude Desktop..."
    python3 - <<PYEOF
import json, os
cfg_path = "$CLAUDE_CONFIG"
mcp_json = "$REPO_ROOT/mcp-compiled.json"
cfg = {}
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        cfg = json.load(f)
with open(mcp_json) as f:
    servers = json.load(f).get("mcpServers", {})
if "mcpServers" not in cfg:
    cfg["mcpServers"] = {}
cfg["mcpServers"].update(servers)
with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)
print(f"  ✅ Claude Desktop updated with {len(servers)} MCP servers")
PYEOF
else
    echo "  Claude Desktop not found — skipping"
fi

echo ""
echo -e "\033[1;35m✨ SUCCESS: CIPHER-MCP fully active on this machine.\033[0m"
echo -e "\033[1;32m   ✅ Agents linked\033[0m"
echo -e "\033[1;32m   ✅ Skills linked\033[0m"
echo -e "\033[1;32m   ✅ 28 MCP Servers compiled → mcp-compiled.json\033[0m"
echo -e "\033[1;32m   ✅ Role profiles: mcp-core / mcp-dev / mcp-hacker / mcp-trading\033[0m"
echo -e "\033[1;32m   ✅ Arbiter deps installed (FastAPI, uvicorn, httpx, pydantic)\033[0m"
echo -e "\033[1;32m   ✅ SUPER_ARCHITECTURE.md auto-loads in every Copilot session\033[0m"
echo ""
echo -e "\033[1;33mNEXT STEPS:\033[0m"
echo "  1. Fill in .env: nano $REPO_ROOT/.env"
echo "  2. On KVM8 — start Arbiter:  python3 $REPO_ROOT/arbiter/consensus_arbiter.py"
echo "  3. On KVM8 — start Bridge:   uvicorn arbiter.mcp_a2a_bridge:bridge_app --port 8001"
echo "  4. Open repo in VS Code — Copilot auto-loads full fleet context"
echo ""
echo -e "\033[1;33mTIP: To re-run on any new machine:\033[0m"
echo "  bash <(curl -sSL https://raw.githubusercontent.com/wolvesfield/CIPHER-MCP/main/setup.sh)"