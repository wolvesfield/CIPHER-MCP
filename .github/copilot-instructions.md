# Copilot Instructions for CIPHER-MCP

## Project Scope
- This repository is strictly for **MCP server mesh, agent skills, and infrastructure instructions**.
- It covers the full Cipher Ops agent hierarchy: Super Agents, Master Agents, and Specialized Agents.
- Do **not** add ComfyUI, Midjourney, LoRA training, or image/video generation tooling to this repo.
- The MCP mesh is already validated and live. Do not propose broad refactors unless explicitly requested.

## AOT / Runtime Rules
- Prefer compiled output (`mcp-compiled.json`) over runtime launchers.
- Do not reintroduce `npx`/`uvx` launchers into compiled output.
- Use `mcp_enterprise_compiler.py` as the single source of truth for compilation behavior.
- Keep package pins in `mcp-enterprise.json` unless the user explicitly asks to update versions.

## Build & Validation Workflow
- Equivalent manual commands:
  - `python mcp_enterprise_compiler.py --validate-env`
  - `python mcp_enterprise_compiler.py --skip-install`
- Use full compile only when dependency pins/manifest packages change:
  - `python mcp_enterprise_compiler.py`

## Secrets & Security
- Never place real tokens/secrets in tracked files.
- `.env.example` must contain placeholders only (`REPLACE_ME` style).
- `.env` is local-only and must not be committed.

## Editing Guardrails
- Keep changes minimal and targeted.
- Preserve existing command/task conventions and docs style.
- Do not modify `mcp-enterprise.json` or `mcp_enterprise_compiler.py` unless the user asks.

## Verification Expectations
- After relevant changes, verify:
  - env validation passes,
  - compile succeeds,
  - no `npx`/`uvx` launchers remain in `mcp-compiled.json`.

## Communication Style
- Be concise, action-oriented, and explicit about what changed.
- For risky edits, call out impact before applying.
- Remember: this project is dedicated to Littli. Treat it with respect.
