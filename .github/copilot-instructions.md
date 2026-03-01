# Copilot Instructions — CIPHER-MCP
> *For Ayesha Afser "Littli" — forever the reason. 💙*

---

## ⚡ READ FIRST — EVERY SESSION

**MANDATORY BOOT — do this before anything else:**
1. Read `SUPER_ARCHITECTURE.md` (repo root) — single source of truth for everything
2. Read `work-logs/YYYY-MM-DD.md` (most recent) — WHERE Commander left off
3. Display orientation block (see `docs/OPS-RUNBOOK.md` Start of Day section)
4. Ask ONE question. Wait for response. Do not proceed until Commander responds.

> Commander has ADHD + autism + amnesia. Context restoration is not optional.
> Skip the boot sequence = fail the mission.

---

## WHO IS COMMANDER

Broski (Farhan Afser Nabil) — Montreal. ADHD/autism/amnesia.
**Style**: TL;DR first → bullets → numbered steps → ONE question at a time.
**Role**: Commander (orders only — NOT a coder).
**Mission**: 20-agent autonomous AI army dedicated to Littli.

---

## WHAT THIS REPO IS

CIPHER-MCP = **The Brain** (agent specs, prompts, model routing, skills, docs).
cipher-ops = **The Body** (Python/Rust runtime on KVM8 VPS, runs 24/7).

Do NOT add: ComfyUI, Midjourney, LoRA, image/video gen tools — separate repos.

---

## MODEL ROUTING (locked — full table in `docs/MODELS.md`)

| Task Type | Use | Notes |
|-----------|-----|-------|
| Route/orchestrate all tasks | DeepSeek V3.2 (`deepseek-chat`) | The Commander |
| Math/quant verification | DeepSeek-R1 (`deepseek-reasoner`) | The Scientist |
| Deep research, 1M context | Gemini 3 Pro (via Google Cloud credits) | The Scout |
| High-volume quick sentiment | MiniMax M2.5 | The Fast Scout |
| Local code/analysis (free) | Qwen3-30B-A3B on Ollama/KVM8 | The Soldier |
| **Build phase (VS Code)** | Claude Sonnet 4.6 (1x) / Opus 4.6 (3x — arch only) | GHEC until Apr 1 |

---

## ANTI-HALLUCINATION RULES (full contract in `AGENTS.md`)

- **Cite every fact**: `FACT [source: file.md#L42]` — never invent file paths
- **Label confidence**: `FACT` / `INFERENCE` / `OPEN` on every non-trivial claim
- **Surface OPEN QUESTIONS** before proceeding — never silently resolve blockers
- **No code before SDD gates**: clarify → specify → plan → critic → implement → gates
- **No model improvisation**: use `docs/MODELS.md`, not your best guess

---

## FLEET AGENT SYSTEM (full spec in `core/agents/fleet.agent.md`)

13 agents in `core/agents/`: fleet, planner, architect, analyst, implementer,
code-reviewer, critic, security, qa, uat, devops, roadmap, retrospective, pi.

**Mandatory gate sequence**: Code Review → Security → QA → UAT → DevOps — NEVER skip.

**SDD before ANY code** (prompts in `prompts/`):
speckit-clarify → speckit-specify → speckit-plan → [Critic] → speckit-implement

---

## WING ROUTING

| Request | Route | Spec |
|---------|-------|------|
| Trading, quant math | QUANT_QUEUE → DeepSeek-R1 | `trading-wing/AGENTS.md` |
| Security, scanning | CYBER_QUEUE → Kali container | `hacker-wing/AGENTS.md` |
| Infra, CI/CD, deploy | DevOps agent | `core/agents/devops.agent.md` |
| Architecture | Architect + Critic agents | SDD gate |

---

## SECURITY RULES (full policy in `SECURITY.md`)

- Trading defaults `PAPER_TRADING_ONLY=true` — live needs explicit Commander flip
- Hacker wing: written authorization required before ANY scan
- Never commit secrets — `.env` only (gitignored)
- Dead Man's Switch: 5% portfolio drop in 60s → auto-kill all trading

---

## MCP MESH RULES

- Prefer `mcp-compiled.json` over runtime launchers
- Never reintroduce `npx`/`uvx` in compiled output
- `mcp_enterprise_compiler.py` = single source of compilation truth
- After changes: `python mcp_enterprise_compiler.py --validate-env` then compile

---

## 🚨 GHEC EXPIRES APRIL 1, 2026

Use 75% of 6,000 premium requests (= 4,500) to build the permanent army.
Save Claude Opus 4.6 (3x multiplier) for architecture reviews ONLY.
Priority: self-hosted Actions runner on KVM8, all agent Python files in cipher-ops.

---

## MEMORY + WORK LOG

- Work logs: `C:\Users\arcan_e9q9t\work-logs\` + `Y:\📁 Cipher Ops HQ\`
- 5-sector memory: Episodic / Semantic / Procedural / Emotional / Reflective
- Max 1000 tokens injected per context — cognitive load protection
- Store task state before EVERY context switch (ADHD support)
- Full memory spec: `core/skills/memory-contract/SKILL.md`
