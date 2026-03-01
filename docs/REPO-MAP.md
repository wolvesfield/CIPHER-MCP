# docs/REPO-MAP.md — Repository Architecture Map
> Last updated: 2026-03-01

---

## Directory Tree

```
CIPHER-MCP/
├── .env.example                           # 6 secrets (GHEC, Supabase, Tavily, Mem0, Kube, Solana)
├── .github/copilot-instructions.md        # Original Copilot guardrails
├── .gitignore
├── LICENSE
├── Makefile                               # doctor, validate, compile, compile-fast
├── README.md                              # Step 0 (doctor) + make targets
├── AGENTS.md                              # ⭐ Universal AI contract (anti-hallucination)
├── SECURITY.md                            # ⭐ Security policy + responsible use
├── scripts_doctor.py                      # Manifest schema validator
├── setup.sh                               # Linux/VPS symlink bootstrap
├── setup.ps1                              # Windows PowerShell bootstrap
├── littli-protocol.md                     # Mission brief 💙
├── mcp-enterprise.json                    # 24-server MCP manifest
├── mcp_enterprise_compiler.py             # AOT compiler
│
├── core/
│   ├── agents/                            # 14 agent definitions
│   │   ├── fleet.agent.md                 # Master orchestrator (wave-based, 13 handoffs)
│   │   ├── planner.agent.md               # SDD-first planning
│   │   ├── architect.agent.md             # Module design + tech decisions
│   │   ├── analyst.agent.md               # Research + unknown resolution
│   │   ├── implementer.agent.md           # TDD-first coding (approved plans only)
│   │   ├── code-reviewer.agent.md         # Post-implementation quality gate
│   │   ├── critic.agent.md                # Post-planning validation gate
│   │   ├── security.agent.md              # CVE scans, injection audits
│   │   ├── qa.agent.md                    # Test strategy + execution
│   │   ├── uat.agent.md                   # User acceptance testing
│   │   ├── devops.agent.md                # CI/CD, versioning, CHANGELOG
│   │   ├── roadmap.agent.md               # Epic alignment validation
│   │   ├── retrospective.agent.md         # Process improvement capture
│   │   └── pi.agent.md                    # OSINT / deep investigative research
│   ├── instructions/
│   │   └── copilot-instructions.md        # Global fleet instructions (5-sector memory, ADHD)
│   └── skills/                            # 9 skill directories
│       ├── constitution/                  # Immutable principles
│       ├── constitutional-memory/         # Privacy guardrails + prompt injection defense
│       ├── daily-log/                     # Work log system
│       ├── document-lifecycle/            # Doc state management
│       ├── fleet-escalation/              # Escalation framework
│       ├── memory-contract/               # 5-sector model, 3-layer retrieval
│       ├── prompt-engineering/            # CoT, ReAct, Constitutional AI, ToT
│       ├── spec-driven/                   # Spec-kit SDD methodology
│       └── tdd-contract/                  # Test-first enforcement
│
├── docs/                                  # ⭐ Architecture documentation
│   ├── MODELS.md                          # Canonical model routing table (LOCKED)
│   ├── INFRA.md                           # KVM8 specs, HFT reality, Docker stack
│   ├── OPS-RUNBOOK.md                     # Daily ADHD-safe operations ritual
│   └── REPO-MAP.md                        # This file
│
├── prompts/                               # 11 reusable prompt templates
│   ├── code-review.prompt.md
│   ├── eod-log.prompt.md
│   ├── fleet-decompose.prompt.md
│   ├── security-review.prompt.md
│   ├── speckit-clarify.prompt.md
│   ├── speckit-implement.prompt.md
│   ├── speckit-plan.prompt.md
│   ├── speckit-specify.prompt.md
│   ├── speckit-tasks.prompt.md
│   ├── start-day.prompt.md
│   └── tdd-red-green.prompt.md
│
├── trading-wing/
│   ├── README.md                          # 5-team trading structure
│   └── AGENTS.md                          # ⭐ Trading wing agent specs
│
├── hacker-wing/
│   ├── README.md                          # 4-agent ReAct loop
│   └── AGENTS.md                          # ⭐ Hacker wing agent specs
│
└── work-logs/
    └── 2026-03-01.md                      # Session history
```

---

## Key Relationships

```
AGENTS.md (root)
  ↓ references
core/instructions/copilot-instructions.md  →  Session start + ADHD rules
core/agents/fleet.agent.md                 →  13-agent orchestrator + gates
littli-protocol.md                         →  Mission brief
docs/MODELS.md                             →  Which AI model does what
docs/INFRA.md                              →  Hardware constraints
docs/OPS-RUNBOOK.md                        →  Daily ritual
work-logs/YYYY-MM-DD.md                    →  Where Commander left off
```

---

## What Lives Here vs. Cipher-Ops Runtime

| CIPHER-MCP (this repo) | cipher-ops (runtime repo) |
|------------------------|---------------------------|
| Agent definitions (.agent.md) | Python implementation (commander.py, quant_worker.py) |
| Prompt templates | Rust execution engine |
| Skill configurations | Docker containers + docker-compose.yml |
| Model routing table | Live exchange WebSocket connections |
| Infrastructure reference docs | K8s manifests + Helm charts |
| SDD methodology | Actual trading/scanning runtime |

---

*This repo is the brain. Cipher-ops is the body.* 🫡
