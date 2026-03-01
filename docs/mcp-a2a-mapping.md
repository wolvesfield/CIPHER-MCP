# MCP → A2A Skill Mapping

> **Source of truth**: How all 24 MCP servers in `mcp-compiled.json` become callable A2A skills
> that any General (Alpha/Bravo/Charlie) can invoke through the Consensus Arbiter.
>
> Bridge service: `arbiter/mcp_a2a_bridge.py` — runs on port 8001

---

## Architecture: The Southbound Bridge

```
Commander (Broski) → Telegram / CLI
         ↓
Consensus Arbiter  (port 8000)
 ├── General Alpha  (Gemini 3 Pro — cloud)
 ├── General Bravo  (GPT-4.1 — cloud)
 └── General Charlie(Qwen3-14B — local Ollama)
         ↓ Generals call tools via
MCP → A2A Bridge   (port 8001)        ← YOU ARE HERE
 ├── mcp-playwright        (browser automation)
 ├── mcp-evm-blockchain    (crypto trading)
 ├── mcp-docker-executor   (container ops)
 └── ... 24 MCP servers total
```

**Flow for a mission** (e.g., "scan target.com for vulnerabilities"):
1. Commander sends SwarmTask to Arbiter at `POST /tasks/send`
2. Arbiter fans out to all 3 Generals in parallel
3. Each General decides which tools it needs
4. General calls `POST /tools/invoke` on the Bridge with `skill_id: "mcp-playwright"`
5. Bridge spawns MCP stdio subprocess, pipes JSON-RPC 2.0, returns result
6. General uses result in its analysis, returns vote with confidence score
7. Arbiter runs consensus strategy, returns final decision

---

## A2A Invocation Format

Any General invokes a skill by posting to the Bridge:

```http
POST http://localhost:8001/tools/invoke
Content-Type: application/json

{
  "skill_id": "mcp-playwright",
  "method": "tools/call",
  "params": {
    "name": "navigate",
    "arguments": { "url": "https://target.com" }
  },
  "timeout_sec": 30
}
```

Response:
```json
{
  "skill_id": "mcp-playwright",
  "success": true,
  "result": { "content": "...", "status": 200 },
  "error": null,
  "latency_ms": 1240
}
```

---

## MCP Server → A2A Skill ID Mapping

### 🔐 HACKING Domain (7 Skills)

| A2A Skill ID | MCP Server | What it Does | Used By |
|---|---|---|---|
| `mcp-playwright` | playwright | Browser automation, DOM inspection, form fuzzing | H-01 Recon, H-04 Web Tester |
| `mcp-puppeteer` | puppeteer | Headless Chrome, screenshot capture, JS execution | H-04 Web Tester |
| `mcp-chrome-devtools` | chrome-devtools | Network traffic inspection, JS debugging, cookie capture | H-04 Web Tester |
| `mcp-browser-devtools-generic` | browser-devtools-generic | Cross-browser devtools protocol | H-04 Web Tester |
| `mcp-antigravity-browser` | antigravity-browser | Stealth browser with anti-fingerprint for recon | H-01 Recon |
| `mcp-fetch` | fetch | Raw HTTP requests for endpoint discovery + fuzzing | H-01 Recon, H-05 SQL Hunter |
| `mcp-hostinger-api` | hostinger-api | Hostinger KVM8 server management | H-01 Recon, I-02 DevOps |

**Example: H-01 Recon scanning a target**
```json
{
  "skill_id": "mcp-antigravity-browser",
  "method": "tools/call",
  "params": {
    "name": "navigate_stealth",
    "arguments": { "url": "https://target.com", "follow_subdomains": true }
  }
}
```

---

### 📈 TRADING Domain (5 Skills)

| A2A Skill ID | MCP Server | What it Does | Used By |
|---|---|---|---|
| `mcp-evm-blockchain` | evm-blockchain | Ethereum/EVM: prices, balances, DeFi reads, gas fees | T-07 Trader, T-02 Technical |
| `mcp-solana-blockchain` | solana-blockchain | Solana: SPL tokens, NFT floors, dApp queries | T-03 Sentiment, T-07 Trader |
| `mcp-tatum-blockchain` | tatum-blockchain | Multi-chain: BTC, ETH, SOL, MATIC — unified API | T-01 Market Analyst |
| `mcp-supabase-postgres` | supabase-postgres | Trade history, positions, P&L records | T-09 Portfolio Manager, T-10 Analyst |
| `mcp-dbhub-io` | dbhub-io | SQLite DB for local backtest storage | T-02 Technical, T-05/T-06 |

**Example: T-07 Trader checking ETH price before order**
```json
{
  "skill_id": "mcp-evm-blockchain",
  "method": "tools/call",
  "params": {
    "name": "get_token_price",
    "arguments": { "token": "ETH", "chain": "mainnet", "vs_currency": "usd" }
  }
}
```

---

### 🛠️ DEV / INFRA Domain (7 Skills)

| A2A Skill ID | MCP Server | What it Does | Used By |
|---|---|---|---|
| `mcp-docker-executor` | docker-executor | Spawn / stop containers on KVM8 | I-01 Self-Healer, I-02 DevOps |
| `mcp-kubernetes-cluster` | kubernetes-cluster | k3s pod management on KVM8 | I-02 DevOps |
| `mcp-google-cloud` | google-cloud | GCS bucket ops, Cloud Run deploys | I-03 System Guardian |
| `mcp-python-secure-sandbox` | python-secure-sandbox | Safe Python execution for backtests and analysis | T-02 Technical, H-03 Exploit Analyst |
| `mcp-generic-openapi` | generic-openapi | Call any REST API from an OpenAPI spec | All agents |
| `mcp-figma-remote` | figma-remote | Design file reading for front-end generation | I-01 Self-Healer (UI fixes) |
| `mcp-github-enterprise-cloud` | github-enterprise-cloud | PR creation, issue management, code push via GHEC | I-01 Self-Healer, Fleet |

**Example: I-01 Self-Healer auto-creating a fix PR**
```json
{
  "skill_id": "mcp-github-enterprise-cloud",
  "method": "tools/call",
  "params": {
    "name": "create_pull_request",
    "arguments": {
      "repo": "wolvesfield/CIPHER-MCP",
      "title": "auto-fix: agent-registry null pointer in routing",
      "body": "Self-Healer detected error at 2026-03-01T04:22:11Z. Auto-fix applied.",
      "branch": "self-heal/2026-03-01-agent-registry"
    }
  }
}
```

---

### 🧠 CORE Domain (5 Skills)

> Core skills available to all Generals for memory, communication, and filesystem ops.

| A2A Skill ID | MCP Server | What it Does | Used By |
|---|---|---|---|
| `mcp-filesystem` | filesystem | Read/write files on KVM8 at `/cipher-ops/` | All agents |
| `mcp-memory` | memory | Persistent KV memory store (long-term agent memory) | All agents |
| `mcp-sequential-thinking` | sequential-thinking | Chain-of-thought scaffolding for multi-step problems | Fleet, Arbiter |
| `mcp-everything` | everything | Ultra-fast local file indexing + search on KVM8 | I-01 Self-Healer |
| `mcp-telegram` | telegram | Send Telegram notifications and receive commands | I-03 System Guardian, Arbiter |

**Example: Arbiter escalating to Commander via Telegram**
```json
{
  "skill_id": "mcp-telegram",
  "method": "tools/call",
  "params": {
    "name": "send_message",
    "arguments": {
      "chat_id": "${TELEGRAM_CHAT_ID}",
      "text": "🚨 Arbiter Escalation: 3 Generals disagree on BTC trade. Review needed."
    }
  }
}
```

---

## Discovery Endpoints

Once the Bridge is running on KVM8:

```bash
# List all registered skills
GET http://localhost:8001/tools

# Filter by domain
GET http://localhost:8001/tools/by-domain/hacking
GET http://localhost:8001/tools/by-domain/trading
GET http://localhost:8001/tools/by-domain/dev
GET http://localhost:8001/tools/by-domain/core

# A2A Agent Card (auto-generated from registry)
GET http://localhost:8001/.well-known/agent.json
```

---

## Deployment on KVM8

```bash
# From /cipher-ops/arbiter/
pip install fastapi uvicorn httpx pydantic

# Start Bridge (exposes all MCP tools as A2A skills)
uvicorn mcp_a2a_bridge:bridge_app --host 0.0.0.0 --port 8001

# Start Arbiter (dispatches to 3 Generals)
python consensus_arbiter.py
```

As systemd services (add to `/etc/systemd/system/`):

```ini
# /etc/systemd/system/cipher-arbiter.service
[Unit]
Description=Cipher Ops Consensus Arbiter
After=network.target

[Service]
WorkingDirectory=/cipher-ops/arbiter
ExecStart=/usr/bin/python3 consensus_arbiter.py
Restart=always
Environment=GENERAL_ALPHA_URL=http://localhost:8010
Environment=GENERAL_BRAVO_URL=http://localhost:8011
Environment=GENERAL_CHARLIE_URL=http://localhost:8012
Environment=TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
Environment=TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}

[Install]
WantedBy=multi-user.target
```

```ini
# /etc/systemd/system/cipher-mcp-bridge.service
[Unit]
Description=Cipher Ops MCP→A2A Bridge
After=network.target

[Service]
WorkingDirectory=/cipher-ops/arbiter
ExecStart=uvicorn mcp_a2a_bridge:bridge_app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Port Map (KVM8)

| Port | Service |
|------|---------|
| 8000 | Consensus Arbiter |
| 8001 | MCP→A2A Bridge |
| 8010 | General Alpha (Gemini proxy) |
| 8011 | General Bravo (GPT proxy) |
| 8012 | General Charlie (Qwen3 local via Ollama) |
| 6333 | Qdrant (vector memory) |
| 5432 | PostgreSQL (trade history) |
| 6379 | Redis (session state) |
| 11434 | Ollama (local models) |

---

*Cipher Ops Legacy Foundation — for Littli 💙*
