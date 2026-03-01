---
mode: ask
description: Resolve spec ambiguities through targeted questions — Step 2 of Spec-Driven Development
---

# Spec-Driven Development — Step 2: CLARIFY

Goal: Resolve ambiguities in the feature spec BEFORE planning begins.
Max 5 questions. One at a time. Spec is updated after each answer.

**Feature branch (or leave blank for current):**
${input:feature_branch:Feature branch name (e.g., 001-user-auth) or leave blank}

---

## Execution

1. Read `specs/[branch]/spec.md`
   If not found: "Run /speckit-specify first"

2. Scan for ambiguity across these categories:
   - Functional scope & behavior (actors, goals, out-of-scope)
   - Domain & data model (entities, relationships, state)
   - User interaction & UX flow (error states, edge cases)
   - Non-functional attributes (performance, security, compliance)
   - Integration & external dependencies
   - Edge cases & failure handling
   - Completion signals / Definition of Done

3. If no meaningful ambiguities → "No critical ambiguities — proceed to /speckit-plan" (done)

4. For each ambiguity (max 5), ask ONE question at a time:
   - Always provide a **Recommended answer** with 1-2 sentence reasoning
   - Format: `**Recommended:** Option [X] — [reason]`
   - Present options as a markdown table
   - Wait for user response before next question
   - Accept: option letter, "yes"/"recommended" (uses your suggestion), or custom answer

5. After each accepted answer:
   - Update spec.md immediately (atomic save)
   - Add to `## Clarifications` section: `- Q: [question] → A: [answer]`
   - Apply clarification to the relevant spec section

6. After all questions:
   - Report: questions asked, sections updated, any Deferred items
   - Suggest: proceed to /speckit-plan
