#!/bin/bash
# Universal Fleet Bootstrap Script for Linux/macOS (VPS)
# Automatically maps the CIPHER-MCP repository to system's global GitHub Copilot agent directories.

set -e

echo -e "\033[1;36m🚀 Initializing CIPHER-MCP Fleet Environment for Linux/VPS...\033[0m"

# Define paths
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COPILOT_GLOBAL_DIR="$HOME/.copilot"
COPILOT_CONFIG_DIR="$HOME/.config/copilot"

# 1. Create target directories
TARGET_AGENTS_DIR="$COPILOT_CONFIG_DIR/agents"
TARGET_SKILLS_DIR="$COPILOT_GLOBAL_DIR/skills"
TARGET_PROMPTS_DIR="$HOME/vs-code-agents/.github/prompts"

echo "Creating target directories..."
mkdir -p "$TARGET_AGENTS_DIR"
mkdir -p "$TARGET_SKILLS_DIR"
mkdir -p "$TARGET_PROMPTS_DIR"

# 2. Setup Global Instructions
SOURCE_INSTRUCTIONS="$REPO_ROOT/core/instructions/copilot-instructions.md"
TARGET_INSTRUCTIONS="$COPILOT_GLOBAL_DIR/copilot-instructions.md"

rm -f "$TARGET_INSTRUCTIONS"
ln -s "$SOURCE_INSTRUCTIONS" "$TARGET_INSTRUCTIONS"
echo -e "\033[1;32m✅ Linked copilot-instructions.md\033[0m"

# 3. Setup Agents
echo "Linking Agents..."
AGENT_COUNT=0
for AGENT_FILE in "$REPO_ROOT/core/agents/"*.md; do
    if [ -f "$AGENT_FILE" ]; then
        BASENAME=$(basename "$AGENT_FILE")
        rm -f "$TARGET_AGENTS_DIR/$BASENAME"
        ln -s "$AGENT_FILE" "$TARGET_AGENTS_DIR/$BASENAME"
        AGENT_COUNT=$((AGENT_COUNT + 1))
    fi
done
echo -e "\033[1;32m✅ Linked $AGENT_COUNT Agents\033[0m"

# 4. Setup Skills
echo "Linking Skills..."
SKILL_COUNT=0
for SKILL_DIR in "$REPO_ROOT/core/skills/"*; do
    if [ -d "$SKILL_DIR" ]; then
        BASENAME=$(basename "$SKILL_DIR")
        rm -rf "$TARGET_SKILLS_DIR/$BASENAME"
        ln -s "$SKILL_DIR" "$TARGET_SKILLS_DIR/$BASENAME"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    fi
done
echo -e "\033[1;32m✅ Linked $SKILL_COUNT Skills\033[0m"

# 5. Setup Prompts
echo "Linking Prompts..."
PROMPT_COUNT=0
for PROMPT_FILE in "$REPO_ROOT/prompts/"*.md; do
    if [ -f "$PROMPT_FILE" ]; then
        BASENAME=$(basename "$PROMPT_FILE")
        rm -f "$TARGET_PROMPTS_DIR/$BASENAME"
        ln -s "$PROMPT_FILE" "$TARGET_PROMPTS_DIR/$BASENAME"
        PROMPT_COUNT=$((PROMPT_COUNT + 1))
    fi
done
echo -e "\033[1;32m✅ Linked $PROMPT_COUNT Prompts\033[0m"

echo -e "\033[1;35m✨ Bootstrap Complete! Your Fleet is now globally active on this system.\033[0m"
echo -e "\033[1;33mNOTE: Edits made to agents or skills will directly update the files in this repository.\033[0m"
