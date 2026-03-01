---
description: Perform a comprehensive code review of implementation changes.
---

Perform a code review of the following implementation:

Files to review: ${input:files:Comma-separated list of files or directories}
Plan reference: ${input:plan:Plan ID or description of what was implemented}

Review against these criteria:

**TDD Compliance**
- Every function has a test
- Tests assert on behavior, not mocks
- No test-only methods in production code

**Code Quality**
- Single responsibility per function/module
- Early returns reduce nesting
- No magic numbers
- Error handling is explicit

**Security**  
- No secrets or credentials
- Safe dependency versions
- No injection vectors

**Standards**
- Follows project coding conventions
- Documentation is accurate
- Scope matches Fleet Plan (no scope creep)

Severity:
- 🔴 BLOCKING — must fix before QA
- 🟡 WARNING — should fix, non-blocking
- 🔵 SUGGESTION — optional

Output a Code Review report with decision: APPROVED or REJECTED.
If REJECTED, list specific required changes for Implementer.
