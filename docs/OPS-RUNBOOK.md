# docs/OPS-RUNBOOK.md — Daily Operations Runbook
> Last updated: 2026-03-01 | ADHD/Autism-Safe Protocol

---

## Purpose

This runbook formalizes the daily ritual that keeps Commander Broski in flow state. Every AI that starts a session MUST follow this sequence. No exceptions.

---

## Start of Day

1. **Read the latest work log**: Open `work-logs/YYYY-MM-DD.md` (today's date or the most recent file).
2. **Display the status block**:
   ```
   ## WHERE YOU LEFT OFF
   [from work-log]

   ## BLOCKED
   [from work-log]

   ## TO DO NEXT
   [from work-log]
   ```
3. **Ask exactly one question**: "Continue with **[top TO DO item]**, or something else?"
4. **Wait for Commander's response** before doing anything.

---

## During Work

### Context Switch Protocol
- When the Commander switches topics, **immediately** write current task state to `work-logs/`.
- Include: what was done, what's left, any blockers discovered.
- This preserves ADHD task state — the Commander can resume later without losing context.

### Response Rules
- Max **1000 tokens** per response chunk.
- Never present more than **3 options** at once.
- If the Commander seems stuck, offer exactly **ONE** concrete next step.
- Respect hyperfocus — don't interrupt a productive flow with suggestions.

### Fleet Orchestrator Rules
- Wave-based parallel execution with dependency tracking.
- Mandatory gate sequence: **Code Review → Security → QA → UAT → DevOps**.
- Store wave summaries to episodic memory via Flowbaby tags.

---

## End of Day

1. **Run the EOD log prompt**: Use `prompts/eod-log.prompt.md`.
2. **The log must contain**:
   - Sessions completed (numbered).
   - Key decisions made.
   - WHERE I LEFT OFF block.
   - BLOCKED items.
   - TO DO NEXT (prioritized).
   - OPEN QUESTIONS surfaced.
3. **Commit the log** to `work-logs/YYYY-MM-DD.md`.

---

## Telegram Commands (Runtime)

| Command | Action |
|---------|--------|
| `/status` | Check all services: DeepSeek, Redis, Qdrant, Qwen MoE online status |
| `/trade [pair] [instruction]` | Route to QUANT_QUEUE → DeepSeek-R1 verifies → Qwen3 executes paper trade |
| `/scan [target]` | Route to CYBER_QUEUE → Ephemeral Kali container → Nmap/Nuclei → auto-destruct |
| `/nuke [password]` | SCORCHED EARTH: Kill all containers, unmount 30TB, revoke API keys |

---

## Emergency Procedures

### Dead Man's Switch (Automated)
- Monitors portfolio balance via read-only API key.
- Triggers if balance drops 5% in 60 seconds.
- Bypasses all AI logic → revokes trading API keys → cancels all orders → market-sells to USDC → sends Telegram alert.

### Manual Kill
- SSH into KVM8: `ssh root@YOUR_VPS_IP`
- Run: `docker kill $(docker ps -q) && umount /mnt/gdrive`
- Or: text `/nuke [password]` from Telegram.

---

*Every day starts the same way. Read the log. Ask one question. Execute.* 🫡
