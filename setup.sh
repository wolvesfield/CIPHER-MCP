#!/bin/bash
# Universal Fleet Master Bootstrap Script for Linux/macOS (VPS)
# Goal: One-command deployment of Agents, Skills, Instructions, and MCP routing configs.

set -e

echo -e "\033[1;36m🚀 Initializing CIPHER-MCP Master Environment...\033[0m"

# 1. Dependency Check
echo "Checking prerequisites..."
for cmd in node npm python3 pip3; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "\033[1;31m❌ Error: $cmd is not installed. Please install it first.\033[0m"
        exit 1
    fi
done

# Install uv if missing (preferred for high-speed MCP)
if ! command -v uv &> /dev/null; then
    echo "Installing uv (high-speed python package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env || true
fi

# Install python-dotenv for the compiler
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
ln -s "$SOURCE_INSTRUCTIONS" "$TARGET_INSTRUCTIONS"

# 4. Setup Agents
echo "Linking 13 Specialist Agents..."
for AGENT_FILE in "$REPO_ROOT/core/agents/"*.md; do
    if [ -f "$AGENT_FILE" ]; then
        ln -sf "$AGENT_FILE" "$COPILOT_CONFIG_DIR/agents/$(basename "$AGENT_FILE")"
    fi
done

# 5. Setup Skills
echo "Linking 9 Core Skills..."
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
    echo "Creating .env from template (Please update your keys later)..."
    cp .env.example .env
fi

python3 bridge/mcp_enterprise_compiler.py

echo -e "\033[1;35m✨ SUCCESS: Your Universal AI Master Repo is fully active.\033[0m"
echo -e "\033[1;32m   - 13 Agents Linked\033[0m"
echo -e "\033[1;32m   - 9 Skills Linked\033[0m"
echo -e "\033[1;32m   - 28 MCP Servers Compiled to mcp-compiled.json\033[0m"
echo -e "\033[1;32m   - Default onboarding profile generated: mcp-master.json\033[0m"
echo -e "\033[1;32m   - Wing profiles generated: mcp-core/dev/hacker/trading.json\033[0m"
echo -e "\033[1;32m   - Workspace: ~/agent-output/ ready.\033[0m"
echo -e "\033[1;33mNOTE: Point your IDE/Host to $REPO_ROOT/mcp-master.json for selective tool activation.\033[0m"
