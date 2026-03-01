---
mode: ask
description: Create a feature spec (PRD) from a natural language description — Step 1 of Spec-Driven Development
---

# Spec-Driven Development — Step 1: SPECIFY

You are writing a feature specification. Specs answer **WHAT** and **WHY** — never HOW.
No technology stack. No APIs. No code structure. Written for business stakeholders.

**Feature description:**
${input:feature_description:Describe the feature you want to build}

---

## Execution

1. Generate a concise branch slug (2-4 words, action-noun format):
   - "Add user authentication" → `user-auth`
   - "Build analytics dashboard" → `analytics-dashboard`
   - Branch name: `[auto-number]-[slug]` (check `specs/` folder for next number)

2. Create directory: `specs/[###-slug]/`

3. Create `specs/[###-slug]/spec.md` using this structure:

```markdown
# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-slug]`
**Created**: [today's date]
**Status**: Draft

## User Scenarios & Testing

### User Story 1 - [Title] (Priority: P1)
[Plain language user journey]
**Why this priority**: [business value]
**Independent Test**: [how to verify this alone delivers value]
**Acceptance Scenarios**:
1. Given [state], When [action], Then [outcome]
2. Given [state], When [action], Then [outcome]

### User Story 2 - [Title] (Priority: P2)
[Next most valuable journey]
**Independent Test**: [standalone verification]
**Acceptance Scenarios**:
1. Given [state], When [action], Then [outcome]

### Edge Cases
- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements

### Functional Requirements
- **FR-001**: System MUST [specific testable capability]
- **FR-002**: System MUST [capability]
- **FR-003**: [NEEDS CLARIFICATION: question] ← only if no reasonable default

### Key Entities (if data involved)
- **[Entity]**: [what it represents, key attributes]

## Success Criteria

- **SC-001**: [Measurable, user-focused metric — e.g., "Users complete X in under Y minutes"]
- **SC-002**: [Business or quality metric]
```

4. Rules while writing:
   - Max **3 [NEEDS CLARIFICATION]** markers — only for decisions that significantly change scope
   - Every requirement must be independently testable
   - Success criteria must be **measurable, technology-agnostic, user-focused**
   - Good: "Users complete checkout in under 3 minutes" ✅
   - Bad: "API response time under 200ms" ❌

5. After saving, store to memory:
```
#flowbabyStoreSummary {
  "topic": "[###-slug] spec created",
  "context": "Feature: [name]. User stories: [count] (P1: [title], P2: [title]). Key requirements: [list]. Success criteria: [list].",
  "sector": "semantic",
  "tags": ["spec", "[slug]", "sdd"]
}
```

6. Report: branch name, spec file path, user story count, any NEEDS CLARIFICATION items
7. Suggest next step: "Run /speckit-clarify to resolve ambiguities, or /speckit-plan if spec is clear"
