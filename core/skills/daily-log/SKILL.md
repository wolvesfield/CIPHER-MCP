---
name: daily-log
description: >
  ADHD/autism-optimized daily work logging system. Saves what was done,
  what is blocked, and what to do next — every single day. At the start
  of every session, surfaces the most recent log FIRST before anything
  else. Use /eod to save end-of-day log. Use /start to recall yesterday.
  Designed for working memory support, context restoration, and preventing
  lost progress for users with ADHD, amnesia, or autism.
---

# Daily Work Log Protocol

Designed for: ADHD · Amnesia · Autism · Neurodivergent working memory support

---

## THE MOST IMPORTANT RULE

**At the start of EVERY session — before any code, before any planning, before anything:**

1. Retrieve the most recent daily log from memory
2. Read the file from `${CIPHER_WORKLOG_DIR:-C:\Users\arcan_e9q9t\work-logs}\` (most recent date)
3. Display it clearly with a warm, grounding greeting
4. Ask: "Ready to continue, or do you want to start something new?"

**This is non-negotiable. Context restoration comes FIRST.**

---

## SESSION START PROTOCOL (/start or automatic)

```
Step 1: Greet by day
  "Good [morning/afternoon/evening]! Today is [day], [date]. Let's get you oriented. 🧠"

Step 2: Retrieve from memory
  #flowbabyRetrieveMemory { "query": "daily work log yesterday where I left off", "maxResults": 3 }

Step 3: Read most recent log file
  Read: ${CIPHER_WORKLOG_DIR:-C:\Users\arcan_e9q9t\work-logs}\[most-recent-date].md

Step 4: Display the "WHERE I LEFT OFF" section FIRST — big and clear
  "📍 WHERE YOU LEFT OFF:
   [one-sentence context from log]"

Step 5: Display BLOCKED items prominently
  If any: "⚠️ STILL BLOCKED: [items]"

Step 6: Display TO DO NEXT list
  "📋 YOUR NEXT STEPS:
   1. [highest priority item]
   2. [second item]
   ..."

Step 7: Ask
  "Want to continue with [top item], or is there something else on your mind?"
```

---

## END-OF-DAY LOG FORMAT (/eod)

When user says /eod, save everything done today.

**File location:** `${CIPHER_WORKLOG_DIR:-C:\Users\arcan_e9q9t\work-logs}\YYYY-MM-DD.md`
Use today's date in the filename.

**Template:**

```markdown
# Work Log — [YYYY-MM-DD] ([Day of Week])

## 📍 WHERE I LEFT OFF
<!-- THE MOST IMPORTANT SECTION — one clear sentence -->
<!-- Bad: "Working on stuff"  -->
<!-- Good: "I was refactoring the auth middleware — tests are written, failing, next step is writing the implementation" -->
[one crystal-clear sentence of exactly where you stopped and what the next step is]

---

## ✅ DONE TODAY
<!-- List everything completed, even small things. Small wins matter. -->
- [ item 1 ]
- [ item 2 ]

---

## 🚧 BLOCKED
<!-- Anything you couldn't move forward on — and WHY -->
- [ item ] — blocked by: [ reason ]
<!-- If nothing blocked: write "Nothing blocked today ✨" -->

---

## 📋 TO DO NEXT (priority order)
<!-- What needs to happen NEXT — ordered by importance -->
- 🔴 HIGH: [ most urgent item ]
- 🟡 MED:  [ medium priority ]
- 🟢 LOW:  [ can wait ]

---

## 🧠 KEY DECISIONS MADE TODAY
<!-- Any architectural, product, or technical decisions -->
- [ decision and why ]
<!-- If none: "No major decisions today" -->

---

## ⚠️ OPEN QUESTIONS
<!-- Things unresolved that need an answer before you can move forward -->
- [ question ]
<!-- If none: "No open questions" -->

---

## 💭 BRAIN DUMP
<!-- Anything on your mind — half-formed ideas, concerns, wins, frustrations -->
<!-- This is for YOU. No format required. Just dump it. -->

---
_Log saved: [timestamp]_
```

---

## HOW TO SAVE A LOG (Auto-fill procedure)

When user runs /eod, Copilot should:

1. **Ask these questions one at a time** (never all at once — sensory overload):
   - "What did you get done today? (bullet points, even tiny things count)"
   - "Anything blocked or stuck?"
   - "What's the #1 most important thing to do first tomorrow?"
   - "Where exactly did you leave off? Give me one sentence."

2. **Auto-fill what Copilot knows:**
   - Pull from today's session context
   - Pull from fleet execution logs if any ran today
   - Pull from any todos that changed status today

3. **Save to file:**
   - Create `${CIPHER_WORKLOG_DIR:-C:\Users\arcan_e9q9t\work-logs}\YYYY-MM-DD.md`
   - Use exact template above

4. **Store to memory:**
   ```
   #flowbabyStoreSummary {
     "topic": "Work log [YYYY-MM-DD] end of day",
     "context": "WHERE LEFT OFF: [sentence]. DONE: [list]. BLOCKED: [list]. TODO: [list].",
     "sector": "episodic",
     "tags": ["daily-log", "work-log", "[date]"],
     "salience": 0.95
   }
   ```
   High salience (0.95) — this memory is critical for context restoration.

5. **Confirm warmly:**
   - "✅ Log saved for [date]. You've made progress. Rest well — tomorrow we'll pick up from [WHERE I LEFT OFF sentence]."

---

## WEEKLY REVIEW (every Monday or on request)

Run a quick weekly review:

1. Read last 7 log files from `work-logs/`
2. Identify:
   - Recurring blockers (flag as PATTERN escalation)
   - Progress streaks (reinforce positive patterns)
   - Open questions that aged more than 3 days (escalate)
3. Output a clear weekly summary:
   ```
   📊 WEEK IN REVIEW ([date range])
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✅ Completed: [n] items
   🚧 Still blocked: [persistent blockers]
   ⚠️ Aging open questions: [list]
   🔁 Recurring patterns: [any loops detected]
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   This week's wins: [highlight best thing]
   ```

---

## ADHD/AUTISM COMMUNICATION RULES

When displaying logs, always:

1. **One thing at a time** — don't dump everything at once
2. **Lead with WHERE I LEFT OFF** — context first, everything else second
3. **Use visual separators** (━━━ lines, clear headers)
4. **Short bullets only** — no paragraphs
5. **Acknowledge small wins** — everything completed counts
6. **Never express frustration** about blockers — neutral, practical
7. **Ask one question at a time** during /eod capture
8. **Use consistent emoji markers** so patterns are recognizable:
   - 📍 = where you left off
   - ✅ = done
   - 🚧 = blocked
   - 📋 = to do
   - ⚠️ = open question / needs attention
   - 🧠 = decision / important to remember
   - 💭 = brain dump / free space

---

## LOG FILE MANAGEMENT

- All logs: `${CIPHER_WORKLOG_DIR:-C:\Users\arcan_e9q9t\work-logs}\YYYY-MM-DD.md`
- Keep all logs permanently — they are your external memory
- Never delete a log file
- Weekly logs auto-generate from daily logs (on Monday)
- Search logs: ask "what was I doing on [date]?" or "when did I work on [topic]?"

---

## IF YOU FORGET TO RUN /eod

If a session starts with no log for yesterday:
1. Acknowledge gently: "No log found for yesterday — that happens. Let's do a quick 2-minute catch-up."
2. Ask: "Do you remember what you were working on last?"
3. Help reconstruct from memory: retrieve flowbaby context for recent sessions
4. Create a catch-up log with [RECONSTRUCTED] tag
5. Move forward — no shame, just context restoration
