---
name: document-lifecycle
description: >
  Fleet document ID assignment and lifecycle management protocol. Use this
  skill at session start to check for stale documents and assign IDs, and
  at session end to ensure DevOps has closed all documents. Enforces the
  Active → In Progress → Committed → Released lifecycle for all agent-output
  documents.
---

# Document Lifecycle — Fleet Document Protocol

## Document ID Assignment (session start)

### Fleet as originating agent:
1. Read `agent-output/.next-id`
   - If file missing: create it with content `1`
2. Assign that number as the Fleet Plan ID
3. Increment: write `ID + 1` back to `agent-output/.next-id`
4. Generate UUID: 8 random hex characters (e.g., `a3f8c921`)

### All subagent documents inherit from Fleet:
- Same ID as the Fleet Plan
- Same UUID
- Origin = Fleet Plan ID

## Document Header (ALL agent-output docs)
```yaml
---
ID: [fleet plan id]
Origin: [fleet plan id or analysis id if inherited]
UUID: [8-char hex]
Status: Active
Agent: [agent name that created this]
Created: [date]
---
```

## Status Lifecycle
```
Active
  → In Progress   (work has begun)
  → Committed     (changes committed to repo)
  → Released      (shipped / deployed)

Terminal (DevOps closes these):
  → Abandoned     (work stopped, not shipped)
  → Deferred      (postponed to future sprint)
  → Superseded    (replaced by newer plan)
```

## Directory Structure
```
agent-output/
├── .next-id              ← sequential ID counter
├── planning/             ← Planner docs
├── architecture/         ← Architect docs + ADRs
├── implementation/       ← Implementer docs
├── analysis/             ← Analyst findings
├── qa/                   ← QA reports (QA-exclusive)
├── uat/                  ← UAT reports
├── retrospective/        ← Retrospective reports
└── closed/               ← Completed/terminal docs
    └── [plan-id]/        ← Grouped by plan
```

## Session Start Self-Check
Scan all agent-output/ subdirectories for documents with Status NOT in
{Committed, Released, Abandoned, Deferred, Superseded, Closed}.

If stale active docs found:
1. List them to the user
2. Ask: continue existing plan or start fresh?
3. Do NOT move to closed/ without user confirmation

## DevOps Closure Procedure
When DevOps gate completes:
1. Update all docs from this plan: Status → Released
2. Move all docs to `agent-output/closed/[plan-id]/`
3. Write closure summary in each doc footer:
   ```
   ---
   Closed: [date]
   Release: [version]
   Closed by: DevOps agent
   ---
   ```

## Naming Convention
```
agent-output/planning/[ID]-[slug].md
agent-output/implementation/[ID]-[module]-impl.md
agent-output/qa/[ID]-qa-report.md
agent-output/uat/[ID]-uat-report.md
```
Where [ID] is zero-padded 3 digits: `001`, `002`, etc.
