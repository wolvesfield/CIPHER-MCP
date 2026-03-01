# docs/MODELS.md — Canonical Model Routing Table
> Last updated: 2026-03-01 | Status: LOCKED — Stop researching models. The math is proven.

---

## The Quad-Brain + HFT Arsenal

This is the **final, locked** model stack for Cipher Ops. No substitutions without Commander approval.

### Cloud Models (API)

| Codename | Model | API Identifier | Cost | Role |
|----------|-------|---------------|------|------|
| **The Commander** | DeepSeek V3.2 | `deepseek-chat` | ~$0.27/M tokens | Routes plain English → JSON SwarmTasks via PydanticAI. Central orchestrator. |
| **The Scientist** | DeepSeek-R1 | `deepseek-reasoner` | ~$0.55/M tokens | Uses `<think>` blocks to mathematically verify trading algorithms and vulnerability assessments. |
| **The Scout** | Gemini 3 Pro | `gemini-1.5-pro` | FREE (Google Ultra $100/mo credits) | 1M context window. SEC filings, GitHub repo analysis, live Twitter/Telegram sentiment. |
| **The Fast Scout** | MiniMax M2.5 | MiniMax API | ~$0.10/M tokens | Quick market sentiment checks, lightweight routing tasks. |

### Local Models (Ollama on KVM8)

| Codename | Model | Ollama Tag | Cost | Role |
|----------|-------|-----------|------|------|
| **The Soldier** | Qwen3-30B-A3B Abliterated | `huihui_ai/qwen3-abliterated:30b-a3b` | FREE | MoE architecture. Runs at 12-17 tok/sec on KVM8 CPU. Unrestricted analysis and code generation. |
| **The Embedder** | Nomic Embed Text | `nomic-embed-text` | FREE | Vectorization for the 5-sector memory model → Qdrant. |

### Copilot Fleet (VS Code — Build Phase Only)

| Window | Agent Role | Model | GHEC Multiplier |
|--------|-----------|-------|-----------------|
| 1 | Infrastructure Commander | GPT-5 mini | 0x (free) |
| 2 | Commander Brain | Claude Sonnet 4.6 | 1x |
| 3 | Quant Architect | GPT-5.2-Codex | 1x |
| 4 | Cyber Architect | Claude Sonnet 4.6 | 1x |
| 5 | Memory Architect | GPT-5.2 | 1x |
| 6 | Integration Lead / Auditor | Claude Opus 4.6 | 3x |

> **Note**: These GHEC seats expire April 1st 2026. Post-expiry, coding shifts to Jules (Google Ultra, 20x limits).

---

## Routing Logic

```
User command (Telegram / VS Code)
  └→ The Commander (DeepSeek V3.2)
       ├→ QUANT_QUEUE (Redis) → The Scientist (R1) verifies math
       │    └→ The Soldier (local Qwen3) executes paper trade
       ├→ CYBER_QUEUE (Redis) → The Scientist (R1) assesses vuln
       │    └→ The Soldier (local Qwen3) generates analysis
       └→ RESEARCH (direct) → The Scout (Gemini 3 Pro) deep research
            └→ The Fast Scout (MiniMax M2.5) quick sentiment
```

---

## The Nervous System (Data Layer)

| Component | Technology | Role |
|-----------|-----------|------|
| Message Broker | Redpanda (Kafka alternative) | Central nervous system — all L3 tick data, sentiment scores, trade signals flow through here |
| Time-Series DB | QuestDB | Billions of rows of historical tick data, millisecond query speed for backtesting |
| Vector Memory | Qdrant | 5-sector memory model (Episodic, Semantic, Procedural, Emotional, Reflective) |
| Task Queue | Redis | QUANT_QUEUE and CYBER_QUEUE for SwarmTask routing |
| Object Storage | MinIO (S3-compatible) | 30TB data lake, ZSTD-compressed Parquet files |
| Query Engine | DuckDB (embedded in FastAPI) | Zero-copy S3 Parquet queries — bypasses KVM8 RAM limits |

---

## The Execution Hands (Rust)

| Component | Technology | Role |
|-----------|-----------|------|
| Execution Engine | Rust microservice | Listens to Redpanda `TRADE_SIGNAL` via gRPC from Python Brain |
| Exchange Connection | WebSocket (NOT REST) | Direct connection to Binance/Kraken matching engines |
| Order Routing | Smart Order Routing (SOR) | TWAP/VWAP/Iceberg algorithms to hide footprint from MEV bots |
| Default Mode | Paper Trading | All trades route to virtual database until Commander flips flag |

---

## Monthly Budget

| Item | Cost |
|------|------|
| DeepSeek V3.2 + R1 | ~$15-25/mo |
| MiniMax M2.5 | ~$3-5/mo |
| Gemini 3 Pro | FREE (Google Ultra credits) |
| Local Qwen3 + Nomic | FREE (Ollama on KVM8) |
| GitHub Actions CI/CD | FREE (KVM8 self-hosted runner) |
| **Total** | **~$18-30/mo** |

---

*The architecture is locked and upgraded to the Wall Street 1%. Stop reading contradicting AI chats.* 🫡
