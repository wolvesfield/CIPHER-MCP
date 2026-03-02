#!/bin/bash
# ============================================================
# CIPHER OPS — MacBook Pro M3 Setup Script
# Run this on your Mac to make it an always-on AI node
# Reachable from VPS + phone via Tailscale
# ============================================================

set -e

echo "============================================"
echo "  CIPHER OPS — Mac M3 Node Setup"
echo "  32GB RAM | M3 Chip | Always-On"
echo "============================================"
echo ""

# ── Step 1: Prevent Sleep ────────────────────────────────
echo "🔋 Step 1: Preventing sleep..."
sudo pmset -a sleep 0
sudo pmset -a displaysleep 0
sudo pmset -a disksleep 0
sudo pmset -a hibernatemode 0
# Allow wake on network access (Wake-on-LAN)
sudo pmset -a womp 1
echo "   ✅ Mac will never sleep (even lid closed with external display)"
echo ""

# ── Step 2: Enable SSH ──────────────────────────────────
echo "🔑 Step 2: Enabling SSH (Remote Login)..."
sudo systemsetup -setremotelogin on 2>/dev/null || echo "   ℹ️  Already enabled or use System Settings → General → Sharing → Remote Login"
echo "   ✅ SSH enabled — you can ssh $(whoami)@$(hostname) from local network"
echo ""

# ── Step 3: Install Homebrew (if missing) ────────────────
echo "🍺 Step 3: Checking Homebrew..."
if ! command -v brew &>/dev/null; then
    echo "   Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
    eval "$(/opt/homebrew/bin/brew shellenv)"
    echo "   ✅ Homebrew installed"
else
    echo "   ✅ Homebrew already installed"
fi
echo ""

# ── Step 4: Install Tailscale ───────────────────────────
echo "🌐 Step 4: Installing Tailscale (private VPN mesh)..."
if ! command -v tailscale &>/dev/null; then
    brew install --cask tailscale
    echo "   ✅ Tailscale installed"
    echo ""
    echo "   ⚠️  ACTION REQUIRED:"
    echo "   1. Open Tailscale from Applications"
    echo "   2. Sign in (use Google/GitHub/email)"
    echo "   3. Note your Mac's Tailscale IP (100.x.x.x)"
    echo "   4. Later: install Tailscale on VPS too so they see each other"
else
    echo "   ✅ Tailscale already installed"
    TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "not connected")
    echo "   📍 Your Tailscale IP: $TAILSCALE_IP"
fi
echo ""

# ── Step 5: Install Docker ─────────────────────────────
echo "🐳 Step 5: Checking Docker..."
if ! command -v docker &>/dev/null; then
    echo "   Installing Docker Desktop..."
    brew install --cask docker
    echo "   ✅ Docker installed"
    echo "   ⚠️  Open Docker Desktop once to complete setup"
else
    echo "   ✅ Docker already installed"
fi
echo ""

# ── Step 6: Install Ollama ──────────────────────────────
echo "🧠 Step 6: Installing Ollama..."
if ! command -v ollama &>/dev/null; then
    brew install ollama
    echo "   ✅ Ollama installed"
else
    echo "   ✅ Ollama already installed"
fi
echo ""

# ── Step 7: Pull AI Models ─────────────────────────────
echo "📦 Step 7: Pulling AI models (this takes a while)..."
echo "   These models fit in your 32GB RAM:"
echo ""

# Start ollama serve in background if not running
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo "   Starting Ollama server..."
    ollama serve &>/dev/null &
    sleep 3
fi

models=(
    "qwen3:30b-a3b"        # 18GB — Delta's primary brain
    "deepseek-r1:14b"      # 9GB  — Reasoning model
    "nomic-embed-text"     # 275MB — Embeddings for memory
)

for model in "${models[@]}"; do
    echo "   📥 Pulling $model ..."
    ollama pull "$model"
    echo "   ✅ $model ready"
    echo ""
done

echo "   Optional big models (pull later if you want):"
echo "   ollama pull llama3.3:70b-instruct-q4_K_M   # 40GB — pushes 32GB limit"
echo "   ollama pull codestral:22b                    # 13GB — code generation"
echo ""

# ── Step 8: Configure Ollama for Network Access ────────
echo "🌍 Step 8: Exposing Ollama to Tailscale network..."

# Create/update launchd plist to set OLLAMA_HOST
OLLAMA_PLIST="$HOME/Library/LaunchAgents/com.ollama.env.plist"

# Add to shell profile
if ! grep -q "OLLAMA_HOST" ~/.zshrc 2>/dev/null; then
    echo '' >> ~/.zshrc
    echo '# CIPHER OPS — Expose Ollama to Tailscale network' >> ~/.zshrc
    echo 'export OLLAMA_HOST=0.0.0.0' >> ~/.zshrc
    echo '# Allow larger contexts for 32GB Mac' >> ~/.zshrc
    echo 'export OLLAMA_MAX_LOADED_MODELS=2' >> ~/.zshrc
    echo 'export OLLAMA_NUM_PARALLEL=2' >> ~/.zshrc
    echo "   ✅ Added OLLAMA_HOST=0.0.0.0 to ~/.zshrc"
else
    echo "   ✅ OLLAMA_HOST already configured"
fi

# Also set for current session
export OLLAMA_HOST=0.0.0.0
echo "   ✅ Ollama will accept connections from VPS via Tailscale"
echo ""

# ── Step 9: Create a launchd service for Ollama ────────
echo "🔄 Step 9: Setting up Ollama auto-start on boot..."

PLIST_PATH="$HOME/Library/LaunchAgents/com.cipher.ollama.plist"
mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cipher.ollama</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OLLAMA_HOST</key>
        <string>0.0.0.0</string>
        <key>OLLAMA_MAX_LOADED_MODELS</key>
        <string>2</string>
        <key>OLLAMA_NUM_PARALLEL</key>
        <string>2</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ollama.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ollama.err</string>
</dict>
</plist>
PLIST

launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"
echo "   ✅ Ollama will auto-start on boot and restart if it crashes"
echo ""

# ── Step 10: Quick Verification ─────────────────────────
echo "🔍 Step 10: Verifying everything..."
echo ""

sleep 2

# Check Ollama
if curl -s http://localhost:11434/api/tags | grep -q "qwen3"; then
    echo "   ✅ Ollama running — qwen3:30b-a3b loaded"
else
    echo "   ⚠️  Ollama may need a restart: ollama serve"
fi

# Check SSH
if sudo systemsetup -getremotelogin 2>/dev/null | grep -q "On"; then
    echo "   ✅ SSH enabled"
else
    echo "   ⚠️  Enable SSH: System Settings → General → Sharing → Remote Login"
fi

# Check Docker
if command -v docker &>/dev/null; then
    if docker info &>/dev/null; then
        echo "   ✅ Docker running"
    else
        echo "   ⚠️  Docker installed but not running — open Docker Desktop"
    fi
fi

# Check Tailscale
if command -v tailscale &>/dev/null; then
    TS_IP=$(tailscale ip -4 2>/dev/null || echo "")
    if [ -n "$TS_IP" ]; then
        echo "   ✅ Tailscale connected — IP: $TS_IP"
    else
        echo "   ⚠️  Tailscale installed but not connected — open the app and sign in"
    fi
fi

echo ""
echo "============================================"
echo "  ✅ MAC M3 NODE SETUP COMPLETE"
echo "============================================"
echo ""
echo "  Your Mac is now:"
echo "  🧠 Running Ollama with 3 AI models"
echo "  🔑 SSH accessible for remote terminal"
echo "  🌐 Tailscale ready (connect to link with VPS)"
echo "  🐳 Docker ready for containers"
echo "  🔋 Never sleeping, always available"
echo ""
echo "  NEXT STEPS:"
echo "  1. Open Tailscale app → Sign in"
echo "  2. Note your Tailscale IP (100.x.x.x)"
echo "  3. On VPS: install Tailscale too"
echo "  4. Test: ssh $(whoami)@<tailscale-ip>"
echo "  5. Test: curl http://<tailscale-ip>:11434/api/tags"
echo ""
echo "  Your VPS can now use this Mac for AI inference:"
echo "  OLLAMA_FALLBACK_URL=http://<tailscale-ip>:11434"
echo ""
echo "============================================"
