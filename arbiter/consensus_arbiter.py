from __future__ import annotations

import os
from fastapi import FastAPI

app = FastAPI(title="Cipher Consensus Arbiter", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "arbiter",
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://ollama:11434"),
    }
"""
CIPHER OPS — Consensus Arbiter
FastAPI async service implementing the Team of Rivals M1-Parallel doctrine.
Dispatches SwarmTasks to 3 independent Generals simultaneously, collects
confidence-scored votes, and runs 4 consensus strategies to produce a
final synthesized decision.

Architecture:
    Commander (Telegram / CLI)
         ↓ SwarmTask
    Consensus Arbiter  ←── YOU ARE HERE
     ├── General Alpha  (Gemini 3 Pro — Cloud Intelligence)
     ├── General Bravo  (GPT-4.1    — Code Factory)
     └── General Charlie(Qwen3 local — VPS Execution)
         ↓ Final Decision
    Execution (trade / scan / deploy)

Consensus Strategies:
    1. Early Termination    — first high-confidence result wins (2.2× faster)
    2. Confidence-Weighted  — weighted vote by confidence score
    3. Full Synthesis       — merge all three into hybrid answer
    4. Red Team Override    — one General attacks the others' conclusions

Research basis: M1-Parallel framework, Team of Rivals (arXiv 2601.14351)
Author: Cipher Ops Legacy Foundation — for Littli 💙
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import httpx
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

log = logging.getLogger("consensus-arbiter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")

# ─── Config ────────────────────────────────────────────────

GENERAL_ENDPOINTS = {
    "alpha": os.getenv("GENERAL_ALPHA_URL", "http://localhost:8010"),   # Gemini General
    "bravo": os.getenv("GENERAL_BRAVO_URL", "http://localhost:8011"),   # GPT General
    "charlie": os.getenv("GENERAL_CHARLIE_URL", "http://localhost:8012"), # VPS Local General
}

# Confidence threshold for Early Termination strategy
EARLY_TERMINATION_THRESHOLD = float(os.getenv("EARLY_TERM_THRESHOLD", "0.85"))

# Minimum confidence for a General's result to count in voting
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.30"))

# Quarantine: auto-quarantine General after N consecutive low-confidence missions
QUARANTINE_THRESHOLD = int(os.getenv("QUARANTINE_THRESHOLD", "5"))

# Escalation: if all Generals disagree, send Telegram alert
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


# ─── Domain weight overrides ────────────────────────────────
# For domain-specific tasks, one General gets extra weight

DOMAIN_WEIGHTS = {
    "trading": {"alpha": 1.0, "bravo": 1.0, "charlie": 2.0},   # VPS wins on speed-critical trades
    "hacking": {"alpha": 2.0, "bravo": 1.0, "charlie": 1.0},   # Gemini wins on threat intel depth
    "research": {"alpha": 2.0, "bravo": 1.0, "charlie": 1.0},  # Gemini wins on research depth
    "dev":      {"alpha": 1.0, "bravo": 2.0, "charlie": 1.0},  # GPT wins on code quality
    "default":  {"alpha": 1.0, "bravo": 1.0, "charlie": 1.0},
}


# ─── Models ────────────────────────────────────────────────

class ConsensusStrategy(str, Enum):
    EARLY_TERMINATION = "early_termination"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    FULL_SYNTHESIS = "full_synthesis"
    RED_TEAM_OVERRIDE = "red_team_override"
    AUTO = "auto"  # Arbiter picks based on urgency + domain


class TaskPriority(str, Enum):
    CRITICAL = "critical"   # Early termination — time-critical trades, active exploits
    HIGH = "high"           # Confidence-weighted — standard analysis
    NORMAL = "normal"       # Full synthesis — research, architecture
    LOW = "low"             # No rush, full synthesis always


class SwarmTask(BaseModel):
    task_id: str
    mission: str = Field(..., description="Natural language mission description")
    domain: str = Field("default", description="trading | hacking | dev | research | default")
    priority: TaskPriority = TaskPriority.NORMAL
    strategy: ConsensusStrategy = ConsensusStrategy.AUTO
    timeout_sec: int = 120
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context for Generals")


class GeneralVote(BaseModel):
    general: str
    signal: Any = None          # The actual result/signal (trade signal, exploit, code, etc.)
    confidence: float = 0.0     # 0.0–1.0
    evidence: list[str] = []    # Citations, data points, reasoning
    latency_ms: int = 0
    error: Optional[str] = None
    quarantined: bool = False


class ConsensusResult(BaseModel):
    task_id: str
    strategy_used: ConsensusStrategy
    final_signal: Any
    final_confidence: float
    votes: list[GeneralVote]
    synthesized_evidence: list[str]
    agreement_level: float      # 0.0 = all disagree, 1.0 = all agree perfectly
    escalated: bool = False     # True if sent to human via Telegram
    latency_ms: int = 0


# ─── Quarantine Tracker ────────────────────────────────────

class QuarantineTracker:
    """Track consecutive low-confidence missions per General."""

    def __init__(self):
        self._consecutive_low: dict[str, int] = defaultdict(int)
        self._quarantined: set[str] = set()

    def record(self, general: str, confidence: float):
        if confidence < MIN_CONFIDENCE:
            self._consecutive_low[general] += 1
            if self._consecutive_low[general] >= QUARANTINE_THRESHOLD:
                if general not in self._quarantined:
                    log.warning(f"🚨 General {general} QUARANTINED after {QUARANTINE_THRESHOLD} low-confidence missions")
                    self._quarantined.add(general)
        else:
            self._consecutive_low[general] = 0
            if general in self._quarantined:
                log.info(f"✅ General {general} RELEASED from quarantine")
                self._quarantined.discard(general)

    def is_quarantined(self, general: str) -> bool:
        return general in self._quarantined

    def active_generals(self) -> list[str]:
        return [g for g in GENERAL_ENDPOINTS if g not in self._quarantined]

    def status(self) -> dict:
        return {
            "quarantined": list(self._quarantined),
            "consecutive_low": dict(self._consecutive_low),
            "active": self.active_generals(),
        }


quarantine = QuarantineTracker()


# ─── A2A Client ────────────────────────────────────────────

async def dispatch_to_general(
    client: httpx.AsyncClient,
    general: str,
    task: SwarmTask,
) -> GeneralVote:
    """Send a SwarmTask to one General via A2A JSON-RPC and collect its vote."""
    if quarantine.is_quarantined(general):
        return GeneralVote(general=general, quarantined=True, error="Quarantined")

    endpoint = GENERAL_ENDPOINTS[general]
    start = time.monotonic()

    payload = {
        "jsonrpc": "2.0",
        "id": task.task_id,
        "method": "tasks/send",
        "params": {
            "id": task.task_id,
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": task.mission}],
            },
            "metadata": {
                "domain": task.domain,
                "priority": task.priority.value,
                "context": task.context,
            },
        },
    }

    try:
        resp = await client.post(
            f"{endpoint}/a2a",
            json=payload,
            timeout=task.timeout_sec,
        )
        resp.raise_for_status()
        data = resp.json()
        elapsed = int((time.monotonic() - start) * 1000)

        result = data.get("result", {})
        confidence = float(result.get("confidence", 0.0))
        quarantine.record(general, confidence)

        return GeneralVote(
            general=general,
            signal=result.get("signal"),
            confidence=confidence,
            evidence=result.get("evidence", []),
            latency_ms=elapsed,
        )

    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        log.error(f"General {general} failed: {e}")
        quarantine.record(general, 0.0)
        return GeneralVote(general=general, error=str(e), latency_ms=elapsed)


# ─── Consensus Strategies ──────────────────────────────────

def _select_strategy(task: SwarmTask) -> ConsensusStrategy:
    """Auto-select strategy based on priority and domain."""
    if task.strategy != ConsensusStrategy.AUTO:
        return task.strategy
    if task.priority == TaskPriority.CRITICAL:
        return ConsensusStrategy.EARLY_TERMINATION
    if task.domain in ("research", "dev"):
        return ConsensusStrategy.FULL_SYNTHESIS
    return ConsensusStrategy.CONFIDENCE_WEIGHTED


def _agreement_level(votes: list[GeneralVote]) -> float:
    """Calculate how much the Generals agree (0.0–1.0)."""
    valid = [v for v in votes if not v.error and not v.quarantined]
    if len(valid) < 2:
        return 1.0
    signals = [str(v.signal) for v in valid]
    majority = max(signals, key=signals.count)
    agree = sum(1 for s in signals if s == majority)
    return agree / len(signals)


def _weighted_vote(votes: list[GeneralVote], domain: str) -> tuple[Any, float, list[str]]:
    """Confidence-weighted vote with domain weight multipliers."""
    weights = DOMAIN_WEIGHTS.get(domain, DOMAIN_WEIGHTS["default"])
    valid = [v for v in votes if not v.error and not v.quarantined and v.confidence >= MIN_CONFIDENCE]

    if not valid:
        return None, 0.0, []

    # Weight each vote
    weighted_scores: dict[str, float] = defaultdict(float)
    weighted_evidence: dict[str, list] = defaultdict(list)

    for v in valid:
        w = weights.get(v.general, 1.0) * v.confidence
        key = str(v.signal)
        weighted_scores[key] += w
        weighted_evidence[key].extend(v.evidence)

    best_signal = max(weighted_scores, key=weighted_scores.__getitem__)
    total_weight = sum(weights.get(v.general, 1.0) * v.confidence for v in valid)
    final_confidence = weighted_scores[best_signal] / total_weight if total_weight > 0 else 0.0

    return best_signal, final_confidence, weighted_evidence[best_signal]


def _synthesize(votes: list[GeneralVote], mission: str) -> tuple[Any, float, list[str]]:
    """Full synthesis: merge all General outputs into hybrid answer."""
    valid = [v for v in votes if not v.error and not v.quarantined]
    if not valid:
        return None, 0.0, []

    # Combine all evidence from all Generals
    all_evidence = []
    for v in valid:
        source = f"[{v.general.upper()}]"
        all_evidence.extend([f"{source} {e}" for e in v.evidence])

    # Average confidence across all Generals
    avg_confidence = sum(v.confidence for v in valid) / len(valid)

    # For synthesis: if majority agree on signal use that; else build compound signal
    signals = [str(v.signal) for v in valid if v.signal is not None]
    if not signals:
        return None, 0.0, all_evidence

    majority_signal = max(set(signals), key=signals.count)
    agree_count = signals.count(majority_signal)

    if agree_count == len(signals):
        # Full agreement — use the signal with highest confidence
        best = max(valid, key=lambda v: v.confidence)
        return best.signal, avg_confidence, all_evidence
    else:
        # Partial agreement — return structured compound result
        compound = {
            "majority_signal": majority_signal,
            "agreement": f"{agree_count}/{len(signals)}",
            "perspectives": {v.general: v.signal for v in valid},
        }
        return compound, avg_confidence * 0.85, all_evidence  # confidence penalty for disagreement


def _red_team(votes: list[GeneralVote]) -> tuple[Any, float, list[str], bool]:
    """
    Red Team Override: randomly assign one General as adversary.
    If Red Team finds a critical flaw, escalate to human.
    Returns: (signal, confidence, evidence, escalate)
    """
    valid = [v for v in votes if not v.error and not v.quarantined]
    if len(valid) < 2:
        return None, 0.0, [], False

    red_team = random.choice(valid)
    majority = [v for v in valid if v != red_team]

    # Majority position
    majority_signal, majority_conf, majority_evidence = _weighted_vote(majority, "default")

    # Red Team challenge: if confidence is very low, flag as critical risk
    if red_team.confidence < 0.4:
        log.warning(f"🔴 Red Team ({red_team.general}) flagging CRITICAL RISK — escalating to human")
        return majority_signal, majority_conf * 0.5, majority_evidence + red_team.evidence, True

    # Red Team agrees with majority — proceed with high confidence
    if str(red_team.signal) == str(majority_signal):
        return majority_signal, min(majority_conf + 0.1, 1.0), majority_evidence, False

    # Red Team disagrees — human escalation
    log.warning(f"🔴 Red Team ({red_team.general}) challenges majority — escalating")
    return majority_signal, majority_conf * 0.7, majority_evidence + red_team.evidence, True


# ─── Telegram Escalation ───────────────────────────────────

async def escalate_to_commander(task: SwarmTask, votes: list[GeneralVote], reason: str):
    """Send all three General analyses to Commander via Telegram when Generals disagree."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured — escalation skipped")
        return

    lines = [
        f"🚨 *ARBITER ESCALATION* — Mission `{task.task_id}`",
        f"Reason: {reason}",
        f"Mission: {task.mission[:200]}",
        "",
        "**General Votes:**",
    ]
    for v in votes:
        status = "🔴 quarantined" if v.quarantined else ("⚠️ error" if v.error else f"confidence={v.confidence:.2f}")
        lines.append(f"• **{v.general.upper()}**: signal=`{v.signal}` | {status}")
        if v.evidence:
            lines.append(f"  Evidence: {', '.join(v.evidence[:3])}")

    lines.append("\nReply with your decision to override.")

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": "\n".join(lines),
                "parse_mode": "Markdown",
            },
        )


# ─── Core Arbiter Logic ────────────────────────────────────

async def run_consensus(task: SwarmTask) -> ConsensusResult:
    """
    Main consensus loop:
    1. Dispatch to all active Generals in parallel
    2. Apply consensus strategy
    3. Escalate if needed
    """
    start = time.monotonic()
    strategy = _select_strategy(task)
    active = quarantine.active_generals()

    log.info(f"[{task.task_id}] Dispatching to {len(active)} Generals | strategy={strategy}")

    async with httpx.AsyncClient() as client:

        if strategy == ConsensusStrategy.EARLY_TERMINATION:
            # Race: first General above threshold wins
            votes: list[GeneralVote] = []
            tasks_map = {
                g: asyncio.create_task(dispatch_to_general(client, g, task))
                for g in active
            }

            winner_vote: Optional[GeneralVote] = None
            pending = set(tasks_map.values())

            while pending and not winner_vote:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for t in done:
                    vote = t.result()
                    votes.append(vote)
                    if not vote.error and vote.confidence >= EARLY_TERMINATION_THRESHOLD:
                        winner_vote = vote
                        for p in pending:
                            p.cancel()
                        break

            # Collect remaining
            for t in pending:
                try:
                    await t
                except asyncio.CancelledError:
                    pass

            if not winner_vote and votes:
                winner_vote = max((v for v in votes if not v.error), key=lambda v: v.confidence, default=votes[0])

            elapsed = int((time.monotonic() - start) * 1000)
            return ConsensusResult(
                task_id=task.task_id,
                strategy_used=strategy,
                final_signal=winner_vote.signal if winner_vote else None,
                final_confidence=winner_vote.confidence if winner_vote else 0.0,
                votes=votes,
                synthesized_evidence=winner_vote.evidence if winner_vote else [],
                agreement_level=_agreement_level(votes),
                latency_ms=elapsed,
            )

        else:
            # All strategies below wait for all Generals
            votes = await asyncio.gather(*[
                dispatch_to_general(client, g, task) for g in active
            ])
            votes = list(votes)

    elapsed = int((time.monotonic() - start) * 1000)
    agreement = _agreement_level(votes)
    escalated = False

    if strategy == ConsensusStrategy.CONFIDENCE_WEIGHTED:
        final_signal, final_conf, evidence = _weighted_vote(votes, task.domain)

        # Escalate if all Generals disagree
        if agreement < 0.34 and len([v for v in votes if not v.error]) >= 2:
            escalated = True
            asyncio.create_task(escalate_to_commander(task, votes, "All Generals disagree"))

    elif strategy == ConsensusStrategy.FULL_SYNTHESIS:
        final_signal, final_conf, evidence = _synthesize(votes, task.mission)

    elif strategy == ConsensusStrategy.RED_TEAM_OVERRIDE:
        final_signal, final_conf, evidence, escalated = _red_team(votes)
        if escalated:
            asyncio.create_task(escalate_to_commander(task, votes, "Red Team challenge"))

    else:
        final_signal, final_conf, evidence = _weighted_vote(votes, task.domain)

    return ConsensusResult(
        task_id=task.task_id,
        strategy_used=strategy,
        final_signal=final_signal,
        final_confidence=final_conf,
        votes=votes,
        synthesized_evidence=evidence,
        agreement_level=agreement,
        escalated=escalated,
        latency_ms=elapsed,
    )


# ─── FastAPI App ───────────────────────────────────────────

app = FastAPI(
    title="CIPHER OPS — Consensus Arbiter",
    description="Team of Rivals M1-Parallel consensus engine for 3-General army",
    version="1.0.0",
)


@app.get("/.well-known/agent.json")
async def agent_card():
    """A2A Agent Card — Arbiter advertises itself to other agents."""
    with open("arbiter/agent-cards/agent-card-arbiter.json") as f:
        return json.load(f)


@app.post("/tasks/send", response_model=ConsensusResult)
async def submit_task(task: SwarmTask, background: BackgroundTasks):
    """Submit a SwarmTask for multi-General consensus."""
    log.info(f"Task received: {task.task_id} | domain={task.domain} | priority={task.priority}")
    result = await run_consensus(task)
    log.info(
        f"Task {task.task_id} done | strategy={result.strategy_used} "
        f"confidence={result.final_confidence:.2f} | {result.latency_ms}ms"
    )
    return result


@app.get("/health")
async def health():
    """Health check — shows active vs quarantined Generals."""
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in GENERAL_ENDPOINTS.items():
            try:
                r = await client.get(f"{url}/health")
                results[name] = "online" if r.status_code == 200 else f"degraded ({r.status_code})"
            except Exception as e:
                results[name] = f"offline ({type(e).__name__})"

    return {
        "arbiter": "online",
        "generals": results,
        "quarantine": quarantine.status(),
    }


@app.get("/generals")
async def list_generals():
    """List all Generals and their endpoints."""
    return {
        "generals": {
            name: {
                "endpoint": url,
                "quarantined": quarantine.is_quarantined(name),
                "consecutive_low_confidence": quarantine._consecutive_low.get(name, 0),
            }
            for name, url in GENERAL_ENDPOINTS.items()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("consensus_arbiter:app", host="0.0.0.0", port=8000, reload=False)
