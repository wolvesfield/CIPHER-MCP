#!/bin/bash
# =============================================================================
# CIPHER-MCP — One-Liner Bootstrap (Linux / macOS / KVM8)
# Clones the repo and runs full setup in a single command.
#
# Usage — paste this on any fresh machine:
#   bash <(curl -sSL https://raw.githubusercontent.com/wolvesfield/CIPHER-MCP/main/setup/bootstrap.sh)
#
# Or with a specific install path:
#   INSTALL_DIR=/opt/cipher bash <(curl -sSL .../setup/bootstrap.sh)
# =============================================================================
set -e

REPO_URL="https://github.com/wolvesfield/CIPHER-MCP.git"
INSTALL_DIR="${INSTALL_DIR:-$HOME/cipher-mcp}"

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   CIPHER-MCP — Universal Machine Bootstrap       ║"
echo "║   For Littli 💙                                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check git
if ! command -v git &>/dev/null; then
    echo "Installing git..."
    apt-get install -y git 2>/dev/null || yum install -y git 2>/dev/null || {
        echo "❌ git not found. Install it first."
        exit 1
    }
fi

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "📦 Repo exists at $INSTALL_DIR — pulling latest..."
    cd "$INSTALL_DIR" && git pull --rebase origin main
else
    echo "📦 Cloning CIPHER-MCP to $INSTALL_DIR..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "🔧 Running setup..."
bash setup.sh

echo ""
echo "✅ Bootstrap complete. Repo at: $INSTALL_DIR"
