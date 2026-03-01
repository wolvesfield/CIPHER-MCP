---
mode: ask
description: Break implementation plan into atomic tasks — Step 4 of Spec-Driven Development
---

# Spec-Driven Development — Step 4: TASKS

Creates tasks.md — the execution checklist for the Implementer.
Organized by user story for independent MVP delivery.

**Feature branch (or leave blank for current):**
${input:feature_branch:Feature branch name (e.g., 001-user-auth) or leave blank}

---

## Execution

Prerequisites: `specs/[branch]/spec.md` + `specs/[branch]/plan.md` must exist.
Also load (if exist): data-model.md, contracts/, research.md

Create `specs/[branch]/tasks.md`:

```markdown
# Tasks: [FEATURE NAME]
**Spec**: specs/[###]/spec.md | **Plan**: specs/[###]/plan.md

## Phase 1: Setup
- [ ] T001 Create project structure per plan.md
- [ ] T002 [P] Initialize dependencies

## Phase 2: Foundational ⚠️ CRITICAL — blocks all user stories
- [ ] T003 [P] Setup database/storage schema
- [ ] T004 [P] Configure authentication framework
- [ ] T005 Setup error handling and logging
**Checkpoint**: Foundation ready — user stories can now begin

## Phase 3: User Story 1 - [Title] (P1) 🎯 MVP
**Goal**: [what this story delivers]
**Independent Test**: [how to verify standalone]

### Tests for US1 ⚠️ Write FIRST, verify FAIL before implementing
- [ ] T010 [P] [US1] Contract test for [endpoint]
- [ ] T011 [P] [US1] Integration test for [journey]

### Implementation for US1
- [ ] T012 [P] [US1] [Entity1] model in src/models/entity1.py
- [ ] T013 [US1] [Service] in src/services/service.py (depends T012)
- [ ] T014 [US1] [Endpoint/Feature] in src/api/endpoint.py

**Checkpoint**: User Story 1 independently functional and testable

## Phase 4: User Story 2 - [Title] (P2)
[Same pattern]

## Phase N: Polish
- [ ] TXXX [P] Documentation
- [ ] TXXX Security hardening
- [ ] TXXX Run all checklists

## Dependencies
- Phase 2 (Foundation) MUST complete before any Phase 3+
- User stories can run in parallel once Foundation complete
- Within each story: tests before models before services before endpoints
- [P] = safe to run in parallel (different files, no dependencies)
```

After creating tasks.md:
- Count total tasks, parallel tasks, user stories
- Store to memory: topic "[branch] tasks ready — [n] tasks across [n] stories" (sector: procedural)
- Suggest: "/speckit-implement to execute the tasks"
