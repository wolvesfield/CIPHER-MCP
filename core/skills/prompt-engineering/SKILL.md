---
name: prompt-engineering
description: >
  Enterprise prompt engineering patterns for agent-memory interactions.
  Use this skill when constructing prompts for complex tasks, when an agent
  needs structured reasoning, when memory context needs to be injected into
  a task prompt, or when the Fleet Reasoning Pipeline is being executed.
  Implements Chain-of-Thought, ReAct, Few-Shot, Constitutional, and
  Tree-of-Thoughts patterns.
---

# Prompt Engineering — Agent Reasoning Patterns

Based on: Prompt Engineering Guide (DAIR.AI) + Microsoft GenAI Guide + Awesome GPT Prompting

---

## PATTERN SELECTION GUIDE

Choose the right pattern for the task:

| Task Type                              | Pattern               |
|----------------------------------------|-----------------------|
| Complex multi-step reasoning           | Chain-of-Thought      |
| Tool use + iterative action            | ReAct                 |
| Classification with examples           | Few-Shot Learning     |
| Privacy/ethics-sensitive decisions     | Constitutional AI     |
| Exploring multiple solution paths      | Tree-of-Thoughts      |
| Consistency validation                 | Self-Consistency      |

---

## PATTERN 1: CHAIN-OF-THOUGHT (CoT)

Best for: Planning, architecture decisions, complex analysis

```
Template:
"Let's approach this step by step:

1. [Analyze the context — what do we know?]
2. [Identify relevant patterns from past experiences]
3. [Apply learned knowledge and constraints]
4. [Formulate response incorporating preferences]

Memory Context:
[injected from L1/L2/L3 retrieval]

Current Task:
[task description]

Step-by-step reasoning:"
```

Activation phrase: `"Let's think step by step:"` or `"Let's approach this systematically:"`

---

## PATTERN 2: ReAct (Reason + Act)

Best for: Implementer, analyst, PI — tasks requiring tool use + reasoning

```
Format:
Thought: [What I understand about the situation]
Action: [Tool I will use / step I will take]
Observation: [What I found / result of action]
Thought: [Updated understanding]
Action: [Next tool / step]
...
Final Answer: [Synthesized conclusion]
```

Example:
```
Thought: The user wants to find security vulnerabilities in the auth module.
Action: search auth/middleware for input validation patterns
Observation: Found 3 unvalidated inputs on lines 45, 78, 112
Thought: These could be injection vectors. Need to check sanitization.
Action: read auth/middleware/validation.py lines 40-120
Observation: No sanitization found. Missing parameterized queries.
Final Answer: 3 SQL injection vulnerabilities found. [details...]
```

---

## PATTERN 3: FEW-SHOT LEARNING

Best for: Sector classification, consistent output formatting

```
Template:
"Classify this memory into the correct sector.

Examples:
Input: 'We decided to use PostgreSQL for the main database'
Output: semantic (factual project decision)

Input: 'Auth endpoint crashed with 500 error during testing'
Output: episodic (specific event that happened)

Input: 'Always write failing test before implementation'
Output: procedural (how-to workflow pattern)

Input: 'User seemed stressed about the deadline'
Output: emotional (mood/state observation)

Input: 'We consistently underestimate security gate time'
Output: reflective (process insight/lesson)

Now classify:
Input: '[new content to classify]'
Output:"
```

---

## PATTERN 4: CONSTITUTIONAL AI

Best for: Security agent, QA, any privacy-sensitive work

```
Principles (always apply):
1. Respect privacy boundaries — never expose or store sensitive data
2. Acknowledge uncertainty explicitly — never fabricate confidence
3. Cite sources when possible — reference memory IDs or file locations
4. Maintain ADHD-friendly structure — clear steps, no overwhelm
5. Be honest about limitations — better to say "unknown" than guess
6. Avoid harm — flag potentially harmful patterns before acting

Template:
"Before responding, check against constitutional principles:

[ ] Does this response respect privacy?
[ ] Am I acknowledging any uncertainty?
[ ] Are my claims supported by evidence?
[ ] Is this structured to minimize cognitive load?
[ ] Could this response cause harm?

Constitutional check complete. Response:
[response]"
```

---

## PATTERN 5: TREE-OF-THOUGHTS (ToT)

Best for: Planner, architect — when multiple approaches need evaluation

```
Template:
"Explore multiple solution paths before deciding.

Path A: [Approach 1]
  Pros: [benefits]
  Cons: [drawbacks]
  Risk: [LOW|MEDIUM|HIGH]
  Memory support: [relevant memories supporting this path]

Path B: [Approach 2]
  Pros: [benefits]
  Cons: [drawbacks]
  Risk: [LOW|MEDIUM|HIGH]
  Memory support: [relevant memories supporting this path]

Path C: [Approach 3]
  Pros: [benefits]
  Cons: [drawbacks]
  Risk: [LOW|MEDIUM|HIGH]
  Memory support: [relevant memories supporting this path]

Evaluation:
Based on paths A/B/C, Path [X] is recommended because:
[reasoning that synthesizes all paths]
```

---

## PATTERN 6: SELF-CONSISTENCY

Best for: Critic, code-reviewer — validating decisions

```
Template:
"Evaluate this decision 3 times independently, then check consistency.

Evaluation 1:
[assess from technical correctness angle]
Decision: [APPROVE|REJECT]

Evaluation 2:
[assess from risk/safety angle]
Decision: [APPROVE|REJECT]

Evaluation 3:
[assess from user value angle]
Decision: [APPROVE|REJECT]

Consistency check:
All 3 agree: [final decision]
Conflict found: [identify the disagreement, flag as OPEN QUESTION]
```

---

## MEMORY-AWARE PROMPT CONSTRUCTION

When injecting memory context into a prompt:

```
## Memory Context
[L1 - Core (Salience ≥ 0.7)]
- [sector] [content] (ID: [id], Salience: [n], Age: [n]d)

[L2 - Extended (Salience ≥ 0.5, if needed)]
- [sector] [content] (ID: [id], Salience: [n], Age: [n]d)

## Current Task
[task description]

## Reasoning Process
[apply chosen pattern above]

## Response Guidelines
- Reference specific memories when applicable (cite memory IDs)
- Acknowledge knowledge gaps explicitly
- Update memories when user provides corrections
- Respect ADHD considerations: clear structure, no overwhelm

## Response:
```

Token budget: **800–1000 tokens total for memory context**.
Always cite memory IDs when referencing stored knowledge.

---

## PROMPT QUALITY CHECKLIST

Before dispatching a prompt to any agent:

- [ ] Pattern selected matches task complexity
- [ ] Memory context injected (L1 minimum)
- [ ] Token budget within 1000 tokens
- [ ] OPEN QUESTION items listed if ambiguous
- [ ] Constitutional principles applied if sensitive
- [ ] Expected output format specified
- [ ] Scope constraints explicit
