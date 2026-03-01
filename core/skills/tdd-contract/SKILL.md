---
name: tdd-contract
description: >
  TDD enforcement protocol for all implementation work. Use this skill when
  reviewing implementation outputs, when Implementer reports completion, or
  when Code Reviewer validates TDD compliance. Defines the Red-Green-Refactor
  contract, Iron Laws, and TDD gate procedure that Fleet enforces on all
  Implementer dispatches.
---

# TDD Contract — Fleet Test-Driven Development Protocol

## The Contract

```
RED     → Write a FAILING test first. The module must NOT exist yet.
GREEN   → Write the MINIMAL code to make the test pass. No extras.
REFACTOR→ Clean up while ALL tests stay green.
REPEAT  → For every function, class, and module.
```

## TDD Gate Procedure (per deliverable)

Fleet checks this sequence for every function or class in the implementation:

```
Step 1: STOP
        No implementation code has been written yet.
        Verify this by checking if the module/function exists.

Step 2: WRITE
        Implementer writes a failing test.
        Test imports the non-existent module/function.
        Example: from mymodule import MyClass  # does not exist yet

Step 3: RUN
        Execute the test. It MUST fail with the correct error:
        - ModuleNotFoundError — module doesn't exist
        - AttributeError — function doesn't exist
        - AssertionError — behavior not yet implemented

Step 4: REPORT
        "TDD Gate: Test [name] fails as expected: [error]. Proceeding."

Step 5: IMPL
        Write the MINIMAL code to make the test pass.
        Do not add features not covered by the test.

Step 6: VERIFY
        Run the test again. It MUST pass.

Step 7: REPEAT
        Move to the next function or class.
```

## Iron Laws (never violated)

1. **Never test mock behavior**
   - ❌ `assert mock.called` — tests that a mock was called
   - ✅ `assert result == expected` — tests actual behavior

2. **Never add test-only methods to production classes**
   - ❌ Adding `get_internal_state()` just for tests
   - ✅ Test through the public API

3. **Never mock without understanding dependencies**
   - Know WHY you are mocking, not just HOW
   - Document mock rationale in test comments

4. **Zero tests = incomplete**
   - Any implementation with zero tests is a constraint violation
   - Fleet must self-escalate immediately
   - Send back to Implementer with: `GATE FAILED: Zero tests found. TDD violated.`

## TDD Compliance Checklist (Code Reviewer validates)

- [ ] Every function/class has at least one test
- [ ] Tests were written BEFORE implementation (verify via git history if possible)
- [ ] Tests assert on BEHAVIOR, not on mock calls
- [ ] No test-only methods in production code
- [ ] All tests pass after implementation
- [ ] Coverage is above threshold (default: 80%)
- [ ] Edge cases are tested (null, empty, boundary values)

## Fleet Rejection Criteria

Fleet REJECTS any Implementer handoff that:
- Contains zero tests
- Has tests that only assert mock behavior
- Has test-only methods in production classes
- Has tests that were clearly written AFTER implementation (no RED phase evidence)

Rejection message:
```
GATE FAILED: TDD Contract Violated
Reason: [specific violation]
Required: [what Implementer must do before resubmitting]
Return to: Implementer
```

## Language-Specific Notes

**Python:**
```python
# Step 2: Write failing test first
import pytest
from mymodule import calculate_total  # ← ImportError expected

def test_calculate_total_with_discount():
    assert calculate_total(100, 0.1) == 90.0
```

**JavaScript/TypeScript:**
```javascript
// Step 2: Write failing test first
import { calculateTotal } from './mymodule';  // ← Module not found

test('calculates total with discount', () => {
  expect(calculateTotal(100, 0.1)).toBe(90);
});
```
