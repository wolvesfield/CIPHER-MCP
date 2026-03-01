# hacker-wing/AGENTS.md — Hacker Wing Agent Specifications
> Last updated: 2026-03-01 | Status: SPEC ONLY — Implementation lives in cipher-ops repo.

---

## Overview

The Hacker Wing operates a 4-agent ReAct loop for **authorized, defensive** security operations. All scans target ONLY systems the Commander owns or has written permission to test.

---

## Agent: Recon

- **Role**: Initial target enumeration and information gathering.
- **Tools**: Nmap port scanning, DNS enumeration, WHOIS lookups.
- **Container**: Ephemeral `kalilinux/kali-rolling` Docker container (auto-destructs after 10 minutes).
- **Output**: Target profile → vectorized into Qdrant.

---

## Agent: Vulnerability Assessor

- **Model**: DeepSeek-R1 (`deepseek-reasoner`)
- **Role**: Analyze Recon findings using `<think>` blocks. Classify vulnerabilities by CVSS score. Cross-reference CVE databases.
- **Output**: Prioritized vulnerability report with remediation recommendations.

---

## Agent: Analysis & Proof-of-Concept

- **Model**: Qwen3-30B-A3B Abliterated (local Ollama)
- **Role**: Generate proof-of-concept analysis for identified vulnerabilities on **authorized targets only**.
- **Constraints**:
  - ⛔ NO offensive payload deployment against public/unauthorized systems.
  - ⛔ NO data exfiltration or modification.
  - ✅ Analysis reports and remediation guidance only.
  - ✅ Proof-of-concept code for authorized penetration testing.
- **Output**: Analysis report → vectorized into Qdrant.

---

## Agent: Report Generator

- **Role**: Compile all findings into structured security assessment reports.
- **Format**: Executive summary, technical findings (CVSS-scored), remediation steps, re-test schedule.
- **Storage**: Reports saved to 30TB data lake under `/domain=security/year=YYYY/month=MM/`.

---

## Operational Flow

```
Commander issues /scan [authorized_target]
  └→ DeepSeek V3.2 routes to CYBER_QUEUE (Redis)
       └→ Recon Agent: Ephemeral Kali container → Nmap/Nuclei scan
            └→ Container auto-destructs (10 min max)
                 └→ Vulnerability Assessor: DeepSeek-R1 <think> analysis
                      └→ Analysis Agent: Local Qwen3 generates PoC report
                           └→ Report Generator: Structured output → Qdrant + Data Lake
```

---

## Security Rules (Non-Negotiable)

1. **Written authorization required** before scanning any target.
2. **Ephemeral containers only** — no persistent attack infrastructure.
3. **10-minute auto-destruct** on all Kali containers.
4. **All results logged** — timestamped, stored in Qdrant, auditable.
5. **No live exploit delivery** — analysis and reporting only.
6. **Commander approval required** for any action beyond passive reconnaissance.

---

*Defensive operations only. We protect — we don't destroy.* 🫡
