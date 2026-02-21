# CIPHER-MCP

Enterprise Model Context Protocol (MCP) Deployment Framework — 24-server matrix with GHEC (GitHub Enterprise Cloud) integration, zero-trust secrets management, and Ahead-Of-Time (AOT) compilation for sub-150 ms boot latency.

---

## Quick Start (Post-Merge)

Follow these five steps after cloning to go from zero to a live 24-server mesh inside VS Code / Cursor / Claude Desktop.

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

Open `.env` and fill in every `REPLACE_ME` value. Key entries:

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

Fix any reported `NOT SET` or `still a placeholder` lines before continuing.

### Step 4 — AOT compile the mesh

```bash
python mcp_enterprise_compiler.py
```

This pre-installs every `npx`/`uvx` package into `.mcp_env/` and writes
`mcp-compiled.json` with absolute binary paths. Typical output:

```
[1/3] Bootstrapping isolated environments ...
[2/3] Installing 16 Node package(s) ...
[2/3] Installing 5 Python package(s) ...
[+] Compiled 24 servers -> mcp-compiled.json
    Boot latency target: <150 ms per server.
    Point your MCP host at mcp-compiled.json to launch the ecosystem.
```

Verify no `npx` or `uvx` strings remain in the compiled output:

```bash
grep -c '"npx"\|"uvx"' mcp-compiled.json   # should print 0
```

### Step 5 — Wire up your MCP host

#### VS Code / GitHub Copilot Chat

Add to your VS Code `settings.json` (or `.vscode/mcp.json`):

```json
{
  "mcp": {
    "servers": "<contents of mcp-compiled.json>.mcpServers"
  }
}
```

Or use the **MCP: Add Server** command and point it at the absolute path of
`mcp-compiled.json`.

Reload the window, then type `#` in Copilot Chat — you should see tools from
all 24 servers, e.g. `#supabase-mcp`, `#solana-blockchain`.

#### Cursor

Open **Settings → MCP** and paste the contents of `mcp-compiled.json` into the
servers list, or set the config file path to the absolute path of
`mcp-compiled.json`.

#### Claude Desktop

In `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
or `%APPDATA%\Claude\claude_desktop_config.json` (Windows), merge the
`mcpServers` block from `mcp-compiled.json` into the existing config.

---

## Verify GHEC (wolvesfield org) access

Once the mesh is running, ask your agent:

> "List all repositories in the wolvesfield organization."

The `github-enterprise-cloud` server will call the GitHub API with your
`GITHUB_ENTERPRISE_TOKEN` and return the org's repository list.  A `401` or
SAML error means the token has not been authorised for the **nochef** enterprise
SSO — visit https://github.com/settings/tokens, find the PAT, and click
**Authorise** next to the nochef organisation.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1 — GHEC Authentication & Secrets Matrix](#phase-1--ghec-authentication--secrets-matrix)
4. [Phase 2 — AOT Compilation (eliminating npx/uvx latency)](#phase-2--aot-compilation-eliminating-npxuvx-latency)
5. [Phase 3 — Master Agent Copilot Prompt](#phase-3--master-agent-copilot-prompt)
6. [Phase 4 — Deployment Telemetry & Failure Analysis](#phase-4--deployment-telemetry--failure-analysis)
7. [The Complete 24-Server Payload](#the-complete-24-server-payload)

---

## Architecture Overview

```
CIPHER-MCP/
├── .env.example              # Secret template — copy to .env and fill in values
├── mcp-enterprise.json       # Canonical 24-server manifest (env-var placeholders)
├── mcp_enterprise_compiler.py# AOT compiler — pre-installs deps, emits mcp-compiled.json
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

## Prerequisites

| Tool | Minimum version | Notes |
|------|-----------------|-------|
| Python | 3.10 | Required to run the AOT compiler |
| Node.js | 18 LTS | Required for Node-based MCP servers |
| npm | 9 | Bundled with Node 18+ |
| uv / uvx | latest | Required for Python-based MCP servers |
| Git | any | |

Optional (recommended):

```bash
pip install python-dotenv   # Enables .env auto-loading inside the compiler
```

---

## Phase 1 — GHEC Authentication & Secrets Matrix

All credentials are stored **outside** the repository in a `.env` file loaded
by the host orchestrator at startup.  Source control only ever sees
`${VAR_NAME}` placeholders.

```bash
# Copy the template
cp .env.example .env

# Edit .env — fill in each REPLACE_ME value
```

Key variables:

| Variable | Description |
|---|---|
| `GITHUB_ENTERPRISE_TOKEN` | Fine-Grained PAT authorised for SAML SSO. Required scopes: `repo`, `read:org`, `read:enterprise`. Enterprise: `https://github.com/enterprises/nochef` |
| `GITHUB_API_URL` | REST base URL. `https://api.github.com` for GHEC Cloud; override for GHES. |
| `GITHUB_ORG_NAME` | Enterprise organisation slug — `wolvesfield`. |
| `SUPABASE_ACCESS_TOKEN` | Supabase Management API personal access token (`sbp_…`). Generate at https://supabase.com/dashboard/account/tokens |
| `TAVILY_API_KEY` | Tavily Search API key. |
| `MEM0_API_KEY` | Mem0 memory API key. |

See `.env.example` for the complete list.

> **Security note:** `.env` is listed in `.gitignore` and will never be
> committed.  Rotate all GHEC tokens via GitHub's Fine-Grained PAT management
> console and re-run pre-flight checks after rotation.

---

## Phase 2 — AOT Compilation (eliminating npx/uvx latency)

The AOT compiler pre-installs every dependency into an isolated `.mcp_env/`
directory and rewrites the manifest to use direct binary paths, eliminating
the 10–45 s cold-start penalty of `npx -y` / `uvx`.

```bash
# One-time compilation (re-run whenever mcp-enterprise.json changes)
python mcp_enterprise_compiler.py

# Custom paths
python mcp_enterprise_compiler.py --input mcp-enterprise.json --output mcp-compiled.json

# Pre-flight env check — verify every ${VAR} is set and not still REPLACE_ME
python mcp_enterprise_compiler.py --validate-env
```

What happens:

1. `bootstrap_environments()` — creates `.mcp_env/node/` (npm) and
   `.mcp_env/python/` (venv) if they do not exist.
2. `collect_dependencies()` — parses every `npx -y` / `uvx` entry, collects
   package names, rewrites server commands to local binary paths, and replaces
   any literal secret values with `${VAR_NAME}` placeholders.
3. `install_node_packages()` / `install_python_packages()` — bulk-installs
   all collected packages into the isolated environments.
4. `validate_env_vars()` — warns about any `${VAR}` references not present in
   the environment so missing secrets are caught before deployment.
5. Emits `mcp-compiled.json` — point your MCP host at this file.

### `--validate-env` pre-flight check

Run this after filling in `.env` and **before** launching the server mesh:

```
$ python mcp_enterprise_compiler.py --validate-env
[+] validate-env PASSED -- all 24 server env vars are set and non-placeholder.
```

If any variable is missing or still contains a `REPLACE_ME` value the command
exits with code `1` and lists every offending variable by server name so you
can fix them individually.

> `.mcp_env/` and `mcp-compiled.json` are listed in `.gitignore` because they
> contain absolute local paths and compiled binaries.

---

## Phase 3 — Master Agent Copilot Prompt

Use the following system prompt when asking your AI coding assistant (Cursor /
Claude / Copilot) to generate **new** MCP servers that integrate cleanly into
this ecosystem:

---

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
* DB connections: Singleton connection pool — one pool, not one connection per
  tool call.
* High-latency tasks (Blockchain RPC, Docker exec): async/await with 15 s
  timeout to prevent orchestrator deadlock.
* Tool descriptions: highly condensed Zod/Pydantic schemas — the orchestrator
  is already managing 30 servers.

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

## Phase 4 — Deployment Telemetry & Failure Analysis

| Brittleness Vector | Diagnostic Signature | Mitigation |
|---|---|---|
| **GHEC Token Expiration** | Tools return `401 Unauthorized` or SAML enforcement errors | Implement a pre-flight token check in the orchestrator. Intercept MCP errors and prompt re-authentication via GitHub SSO before routing to the LLM. |
| **Context Window Saturation** | LLM ignores instructions or hallucinates tool arguments | 24 servers ≈ 120+ tools. Use **Semantic Tool Routing**: calculate embeddings for each query and inject only the 3–5 most relevant servers per turn. |
| **Orphaned Process Leaks** | Host memory spikes linearly; SQLite locks accumulate | Send `SIGTERM` to all child processes on shutdown, followed by `SIGKILL` after 3 000 ms. AOT binaries bypass standard wrappers so explicit cleanup is mandatory. |

---

## The Complete 24-Server Payload

> All sensitive values in `mcp-enterprise.json` use `${VAR_NAME}` syntax.
> They are substituted at runtime from your `.env` file.

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
| 15 | `dbhub-io` | Node/npx | DBHub.io database hub (https://dbhub.ai/) |
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

## License

See [LICENSE](LICENSE).
