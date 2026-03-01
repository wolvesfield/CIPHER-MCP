---
mode: ask
description: End-of-day work log — save what you did, what's blocked, and what's next
---

# End of Day — Work Log

Let's capture today before you go. This is your external memory. 🧠

I'll ask you one thing at a time. Take your time.

---

**Step 1 of 4 — What did you get done today?**
(Bullet points. Even tiny things count. Even "showed up" counts.)

${input:done_today:What did you accomplish today?}

---

**Step 2 of 4 — Anything blocked or stuck?**
(What couldn't you move forward on, and why?)

${input:blocked:What is blocked and why?}

---

**Step 3 of 4 — What's the most important thing to do FIRST tomorrow?**
(Just one thing — the thing that matters most)

${input:next_priority:What is the #1 priority for tomorrow?}

---

**Step 4 of 4 — Where EXACTLY did you leave off?**
(One clear sentence. "I was doing X — next step is Y.")

${input:where_left_off:Complete this: I was working on ___ and the next step is ___}

---

Now save the log and store it to memory.

Create file: `C:\Users\arcan_e9q9t\work-logs\[today's date YYYY-MM-DD].md`

Use this structure:
```
# Work Log — [date] ([day of week])

## 📍 WHERE I LEFT OFF
[where_left_off]

---

## ✅ DONE TODAY
[done_today as bullets]

---

## 🚧 BLOCKED
[blocked as bullets, or "Nothing blocked today ✨"]

---

## 📋 TO DO NEXT
🔴 HIGH: [next_priority]
[any other items from done_today context]

---

## 🧠 KEY DECISIONS MADE TODAY
[any decisions from this session, or "No major decisions today"]

## ⚠️ OPEN QUESTIONS
[any unresolved questions from this session, or "No open questions"]

---
_Log saved: [current timestamp]_
```

Then store to memory:
```
#flowbabyStoreSummary {
  "topic": "Work log [date] end of day",
  "context": "WHERE LEFT OFF: [where_left_off]. DONE: [done_today]. BLOCKED: [blocked]. TODO NEXT: [next_priority].",
  "sector": "episodic",
  "tags": ["daily-log", "eod", "[date]"],
  "salience": 0.95
}
```

After saving, confirm warmly:
"✅ Log saved for [date]. Tomorrow we'll pick up from: **[where_left_off]**. Rest well."
