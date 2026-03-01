# CIPHER-MCP

MCP server mesh, agent skills, and operational instructions for the **Cipher Ops** autonomous agent infrastructure — Super Agents, Master Agents, and specialized task agents running 24/7.

*Built in memory of Ayesha Afser "Littli".*

---

## What This Repo Is

This is the single source of truth for:

- **MCP Server Mesh** — 24-server enterprise manifest with AOT compilation for sub-150 ms boot
- **Agent Skills & Instructions** — prompts, behaviors, and operational configs for every agent tier
- **Infrastructure Configs** — secrets templates, compilation tooling, and deployment guides

This repo does **not** contain ComfyUI, Midjourney, LoRA training, or any image/video generation tooling. Those live in their own repos.

---

## Agent Hierarchy

```
┌─────────────────────────────────────────────┐
│              SUPER AGENTS                    │
│  (Orchestrators — route tasks, manage state) │
├─────────────────────────────────────────────┤
│              MASTER AGENTS                   │
│  (Wing leads — Trading, Hacker, Ops)         │
├─────────────────────────────────────────────┤
│           SPECIALIZED AGENTS                 │
│  (24 MCP servers — each a focused tool)      │
└─────────────────────────────────────────────┘
```

- **Super Agents** — top-level orchestrators that receive commands (WhatsApp/Telegram/voice via OpenClaw), decide which wing handles the task, and coordinate cross-wing operations.
- **Master Agents** — wing leaders (Trading Wing, Hacker Wing, Infrastructure Wing) that decompose tasks and dispatch to specialized agents.
- **Specialized Agents** — the 24 MCP servers below. Each is a focused tool: blockchain, database, browser automation, code execution, memory, etc.

---

## Quick Start

### Step 1 — Install prerequisites

```bash
# Node 18+ (https://nodejs.org)
node --version   # must be >= 18

# Python 3.10+ with uv
pip install uv

# Optional but recommended — enables .env auto-loading in the compiler
pip install python-dotenv
```

### Step 2 — Configure your secrets

```bash
cp .env.example .env
```

Open `.env` and fill in every `REPLACE_ME` value:

| Variable | Where to get it |
|---|---|
| `GITHUB_ENTERPRISE_TOKEN` | https://github.com/settings/tokens — Fine-Grained PAT, authorise for the **nochef** enterprise |
| `SUPABASE_ACCESS_TOKEN` | https://supabase.com/dashboard/account/tokens (`sbp_…`) |
| `TAVILY_API_KEY` | https://app.tavily.com |
| `MEM0_API_KEY` | https://app.mem0.ai |
| `KUBECONFIG` | Absolute path to your local `~/.kube/config` |
| `SOLANA_RPC_URL` | `https://api.mainnet-beta.solana.com` (public, no key needed) |

### Step 3 — Validate your environment

```bash
python mcp_enterprise_compiler.py --validate-env
```

Expected output when all variables are set:

```
[+] validate-env PASSED -- all 24 server env vars are set and non-placeholder.
```

### Step 4 — AOT compile the mesh

```bash
python mcp_enterprise_compiler.py
```

This pre-installs every `npx`/`uvx` package into `.mcp_env/` and writes
`mcp-compiled.json` with absolute binary paths.

For faster rebuilds after deps are already installed:

```bash
python mcp_enterprise_compiler.py --skip-install
```

Verify no runtime launchers remain:

```bash
grep -c '"npx"\|"uvx"' mcp-compiled.json   # should print 0
```

### Step 5 — Wire up your MCP host

**VS Code / GitHub Copilot Chat** — add to `settings.json` or `.vscode/mcp.json`:

```json
{
  "mcp": {
    "servers": "<contents of mcp-compiled.json>.mcpServers"
  }
}
```

**Cursor** — Settings → MCP → paste contents of `mcp-compiled.json`.

**Claude Desktop** — merge `mcpServers` from `mcp-compiled.json` into `claude_desktop_config.json`.

---

## Architecture

```
CIPHER-MCP/
├── .env.example               # Secret template — copy to .env and fill in
├── mcp-enterprise.json        # Canonical 24-server manifest (env-var placeholders)
├── mcp_enterprise_compiler.py # AOT compiler — pre-installs deps, emits mcp-compiled.json
├── littli-protocol.md         # Mission context for AI companion sessions
└── README.md
```

**Runtime flow:**

```
.env  ──load──▶  orchestrator process
                     │
                     ├── mcp_enterprise_compiler.py  ──▶  .mcp_env/ (isolated binaries)
                     │                                ──▶  mcp-compiled.json
                     │
                     └── MCP host  ──▶  mcp-compiled.json  ──▶  24 × MCP server processes
```

---

## Secrets & Security

All credentials are stored **outside** the repository in a `.env` file. Source control only sees `${VAR_NAME}` placeholders.

> `.env` is in `.gitignore` and will never be committed. Rotate all GHEC tokens via GitHub's Fine-Grained PAT console and re-run `--validate-env` after rotation.

---

## AOT Compilation Details

The AOT compiler eliminates the 10–45 s cold-start penalty of `npx -y` / `uvx`:

1. `bootstrap_environments()` — creates `.mcp_env/node/` and `.mcp_env/python/` if needed.
2. `collect_dependencies()` — parses every `npx -y` / `uvx` entry, rewrites to local binary paths.
3. `install_node_packages()` / `install_python_packages()` — bulk-installs into isolated envs.
4. `validate_env_vars()` — warns about any missing `${VAR}` references.
5. Emits `mcp-compiled.json` — point your MCP host here.

---

## Master Agent System Prompt

Use this when asking an AI assistant to generate **new** MCP servers for the mesh:

```
# SYSTEM DIRECTIVE: ENTERPRISE MCP ARCHITECT (GHEC-FIRST)
You are an elite systems architect adding a new MCP server to a 24-node
Enterprise Service Mesh compiled with the CIPHER-MCP AOT framework.

## OPERATING CONTEXT
* Ecosystem: 24 concurrent MCP servers (Blockchain, Docker, Supabase, Figma).
* Execution: AOT compiled — DO NOT use `npx -y` or `uvx` at runtime.
* Licensing: Strict GHEC/SSO compliance (enterprise: nochef, org: wolvesfield).

## REQUIREMENTS FOR EVERY NEW SERVER

### Auth & Secrets
* Accept GITHUB_API_URL and GITHUB_ENTERPRISE_TOKEN via environment variables.
* Validate SAML SSO token scopes on boot; fail-fast if scopes are insufficient.
* Never hardcode credentials — use dotenv for local testing only.

### Performance & Reliability
* Language: TypeScript (Node.js) or Python.
* Transport: stdio.
* DB connections: Singleton connection pool.
* High-latency tasks: async/await with 15 s timeout.
* Tool descriptions: highly condensed Zod/Pydantic schemas.

### Required Files
1. `src/index.*`   — stdio transport init, error handling, GHEC env validation.
2. `src/tools.*`   — tool registration; namespace names (e.g. `ghec_repo_scan`).
3. `package.json` or `pyproject.toml` — @modelcontextprotocol/sdk dependency.
4. `Dockerfile`   — Distroless/Alpine image for containerised deployment.
5. `mcp-injection.json` — Compiled config snippet with local binary path.

## EXECUTION CHAIN
1. Ask: target language (TS/Python) and enterprise use-case.
2. Output the directory tree.
3. Generate all files in compliance with GHEC and AOT constraints.
4. Provide verification steps using MCP Inspector to test the GHEC SAML token.
```

---

## Deployment Telemetry & Failure Analysis

| Brittleness Vector | Diagnostic Signature | Mitigation |
|---|---|---|
| **GHEC Token Expiration** | `401 Unauthorized` or SAML errors | Pre-flight token check. Re-authenticate via GitHub SSO before routing to the LLM. |
| **Context Window Saturation** | LLM ignores instructions or hallucinates tool args | 24 servers ≈ 120+ tools. Use **Semantic Tool Routing**: inject only the 3–5 most relevant servers per turn. |
| **Orphaned Process Leaks** | Host memory spikes; SQLite locks | `SIGTERM` all children on shutdown, `SIGKILL` after 3 s. |

---

## The 24-Server Mesh

> All sensitive values in `mcp-enterprise.json` use `${VAR_NAME}` syntax, substituted at runtime from `.env`.

| # | Server Key | Stack | Purpose |
|---|---|---|---|
| 1 | `sqlite-audit-db` | Python/uvx | Local SQLite audit log |
| 2 | `filesystem` | Node/npx | Workspace file access |
| 3 | `fetch` | Python/uvx | HTTP fetch utility |
| 4 | `github` | Node/npx | GitHub REST/GraphQL (GHEC) |
| 5 | `playwright` | Node/npx | Browser automation |
| 6 | `puppeteer` | Node/npx | Browser automation (alt) |
| 7 | `chrome-devtools` | Node/npx | Chrome DevTools Protocol |
| 8 | `browser-devtools-generic` | Node/npx | Generic browser DevTools |
| 9 | `tavily-search` | Node/npx | Web search (Tavily) |
| 10 | `supabase-postgres` | Node/npx | Supabase Management API |
| 11 | `desktop-commander` | Node/npx | Desktop automation |
| 12 | `generic-openapi` | Node/npx | Generic OpenAPI proxy |
| 13 | `evm-blockchain` | Node/npx | EVM chain interaction |
| 14 | `tatum-blockchain` | Node/npx | Tatum multi-chain API |
| 15 | `dbhub-io` | Node/npx | DBHub.io database hub |
| 16 | `context7` | Node/node | Custom context management |
| 17 | `serena` | Node/node | Custom orchestration agent |
| 18 | `docker-executor` | Node/npx | Docker container management |
| 19 | `figma-remote` | SSE (remote) | Figma design data |
| 20 | `mem0-memory` | Python/uvx | Persistent AI memory |
| 21 | `python-secure-sandbox` | Python/uvx | Python code execution sandbox |
| 22 | `github-enterprise-cloud` | Node/npx | GHEC — enterprise-scoped GitHub (org: wolvesfield) |
| 23 | `kubernetes-cluster` | Node/npx | Kubernetes cluster management |
| 24 | `solana-blockchain` | Node/npx | Solana on-chain interactions |

---

## Daily Use Checklist

1. Run `python mcp_enterprise_compiler.py --validate-env` — confirm `PASSED`.
2. If packages changed in `mcp-enterprise.json`, run full compile: `python mcp_enterprise_compiler.py`
3. If only env values changed, fast rebuild: `python mcp_enterprise_compiler.py --skip-install`
4. Test in Copilot Chat: *"List all repositories in the wolvesfield organization."*

---

## License

See [LICENSE](LICENSE).
