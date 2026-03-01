# trading-wing/AGENTS.md — Trading Wing Agent Specifications
> Last updated: 2026-03-01 | Status: SPEC ONLY — Implementation lives in cipher-ops repo.

---

## Overview

The Trading Wing operates a 5-agent adversarial pipeline. No single agent can approve a trade alone. The Bullish and Bearish Researchers debate every signal before the Execution Hands touch an order. All trades default to **paper mode** until Commander flips `PAPER_TRADING_ONLY=false`.

---

## Agent: Quant Scientist

- **Model**: DeepSeek-R1 (`deepseek-reasoner`)
- **Role**: Mathematical verification of every trade signal using `<think>` extended reasoning blocks.
- **Responsibilities**:
  - Calculate RSI, MACD, Bollinger Bands, volume profiles on incoming tick data.
  - Verify Sharpe Ratio is positive before any trade is approved.
  - Run Monte Carlo simulations for position sizing.
  - Publish verified signals to `QUANT_QUEUE` (Redis).
- **Hard Constraint**: If Sharpe Ratio < 0 or max drawdown > 5% triggered → veto the trade.
- **Output**: Verified trade signal JSON → Redis `QUANT_QUEUE`.

---

## Agent: Research Scout

- **Models**: Gemini 3 Pro (The Scout) + MiniMax M2.5 (The Fast Scout)
- **Role**: Market context, sentiment, and macro intelligence gathering.
- **Responsibilities**:
  - Monitor live Reddit, Twitter/X, Telegram channels for sentiment signals.
  - Ingest SEC filings, earnings reports, macro news via Gemini's 1M context window.
  - MiniMax M2.5 handles high-volume quick sentiment checks (volume threshold: >100 signals/min).
  - Gemini 3 Pro handles deep research (SEC 10-K analysis, GitHub repo analysis for crypto).
- **Output**: Sentiment score + macro context → Quant Scientist for final verification.

---

## Agent: Execution Hands

- **Stack**: Rust microservice (not Python — latency-critical)
- **Role**: Order execution with minimal market footprint.
- **Responsibilities**:
  - Listens to `TRADE_SIGNAL` topic on Redpanda via gRPC from Python Brain.
  - Connects to exchange via **WebSocket** (NOT REST — too slow).
  - Smart Order Routing (SOR): TWAP / VWAP / Iceberg algorithms to hide footprint from MEV bots.
  - All trades routed to **paper trading virtual database** by default.
- **Default Mode**: `PAPER_TRADING_ONLY=true` — all signals simulate against live prices, no real orders.
- **Live Mode**: Commander explicitly sets `PAPER_TRADING_ONLY=false` in `.env` + confirms via Telegram.
- **Exchanges**: Binance (crypto), Kraken (alt), Alpaca (US equities) — configured in `.env`.

---

## Agent: Risk Guardian

- **Model**: DeepSeek-R1 (`deepseek-reasoner`)
- **Role**: Portfolio-level risk enforcement with veto power over all trades.
- **Responsibilities**:
  - Monitor portfolio balance via **read-only API key** (no trading permissions on this key).
  - Enforce hard limits:
    - Max drawdown: **5% in 60 seconds** → Dead Man's Switch triggers.
    - Max drawdown: **10% in 24 hours** → All trading paused, Telegram alert sent.
    - Max position size: **15% of portfolio** per single asset.
  - VaR (Value at Risk) calculation on every proposed position.
  - **Dead Man's Switch** (automated, bypasses all AI): balance drops 5% in 60s → revoke trading API keys → cancel all open orders → market-sell to USDC → Telegram `/nuke` alert to Commander.
- **Veto Power**: Risk Guardian can block any trade. No other agent can override.
- **Output**: APPROVED / VETOED JSON → Execution Hands.

---

## Agent: Data Ingestor

- **Role**: L3 tick data pipeline — the nervous system for all trading decisions.
- **Stack**: Redpanda (Kafka alternative) → QuestDB → MinIO data lake.
- **Responsibilities**:
  - Connect to exchange WebSocket feeds for L3 order book data (bid/ask, volume, timestamp).
  - Publish raw ticks to Redpanda `TICK_RAW` topic.
  - QuestDB ingests ticks → millisecond-resolution time-series for backtesting.
  - MinIO stores compressed Parquet files: `/domain=trading/year=YYYY/month=MM/day=DD/`.
  - Triggers Quant Scientist when new signal thresholds are crossed.
- **Compression**: Snappy (read-optimized for backtesting) or ZSTD (storage-optimized for archive).

---

## Operational Flow

```
Commander issues /trade [pair] [instruction]
  └→ DeepSeek V3.2 (Commander) routes to QUANT_QUEUE (Redis)
       └→ Research Scout: Gemini 3 Pro pulls macro context + MiniMax M2.5 sentiment scan
            └→ Quant Scientist: DeepSeek-R1 <think> math verification
                 └→ Risk Guardian: DeepSeek-R1 VaR check + drawdown validation
                      └→ If APPROVED → Execution Hands (Rust): SOR → Exchange WebSocket
                           └→ Data Ingestor: log trade → QuestDB + MinIO + Qdrant
                                └→ Performance report → Telegram notification to Commander
```

---

## Paper Trading → Live Trading Gate

| Stage | Requirement | Duration |
|-------|------------|---------|
| Paper Only | Default mode | Until manual Commander override |
| Paper Parallel | Run paper + live simultaneously, compare decisions | 30 days minimum |
| Live Full | Commander approves after positive Sharpe Ratio sustained | Post 30-day proof |

**Rule**: The army paper trades first. No exceptions. Prove the math before real money moves.

---

## Data Flow Diagram

```
Exchange WebSocket (L3 ticks)
  └→ Data Ingestor → Redpanda TICK_RAW
       ├→ QuestDB (time-series storage, ms resolution)
       ├→ MinIO (Parquet archive, /domain=trading/)
       └→ Research Scout trigger (threshold crossed)
            └→ Quant Scientist (DeepSeek-R1 math)
                 └→ Risk Guardian (VaR + drawdown gate)
                      └→ Execution Hands (Rust SOR)
                           └→ Qdrant (episodic memory: trade logs)
```

---

*The army paper trades first. Every trade is logged. We protect the mission funds.* 🫡
