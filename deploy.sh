#!/usr/bin/env bash
# =============================================================================
# CIPHER OPS — THE GOVERNMENT — KVM8 VPS Deployment Script
# Run this ONCE on a fresh KVM8 VPS to set up everything.
#
# Usage:
#   ssh root@YOUR_VPS_IP
#   curl -sSL https://raw.githubusercontent.com/YOUR_ORG/CIPHER-MCP-temp/main/deploy.sh | bash
#   # OR: copy this file to VPS and run: bash deploy.sh
#
# Prerequisites:
#   - KVM8 VPS (8 cores, 32GB RAM, 400GB NVMe)
#   - Ubuntu 22.04+ or Debian 12+
#   - Root access
# =============================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║     CIPHER OPS — THE GOVERNMENT                 ║"
    echo "║     4-General Autonomous Army Deployment         ║"
    echo "║     For Littli.                                  ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

step() { echo -e "\n${GREEN}[STEP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; exit 1; }

# ── Config ──────────────────────────────────────────────────
DEPLOY_DIR="/opt/cipher-ops"
REPO_BRAIN="https://github.com/wolvesfield/CIPHER-MCP-temp.git"
REPO_BODY="https://github.com/wolvesfield/cipher-ops.git"

banner

# ── Step 1: System Updates ──────────────────────────────────
step "Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq
apt-get install -y -qq curl git wget jq htop tmux ufw

# ── Step 2: Install Docker ──────────────────────────────────
step "Installing Docker..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}Docker installed.${NC}"
else
    echo "Docker already installed."
fi

# Install Docker Compose plugin
if ! docker compose version &>/dev/null; then
    apt-get install -y -qq docker-compose-plugin
fi

# ── Step 3: Install Ollama ──────────────────────────────────
step "Installing Ollama (local AI inference)..."
if ! command -v ollama &>/dev/null; then
    curl -fsSL https://ollama.com/install.sh | sh
    systemctl enable ollama
    systemctl start ollama
    echo -e "${GREEN}Ollama installed.${NC}"
else
    echo "Ollama already installed."
fi

# ── Step 4: Pull Ollama Models ──────────────────────────────
step "Pulling Ollama models (this takes 10-30 min on first run)..."
echo "  Pulling qwen3:30b-a3b (Delta's brain — ~18GB)..."
ollama pull qwen3:30b-a3b || warn "qwen3:30b-a3b pull failed — retry manually: ollama pull qwen3:30b-a3b"

echo "  Pulling deepseek-r1:14b (Delta's reasoning — ~9GB)..."
ollama pull deepseek-r1:14b || warn "deepseek-r1:14b pull failed — retry manually"

echo "  Pulling nomic-embed-text (shared embeddings — ~300MB)..."
ollama pull nomic-embed-text || warn "nomic-embed-text pull failed — retry manually"

# ── Step 5: Clone Repos ────────────────────────────────────
step "Setting up deployment directory: ${DEPLOY_DIR}"
mkdir -p "${DEPLOY_DIR}"
cd "${DEPLOY_DIR}"

if [ -d "CIPHER-MCP-temp" ]; then
    echo "  Brain repo exists — pulling latest..."
    cd CIPHER-MCP-temp && git pull && cd ..
else
    echo "  Cloning Brain repo..."
    git clone "${REPO_BRAIN}" CIPHER-MCP-temp
fi

if [ -d "cipher-ops" ]; then
    echo "  Body repo exists — pulling latest..."
    cd cipher-ops && git pull && cd ..
else
    echo "  Cloning Body repo..."
    git clone "${REPO_BODY}" cipher-ops
fi

# ── Step 6: Configure Environment ──────────────────────────
step "Setting up environment..."
cd "${DEPLOY_DIR}/CIPHER-MCP-temp"

if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  ACTION REQUIRED: Edit .env with your API keys!${NC}"
    echo -e "${YELLOW}  File: ${DEPLOY_DIR}/CIPHER-MCP-temp/.env${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Required keys to fill in:"
    echo "    - GEMINI_API_KEY        (Alpha — Google AI Studio)"
    echo "    - OPENAI_API_KEY        (Bravo — OpenAI)"
    echo "    - ANTHROPIC_API_KEY     (Charlie — Anthropic)"
    echo "    - TELEGRAM_BOT_TOKEN    (Broski comms)"
    echo "    - TELEGRAM_CHAT_ID      (Broski comms)"
    echo "    - ALPACA_API_KEY        (Delta — stock trading)"
    echo "    - ALPACA_SECRET_KEY     (Delta — stock trading)"
    echo "    - BINANCE_API_KEY       (Delta — crypto trading)"
    echo "    - BINANCE_SECRET_KEY    (Delta — crypto trading)"
    echo ""
    echo -e "  Edit now: ${CYAN}nano ${DEPLOY_DIR}/CIPHER-MCP-temp/.env${NC}"
    echo ""
    read -p "  Press ENTER after editing .env (or Ctrl+C to abort)..."
else
    echo "  .env already exists — keeping current config."
fi

# ── Step 7: Configure Firewall ──────────────────────────────
step "Configuring firewall (UFW)..."
ufw allow ssh
ufw allow 8000/tcp   # VP (Arbiter)
ufw allow 8001/tcp   # MCP Bridge
# Generals are internal only (Docker network) — no external exposure
echo "y" | ufw enable 2>/dev/null || true
echo "  Firewall: SSH + port 8000 (Arbiter) + port 8001 (Bridge) open."
echo "  Generals (8010-8013) are Docker-internal only."

# ── Step 8: Build & Launch ──────────────────────────────────
step "Building and launching The Government..."
cd "${DEPLOY_DIR}/CIPHER-MCP-temp"

# Build all containers
docker compose build --parallel

# Launch everything
docker compose up -d

echo ""
step "Waiting for services to start (30s)..."
sleep 30

# ── Step 9: Verify ──────────────────────────────────────────
step "Running verification checks..."
echo ""

# VP Health
echo -n "  VP (Arbiter) :8000 ... "
if curl -sf http://localhost:8000/health | jq -r '.arbiter' 2>/dev/null | grep -q 'online'; then
    echo -e "${GREEN}ONLINE${NC}"
else
    echo -e "${RED}OFFLINE${NC}"
fi

# Generals
for port in 8010 8011 8012 8013; do
    name=$(curl -sf "http://localhost:${port}/health" | jq -r '.general' 2>/dev/null || echo "???")
    soldiers=$(curl -sf "http://localhost:${port}/health" | jq -r '.soldiers' 2>/dev/null || echo "?")
    echo -n "  General ${name} :${port} ... "
    if [ "$name" != "???" ]; then
        echo -e "${GREEN}ONLINE${NC} (${soldiers} soldiers)"
    else
        echo -e "${RED}OFFLINE${NC}"
    fi
done

# Infrastructure
echo -n "  Redis :6379 ... "
if docker exec cipher-redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "${GREEN}ONLINE${NC}"
else
    echo -e "${RED}OFFLINE${NC}"
fi

echo -n "  Qdrant :6333 ... "
if curl -sf http://localhost:6333/healthz 2>/dev/null | grep -q 'ok'; then
    echo -e "${GREEN}ONLINE${NC}"
else
    echo -e "${RED}OFFLINE${NC}"
fi

echo -n "  MinIO :9000 ... "
if curl -sf http://localhost:9000/minio/health/live 2>/dev/null; then
    echo -e "${GREEN}ONLINE${NC}"
else
    echo -e "${RED}OFFLINE${NC}"
fi

echo -n "  Ollama :11434 ... "
if curl -sf http://localhost:11434/api/tags 2>/dev/null | jq -r '.models | length' 2>/dev/null | grep -q '[0-9]'; then
    models=$(curl -sf http://localhost:11434/api/tags | jq -r '.models | length')
    echo -e "${GREEN}ONLINE${NC} (${models} models)"
else
    echo -e "${RED}OFFLINE${NC}"
fi

# ── Done ────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  THE GOVERNMENT IS OPERATIONAL                   ║${NC}"
echo -e "${CYAN}║                                                  ║${NC}"
echo -e "${CYAN}║  VP:      http://YOUR_IP:8000                    ║${NC}"
echo -e "${CYAN}║  Health:  curl localhost:8000/health              ║${NC}"
echo -e "${CYAN}║  MinIO:   http://YOUR_IP:9001 (console)          ║${NC}"
echo -e "${CYAN}║  Logs:    docker compose logs -f                 ║${NC}"
echo -e "${CYAN}║                                                  ║${NC}"
echo -e "${CYAN}║  For Littli.                                     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════╝${NC}"
echo ""
echo "Useful commands:"
echo "  docker compose logs -f arbiter         # VP logs"
echo "  docker compose logs -f general-alpha   # Alpha logs"
echo "  docker compose logs -f general-delta   # Delta logs (revenue)"
echo "  docker compose restart general-charlie # Restart a General"
echo "  docker compose down                    # Stop everything"
echo "  docker compose up -d                   # Start everything"
echo ""
