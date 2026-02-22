# Copilot Instructions for CIPHER-MCP

## Project Mode
- Treat this repository as **production-locked infrastructure**.
- The MCP mesh is already validated and live.
- Do not propose broad refactors or architectural changes unless explicitly requested.

## AOT / Runtime Rules
- Prefer compiled output (`mcp-compiled.json`) over runtime launchers.
- Do not reintroduce `npx`/`uvx` launchers into compiled output.
- Use `mcp_enterprise_compiler.py` as the single source of truth for compilation behavior.
- Keep package pins in `mcp-enterprise.json` unless the user explicitly asks to update versions.

## Build & Validation Workflow
- Default workflow command (Windows):
  - `Ctrl+Shift+B` (runs **Validate & Compile** task)
- Equivalent manual commands:
  - `py -3 mcp_enterprise_compiler.py --validate-env`
  - `py -3 mcp_enterprise_compiler.py --skip-install`
- Use full compile only when dependency pins/manifest packages change:
  - `py -3 mcp_enterprise_compiler.py`

## Secrets & Security
- Never place real tokens/secrets in tracked files.
- `.env.example` must contain placeholders only (`REPLACE_ME` style).
- `.env` is local-only and must not be committed.

## Editing Guardrails
- Keep changes minimal and targeted.
- Preserve existing command/task conventions and docs style.
- Do not modify `mcp-enterprise.json` or `mcp_enterprise_compiler.py` unless the user asks.
- If changing README commands, prefer Windows-friendly `py -3 ...` examples.

## Verification Expectations
- After relevant changes, verify:
  - env validation passes,
  - compile succeeds,
  - no `npx`/`uvx` launchers remain in `mcp-compiled.json`.

## Communication Style
- Be concise, action-oriented, and explicit about what changed.
- For risky edits, call out impact before applying.
