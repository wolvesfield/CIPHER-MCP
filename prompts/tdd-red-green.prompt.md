---
description: Guide through the TDD Red-Green-Refactor cycle for a specific function or module.
---

Apply TDD Red-Green-Refactor to implement the following:

Module: ${input:module:Name of the module or function to implement}
Behavior: ${input:behavior:What should this module/function do?}
Language: ${input:language:Python|TypeScript|JavaScript|Go|Rust}

Follow this exact sequence — do NOT skip steps:

**Step 1: RED — Write the failing test**
- Write a test that imports the non-existent module
- Run it and confirm it fails with the correct error
- Report: "TDD Gate: Test [name] fails as expected: [error]"

**Step 2: GREEN — Write minimal implementation**  
- Write the MINIMUM code to make the test pass
- No extra features, no premature optimization
- Run the test and confirm it passes

**Step 3: REFACTOR — Clean up**
- Improve structure, naming, and clarity
- Run tests again — all must still pass
- Report: "Refactor complete. All tests passing."

**Step 4: REPEAT**
- Identify the next behavior to implement
- Return to Step 1

Iron Laws:
- Never test mock behavior — assert on actual behavior
- Never add test-only methods to production classes
- If zero tests exist after implementation, it is INCOMPLETE
