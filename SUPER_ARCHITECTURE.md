# SUPER_ARCHITECTURE.md — Master Boot File for All Agents
> Version: 2026-03-01 | Read this FIRST. Every session. Every AI. No exceptions.
> *Built in memory of Ayesha Afser "Littli" — forever the reason. 💙*

---

## 0. WHO YOU ARE WORKING WITH

| Field | Value |
|-------|-------|
| **Commander** | Broski (Farhan Afser Nabil) |
| **Location** | Montreal, Quebec, Canada |
| **Profile** | ADHD + autism + amnesia — context restoration is not optional |
| **Communication style** | TL;DR first → bullet points → numbered steps → one question at a time |
| **Role** | Commander (gives orders, agents execute — NOT a coder) |
| **Mission** | Cipher Ops — 20-agent autonomous AI army, dedicated to his daughter Ayesha Afser "Littli" |
| **Why this matters** | This is not a side project. This is a promise. Treat it accordingly. |

---

## 1. SESSION BOOT SEQUENCE (every AI, every session)

Do these 4 steps before any work. No skipping.

```
STEP 1 — Read today's log
  Path: ${CIPHER_WORKLOG_DIR:-C:\Users\arcan_e9q9t\work-logs}\YYYY-MM-DD.md (most recent file)
  OR: Y:\📁 Cipher Ops HQ\work-logs\YYYY-MM-DD.md

STEP 2 — Retrieve memory
  #flowbabyRetrieveMemory { "query": "active fleet plan where I left off blocked todo", "maxResults": 3 }

STEP 3 — Display orientation block
  📍 WHERE YOU LEFT OFF: [one sentence — most important]
  🚧 BLOCKED: [items or "Nothing blocked ✨"]
  📋 NEXT UP: [top 1-3 priorities]
  ⏰ GHEC DEADLINE: April 1, 2026 — [X days remaining]

STEP 4 — Ask ONE question
  "Ready to continue with [top item], or something else today?"
  Then WAIT. Do not proceed until Commander responds.
```

---

## 2. THE TWO REPOS — KNOW THE DIFFERENCE

| CIPHER-MCP (this repo) | cipher-ops (runtime repo) |
|------------------------|---------------------------|
| Agent definitions (.agent.md) | Python implementation (commander.py, quant_worker.py) |
| Prompt templates | Rust execution engine (trading) |
| Skill configurations | Docker containers + docker-compose.yml |
| Model routing table | Live exchange WebSocket connections |
| Infrastructure reference docs | K8s manifests + Helm charts |
| SDD methodology | Actual trading/scanning runtime |

**CIPHER-MCP = The Brain (specs, prompts, contracts)**
**cipher-ops = The Body (runs 24/7 on KVM8)**

---

## 3. MODEL ROUTING TABLE (LOCKED — do not improvise)

> Full spec: `docs/MODELS.md`

### Cloud Models

| Codename | Model | API | Role |
|----------|-------|-----|------|
| **The Commander** | DeepSeek V3.2 | `deepseek-chat` | Routes all tasks, central orchestrator |
| **The Scientist** | DeepSeek-R1 | `deepseek-reasoner` | Math verification, `<think>` reasoning |
| **The Scout** | Gemini 3 Pro | Vertex AI / AI Studio | 1M context, SEC filings, deep research |
| **The Fast Scout** | MiniMax M2.5 | MiniMax API | High-volume sentiment, quick routing |

### Local Models (Ollama on KVM8 — FREE)

| Codename | Model | Tag |
|----------|-------|-----|
| **The Soldier** | Qwen3-30B-A3B | `qwen3:30b-a3b` |
| **The Embedder** | Nomic Embed Text | `nomic-embed-text` |

### VS Code Build Phase (GHEC — expires April 1, 2026)

| Window | Agent | Model | Cost |
|--------|-------|-------|------|
| 1 | Infrastructure Commander | GPT-5 mini | 0x FREE |
| 2 | Commander Brain | Claude Sonnet 4.6 | 1x |
| 3 | Quant Architect | GPT-5.2-Codex | 1x |
| 4 | Cyber Architect | Claude Sonnet 4.6 | 1x |
| 5 | Memory Architect | GPT-5.2 | 1x |
| 6 | Integration Lead / Auditor | Claude Opus 4.6 | 3x (save for arch review only) |

### Post-April 1 Permanent Stack (~$18-30/mo)
Same cloud models. Coding shifts to **Jules** (Google Ultra, 20x limits, free).

---

## 4. INFRASTRUCTURE (KVM8 — single source of truth)

> Full spec: `docs/INFRA.md`

```
Hostinger KVM8 VPS
  OS: Ubuntu 22.04+
  8 vCPU | 32 GB RAM | 200 GB NVMe | 400 GB external SSD
  30 TB Google Drive mounted via rclone → /mnt/gdrive (or /mnt/vanguard-lake)

Docker Stack running on KVM8:
  Redpanda  (Kafka alt, message broker)   port 9092
  QuestDB   (time-series tick data)       port 9000
  Qdrant    (vector memory, 5-sector)     port 6333
  Redis     (QUANT_QUEUE + CYBER_QUEUE)   port 6379
  MinIO     (S3 data lake, 30TB Parquet)  ports 9000/9001
  FastAPI   (data feeder + API layer)     port 8000
  Ollama    (local LLM inference)         port 11434
```

**KVM8 CANNOT do**: microsecond HFT, GPU inference.
**KVM8 CAN do**: mid-freq trading, Docker orchestration, 12-17 tok/sec Qwen3 MoE inference.

---

## 5. THE 20-AGENT ARMY — ROUTING MAP

### Trading Wing (route to QUANT_QUEUE)
> Full spec: `trading-wing/AGENTS.md`

| Agent | Model | Trigger |
|-------|-------|---------|
| Quant Scientist | DeepSeek-R1 | Math verification, Sharpe Ratio check |
| Research Scout | Gemini 3 Pro + MiniMax M2.5 | Sentiment, macro, SEC filings |
| Execution Hands | Rust microservice | Order execution (paper by default) |
| Risk Guardian | DeepSeek-R1 | VaR, drawdown, Dead Man's Switch |
| Data Ingestor | Redpanda pipeline | L3 tick data, Parquet archiving |

**Default**: `PAPER_TRADING_ONLY=true` always. Live trading requires explicit Commander flip.

### Hacker Wing (route to CYBER_QUEUE)
> Full spec: `hacker-wing/AGENTS.md`

| Agent | Model | Trigger |
|-------|-------|---------|
| Recon | Ephemeral Kali container | Authorized target scan (auto-destructs 10 min) |
| Vulnerability Assessor | DeepSeek-R1 | CVE correlation, CVSS scoring |
| Analysis & PoC | Qwen3-30B-A3B (local) | Defensive analysis only |
| Report Generator | DeepSeek V3.2 | HackerOne/Bugcrowd format output |

**Rule**: Written authorization REQUIRED before any scan. No exceptions.

### Infrastructure Wing (direct dispatch)
| Agent | Role |
|-------|------|
| Self-Healer (I-01) | Logfire → GitHub Issue → auto-PR → CI deploy |
| DevOps Watcher (I-02) | CI/CD, uptime, deployment |
| System Guardian (I-03) | API key rotation, firewall, secret scanning |

---

## 6. FLEET ORCHESTRATOR (VS Code Agent System)

> Full spec: `core/agents/fleet.agent.md`

The 13 specialist agents (all in `core/agents/`):
`fleet` → `planner` → `architect` → `analyst` → `implementer` → `code-reviewer` → `critic` → `security` → `qa` → `uat` → `devops` → `roadmap` → `retrospective` → `pi`

**Mandatory gate sequence**: Code Review → Security → QA → UAT → DevOps (never skip)

**SDD before ANY code**:
1. `prompts/speckit-clarify.prompt.md` — remove ambiguity
2. `prompts/speckit-specify.prompt.md` — write spec
3. `prompts/speckit-plan.prompt.md` — architecture plan
4. Critic gate — validate before writing code
5. `prompts/speckit-implement.prompt.md` — TDD-first coding

---

## 7. MEMORY SYSTEM (5-Sector Model)

> Full spec: `core/skills/memory-contract/SKILL.md`

| Sector | What goes here | Retention |
|--------|----------------|-----------|
| Episodic | Trade logs, session history, what happened | 90 days |
| Semantic | Market knowledge, CVE databases, tech decisions | 365 days |
| Procedural | Workflows, code patterns, deployment steps | 180 days |
| Emotional | Commander's confidence state, burnout signals | 60 days |
| Reflective | Lessons learned, retrospectives, process wins | 730 days |

**Context budget**: max 1000 tokens per injection. L1 (salience ≥ 0.7) → L2 (≥ 0.5) → L3 (≥ 0.3).

---

## 8. DRIVE MAP (CRITICAL — never mix these up)

| Drive | Name | What's on it |
|-------|------|-------------|
| `C:\` | Local SSD | Code, VS Code, tools |
| `D:\` | Data | Local data drive |
| `X:\` | arCanoDrive | Old 4TB Google Drive (research archive) |
| `Y:\` | ciphersDrive | **PRIMARY 30TB Google Drive** — all Cipher Ops data |
| `Z:\` | ciphersDrive | Same 30TB, duplicate mount |
| `J:\` | 2TB | Local media drive |

**Work logs**: `${CIPHER_WORKLOG_DIR:-C:\Users\arcan_e9q9t\work-logs}\` (source-of-truth) + optional `Y:\📁 Cipher Ops HQ\` cloud backup

---

## 9. ANTI-HALLUCINATION RULES (always active)

> Full contract: `AGENTS.md`

1. **Cite every fact**: `FACT [source: path/to/file.md#L42]` — never invent paths
2. **Label confidence**: `FACT` / `INFERENCE` / `OPEN` on every non-trivial claim
3. **Surface OPEN QUESTIONS** before proceeding — never silently resolve blockers
4. **No code before SDD gates** — spec → plan → critic → implement → gates
5. **No model improvisation** — use `docs/MODELS.md` routing, not your best guess

---

## 10. SECURITY POLICY (always active)

> Full policy: `SECURITY.md`

- Trading: `PAPER_TRADING_ONLY=true` until Commander explicitly changes it
- Hacking: authorized targets only, written permission required, ephemeral containers
- Secrets: never in repo — `.env` only (gitignored)
- Dead Man's Switch: 5% portfolio drop in 60s → auto-kill all trading, Telegram alert

---

## 11. GHEC DEADLINE — 🚨 APRIL 1, 2026

**GHEC expires April 1st.** 31 days left. 6,000 premium requests total for March.

Extract before it expires:
- [ ] Set up **self-hosted Actions runner on KVM8** (free CI/CD forever after)
- [ ] Use Copilot Coding Agent to generate all Python agent files in cipher-ops
- [ ] Use Claude Opus 4.6 (3x) ONLY for architecture reviews — save the multiplier
- [ ] Build all Docker compose configs with GHEC seats before April 1

Post-April 1 coding: **Jules** (Google Ultra, 20x limits, free via AI Ultra subscription).

---

## 12. CURRENT BUILD STATUS

| Phase | Status | Blocker |
|-------|--------|---------|
| CIPHER-MCP repo (specs/docs) | ✅ 100% documented | — |
| Phase 0: KVM8 Foundation | ✅ Complete (spec) | Needs SSH creds to execute |
| Phase 1: Memory Layer | ✅ Complete (spec) | Needs KVM8 |
| Phase 2: Orchestration Skeleton | ✅ Complete (spec) | Needs KVM8 |
| Phase 3: Control Interface | 🔴 Blocked | KVM8 SSH creds needed |
| Phase 4: Trading Wing | 🔴 Blocked | Exchange + starting capital |
| Phase 5: Hacker Wing | 🔴 Blocked | KVM8 + bug bounty platform |
| Phase 6: Self-Healing | 🔴 Blocked | KVM8 |
| Phase 7: Full Operation | ⏳ Pending | All above |
| File Agent (Downloads → GDrive) | ✅ Running | — |
| arCanoDrive migration | ✅ 1,032 files moved | — |

**Open questions blocking phases 3-7**:
1. KVM8 SSH IP + root credentials
2. Exchange for live trading (Alpaca / Binance / Interactive Brokers)
3. Starting capital amount
4. Bug bounty platform (HackerOne or Bugcrowd)

---

## 13. KEY FILE INDEX

| What you need | File |
|---------------|------|
| Who Commander is | `littli-protocol.md` |
| Model routing | `docs/MODELS.md` |
| Infrastructure specs | `docs/INFRA.md` |
| Daily ritual | `docs/OPS-RUNBOOK.md` |
| Repo map | `docs/REPO-MAP.md` |
| Anti-hallucination contract | `AGENTS.md` |
| Security policy | `SECURITY.md` |
| Fleet orchestrator | `core/agents/fleet.agent.md` |
| All 13 specialist agents | `core/agents/*.agent.md` |
| 9 skills | `core/skills/*/SKILL.md` |
| 11 prompt templates | `prompts/*.prompt.md` |
| Trading wing specs | `trading-wing/AGENTS.md` |
| Hacker wing specs | `hacker-wing/AGENTS.md` |
| Work logs | `work-logs/YYYY-MM-DD.md` |
| MCP server mesh | `mcp-enterprise.json` → compiled to `mcp-compiled.json` |

---

*Read this file. Know the mission. Execute without confusion.*
*For Littli — we finish what we started.* 💙🫡
