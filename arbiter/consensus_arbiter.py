"""
CIPHER OPS — Consensus Arbiter (Vice President)
FastAPI async service implementing the 4-General Government doctrine.
Dispatches SwarmTasks to 4 Generals simultaneously, collects
confidence-scored votes with domain-weighted consensus, and runs 4
consensus strategies to produce a final synthesized decision.

Architecture:
    Broski (Telegram / CLI)
         |  (escalation ONLY for: live flip, budget, new scope)
    Vice President (Consensus Arbiter)  <-- YOU ARE HERE
     |-- General Alpha  (Gemini 3 Pro  -- The Scout)       :8010
     |-- General Bravo  (GPT-5.3-Codex -- The Builder)     :8011
     |-- General Charlie (Claude Opus 4.6 -- The Guardian)  :8012
     |-- General Delta  (Qwen3-30B     -- The Operator)     :8013
         |  Final Decision
    Execution (trade / deploy / publish)

Safety Rules:
    - Charlie down -> PAUSE all new trades until Guardian returns
    - Delta down  -> HALT all execution, CRITICAL alert to Broski
    - Soldier fails 3x at low confidence -> HELP_REQUEST to VP

Research basis: M1-Parallel framework, Team of Rivals (arXiv 2601.14351)
Author: Cipher Ops — The Government, for Littli
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

log = logging.getLogger("consensus-arbiter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s -- %(message)s")

# -- Config --

GENERAL_ENDPOINTS = {
    "alpha":   os.getenv("GENERAL_ALPHA_URL",   "http://localhost:8010"),
    "bravo":   os.getenv("GENERAL_BRAVO_URL",   "http://localhost:8011"),
    "charlie": os.getenv("GENERAL_CHARLIE_URL", "http://localhost:8012"),
    "delta":   os.getenv("GENERAL_DELTA_URL",   "http://localhost:8013"),
}

EARLY_TERMINATION_THRESHOLD = float(os.getenv("EARLY_TERM_THRESHOLD", "0.85"))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "0.30"))
QUARANTINE_THRESHOLD = int(os.getenv("QUARANTINE_THRESHOLD", "5"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
REDIS_SAFETY_KEY = "arbiter:safety_flags"
REDIS_DECISIONS_CHANNEL = "arbiter:decisions"

# -- Redis Client (shared across module) --
_redis: aioredis.Redis | None = None
_background_tasks: list[asyncio.Task] = []

# -- Domain weight overrides (4 Generals) --

DOMAIN_WEIGHTS = {
    "trading":   {"alpha": 1.5, "bravo": 1.0, "charlie": 1.0, "delta": 2.0},
    "macro":     {"alpha": 2.0, "bravo": 1.0, "charlie": 1.0, "delta": 1.5},
    "dev":       {"alpha": 1.0, "bravo": 2.0, "charlie": 1.5, "delta": 1.0},
    "security":  {"alpha": 1.0, "bravo": 1.0, "charlie": 2.0, "delta": 1.0},
    "arbitrage": {"alpha": 1.0, "bravo": 1.0, "charlie": 1.0, "delta": 2.0},
    "research":  {"alpha": 2.0, "bravo": 1.0, "charlie": 1.0, "delta": 1.0},
    "default":   {"alpha": 1.0, "bravo": 1.0, "charlie": 1.0, "delta": 1.0},
}

# -- Safety state (persisted to Redis so it survives restarts) --
_charlie_down = False
_delta_down = False


async def _persist_safety_flags():
    """Write safety flags to Redis so they survive container restarts."""
    if _redis:
        try:
            await _redis.hset(REDIS_SAFETY_KEY, mapping={
                "charlie_down": str(_charlie_down).lower(),
                "delta_down": str(_delta_down).lower(),
                "updated_at": str(time.time()),
            })
        except Exception as exc:
            log.warning(f"Failed to persist safety flags: {exc}")


async def _restore_safety_flags():
    """Read safety flags from Redis on startup."""
    global _charlie_down, _delta_down
    if _redis:
        try:
            flags = await _redis.hgetall(REDIS_SAFETY_KEY)
            if flags:
                _charlie_down = flags.get("charlie_down", "false") == "true"
                _delta_down = flags.get("delta_down", "false") == "true"
                log.info(f"Safety flags restored: charlie_down={_charlie_down}, delta_down={_delta_down}")
        except Exception as exc:
            log.warning(f"Failed to restore safety flags: {exc}")


async def _publish_decision(task: SwarmTask, result: ConsensusResult):
    """Publish consensus decision to Redis for Data Lake consumption."""
    if not _redis:
        return
    try:
        decision = {
            "type": "consensus_decision",
            "task_id": task.task_id,
            "domain": task.domain,
            "strategy": result.strategy_used.value,
            "final_confidence": result.final_confidence,
            "agreement_level": result.agreement_level,
            "escalated": result.escalated,
            "votes": len(result.votes),
            "latency_ms": result.latency_ms,
            "timestamp": time.time(),
        }
        await _redis.publish(REDIS_DECISIONS_CHANNEL, json.dumps(decision, default=str))

        # Also publish to domain-specific channel
        domain_channel = f"intel.{task.domain}.all"
        await _redis.publish(domain_channel, json.dumps({
            **decision,
            "final_signal": str(result.final_signal)[:500],
            "evidence_count": len(result.synthesized_evidence),
        }, default=str))
    except Exception as exc:
        log.warning(f"Failed to publish decision: {exc}")


# -- Models --

class ConsensusStrategy(str, Enum):
    EARLY_TERMINATION = "early_termination"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    FULL_SYNTHESIS = "full_synthesis"
    RED_TEAM_OVERRIDE = "red_team_override"
    AUTO = "auto"


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class SwarmTask(BaseModel):
    task_id: str
    mission: str = Field(..., description="Natural language mission description")
    domain: str = Field("default", description="trading|macro|dev|security|arbitrage|research|default")
    priority: TaskPriority = TaskPriority.NORMAL
    strategy: ConsensusStrategy = ConsensusStrategy.AUTO
    timeout_sec: int = 120
    context: dict[str, Any] = Field(default_factory=dict)


class GeneralVote(BaseModel):
    general: str
    signal: Any = None
    confidence: float = 0.0
    evidence: list[str] = []
    latency_ms: int = 0
    error: Optional[str] = None
    quarantined: bool = False
    soldier: Optional[str] = None  # which soldier handled it


class ConsensusResult(BaseModel):
    task_id: str
    strategy_used: ConsensusStrategy
    final_signal: Any
    final_confidence: float
    votes: list[GeneralVote]
    synthesized_evidence: list[str]
    agreement_level: float
    escalated: bool = False
    latency_ms: int = 0


# -- Quarantine Tracker (per-General AND per-soldier) --

class QuarantineTracker:
    """Track consecutive low-confidence missions per General and per soldier."""

    def __init__(self):
        self._consecutive_low: dict[str, int] = defaultdict(int)
        self._quarantined: set[str] = set()
        self._help_requests: dict[str, int] = defaultdict(int)

    def record(self, key: str, confidence: float):
        """key can be general name or 'general:soldier_id'"""
        if confidence < MIN_CONFIDENCE:
            self._consecutive_low[key] += 1
            if self._consecutive_low[key] >= QUARANTINE_THRESHOLD:
                if key not in self._quarantined:
                    log.warning(f"QUARANTINED {key} after {QUARANTINE_THRESHOLD} low-confidence missions")
                    self._quarantined.add(key)
        else:
            self._consecutive_low[key] = 0
            if key in self._quarantined:
                log.info(f"RELEASED {key} from quarantine")
                self._quarantined.discard(key)

    def record_failure(self, key: str):
        """Track failures for help protocol. 3 failures -> HELP_REQUEST."""
        self._help_requests[key] = self._help_requests.get(key, 0) + 1
        return self._help_requests[key] >= 3

    def clear_failures(self, key: str):
        self._help_requests[key] = 0

    def is_quarantined(self, key: str) -> bool:
        return key in self._quarantined

    def active_generals(self) -> list[str]:
        return [g for g in GENERAL_ENDPOINTS if g not in self._quarantined]

    def status(self) -> dict:
        return {
            "quarantined": list(self._quarantined),
            "consecutive_low": dict(self._consecutive_low),
            "active": self.active_generals(),
            "help_requests": dict(self._help_requests),
        }


quarantine = QuarantineTracker()


# -- A2A Client --

async def dispatch_to_general(
    client: httpx.AsyncClient,
    general: str,
    task: SwarmTask,
) -> GeneralVote:
    """Send a SwarmTask to one General via A2A JSON-RPC."""
    if quarantine.is_quarantined(general):
        return GeneralVote(general=general, quarantined=True, error="Quarantined")

    # Safety rules
    global _charlie_down, _delta_down
    if general == "charlie" and _charlie_down:
        return GeneralVote(general=general, error="Charlie (Guardian) is DOWN — safety pause")
    if general == "delta" and _delta_down:
        return GeneralVote(general=general, error="Delta (Operator) is DOWN — critical halt")

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
        resp = await client.post(f"{endpoint}/a2a", json=payload, timeout=task.timeout_sec)
        resp.raise_for_status()
        data = resp.json()
        elapsed = int((time.monotonic() - start) * 1000)

        result = data.get("result", {})
        confidence = float(result.get("confidence", 0.0))
        soldier = result.get("soldier")

        # Record both general-level and soldier-level quarantine
        quarantine.record(general, confidence)
        if soldier:
            quarantine.record(f"{general}:{soldier}", confidence)

        return GeneralVote(
            general=general,
            signal=result.get("signal"),
            confidence=confidence,
            evidence=result.get("evidence", []),
            latency_ms=elapsed,
            soldier=soldier,
        )

    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        log.error(f"General {general} failed: {e}")
        quarantine.record(general, 0.0)

        # Update safety state and persist to Redis
        if general == "charlie":
            _charlie_down = True
            log.warning("SAFETY PAUSE: Charlie (Guardian) is DOWN — pausing all new trades")
            asyncio.create_task(alert_broski(f"Charlie (Guardian) DOWN — trades paused"))
            asyncio.create_task(_persist_safety_flags())
        elif general == "delta":
            _delta_down = True
            log.warning("CRITICAL: Delta (Operator) DOWN — halting all execution")
            asyncio.create_task(alert_broski(f"CRITICAL: Delta (Operator) DOWN — execution halted"))
            asyncio.create_task(_persist_safety_flags())

        return GeneralVote(general=general, error=str(e), latency_ms=elapsed)


# -- Help Protocol --

async def handle_help_request(
    general: str,
    soldier_id: str,
    task: SwarmTask,
    original_error: str,
) -> GeneralVote | None:
    """
    When a soldier fails 3x at low confidence, VP finds the best helper
    General for that domain and routes the subtask there.
    """
    key = f"{general}:{soldier_id}"
    needs_help = quarantine.record_failure(key)

    if not needs_help:
        return None

    log.warning(f"HELP_REQUEST from {key} — finding helper General")

    # Find best helper based on domain weights
    weights = DOMAIN_WEIGHTS.get(task.domain, DOMAIN_WEIGHTS["default"])
    helper_candidates = [
        (g, w) for g, w in weights.items()
        if g != general and not quarantine.is_quarantined(g)
    ]
    if not helper_candidates:
        return None

    helper_general = max(helper_candidates, key=lambda x: x[1])[0]
    log.info(f"Routing help from {key} to {helper_general}")

    async with httpx.AsyncClient() as client:
        helper_task = SwarmTask(
            task_id=f"{task.task_id}-help",
            mission=f"[HELP REQUEST from {key}] {task.mission}\nOriginal error: {original_error}",
            domain=task.domain,
            priority=task.priority,
            timeout_sec=task.timeout_sec,
            context={**task.context, "help_for": key},
        )
        result = await dispatch_to_general(client, helper_general, helper_task)

    if result and not result.error:
        quarantine.clear_failures(key)

    return result


# -- Consensus Strategies --

def _select_strategy(task: SwarmTask) -> ConsensusStrategy:
    if task.strategy != ConsensusStrategy.AUTO:
        return task.strategy
    if task.priority == TaskPriority.CRITICAL:
        return ConsensusStrategy.EARLY_TERMINATION
    if task.domain in ("research", "dev", "macro"):
        return ConsensusStrategy.FULL_SYNTHESIS
    return ConsensusStrategy.CONFIDENCE_WEIGHTED


def _agreement_level(votes: list[GeneralVote]) -> float:
    valid = [v for v in votes if not v.error and not v.quarantined]
    if len(valid) < 2:
        return 1.0
    signals = [str(v.signal) for v in valid]
    majority = max(signals, key=signals.count)
    agree = sum(1 for s in signals if s == majority)
    return agree / len(signals)


def _weighted_vote(votes: list[GeneralVote], domain: str) -> tuple[Any, float, list[str]]:
    weights = DOMAIN_WEIGHTS.get(domain, DOMAIN_WEIGHTS["default"])
    valid = [v for v in votes if not v.error and not v.quarantined and v.confidence >= MIN_CONFIDENCE]

    if not valid:
        return None, 0.0, []

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
    valid = [v for v in votes if not v.error and not v.quarantined]
    if not valid:
        return None, 0.0, []

    all_evidence = []
    for v in valid:
        source = f"[{v.general.upper()}]"
        all_evidence.extend([f"{source} {e}" for e in v.evidence])

    avg_confidence = sum(v.confidence for v in valid) / len(valid)

    signals = [str(v.signal) for v in valid if v.signal is not None]
    if not signals:
        return None, 0.0, all_evidence

    majority_signal = max(set(signals), key=signals.count)
    agree_count = signals.count(majority_signal)

    if agree_count == len(signals):
        best = max(valid, key=lambda v: v.confidence)
        return best.signal, avg_confidence, all_evidence
    else:
        compound = {
            "majority_signal": majority_signal,
            "agreement": f"{agree_count}/{len(signals)}",
            "perspectives": {v.general: v.signal for v in valid},
        }
        return compound, avg_confidence * 0.85, all_evidence


def _red_team(votes: list[GeneralVote]) -> tuple[Any, float, list[str], bool]:
    """
    Red Team Override: Charlie (Guardian) is the default adversary.
    If Charlie flags CRITICAL risk, escalate to Broski.
    """
    valid = [v for v in votes if not v.error and not v.quarantined]
    if len(valid) < 2:
        return None, 0.0, [], False

    # Charlie is the Red Team by default (The Guardian reviews everything)
    charlie_vote = next((v for v in valid if v.general == "charlie"), None)
    if charlie_vote:
        red_team = charlie_vote
        majority = [v for v in valid if v != red_team]
    else:
        red_team = random.choice(valid)
        majority = [v for v in valid if v != red_team]

    majority_signal, majority_conf, majority_evidence = _weighted_vote(majority, "default")

    if red_team.confidence < 0.4:
        log.warning(f"RED TEAM ({red_team.general}) flagging CRITICAL RISK — escalating")
        return majority_signal, majority_conf * 0.5, majority_evidence + red_team.evidence, True

    if str(red_team.signal) == str(majority_signal):
        return majority_signal, min(majority_conf + 0.1, 1.0), majority_evidence, False

    log.warning(f"RED TEAM ({red_team.general}) challenges majority — escalating")
    return majority_signal, majority_conf * 0.7, majority_evidence + red_team.evidence, True


# -- Telegram Alerts --

async def alert_broski(message: str):
    """Send alert to Broski via Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured — alert skipped")
        return

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"},
        )


async def escalate_to_commander(task: SwarmTask, votes: list[GeneralVote], reason: str):
    """Send all four General analyses to Broski via Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured — escalation skipped")
        return

    lines = [
        f"*ARBITER ESCALATION* — Mission `{task.task_id}`",
        f"Reason: {reason}",
        f"Mission: {task.mission[:200]}",
        "",
        "**General Votes:**",
    ]
    for v in votes:
        status = "quarantined" if v.quarantined else ("error" if v.error else f"confidence={v.confidence:.2f}")
        soldier_info = f" (soldier: {v.soldier})" if v.soldier else ""
        lines.append(f"  *{v.general.upper()}*{soldier_info}: signal=`{v.signal}` | {status}")
        if v.evidence:
            lines.append(f"  Evidence: {', '.join(v.evidence[:3])}")

    lines.append("\nReply with your decision to override.")

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": "\n".join(lines), "parse_mode": "Markdown"},
        )


# -- Core Arbiter Logic --

async def run_consensus(task: SwarmTask) -> ConsensusResult:
    """
    Main consensus loop:
    1. Check safety state (Charlie/Delta down rules)
    2. Dispatch to all active Generals in parallel
    3. Apply consensus strategy
    4. Escalate if needed
    """
    global _charlie_down, _delta_down

    start = time.monotonic()
    strategy = _select_strategy(task)
    active = quarantine.active_generals()

    # Safety: if Charlie is down, reject new trading tasks
    if _charlie_down and task.domain in ("trading", "arbitrage"):
        return ConsensusResult(
            task_id=task.task_id,
            strategy_used=strategy,
            final_signal=None,
            final_confidence=0.0,
            votes=[],
            synthesized_evidence=["SAFETY PAUSE: Guardian (Charlie) is offline — no new trades"],
            agreement_level=0.0,
            escalated=True,
            latency_ms=0,
        )

    # Safety: if Delta is down, reject all execution tasks
    if _delta_down and task.domain in ("trading", "arbitrage"):
        return ConsensusResult(
            task_id=task.task_id,
            strategy_used=strategy,
            final_signal=None,
            final_confidence=0.0,
            votes=[],
            synthesized_evidence=["CRITICAL HALT: Operator (Delta) is offline — execution stopped"],
            agreement_level=0.0,
            escalated=True,
            latency_ms=0,
        )

    log.info(f"[{task.task_id}] Dispatching to {len(active)} Generals | strategy={strategy}")

    async with httpx.AsyncClient() as client:

        if strategy == ConsensusStrategy.EARLY_TERMINATION:
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

            for t in pending:
                try:
                    await t
                except asyncio.CancelledError:
                    pass

            if not winner_vote and votes:
                winner_vote = max(
                    (v for v in votes if not v.error),
                    key=lambda v: v.confidence,
                    default=votes[0],
                )

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
            votes = await asyncio.gather(*[
                dispatch_to_general(client, g, task) for g in active
            ])
            votes = list(votes)

    elapsed = int((time.monotonic() - start) * 1000)
    agreement = _agreement_level(votes)
    escalated = False

    if strategy == ConsensusStrategy.CONFIDENCE_WEIGHTED:
        final_signal, final_conf, evidence = _weighted_vote(votes, task.domain)
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


# -- FastAPI App with Lifespan --

async def _startup_health_check():
    """Probe all 4 Generals on boot. Log who's online, set safety flags."""
    global _charlie_down, _delta_down
    log.info("Running startup health check on all Generals...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        for name, url in GENERAL_ENDPOINTS.items():
            try:
                r = await client.get(f"{url}/health")
                if r.status_code == 200:
                    data = r.json()
                    soldiers = data.get("soldiers", "?")
                    log.info(f"  {name.upper()}: ONLINE ({soldiers} soldiers)")
                else:
                    log.warning(f"  {name.upper()}: DEGRADED (HTTP {r.status_code})")
            except Exception as e:
                log.warning(f"  {name.upper()}: OFFLINE ({type(e).__name__})")
                if name == "charlie":
                    _charlie_down = True
                elif name == "delta":
                    _delta_down = True

    if _charlie_down:
        log.warning("SAFETY PAUSE active: Charlie (Guardian) offline at boot")
    if _delta_down:
        log.warning("CRITICAL HALT active: Delta (Operator) offline at boot")

    await _persist_safety_flags()


async def _watchdog_loop():
    """Lightweight watchdog: check Generals every 30s and update safety flags."""
    global _charlie_down, _delta_down
    while True:
        await asyncio.sleep(30)
        try:
            changed = False
            async with httpx.AsyncClient(timeout=5.0) as client:
                for name, url in GENERAL_ENDPOINTS.items():
                    try:
                        r = await client.get(f"{url}/health")
                        online = r.status_code == 200
                    except Exception:
                        online = False

                    if name == "charlie":
                        if online and _charlie_down:
                            _charlie_down = False
                            changed = True
                            log.info("WATCHDOG: Charlie RECOVERED")
                        elif not online and not _charlie_down:
                            _charlie_down = True
                            changed = True
                            log.warning("WATCHDOG: Charlie DOWN — safety pause")
                            asyncio.create_task(alert_broski("WATCHDOG: Charlie (Guardian) DOWN — trades paused"))
                    elif name == "delta":
                        if online and _delta_down:
                            _delta_down = False
                            changed = True
                            log.info("WATCHDOG: Delta RECOVERED")
                        elif not online and not _delta_down:
                            _delta_down = True
                            changed = True
                            log.warning("WATCHDOG: Delta DOWN — critical halt")
                            asyncio.create_task(alert_broski("WATCHDOG: Delta (Operator) DOWN — CRITICAL"))

            if changed:
                await _persist_safety_flags()
        except Exception as exc:
            log.error(f"Watchdog error: {exc}")


async def _teaching_loop():
    """Schedule nightly teaching cycle at 2 AM."""
    import datetime
    while True:
        now = datetime.datetime.now()
        next_2am = now.replace(hour=2, minute=0, second=0, microsecond=0)
        if now >= next_2am:
            next_2am += datetime.timedelta(days=1)
        wait_seconds = (next_2am - now).total_seconds()
        log.info(f"Next teaching cycle in {wait_seconds:.0f}s (at {next_2am})")
        await asyncio.sleep(wait_seconds)

        log.info("TEACHING CYCLE: starting nightly knowledge consolidation")
        try:
            # Gather high-confidence decisions from last 24h via Redis
            if _redis:
                # Publish teaching trigger so soldiers with MemoryManager can run it
                await _redis.publish("intel.teaching.all", json.dumps({
                    "type": "teaching_cycle_trigger",
                    "timestamp": time.time(),
                }))
                log.info("TEACHING CYCLE: trigger published to Redis")
        except Exception as exc:
            log.error(f"Teaching cycle failed: {exc}")


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Boot Redis, restore safety state, start background loops."""
    global _redis

    # 1. Connect to Redis
    try:
        _redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
        await _redis.ping()
        log.info(f"Redis connected: {REDIS_URL}")
    except Exception as exc:
        _redis = None
        log.warning(f"Redis unavailable (degraded mode): {exc}")

    # 2. Restore safety flags from Redis (survive restarts)
    await _restore_safety_flags()

    # 3. Run startup health check on all Generals
    await _startup_health_check()

    # 4. Start background tasks
    _background_tasks.append(asyncio.create_task(_watchdog_loop()))
    _background_tasks.append(asyncio.create_task(_teaching_loop()))
    log.info("Background tasks started: watchdog (30s), teaching (2AM nightly)")

    log.info("VP (Consensus Arbiter) is ONLINE. The Government is operational.")

    yield  # App is running

    # Cleanup
    for task in _background_tasks:
        task.cancel()
    if _redis:
        await _redis.aclose()
    log.info("VP shutting down.")


app = FastAPI(
    title="CIPHER OPS — Vice President (Consensus Arbiter)",
    description="4-General Government consensus engine. 18 soldiers. 5 revenue streams. For Littli.",
    version="2.1.0",
    lifespan=lifespan,
)


@app.get("/.well-known/agent.json")
async def agent_card():
    with open("arbiter/agent-cards/agent-card-arbiter.json") as f:
        return json.load(f)


@app.post("/tasks/send", response_model=ConsensusResult)
async def submit_task(task: SwarmTask, background: BackgroundTasks):
    log.info(f"Task received: {task.task_id} | domain={task.domain} | priority={task.priority}")
    result = await run_consensus(task)
    log.info(
        f"Task {task.task_id} done | strategy={result.strategy_used} "
        f"confidence={result.final_confidence:.2f} | {result.latency_ms}ms"
    )
    # Publish decision to Redis for Data Lake and cross-General awareness
    background.add_task(_publish_decision, task, result)
    return result


@app.get("/health")
async def health():
    global _charlie_down, _delta_down
    changed = False
    results = {}
    async with httpx.AsyncClient(timeout=5.0) as client:
        for name, url in GENERAL_ENDPOINTS.items():
            try:
                r = await client.get(f"{url}/health")
                if r.status_code == 200:
                    results[name] = "online"
                    # Reset safety flags if General comes back
                    if name == "charlie" and _charlie_down:
                        _charlie_down = False
                        changed = True
                        log.info("Charlie (Guardian) RECOVERED — safety pause lifted")
                    elif name == "delta" and _delta_down:
                        _delta_down = False
                        changed = True
                        log.info("Delta (Operator) RECOVERED — execution resumed")
                else:
                    results[name] = f"degraded ({r.status_code})"
            except Exception as e:
                results[name] = f"offline ({type(e).__name__})"
                if name == "charlie" and not _charlie_down:
                    _charlie_down = True
                    changed = True
                elif name == "delta" and not _delta_down:
                    _delta_down = True
                    changed = True

    # Persist any safety flag changes to Redis
    if changed:
        asyncio.create_task(_persist_safety_flags())

    return {
        "arbiter": "online",
        "role": "Vice President",
        "generals": results,
        "quarantine": quarantine.status(),
        "safety": {
            "charlie_down_pause": _charlie_down,
            "delta_down_halt": _delta_down,
        },
        "soldiers_total": 18,
        "redis_connected": _redis is not None,
    }


@app.get("/generals")
async def list_generals():
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
