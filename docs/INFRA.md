# docs/INFRA.md — Infrastructure Reference
> Last updated: 2026-03-01 | Status: LOCKED

---

## Current Hardware: Hostinger KVM8 (Alpha Sandbox)

| Spec | Value |
|------|-------|
| Type | Virtual KVM (NOT bare metal) |
| vCPUs | 8 |
| RAM | 32 GB |
| Storage | 200 GB NVMe SSD (OS + Docker) |
| External Storage | 30 TB Google Drive mounted via rclone at `/mnt/gdrive` (or `/mnt/vanguard-lake`) |
| Network | Shared datacenter — subject to jitter |
| OS | Ubuntu 22.04+ |
| Location | Hostinger EU/US datacenter |

### What the KVM8 CAN Do
- Run Ollama with Qwen3-30B-A3B MoE at 12-17 tokens/sec on CPU.
- Host Docker containers: Redpanda, QuestDB, Qdrant, Redis, MinIO, FastAPI.
- Run the GitHub Actions self-hosted runner (free CI/CD forever).
- Execute mid-frequency trading strategies (seconds-to-minutes timeframe).
- Paper trade against live exchange WebSocket feeds.

### What the KVM8 CANNOT Do
- True microsecond HFT — virtualized networking introduces jitter.
- GPU inference — no dedicated GPU available.
- Compete with colocated bare-metal servers sitting inside exchange datacenters.

---

## The HFT Truth (Phase 2 — Future)

True HFT requires **bare-metal colocation**:
- **Binance**: AWS Tokyo (ap-northeast-1) — your execution server must physically sit in that datacenter.
- **US Equities / Crypto Gateways**: Equinix NY4 (New York) or LD4 (London).
- **The Plan**: Build the full Python Brain + Rust Hands pipeline on KVM8 as the Alpha Sandbox. Paper trade. Once it proves $50k profit, lift-and-shift the **exact same code** to a Tokyo bare-metal server.

---

## Docker Stack (KVM8)

```yaml
Services:
  - Redpanda (message broker) — port 9092
  - QuestDB (time-series DB) — port 9000
  - Qdrant (vector memory) — port 6333
  - Redis (task queues) — port 6379
  - MinIO (S3-compatible object storage) — ports 9000/9001
  - FastAPI Data Feeder — port 8000
  - Ollama (local LLM inference) — port 11434
```

---

## Kubernetes (k3s) — Target Architecture

| Node | Role | Hardware |
|------|------|----------|
| KVM8 | Control Plane + GHEC Self-Hosted Runner | 8 vCPU / 32 GB RAM |
| Cloud Pro 1 | Worker Node | Per Hostinger Cloud Pro spec |
| Cloud Pro 2 | Worker Node | Per Hostinger Cloud Pro spec |

Features:
- Istio Service Mesh (Zero Trust mTLS between all pods).
- Prometheus + Grafana (observability).
- HPA auto-scaling (3-15 replicas based on CPU utilization at 75% threshold).
- GHCR (GitHub Container Registry) for Docker images.

---

## Data Lake Architecture

```
30TB Google Drive
  └→ rclone mount at /mnt/gdrive (or /mnt/vanguard-lake)
       └→ MinIO (S3-compatible gateway)
            └→ DuckDB (zero-copy Parquet query engine inside FastAPI)
                 └→ NDJSON streaming to PydanticAI agents (chunk-by-chunk)

Partition scheme: /domain/year=YYYY/month=MM/day=DD/*.parquet
Compression: Snappy (read-optimized) or ZSTD (storage-optimized)
```

---

## Self-Healing Loop

```
Runtime exception or OOM crash
  └→ Logfire catches anomaly + stack trace
       └→ Webhook fires to GitHub Actions
            └→ Auto-creates GitHub Issue (labeled "self-healing")
                 └→ OpenClaw Coder Agent reads issue, patches code, opens PR
                      └→ CI/CD auto-deploys to KVM8 via SSH
```

---

## Post-April 1st Continuity

| Capability | Before April 1st | After April 1st |
|------------|------------------|-----------------|
| AI Coding | 6x GHEC Copilot Plus seats | Jules via Google Ultra (20x limits) |
| CI/CD | GHEC Actions (50K min) | KVM8 self-hosted runner (free forever) |
| Local LLM | Qwen3-30B-A3B on KVM8 | Same (free forever) |
| Research | Gemini 3 Pro | Same (free via $100/mo Google credits) |
| Routing | DeepSeek V3.2 + R1 | Same (~$18-30/mo) |

---

*Your KVM8 is the sandbox. Tokyo bare-metal is the endgame.* 🫡
