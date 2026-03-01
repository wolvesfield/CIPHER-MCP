---
description: Conduct a thorough security audit of specified files or modules.
---

Conduct a security audit of the following:

Target: ${input:target:Files, modules, or directories to audit}
Focus: ${input:focus:general|injection|secrets|auth|dependencies|infrastructure}

Apply the Security audit checklist:

**Injection & Input Validation**
- SQL injection, XSS, command injection, path traversal
- All user inputs validated and sanitized

**Secrets & Credentials**
- API keys, tokens, passwords in code or logs
- Secrets managed via environment variables

**Authentication & Authorization**
- All endpoints protected appropriately
- Session management correct
- JWT signatures verified

**Dependencies**
- Known CVEs in any dependency
- Lockfile committed
- No abandoned packages

**Infrastructure**
- No debug endpoints exposed
- Error messages don't leak internals

Severity levels:
- 🔴 CRITICAL — requires IMMEDIATE escalation
- 🟠 HIGH — must fix before release
- 🟡 MEDIUM — fix next sprint
- 🔵 LOW — informational

Output a structured Security Audit report. If CRITICAL findings exist,
escalate immediately to Fleet.
