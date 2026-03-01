---
description: Decompose a complex request into a Fleet parallel execution plan with wave structure, agent assignments, and dependency graph.
---

Decompose the following request into a Fleet execution plan.

Request: ${input:request:Describe the full task to decompose}

Follow the Fleet decomposition protocol:

1. Run the STRUCTURED REASONING PIPELINE (UNDERSTAND → ANALYZE → REASON → SYNTHESIZE → CONCLUDE)

2. Output a Fleet Plan table:
```
📋 FLEET PLAN
TASK ID | SUBAGENT | SCOPE | DEPENDS ON | STATUS
```

3. Define waves:
- WAVE 1 (parallel): independent tasks
- WAVE 2+: tasks dependent on earlier waves  
- SEQUENTIAL GATES: Code Review → Security → QA → UAT → DevOps

4. List any OPEN QUESTIONS that must be resolved before implementation begins.

5. State the Value Statement: what the user gets when this is complete.
