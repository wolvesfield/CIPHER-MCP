---
name: fleet-escalation
description: >
  Fleet escalation framework and response protocol. Use this skill when a
  gate fails, a conflict is detected between agents, scope exceeds estimates,
  or a recurring pattern (3+ occurrences) is identified. Defines the four
  escalation levels (IMMEDIATE, SAME-DAY, PLAN-LEVEL, PATTERN) and required
  actions for each.
---

# Fleet Escalation Framework

## Escalation Levels

| Level      | Timing | Trigger Examples                                      |
|------------|--------|-------------------------------------------------------|
| IMMEDIATE  | <1h    | Security gate: critical CVE found                     |
|            |        | Gate failure blocking ALL downstream agents           |
|            |        | Secret or credential exposed in code                  |
|            |        | TDD contract: zero tests submitted as "complete"      |
| SAME-DAY   | <4h    | Agent conflict on overlapping files                   |
|            |        | Value statement undeliverable with current approach   |
|            |        | Architecture mismatch discovered mid-implementation   |
|            |        | Unexpected API breaking change                        |
| PLAN-LEVEL | —      | Scope significantly larger than estimated             |
|            |        | Acceptance criteria unverifiable                      |
|            |        | Core assumption invalidated by Analyst findings       |
| PATTERN    | —      | 3+ occurrences of same gate failure                   |
|            |        | Same agent conflict recurring across plans            |
|            |        | Persistent TDD violations                             |

## Required Actions Per Level

### IMMEDIATE
1. **Halt fleet** — stop ALL agent dispatches immediately
2. **Surface to user** — present the specific issue clearly
3. **Await explicit direction** — do not proceed without user ACK
4. **Document in Fleet Log** — record issue, time, user decision

```
🚨 IMMEDIATE ESCALATION
Issue: [specific problem]
Impact: [what is blocked / at risk]
Options:
  A) [option 1]
  B) [option 2]
Awaiting your decision before proceeding.
```

### SAME-DAY
1. **Flag the wave** — mark affected tasks as BLOCKED
2. **Re-route** — send to Planner (scope) or Architect (design) as appropriate
3. **Continue non-blocked waves** — don't halt unaffected work
4. **Report to user** — inform but don't require immediate response

```
⚠️ SAME-DAY ESCALATION
Issue: [specific problem]
Affected tasks: [T-XX, T-XX]
Action taken: Routing to [Planner/Architect]
Other waves: Continuing [T-XX, T-XX]
Expected resolution: [same day]
```

### PLAN-LEVEL
1. **Invoke Planner** for re-scope
2. **Invoke Critic** for re-approval of revised plan
3. **Suspend implementation** until new plan approved
4. **Notify user** with summary and revised timeline

```
📋 PLAN-LEVEL ESCALATION
Issue: [scope/assumption problem]
Current plan: [plan-id]
Action: Returning to planning phase
Re-scope required: [what needs to change]
User input needed: [specific decisions needed]
```

### PATTERN
1. **Invoke Retrospective agent**
2. **Store pattern findings in memory**
3. **Propose process change** to Fleet configuration
4. **Document in agent-output/retrospective/**

```
🔄 PATTERN ESCALATION
Recurrence: [n] times — [description]
Occurrences: [plan-01, plan-03, plan-05]
Root cause: [systemic issue]
Retrospective: Dispatched
```

## Conflict Resolution (Two Agents, Same File)

1. **Flag conflict** — do not merge silently
2. **Apply higher-priority agent's version**:
   - Security > Code Reviewer > Implementer
   - Planner > Implementer on scope questions
3. **Log override** in Fleet Log:
   ```
   CONFLICT RESOLVED: [file]
   Winner: [agent] (priority)
   Reason: [why]
   Overridden: [losing agent]'s version
   ```
4. **Notify both agents** of resolution

## Fleet Log Format

Every escalation must be logged:
```
[TIMESTAMP] ESCALATION [LEVEL]: [brief description]
Trigger: [what caused it]
Agents affected: [list]
Action taken: [what Fleet did]
User decision: [if applicable]
Resolved: [yes/no, how]
```
