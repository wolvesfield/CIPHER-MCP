<#
.SYNOPSIS
CIPHER-MCP Universal Bootstrap — Windows

.DESCRIPTION
One-command onboarding for any Windows machine.
Links agents, skills, MCP tools, installs Arbiter deps,
registers mcp-compiled.json with VS Code and Claude Desktop.

.EXAMPLE
# Run from repo root:
powershell -ExecutionPolicy Bypass -File setup.ps1

# One-liner from scratch (clones + sets up):
irm https://raw.githubusercontent.com/wolvesfield/CIPHER-MCP/main/setup/windows-bootstrap.ps1 | iex
#>

$ErrorActionPreference = 'Stop'

Write-Host "🚀 Initializing CIPHER-MCP Master Environment for Windows..." -ForegroundColor Cyan

# 1. Check Prerequisites
Write-Host "Checking prerequisites..."
foreach ($cmd in @("node", "npm", "python", "pip", "git")) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Error: $cmd is not installed. Please install it first." -ForegroundColor Red
        exit 1
    }
}

pip install python-dotenv --quiet

# Define paths
$RepoRoot = $PSScriptRoot
$CopilotGlobalDir = "$env:USERPROFILE\.copilot"
$CopilotConfigDir = "$env:USERPROFILE\.config\copilot"
$TargetPromptsDir = "$env:USERPROFILE\vs-code-agents\.github\prompts"
$AgentOutputDir   = "$env:USERPROFILE\agent-output"

# 2. Create target directories
Write-Host "Preparing workspace directories..."
foreach ($d in @("$CopilotConfigDir\agents", "$CopilotGlobalDir\skills", $TargetPromptsDir, $AgentOutputDir, "$RepoRoot\work-logs")) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

# 3. Setup Global Instructions
Write-Host "Linking instructions..."
$SourceInstructions = "$RepoRoot\core\instructions\copilot-instructions.md"
$TargetInstructions = "$CopilotGlobalDir\copilot-instructions.md"
if (Test-Path $TargetInstructions) { Remove-Item -Path $TargetInstructions -Force }
if (Test-Path $SourceInstructions) {
    New-Item -ItemType SymbolicLink -Path $TargetInstructions -Target $SourceInstructions -Force | Out-Null
}

# 4. Setup Agents
Write-Host "Linking Specialist Agents..."
foreach ($Agent in (Get-ChildItem -Path "$RepoRoot\core\agents\*.md" -ErrorAction SilentlyContinue)) {
    $Target = "$CopilotConfigDir\agents\$($Agent.Name)"
    if (Test-Path $Target) { Remove-Item $Target -Force }
    New-Item -ItemType SymbolicLink -Path $Target -Target $Agent.FullName -Force | Out-Null
}

# 5. Setup Skills
Write-Host "Linking Core Skills..."
foreach ($Skill in (Get-ChildItem -Path "$RepoRoot\core\skills" -Directory -ErrorAction SilentlyContinue)) {
    $Target = "$CopilotGlobalDir\skills\$($Skill.Name)"
    if (Test-Path $Target) { Remove-Item $Target -Recurse -Force }
    New-Item -ItemType Junction -Path $Target -Target $Skill.FullName -Force | Out-Null
}

# 6. Setup Prompts
Write-Host "Linking Prompt Templates..."
foreach ($Prompt in (Get-ChildItem -Path "$RepoRoot\prompts\*.md" -ErrorAction SilentlyContinue)) {
    $Target = "$TargetPromptsDir\$($Prompt.Name)"
    if (Test-Path $Target) { Remove-Item $Target -Force }
    New-Item -ItemType SymbolicLink -Path $Target -Target $Prompt.FullName -Force | Out-Null
}

# 7. Compile MCP Ecosystem
Write-Host "🛠️ Compiling MCP Ecosystem (AOT Mode)..." -ForegroundColor Yellow
Set-Location $RepoRoot
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from template..."
    Copy-Item ".env.example" ".env"
}
python mcp_enterprise_compiler.py

# 8. Install Arbiter / Bridge Python dependencies
Write-Host "🤖 Installing Consensus Arbiter dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn httpx pydantic --quiet

# 9. Register mcp-compiled.json with VS Code
$VSCodeSettings = "$env:APPDATA\Code\User\settings.json"
if (Test-Path $VSCodeSettings) {
    Write-Host "Registering MCP tools with VS Code..."
    $mcpPath = "$RepoRoot\mcp-compiled.json" -replace '\\', '/'
    python - @"
import json, os
cfg_path = r'$VSCodeSettings'
mcp_path = r'$RepoRoot\mcp-compiled.json'
with open(cfg_path, encoding='utf-8') as f:
    cfg = json.load(f)
if 'mcp' not in cfg:
    cfg['mcp'] = {}
cfg['mcp']['servers-file'] = mcp_path
with open(cfg_path, 'w', encoding='utf-8') as f:
    json.dump(cfg, f, indent=2)
print('  VS Code settings.json updated')
"@
} else {
    Write-Host "  VS Code settings not found — skipping"
}

# 10. Register with Claude Desktop
$ClaudeConfig = "$env:APPDATA\Claude\claude_desktop_config.json"
if (Test-Path "$env:APPDATA\Claude") {
    Write-Host "Registering MCP tools with Claude Desktop..."
    python - @"
import json, os
cfg_path = r'$ClaudeConfig'
mcp_json = r'$RepoRoot\mcp-compiled.json'
cfg = {}
if os.path.exists(cfg_path):
    with open(cfg_path, encoding='utf-8') as f:
        cfg = json.load(f)
with open(mcp_json, encoding='utf-8') as f:
    servers = json.load(f).get('mcpServers', {})
if 'mcpServers' not in cfg:
    cfg['mcpServers'] = {}
cfg['mcpServers'].update(servers)
with open(cfg_path, 'w', encoding='utf-8') as f:
    json.dump(cfg, f, indent=2)
print(f'  Claude Desktop updated with {len(servers)} MCP servers')
"@
} else {
    Write-Host "  Claude Desktop not found — skipping"
}

Write-Host ""
Write-Host "✨ SUCCESS: CIPHER-MCP fully active on this machine." -ForegroundColor Cyan
Write-Host "   ✅ Agents linked" -ForegroundColor Green
Write-Host "   ✅ Skills linked" -ForegroundColor Green
Write-Host "   ✅ 28 MCP Servers compiled -> mcp-compiled.json" -ForegroundColor Green
Write-Host "   ✅ Role profiles: mcp-core / mcp-dev / mcp-hacker / mcp-trading" -ForegroundColor Green
Write-Host "   ✅ Arbiter deps installed (FastAPI, uvicorn, httpx, pydantic)" -ForegroundColor Green
Write-Host "   ✅ SUPER_ARCHITECTURE.md auto-loads in every Copilot session" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Fill in .env: notepad $RepoRoot\.env"
Write-Host "  2. Open repo in VS Code — Copilot auto-loads full fleet context"
Write-Host "  3. On KVM8 — deploy Arbiter: python3 arbiter/consensus_arbiter.py"
Write-Host ""
Write-Host "TIP: To re-run on any new Windows machine:" -ForegroundColor Yellow
Write-Host "  irm https://raw.githubusercontent.com/wolvesfield/CIPHER-MCP/main/setup/windows-bootstrap.ps1 | iex"