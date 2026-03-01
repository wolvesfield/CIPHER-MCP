---
name: memory-contract
description: >
  Unified AI Memory System protocol for Fleet agents. Governs how all agents
  retrieve and store memory using a 5-sector model (episodic, semantic,
  procedural, emotional, reflective), 3-layer progressive retrieval, temporal
  knowledge graph queries, composite scoring, consolidation, and constitutional
  guardrails. Use at session start, before each wave, at gate transitions, and
  when a subagent returns results.
---

# Memory Contract — Unified AI Memory Protocol

Based on: Flowbaby + Mem0 + Claude-Mem + OpenMemory + Pathway

---

## 5-SECTOR MEMORY MODEL

Every memory stored by any agent belongs to exactly one sector:

| Sector      | What goes here                                      | Decay Rate | Retention |
|-------------|-----------------------------------------------------|------------|-----------|
| episodic    | Specific events, what happened, errors, decisions   | 0.05/day   | 90 days   |
| semantic    | Facts, concepts, project knowledge, standards       | 0.01/day   | 365 days  |
| procedural  | How-to patterns, code patterns, workflows           | 0.02/day   | 180 days  |
| emotional   | Burnout indicators, productivity patterns, morale   | 0.08/day   | 60 days   |
| reflective  | Insights, retrospective learnings, process wisdom   | 0.005/day  | 730 days  |

**Classification guide:**
- "We decided to use FastAPI" → semantic
- "The auth module failed with 500 error on 2026-03-01" → episodic
- "Always run tests before commit" → procedural
- "User is in hyperfocus, energy high" → emotional
- "We tend to skip UAT — needs process fix" → reflective

---

## AGENT-SPECIFIC SECTOR FOCUS (Table 8)

Each agent retrieves from and stores to specific sectors:

| Agent         | Retrieve From              | Store To                  |
|---------------|----------------------------|---------------------------|
| planner       | semantic, reflective       | semantic, reflective      |
| implementer   | procedural, episodic       | procedural, episodic      |
| architect     | semantic, reflective       | semantic, reflective      |
| analyst       | episodic, reflective       | episodic, semantic        |
| code-reviewer | procedural, semantic       | procedural, episodic      |
| critic        | semantic, reflective       | semantic, reflective      |
| security      | episodic, procedural       | episodic, procedural      |
| qa            | episodic, procedural       | episodic, procedural      |
| uat           | episodic, reflective       | episodic, reflective      |
| devops        | procedural                 | procedural                |
| roadmap       | semantic, reflective       | semantic, reflective      |
| retrospective | reflective (all sectors)   | reflective                |
| pi            | episodic, semantic         | episodic, semantic        |

---

## PHASE 0 — SESSION BOOT (MANDATORY)

On every session start, execute ALL steps:

```
Step 1: Retrieve active context
  #flowbabyRetrieveMemory {
    "query": "active fleet plans constraints decisions",
    "maxResults": 5
  }

Step 2: Retrieve sector-specific context for the task
  Layer 1 (Core): query your sector, min_salience 0.7, limit 5
  Layer 2 (Extended): query your sector, min_salience 0.5, limit 10
  Layer 3 (Archive): only if L1+L2 insufficient, min_salience 0.3, limit 20

Step 3: Check for stale memories (not accessed in 30+ days)
  — note these for decay (lower salience weight in retrieval)

Step 4: Check temporal context
  — "what was true on [date]?" queries for time-sensitive facts

Step 5: Confirm memory health
  [ ] Active fleet plans identified
  [ ] Key constraints loaded
  [ ] Last gate decisions visible
  [ ] In-progress implementation state known
```

---

## PROGRESSIVE RETRIEVAL — 3 LAYERS (Claude-Mem)

Always retrieve in layers. Start with L1. Only go deeper if needed.
This achieves 10x token savings vs. flooding context.

```
LAYER 1 — CORE CONTEXT
  Query: [specific task-relevant query]
  Sectors: [agent's primary sectors]
  Min salience: 0.7
  Max results: 5
  Token budget: ~200 tokens
  Use when: Starting any task

LAYER 2 — EXTENDED CONTEXT
  Query: [broader related query]
  Sectors: [agent's primary + secondary sectors]
  Min salience: 0.5
  Max results: 10
  Token budget: ~400 tokens
  Use when: L1 didn't have enough context

LAYER 3 — DEEP ARCHIVE
  Query: [historical/pattern query]
  Sectors: all
  Min salience: 0.3
  Max results: 20
  Token budget: ~800 tokens
  Use when: Complex decisions needing full history
```

Context injection target: **800–1000 tokens total** (Flowbaby principle).
Never inject more than 1000 tokens — cognitive overload prevention.

---

## COMPOSITE SCORING

When retrieving, memories are ranked by composite score:

```
score = (salience × 0.4) + (recency × 0.3) + (coactivation × 0.3)

Where:
  salience     = 0.0–1.0, how important this memory is
  recency      = 1.0 for today, decays per sector rate
  coactivation = how often this memory is retrieved together with others
```

When referencing memories, always note their salience:
`[procedural] Always run TDD first (ID: mem_abc123, Salience: 0.87)`

---

## RETRIEVE PROCEDURE

Standard retrieve:
```
#flowbabyRetrieveMemory {
  "query": "...",
  "maxResults": 5
}
```

Query patterns by context:
- Before planning:      `"active epics roadmap open questions constraints"`
- Before implementing:  `"[module name] code patterns TDD precedents"`
- Before security gate: `"security findings CVEs injection patterns"`
- Before DevOps gate:   `"versioning conventions CHANGELOG format release"`
- After error:          `"[error type] patterns lessons learned solutions"`
- Temporal query:       `"[subject] state history what was true"`

---

## STORE PROCEDURE

Always store using the correct sector:

```
#flowbabyStoreSummary {
  "topic": "3-7 words — specific not generic",
  "context": "full narrative: what happened, why, outcome",
  "decisions": ["decision-1", "decision-2"],
  "sector": "episodic|semantic|procedural|emotional|reflective",
  "tags": ["tag1", "tag2"],
  "salience": 0.0-1.0
}
```

**Good topics (specific):**
- ✅ "auth module JWT expiry 24h decided"
- ✅ "TDD gate failed implementer returned"
- ✅ "user prefers TypeScript for backend"
- ❌ "implementation decision" (too generic)
- ❌ "something happened" (useless)

**When to store:**
- Fleet Plan completion → semantic (project knowledge)
- Each wave completion → episodic (what happened)
- Gate pass/fail → episodic + procedural (what to do next time)
- Key decision → semantic (fact)
- Error/blocker → episodic + procedural (lesson)
- Pattern recognized → reflective (insight)

---

## REINFORCEMENT

When a memory proves useful, reinforce it:
```
Reinforce: memory_id=[ID]
Action: increase salience by 0.1, update last_accessed timestamp
Use when: a retrieved memory directly helped solve a problem
```

---

## TEMPORAL KNOWLEDGE GRAPH

For time-sensitive facts, use temporal queries:

```
Temporal store: subject + predicate + object + valid_from
Example: "ProjectX uses FastAPI valid_from 2026-03-01"

Temporal query: "what was [subject]'s [predicate] on [date]?"
Example: "What framework was ProjectX using on 2026-02-01?"

Temporal classes:
  atemporal  — never changes (e.g., "Python is interpreted")
  static     — true from a point in time (e.g., "uses FastAPI since v2")
  dynamic    — evolves over time (e.g., "current sprint status")
```

---

## CONSOLIDATION (Cross-Sector Synthesis)

Trigger consolidation when:
- 7+ days since last consolidation
- Wave execution complete
- Major gate passed
- User explicitly requests insights

Consolidation query:
```
#flowbabyRetrieveMemory {
  "query": "patterns insights reflections learnings last 7 days",
  "maxResults": 20
}
```

After consolidation, store insights to **reflective** sector:
- What patterns emerged?
- What should change in the process?
- What worked well and should be repeated?

---

## CONSTITUTIONAL GUARDRAILS

Before storing ANY memory, validate:
- ❌ No API keys, tokens, or passwords
- ❌ No PII (phone numbers, addresses, SSNs)
- ❌ No credentials or secrets of any kind
- ✅ Redact sensitive data before storing
- ✅ Emotional state tracking requires explicit consent
- ✅ User-controlled deletion ("right to forget" — any memory can be deleted on request)
- ✅ Separate personal from professional memory spaces

If content contains credentials: REJECT with message
`"Memory contains sensitive data — please redact before storing"`

---

## ADHD/AUTISM SUPPORT PATTERNS

This memory system provides cognitive support:

1. **Context switches** — always store task state before switching
   `"Working on [task] — at step [n] — next: [what to do]"`

2. **Session resume** — always retrieve at start:
   `"What was I working on? What was the next step?"`

3. **Hyperfocus preservation** — capture flow state context fully
   `"In deep flow on [task] — key insights: [...]"`

4. **Time blindness mitigation** — always timestamp decisions
   Include date context in all stores: `"On 2026-03-01, decided..."`

5. **Information overload prevention** — never exceed 1000 token injection
   Use L1 only unless deeper context is genuinely needed

---

## NO-MEMORY MODE

If flowbaby tools are unavailable:
1. Announce: `⚠️ NO-MEMORY MODE — proceeding with visible reasoning only`
2. Document ALL reasoning explicitly in output
3. Ask user to confirm any critical context
4. Continue full Fleet operation — memory is non-blocking

---

## MEMORY HEALTH INDICATORS

Healthy memory system:
- Episodic: active recent events (last 90 days)
- Semantic: stable project knowledge
- Procedural: consistently-used patterns
- Emotional: mood/energy tracking active
- Reflective: insights generated weekly

Warning signs:
- No reflective memories → consolidation overdue
- Very high emotional decay → burnout risk pattern
- Procedural conflicts → process inconsistency
