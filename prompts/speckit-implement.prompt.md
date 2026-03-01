---
mode: ask
description: Execute all tasks from tasks.md — Step 5 of Spec-Driven Development
---

# Spec-Driven Development — Step 5: IMPLEMENT

Executes tasks.md in order. TDD-first mandatory. Marks tasks complete as they're done.

**Feature branch (or leave blank for current):**
${input:feature_branch:Feature branch name (e.g., 001-user-auth) or leave blank}

**Override (optional — specific task range or user story):**
${input:scope:e.g., "Phase 3 only" or "T010-T017" or leave blank for all}

---

## Execution

### Pre-flight Checks
1. Load REQUIRED: `specs/[branch]/tasks.md` and `specs/[branch]/plan.md`
   If missing: "Run /speckit-tasks first"
2. Load IF EXISTS: data-model.md, contracts/, research.md, quickstart.md
3. Check checklists in `specs/[branch]/checklists/`:
   - Count incomplete items per checklist
   - If any incomplete: "Incomplete checklists found: [list]. Proceed anyway? (yes/no)"
   - Wait for response
4. Verify/create ignore files (.gitignore etc.) per plan.md tech stack

### Implementation Loop
For each phase in tasks.md (in order):

**Phase 1-2 (Setup + Foundation):**
- Execute all tasks respecting [P] markers
- Mark [X] in tasks.md when complete
- Report after each task: "✅ T001 complete — [what was done]"
- CHECKPOINT: "Foundation complete — starting user story implementation"

**Phase 3+ (User Stories — TDD FIRST):**
⚠️ For EVERY user story:
1. Write ALL test tasks first (lines marked with "Test")
2. Run tests — they MUST FAIL (if they pass, spec may be wrong)
3. Report: "TDD Gate: [test] fails as expected ✅ — proceeding with implementation"
4. Implement minimal code to pass tests
5. Run tests — they MUST PASS
6. Refactor while keeping tests green
7. CHECKPOINT: validate story independently before next story

**Error handling:**
- Sequential task failure: HALT — report error with context, suggest fix
- Parallel [P] task failure: continue others, report failed ones at end
- Gate failure: escalate to Fleet immediately

### Completion
1. Mark all completed tasks as [X] in tasks.md
2. Run all tests — report coverage
3. Validate against spec.md success criteria
4. Store to memory:
   ```
   #flowbabyStoreSummary {
     "topic": "[branch] implementation complete [stories]",
     "context": "Implemented [feature]. Tasks: [n]/[total] complete. Stories delivered: [list]. Tests: [coverage]%. Spec criteria met: [list].",
     "sector": "episodic",
     "tags": ["implementation", "complete", "[branch]"]
   }
   ```
5. Report: tasks completed, stories delivered, test coverage, spec criteria met
6. Suggest: "Run /code-review for Code Review Gate, then /security-review"
