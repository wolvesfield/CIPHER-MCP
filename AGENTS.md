# AGENTS.md — Universal AI Contract for CIPHER-MCP
> Last updated: 2026-03-01 | Status: ACTIVE — All AIs reading this repo MUST comply.

---

## Purpose

This contract applies to **every AI** that reads, modifies, or operates within this repository — GitHub Copilot, Claude, GPT, Gemini, DeepSeek, Jules, or any other model. No exceptions.

Cipher Ops is a production system built in memory of Ayesha Afser "Littli". Every hallucination, shortcut, or ignored constraint is a failure to honor her memory. We do not cut corners.

---

## Anti-Hallucination Rules (Non-Negotiable)

### 1. Cite Before You Claim
- Every factual claim about the codebase **MUST** cite the specific file and line range.
- Format: `FACT [source: path/to/file.md#L42]`
- If you cannot cite it, label it: `INFERENCE — unverified`
- **NEVER** invent file paths, function names, or API signatures.

### 2. Label Your Confidence
All statements fall into one of three categories:
```
FACT       — directly verifiable in this repo right now
INFERENCE  — logical conclusion from available facts (state your reasoning)
OPEN       — unknown, needs Commander input before proceeding
```

### 3. Surface OPEN QUESTIONS — Never Silently Resolve Them
- If you encounter an ambiguity that affects architecture, routing, or security → **STOP and surface it**.
- Format: `OPEN QUESTION: [question] | Impact: [what breaks if wrong]`
- Do NOT make a guess and proceed. Ask once, clearly, then wait.

### 4. SDD Gate Sequence (Mandatory Before Any Code)
No implementation may begin without completing this sequence:
```
1. speckit-clarify  — remove all ambiguity from the request
2. speckit-specify  — write the specification (inputs, outputs, contracts)
3. speckit-plan     — architecture decision, module breakdown
4. [Critic review]  — validate plan before any code is written
5. speckit-implement — TDD-first: red → green → refactor
6. Code Review → Security → QA → UAT → DevOps gates
```
Use the corresponding files in `prompts/` for each step.

---

## Memory Contract (Read Before Every Session)

At the start of every session, you MUST:
1. **READ `DAILY-LOG.md`** — the shared work log. Check what's done, what's in progress, what's next.
2. **CHECK "In Progress"** — if another agent is working on something, do NOT touch it.
3. **CLAIM your task** — move it from "To Do" → "In Progress" with your agent name and timestamp.
4. **LOG your work** — when done, write what you did under today's date in the Completed section.

Also retrieve:
1. Latest `work-logs/YYYY-MM-DD.md` — WHERE I LEFT OFF
2. `docs/MODELS.md` — which model does what (do not improvise model assignments)
3. `docs/INFRA.md` — hardware constraints (do not design beyond KVM8 limits)
4. `docs/OPS-RUNBOOK.md` — Commander's daily ritual (follow it)

**5-Sector Memory Model** (from `core/skills/memory-contract/SKILL.md`):
- Episodic — trade logs, session history, mission reports
- Semantic — domain knowledge, CVE databases, market patterns
- Procedural — workflows, runbooks, deployment patterns
- Emotional — Commander's confidence state, risk tolerance
- Reflective — lessons learned, what broke, what to improve

---

## Wing Routing

| Request Type | Route To | Spec File |
|-------------|----------|-----------|
| Trading analysis, quant math | `trading-wing/AGENTS.md` | QUANT_QUEUE |
| Security, scanning, bug bounty | `hacker-wing/AGENTS.md` | CYBER_QUEUE |
| Infrastructure, deployment, CI/CD | `core/agents/devops.agent.md` | Direct |
| Architecture decisions | `core/agents/architect.agent.md` + `core/agents/critic.agent.md` | SDD gate |
| Orchestration / planning | `core/agents/fleet.agent.md` | Wave-based |

---

## What This Repo Is NOT

- ❌ This repo does NOT contain live trading credentials or exchange API keys.
- ❌ This repo does NOT contain executable exploit payloads.
- ❌ This repo does NOT contain PII or user data.
- ❌ ComfyUI, Midjourney, LoRA training — those live in separate repos.

The runtime Python/Rust implementation lives in the **cipher-ops** repo.
This repo is the **brain** (specs, prompts, agent definitions). cipher-ops is the **body**.

---

## Commander Profile (Always Keep in Mind)

- **Name**: Broski (Farhan Afser Nabil)
- **Location**: Montreal, Quebec, Canada
- **Profile**: ADHD + autism + amnesia — needs structured, concise output
- **Style**: TL;DR first. Bullet points. Number steps. One question at a time.
- **Role**: Commander — gives orders, agents execute. Not a coder.
- **Mission**: Cipher Ops is dedicated to his daughter Ayesha Afser "Littli". This is not a side project.

**Never overwhelm. Never skip steps. Never hallucinate.** 🫡💙

---

*Every file in this repo is a promise kept to Littli.* 💙
