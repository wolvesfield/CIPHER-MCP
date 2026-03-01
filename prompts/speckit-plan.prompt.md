---
mode: ask  
description: Create implementation plan from spec — Step 3 of Spec-Driven Development
---

# Spec-Driven Development — Step 3: PLAN

Creates: research.md → data-model.md → contracts/ → plan.md
Source of truth: spec.md (do NOT modify it during planning)

**Feature branch (or leave blank for current):**
${input:feature_branch:Feature branch name (e.g., 001-user-auth) or leave blank}

**Technology context (optional — helps with research):**
${input:tech_context:e.g., "Python FastAPI PostgreSQL" or leave blank to infer}

---

## Execution

### Constitution Check (MANDATORY GATE)
1. Load `memory/constitution.md`
   If missing: warn "No constitution found — recommend running /speckit-constitution first"
2. Check all gates against spec requirements
3. If any gate FAILS: STOP — error with specific violation
   Document justified exceptions in plan.md "Complexity Tracking" section

### Phase 0: Research
1. Identify all unknowns and NEEDS CLARIFICATION items from spec
2. For each unknown, research and document in `specs/[branch]/research.md`:
   ```
   ## [Topic]
   **Decision**: [what was chosen]
   **Rationale**: [why chosen]
   **Alternatives considered**: [what else evaluated]
   ```
3. All NEEDS CLARIFICATION must be resolved before Phase 1

### Phase 1: Design
1. Extract entities from spec → `specs/[branch]/data-model.md`
   - Entity name, fields, relationships, validation rules, state transitions
2. Define interface contracts → `specs/[branch]/contracts/`
   - APIs for web services, CLI schemas for tools, UI contracts for apps
   - Skip if purely internal project
3. Create `specs/[branch]/plan.md` using template:
   ```markdown
   # Implementation Plan: [FEATURE]
   **Branch**: [###] | **Date**: [DATE] | **Spec**: specs/[###]/spec.md

   ## Summary
   [Primary requirement + chosen technical approach]

   ## Technical Context
   Language/Version: [specific version]
   Primary Dependencies: [list with versions]
   Storage: [or N/A]
   Testing: [framework]
   Target Platform: [specific target]
   Project Type: [library/cli/web-service/mobile-app]

   ## Constitution Check
   [Each gate: PASS ✅ or FAIL ❌ with justification]

   ## Project Structure
   [Concrete file tree — real paths, no option labels]

   ## Complexity Tracking
   [Only if gate violations need justification]
   ```

### After Plan Complete
Store to memory:
```
#flowbabyStoreSummary {
  "topic": "[branch] implementation plan ready",
  "context": "Plan for [feature]. Tech: [stack]. Structure: [summary]. Constitution: [PASS/FAIL]. Research findings: [key decisions].",
  "sector": "semantic",
  "tags": ["plan", "[branch]", "sdd"]
}
```
Suggest: "/speckit-tasks to break plan into executable tasks"
