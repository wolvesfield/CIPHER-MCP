---
name: spec-driven
description: >
  Spec-Driven Development (SDD) methodology from github/spec-kit. Specs are
  the source of truth — code serves specifications, never the other way around.
  Use this skill whenever building a new feature, planning any implementation,
  or when the Planner agent is activated. Enforces the 5-step workflow:
  specify → clarify → plan → tasks → implement.
---

# Spec-Driven Development (SDD)

Based on: github.com/github/spec-kit — Specification-Driven Development methodology

---

## THE POWER INVERSION

Traditional development: specs serve code (docs written then discarded).
SDD: **code serves specs** — specs are the source of truth, code is their expression.

- Specifications generate implementation plans
- Implementation plans generate code
- Debugging means fixing specs, not just code
- Refactoring means restructuring for clarity
- Pivoting means updating specs first

Intent is expressed in natural language. Code is the last-mile delivery.

---

## THE 5-STEP WORKFLOW (MANDATORY ORDER)

```
STEP 1: SPECIFY    → Write the feature spec (PRD)
STEP 2: CLARIFY    → Resolve ambiguities (max 5 questions)
STEP 3: PLAN       → Research + design + contracts
STEP 4: TASKS      → Break plan into atomic, ordered tasks
STEP 5: IMPLEMENT  → Execute tasks (TDD-first mandatory)
```

**NEVER skip steps. NEVER implement before spec exists.**
**NEVER code before plan. NEVER plan before spec.**

---

## DIRECTORY STRUCTURE

Every feature creates this structure:
```
specs/
└── [###-feature-name]/
    ├── spec.md            ← STEP 1 output (the source of truth)
    ├── plan.md            ← STEP 3 output (implementation plan)
    ├── research.md        ← STEP 3 Phase 0 output
    ├── data-model.md      ← STEP 3 Phase 1 output
    ├── contracts/         ← STEP 3 Phase 1 output (API/interface contracts)
    ├── tasks.md           ← STEP 4 output (task checklist)
    └── checklists/        ← quality gate checklists

memory/
└── constitution.md        ← immutable project principles (load-constitution skill)
```

Branch naming: `###-feature-name` (number auto-incremented, 2-4 word slug)
Example: `001-user-auth`, `002-payment-flow`, `003-analytics-dashboard`

---

## STEP 1: SPECIFY (spec.md)

The spec answers: **WHAT** and **WHY** — never HOW.
Written for business stakeholders, not developers.
No technology stack, no APIs, no code structure.

### Spec Structure:
```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`
**Created**: [DATE]
**Status**: Draft

## User Scenarios & Testing (mandatory)
[Prioritized user journeys — P1=MVP, P2, P3... each INDEPENDENTLY TESTABLE]

### User Story 1 - [Title] (Priority: P1)
[Plain language description]
**Why this priority**: [value explanation]
**Independent Test**: [how to test standalone]
**Acceptance Scenarios**:
1. Given [state], When [action], Then [outcome]

## Requirements (mandatory)
### Functional Requirements
- **FR-001**: System MUST [specific testable capability]
- **FR-002**: [NEEDS CLARIFICATION: specific question] ← max 3 total

## Success Criteria (mandatory)
- **SC-001**: [Measurable, technology-agnostic, user-focused metric]

## Edge Cases
- What happens when [boundary condition]?
```

### Spec Quality Rules:
- **Max 3 `[NEEDS CLARIFICATION]` markers** — only for decisions that significantly impact scope
- Every requirement must be **testable and unambiguous**
- Success criteria must be **measurable, technology-agnostic, user-focused**
- User stories must be **independently testable** — each is a viable MVP slice
- User stories must be **prioritized** (P1, P2, P3...)
- Good SC: "Users complete checkout in under 3 minutes" ✅
- Bad SC: "API response time under 200ms" ❌ (too technical)

### NEEDS CLARIFICATION — when to use:
Use ONLY when:
- Choice significantly impacts feature scope or user experience
- Multiple reasonable interpretations with different implications exist
- No reasonable default exists

Do NOT ask about:
- Performance targets (use industry standards)
- Error handling (use user-friendly defaults)
- Authentication method (use standard OAuth2/session)
- Data retention (use domain standards)

---

## STEP 2: CLARIFY (interactive)

Run before planning. Detect ambiguity using this taxonomy:
- Functional scope & behavior
- Domain & data model
- Interaction & UX flow
- Non-functional quality attributes
- Integration & external dependencies
- Edge cases & failure handling
- Constraints & tradeoffs
- Completion signals / Definition of Done

Rules:
- **Max 5 questions total per session**
- One question at a time (never dump all at once)
- Always provide a recommended answer with reasoning
- After each answer: update spec.md immediately (atomic save)
- If no meaningful ambiguities → "No critical ambiguities detected — proceed to /speckit.plan"
- If clarification would block functional clarity: ask it
- If it's an implementation detail: skip it

---

## STEP 3: PLAN (plan.md + research.md + data-model.md + contracts/)

### Phase 0: Research
For each NEEDS CLARIFICATION and each unknown:
- Dispatch research agent with specific query
- Consolidate findings in research.md:
  ```
  Decision: [what was chosen]
  Rationale: [why chosen]
  Alternatives considered: [what else evaluated]
  ```

### Constitution Check Gate (MANDATORY):
Load `memory/constitution.md`. Check every gate.
If any gate fails: ERROR — justify or fix before proceeding.
Document any justified exceptions in "Complexity Tracking" section of plan.md.

### Phase 1: Design
From spec entities → data-model.md (entities, fields, relationships, state transitions)
From spec requirements → contracts/ (API endpoints, CLI schemas, UI contracts)
Update agent context file after design is complete.

### Plan Template:
```
# Implementation Plan: [FEATURE]
**Branch**: [###-feature-name] | **Date**: [DATE] | **Spec**: specs/[###]/spec.md

## Summary
[Primary requirement + technical approach]

## Technical Context
Language/Version: [or NEEDS CLARIFICATION]
Primary Dependencies: [or NEEDS CLARIFICATION]
Storage: [or N/A]
Testing: [or NEEDS CLARIFICATION]
Target Platform: [or NEEDS CLARIFICATION]
Project Type: [library/cli/web-service/mobile-app]
Performance Goals: [specific targets]
Constraints: [specific constraints]

## Constitution Check
[Gate results — PASS or FAIL with justification]

## Project Structure
[File tree — concrete paths, no Option labels in final]

## Complexity Tracking
[Only if Constitution Check has violations that need justification]
```

---

## STEP 4: TASKS (tasks.md)

Break the plan into atomic, independently executable tasks.
Group by user story so each story can be delivered as an MVP increment.

### Task Format:
```
- [ ] T001 Create project structure per plan
- [ ] T002 [P] Initialize dependencies                ← [P] = parallel safe
- [ ] T003 [P] [US1] Entity model in src/models/x.py ← [Story] = user story tag
- [ ] T004 [US1] Service layer (depends on T003)
```

### Phase Structure:
```
Phase 1: Setup (shared infrastructure)
Phase 2: Foundational (blocks ALL user stories — CRITICAL)
Phase 3: User Story 1 - [Title] (P1) 🎯 MVP
  ⚠️ Write tests FIRST, ensure they FAIL before implementing
Phase 4: User Story 2 - [Title] (P2)
Phase 5: User Story 3 - [Title] (P3)
Phase N: Polish & Cross-cutting concerns
```

### Execution Rules:
- Foundation (Phase 2) MUST complete before ANY user story begins
- Tests MUST be written AND FAILING before implementation
- User stories can run in parallel once Foundation is complete
- [P] tasks within same phase can run simultaneously
- Commit after each task or logical group
- CHECKPOINT after each user story — validate independently before proceeding

### Within-story order:
Tests (fail first) → Models → Services → Endpoints/CLI → Integration → Polish

---

## STEP 5: IMPLEMENT (task-by-task execution)

Before starting:
1. Check all checklists — if any incomplete, ask "proceed anyway? (yes/no)"
2. Load: tasks.md (REQUIRED), plan.md (REQUIRED), data-model.md, contracts/, research.md
3. Verify/create ignore files (.gitignore, .dockerignore, etc.) per tech stack

Execute:
- Phase-by-phase — complete each phase before next
- Mark tasks as [X] in tasks.md when complete
- TDD-first: tests fail → implement → tests pass
- Halt on non-parallel task failure
- Report progress after each completed task
- Final validation: all tasks done, tests pass, spec satisfied

---

## INCREMENTAL DELIVERY STRATEGY

### MVP First (User Story 1 Only):
1. Setup → Foundation → User Story 1
2. STOP AND VALIDATE independently
3. Ship if ready, then add P2, P3...

### Parallel Team Strategy:
- All developers complete Foundation together
- Then each developer takes one user story
- Stories integrate independently

---

## QUALITY GATES

Between steps, validate:

| Gate | Trigger | Check |
|------|---------|-------|
| Spec Quality | After specify | ≤3 NEEDS CLARIFICATION, all stories independent, criteria measurable |
| Clarify Complete | After clarify | No unresolved ambiguities blocking planning |
| Constitution | Before plan Phase 1 | All gates pass or exceptions justified |
| Research Complete | Before design | All NEEDS CLARIFICATION resolved |
| Tasks Ready | Before implement | tasks.md exists, stories grouped, test tasks before impl tasks |
| TDD Gate | During implement | Tests written and FAILING before code written |
| Story Complete | After each story | Story passes independent test from spec |

---

## MEMORY INTEGRATION

Spec-driven workflow stores to **semantic** sector:
```
Store spec created:
  topic: "[###-feature-name] spec created"
  sector: semantic
  tags: ["spec", "feature", "[name]"]

Store plan created:
  topic: "[###-feature-name] implementation plan ready"
  sector: semantic
  tags: ["plan", "feature", "[name]"]

Store constitution decision:
  topic: "constitution gate [PASS/FAIL] [feature]"
  sector: procedural
  tags: ["constitution", "gate"]

Store completion:
  topic: "[###-feature-name] implemented [US1/US2/...]"
  sector: episodic
  tags: ["implementation", "complete", "[feature]"]
```

---

## SDD WITH FLEET

In fleet, the SDD workflow maps to agents:

```
SPECIFY  → Planner agent (creates spec.md)
CLARIFY  → Planner agent + user interaction
PLAN     → Planner (research) + Architect (design) + Analyst (unknowns)
TASKS    → Planner agent (creates tasks.md)
IMPLEMENT→ Implementer agent (TDD-first, per tasks.md)
REVIEW   → Code Reviewer → Security → QA → UAT → DevOps
```

Fleet dispatches in waves:
- Wave 1: Planner (specify + clarify + plan + tasks)
- Wave 2: Critic (reviews spec + plan quality)
- Wave 3: Implementer (per tasks.md, TDD-first)
- Gates: Code Review → Security → QA → UAT → DevOps
```
