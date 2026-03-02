---
mode: ask
description: Start-of-day orientation — retrieves yesterday's log and orients you for the day
---

# Good Morning — Let's Get You Oriented 🧠

Today is [current date and day of week].

---

## Step 1 — Retrieve yesterday's context

Read the most recent file from: `${CIPHER_WORKLOG_DIR:-C:\Users\arcan_e9q9t\work-logs}\`
Also retrieve from memory:
```
#flowbabyRetrieveMemory {
  "query": "daily work log where I left off yesterday blocked todo",
  "maxResults": 3
}
```

---

## Step 2 — Display context (in this exact order)

### 📍 WHERE YOU LEFT OFF
[Display the WHERE I LEFT OFF section from yesterday's log — make this the BIGGEST, CLEAREST thing on screen]

---

### 🚧 STILL BLOCKED
[If there are blocked items from yesterday — show them here]
[If nothing blocked: "Nothing blocked from yesterday ✨"]

---

### 📋 YOUR NEXT STEPS (from yesterday)
[Show the TO DO NEXT list in priority order]

---

### ✅ WHAT YOU ACCOMPLISHED YESTERDAY
[Show the DONE TODAY section — this is important for morale and continuity]

---

## Step 3 — Ask one question

"Ready to continue with **[top TO DO item]**, or is something else on your mind today?"

---

## Step 4 — Wait for response

Do NOT start doing anything until the user responds.
Their first message tells you what today's focus is.
Then help them move forward — one step at a time.

---

## If no log found for yesterday

Say gently:
"No log found for yesterday — that's okay, it happens. 
Do you remember what you were working on? 
Even a few words helps me help you get back on track."

Then:
1. Retrieve flowbaby memory for recent context
2. Help reconstruct what was happening
3. Create a [RECONSTRUCTED] log entry
4. Move forward without judgment
