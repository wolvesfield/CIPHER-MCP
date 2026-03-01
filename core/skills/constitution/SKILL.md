---
name: constitution
description: >
  Project constitution framework — immutable architectural principles that all
  agents must check before any implementation. Based on github/spec-kit's
  constitution model. Load this skill when creating a new project constitution,
  when a Planner or Architect agent runs the Constitution Check gate, or when
  an Implementer needs to validate their approach against project principles.
---

# Constitution Skill — Immutable Architectural Principles

Based on: github.com/github/spec-kit — Constitution-driven architecture

---

## WHAT IS A CONSTITUTION

A project constitution defines immutable architectural principles.
Unlike specs (which define features) and plans (which define implementation),
the constitution defines **how the project must always be built**.

**Immutability**: Core principles don't change with features.
**Supremacy**: Constitution overrides all other practices.
**Consistency**: All AI-generated code across all time follows the same principles.
**Quality**: Embeds test-first, simplicity, observability guarantees.

---

## LOCATION

```
memory/constitution.md    ← per project
~/.copilot/copilot-instructions.md  ← global (always-on rules)
```

---

## CONSTITUTION CHECK GATE (MANDATORY)

Every implementation plan MUST run this gate BEFORE Phase 1 design:

```
CONSTITUTION CHECK PROCEDURE:

1. Load memory/constitution.md
   If missing: WARN "No constitution found — using global defaults"
   
2. For each principle in the constitution:
   - Evaluate: does this plan/feature comply?
   - Result: PASS ✅ or FAIL ❌
   
3. If any gate FAILS:
   Option A: Fix the approach to comply
   Option B: Justify exception in plan.md "Complexity Tracking" section:
     - Violation: [what principle is violated]
     - Why Needed: [specific technical reason]
     - Simpler Alternative Rejected Because: [why compliant approach won't work]
   
4. NEVER proceed with unjustified violations
5. Re-check after Phase 1 design (design may introduce new violations)
```

---

## DEFAULT GATE SET (when no constitution.md exists)

| Gate | Check | Fail Condition |
|------|-------|----------------|
| Spec-First | Does spec.md exist? | Implementation before spec |
| TDD | Tests before implementation? | Code before tests |
| Independent Stories | Can P1 ship without P2? | Stories tightly coupled |
| Simplicity | Simplest solution chosen? | Unnecessary abstraction |
| Observability | CLI/logging inspectable? | Silent failures possible |
| Security | No secrets in code/logs? | Hardcoded credentials |

---

## CREATING A PROJECT CONSTITUTION

When a new project starts, create `memory/constitution.md`:

```
1. Start from the template at C:\Users\arcan_e9q9t\memory\constitution.md
2. Fill in project-specific constraints (language, framework, storage, etc.)
3. Review the 7 default principles — keep, modify, or add project-specific ones
4. Set the ratification date
5. Store to memory:
   #flowbabyStoreSummary {
     "topic": "[project] constitution ratified",
     "context": "Constitution established with [n] principles. Core gates: [list]. Project stack: [stack].",
     "sector": "semantic",
     "tags": ["constitution", "project-setup"],
     "salience": 0.95
   }
```

---

## AMENDING THE CONSTITUTION

Amendments require ALL of:
1. **Documented rationale** — why is this change necessary?
2. **Approval** — explicit user or team acknowledgment
3. **Migration plan** — how does existing code conform to the new principle?
4. **Version bump** — increment constitution version number
5. **Amendment log entry** — add dated entry to amendment log

**Never amend silently.** Always surface amendments to user before applying.

---

## ARCHITECTURAL PATTERNS (per principle)

### Spec-First patterns:
```
specs/[###-name]/spec.md         ← create first, always
specs/[###-name]/plan.md         ← after spec approved
specs/[###-name]/tasks.md        ← after plan approved
src/[module]/                    ← after tasks defined
```

### TDD patterns:
```
tests/contract/test_[name].py    ← FIRST (contracts)
tests/integration/test_[name].py ← FIRST (journeys)
src/models/[entity].py           ← after tests fail
src/services/[service].py        ← after tests fail
src/api/[endpoint].py            ← after tests fail
```

### Simplicity gate — questions to ask:
- Does this need a class or would a function work?
- Does this need a database or would a file work?
- Does this need a service or would a module work?
- Can this be a library that's independently testable?

### Observability patterns:
```python
# Every operation: structured log entry
logger.info("operation_name", extra={"entity_id": id, "action": action, "result": result})

# Every CLI: --verbose flag, --json output flag
# Every error: stderr with error type, context, and suggested fix
```

---

## CONSTITUTION AND FLEET

In fleet, the Constitution skill is used by:

| Agent | When | How |
|-------|------|-----|
| Planner | After spec, before plan Phase 1 | Run Constitution Check Gate |
| Architect | During design | Validate all architectural decisions |
| Code Reviewer | Post-implementation | Verify constitution compliance |
| Critic | During plan review | Check constitution alignment |

Constitution violations discovered by Code Reviewer or Critic:
- Escalate to SAME-DAY level
- Route back to Implementer with specific violation
- Do NOT approve until resolved or exception justified

---

## MEMORY STORAGE FOR CONSTITUTION CHECKS

```
#flowbabyStoreSummary {
  "topic": "Constitution check [feature] [PASS/FAIL]",
  "context": "Gates checked: [list]. Results: [pass/fail per gate]. Exceptions justified: [list]. Plan approved to proceed: [yes/no].",
  "sector": "procedural",
  "tags": ["constitution-check", "[feature]", "[result]"]
}
```
