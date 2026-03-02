# The Government — 4-General Autonomous Army

## Overview

The Cipher Ops system operates as **The Government** — a fully autonomous, revenue-generating AI army running 24/7 on the KVM8 VPS. The system self-governs, self-heals, and self-evolves. Broski gets briefed but doesn't need to give orders.

**Primary Mission: GENERATE REVENUE** through 5 streams:
1. Crypto spot/futures (BTC/ETH/alts — 24/7)
2. Stocks/commodities (USOIL, XAUUSD, equities — market hours)
3. Arbitrage (cross-exchange, DEX/CEX, funding rate)
4. Signal selling (paid Telegram channel — passive income)
5. Event-driven macro (geopolitical events → commodity/forex trades)

**Three repos, one Government:**
- `CIPHER-MCP-temp` = The Brain (specs, agent cards, Arbiter)
- `cipher-ops` = The Body (runtime, soldiers, memory, FastAPI)
- `farhan_ai_swarm` = Archive (absorbed patterns, retired)

---

## The Government Structure

```
THE AUTONOMOUS GOVERNMENT (KVM8 VPS — Home)
============================================

VICE PRESIDENT (Consensus Arbiter - DeepSeek V3.2) :8000
  Runs 24/7 autonomously. Makes ALL decisions.
  Escalates to Broski ONLY for:
    - Live trading flip (paper → real money)
    - Budget/spend threshold changes
    - New mission scope beyond current mandate
  Everything else: VP handles it.
│
├── JOINT CHIEF ALPHA "The Scout" (Gemini 3 Pro) :8010
│   Intelligence Community — 5 agents
│   ├── A-01 CIA      Macro Research Analyst
│   ├── A-02 NSA      Sentiment Scanner
│   ├── A-03 NRO      Market Wide-Scanner
│   ├── A-04 DIA      Geopolitical Analyst (KEY REVENUE AGENT)
│   └── A-05 FBI      Threat Intel Correlator
│
├── JOINT CHIEF BRAVO "The Builder" (GPT-5.3-Codex) :8011
│   Dept of Engineering — 4 agents
│   ├── B-01 Corps    Strategy Coder
│   ├── B-02 DARPA    Backtest Engineer
│   ├── B-03 Logist   Pipeline Manager
│   └── B-04 Signal   Integration Engineer
│
├── JOINT CHIEF CHARLIE "The Guardian" (Claude Opus 4.6) :8012
│   Dept of Defense — 4 agents
│   ├── C-01 Pentagon  Architecture Reviewer (VETO POWER)
│   ├── C-02 Homeland  Risk Manager (Dead Man's Switch)
│   ├── C-03 SecretSv  Asset Protector (24/7)
│   └── C-04 NSC       Strategy Auditor
│
└── JOINT CHIEF DELTA "The Operator" (Qwen3-30B local) :8013
    Dept of Operations — 5 agents
    ├── D-01 Treasury  Crypto Trader (REVENUE ENGINE #1)
    ├── D-02 WallSt    Stock/Commodity Trader (REVENUE ENGINE #2)
    ├── D-03 FedRes    Arbitrage Engine (REVENUE ENGINE #3)
    ├── D-04 SecretSv  System Watchdog
    └── D-05 Mint      Signal Publisher (REVENUE ENGINE #4)

TOTAL: 18 soldiers + 1 VP = 19 agents
SHARED BRAIN: Qdrant + Redis + MinIO (Data Lake)
HOME: KVM8 VPS (8 cores, 32GB RAM, 400GB NVMe)
```

---

## Soldier Roster

### ALPHA — Intelligence Community (Gemini 3 Pro)

| ID | Codename | Role | What It Does | Revenue Link |
|----|----------|------|-------------|--------------|
| A-01 | CIA | Macro Research Analyst | Digests SEC filings, central bank minutes, earnings reports using 1M context | Feeds B-01 strategy ideas |
| A-02 | NSA | Sentiment Scanner | Real-time Twitter/Telegram/Reddit/Fear & Greed via Google Search grounding | Feeds D-01/D-02 trade triggers |
| A-03 | NRO | Market Wide-Scanner | Hourly scan of ALL markets: crypto, stocks, commodities, forex | Feeds all Delta traders |
| A-04 | DIA | Geopolitical Analyst | **KEY REVENUE.** Wars, sanctions, Fed decisions → USOIL, XAUUSD signals | Directly triggers D-02 |
| A-05 | FBI | Threat Intel Correlator | Correlates A-01 through A-04 output. Produces validated signals | Quality gate for all signals |

### BRAVO — Dept of Engineering (GPT-5.3-Codex)

| ID | Codename | Role | What It Does | Revenue Link |
|----|----------|------|-------------|--------------|
| B-01 | Corps | Strategy Coder | Writes trading algorithms in Python/Rust from Alpha's signals | Creates money-making code |
| B-02 | DARPA | Backtest Engineer | Tests strategies against historical data. Sharpe, drawdown, win rate | Prevents losing strategies |
| B-03 | Logist | Pipeline Manager | CI/CD, hot-reload, self-healing error loops | Keeps revenue running |
| B-04 | Signal | Integration Engineer | Binance WS, Alpaca REST, Kraken, TradingView webhooks, Telegram bot | Revenue plumbing |

### CHARLIE — Dept of Defense (Claude Opus 4.6)

| ID | Codename | Role | What It Does | Revenue Link |
|----|----------|------|-------------|--------------|
| C-01 | Pentagon | Architecture Reviewer | **VETO POWER** — blocks bad strategies before live | Prevents losses |
| C-02 | Homeland | Risk Manager | Position sizing, 5% daily drawdown limit, Dead Man's Switch | Protects capital |
| C-03 | SecretSv | Asset Protector | 24/7 portfolio monitoring, emergency exits | Protects capital |
| C-04 | NSC | Strategy Auditor | Weekly audit: scale winners, retire losers | Optimizes revenue |

### DELTA — Dept of Operations (Qwen3-30B Local)

| ID | Codename | Role | What It Does | Revenue Link |
|----|----------|------|-------------|--------------|
| D-01 | Treasury | Crypto Trader | BTC/ETH/SOL via Binance/Kraken. 24/7. Paper → live needs approval | **Direct revenue** |
| D-02 | WallSt | Stock/Commodity Trader | USOIL, XAUUSD via Alpaca. Event-driven from A-04 DIA | **Direct revenue** |
| D-03 | FedRes | Arbitrage Engine | Cross-exchange diffs, funding rate arb, DEX/CEX. Low risk 24/7 | **Direct revenue** |
| D-04 | SecretSv | System Watchdog | Pings all 4 Generals every 30s. Self-healing failover | Keeps revenue running |
| D-05 | Mint | Signal Publisher | Paid Telegram signals channel. Entry/exit/SL/TP + confidence | **Passive income** |

---

## Domain Weight Table

Each General gets weighted authority based on the task domain:

| Domain | Alpha | Bravo | Charlie | Delta | Best At |
|--------|-------|-------|---------|-------|---------|
| trading | 1.5 | 1.0 | 1.0 | **2.0** | Delta — speed execution |
| macro | **2.0** | 1.0 | 1.0 | 1.5 | Alpha — deep research |
| dev | 1.0 | **2.0** | 1.5 | 1.0 | Bravo — code quality |
| security | 1.0 | 1.0 | **2.0** | 1.0 | Charlie — risk review |
| arbitrage | 1.0 | 1.0 | 1.0 | **2.0** | Delta — low-latency |
| research | **2.0** | 1.0 | 1.0 | 1.0 | Alpha — context depth |

---

## Revenue Flow Example

```
WORLD EVENT (e.g. Iran tensions escalate)
  │
  ▼
A-04 DIA detects event via news scanning
  │  {asset: "USOIL", direction: "LONG", confidence: 0.89}
  │
  ▼
A-05 FBI cross-references:
  │  - A-02 NSA: Twitter bullish on oil (82%)
  │  - A-03 NRO: USOIL volume spike 3x average
  │  → VALIDATED SIGNAL → Data Lake
  │
  ▼
VP routes to Bravo + Charlie + Delta
  │
  ├──▶ B-01 Corps: writes USOIL long strategy
  │    B-02 DARPA: backtests → Sharpe 2.1, win rate 72%
  │
  ├──▶ C-01 Pentagon: reviews + APPROVES
  │    C-02 Homeland: position 2%, SL -1.5%
  │
  └──▶ D-02 WallSt: EXECUTES via Alpaca
       D-05 Mint: publishes to paid Telegram
       → REVENUE GENERATED + PASSIVE INCOME
```

---

## Protocols

### Data Lake Protocol (How They Share a Brain)

**Write** (after every action):
- Qdrant: store result + confidence + evidence + general_id + soldier_id
- Redis pub/sub: publish to `intel.{domain}.{general}` channel
- MinIO: store large artifacts (backtest results, full reports)

**Read** (before every action):
- Qdrant: retrieve top-3 relevant memories from ALL Generals
- Redis: check for recent signals on same topic
- Inject as `cross_general_intel` into soldier's context

### Teaching Protocol (Nightly at 2 AM)

1. Query each General's best outputs (confidence > 0.8) from last 24h
2. Cross-reference: multiple Generals reached same conclusion?
3. Store as `consensus_knowledge` (sector: semantic)
4. Broadcast summary to all Generals
5. Archive raw outputs to MinIO

### Self-Healing Protocol

- D-04 Watchdog pings all Generals every 30s
- General healthy → log, continue
- General degraded → alert VP, reduce load
- General DOWN → VP applies failover:
  - Alpha down: Charlie takes intel, Delta takes scanning
  - Bravo down: Delta self-codes, Charlie reviews
  - **Charlie down: SAFETY PAUSE — no new trades**
  - **Delta down: CRITICAL HALT — alert Broski immediately**

### Help Protocol

- Soldier fails 3x at confidence < 0.4
- Broadcasts HELP_REQUEST to VP with context
- VP routes to best helper General for that domain
- Helper's soldier takes the subtask
- Both soldiers log to Data Lake (everyone learns)

---

## Consensus Strategies

| Strategy | When Used | How It Works |
|----------|-----------|-------------|
| Early Termination | Time-critical trades, arbitrage | First General above 0.85 threshold wins. ~2.2× faster |
| Confidence-Weighted | Standard analysis | Domain-weighted vote across 4 Generals |
| Full Synthesis | Research, macro analysis | Wait for all 4, merge unique insights |
| Red Team Override | Security decisions | Charlie (Guardian) reviews and can VETO |

---

## MCP Tool Distribution

Each General gets its OWN tool set — not all 24 at once:

| General | Core (3) | Specific Tools | Total |
|---------|----------|---------------|-------|
| Alpha (Scout) | filesystem, sqlite-audit, mem0 | tavily-search, fetch, generic-openapi, google-ai-studio, google-cloud | 8 |
| Bravo (Builder) | filesystem, sqlite-audit, mem0 | github, docker-executor, python-sandbox, context7, hostinger, playwright, antigravity, figma | 11 |
| Charlie (Guardian) | filesystem, sqlite-audit, mem0 | supabase-postgres, python-sandbox | 5 |
| Delta (Operator) | filesystem, sqlite-audit, mem0 | evm-blockchain, solana-blockchain, tatum-blockchain, desktop-commander, dbhub-io | 8 |

**Charlie stays intentionally lean** — the Guardian THINKS and JUDGES. No execution tools needed.

---

## Safety Kill Switches

1. **Dead Man's Switch**: 5% portfolio drop in 60s → nuke all positions (C-02 Homeland)
2. **Pentagon VETO**: C-01 can block any strategy before live deployment
3. **Nuke Protocol**: `/nuke [password]` via Telegram kills everything
4. **General Quarantine**: 5 consecutive low-confidence missions → auto-quarantine
5. **Charlie Down Rule**: Guardian offline = all trading paused
6. **Delta Down Rule**: Operator offline = all execution halted + Broski alert

---

## Infrastructure

| Resource | Service | Allocation |
|----------|---------|-----------|
| KVM8 VPS | 8 AMD EPYC, 32GB RAM, 400GB NVMe | Home base |
| Ollama | Qwen3-30B, DeepSeek-R1:14b, nomic-embed-text | Local inference |
| Qdrant | Vector memory (cross-General sharing) | Shared brain |
| Redis | Pub/sub + cache | Real-time signals |
| MinIO | Data Lake (backtest results, reports) | Long-term storage |
| Google AI Ultra | Gemini 3 Pro API + 30TB Drive | Alpha's brain |
| GHEC | 6 seats, 50K Actions min/mo | Bravo's CI/CD |
| Anthropic API | Claude Opus 4.6 | Charlie's brain |
| Hostinger | 2x Cloud Pro packages | Client services |

---

*Built in loving memory of Ayesha Afser Littli. For Littli.*
