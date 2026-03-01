# Hacker Wing — Shadow Operations

## Agent Loop (ReAct)
1. Recon Agent → Nmap scan
2. Vuln Analysis Agent → Nuclei + CVE correlation  
3. Exploitation Agent → Sqlmap, Ffuf, Playwright
4. Report Agent → Store in legacy-foundation/reports/

## MCP Tools
- Nmap: network reconnaissance
- Nuclei: vulnerability scanning
- Sqlmap: SQL injection testing
- Ffuf: directory fuzzing
- Playwright: browser automation

## Hard Rules
- Authorized targets ONLY
- Bug bounty programs only
- All findings → legacy-foundation/memory/semantic/
