# SECURITY.md — Cipher Ops Security Policy
> Last updated: 2026-03-01 | Status: ACTIVE

---

## Scope

This repository (CIPHER-MCP) contains AI agent definitions, prompt templates, skill configurations, and orchestration logic. It does NOT contain live trading credentials, exchange API keys, or executable exploit code.

---

## Responsible Use Policy

### Trading Wing
- All trading logic defaults to **paper trading mode** (`PAPER_TRADING_ONLY=true` in `.env`).
- Live trading requires explicit Commander authorization and a separate `.env` flag change.
- Risk controls (5% max drawdown, Dead Man's Switch) are mandatory before any live deployment.
- Virtual stop-losses are held in memory — never placed visibly on exchange order books.
- API keys for exchanges must use the minimum required permissions (trade-only, no withdrawal).

### Hacker Wing
- All scanning and reconnaissance activities are restricted to **authorized targets only**.
- Authorized targets must be documented in writing before any scan begins.
- Ephemeral Kali Docker containers auto-destruct after 10 minutes maximum.
- All scan results are logged, timestamped, and vectorized into Qdrant.
- **PROHIBITED**: Generating or deploying offensive exploit payloads against unauthorized systems.
- **PROHIBITED**: Accessing, exfiltrating, or modifying data on systems without written permission.
- The local Qwen3 model is used for vulnerability analysis and report generation — not payload delivery.

### Data Handling
- No PII (Personally Identifiable Information) is stored in this repo.
- The 30TB data lake is mounted via rclone and accessed through DuckDB/MinIO — data stays on the volume.
- GDPR anonymization is enforced in the data sub-agent pipeline (drop `user_id` columns, deduplicate).
- Parquet files use Snappy/ZSTD compression with time-based partitioning (`/domain/YYYY/MM/DD/`).

---

## Secret Management

| Secret | Storage | Notes |
|--------|---------|-------|
| Exchange API Keys | `.env` (gitignored) | Never committed to repo |
| GHEC PAT | GitHub Secrets | Used by CI/CD workflows |
| DeepSeek / MiniMax API Keys | `.env` (gitignored) | Rotated monthly |
| Google AI Ultra / Gemini | `.env` (gitignored) | Free tier via $100/mo credits |
| KVM8 SSH Key | GitHub Secrets | Used by deploy workflow only |
| Logfire Token | `.env` (gitignored) | Observability only |

---

## Incident Response

1. **Self-Healing Loop**: Logfire detects anomaly → Webhook fires → GitHub Issue auto-created → OpenClaw Agent patches → CI/CD redeploys.
2. **Dead Man's Switch** (runtime): If portfolio drops 5% in 60 seconds → bypass all AI → revoke API keys → cancel orders → market-sell to USDC → Telegram `/nuke` alert.
3. **Manual Override**: Commander texts `/nuke [password]` via Telegram → kills all Docker containers, unmounts 30TB drive, revokes all API keys.

---

## Reporting Vulnerabilities

If you discover a security issue in this repo, contact: `contact@genxintel.com`

---

*For Ayesha Afser "Littli" — We finish what we started. 💙*
