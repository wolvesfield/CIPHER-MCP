<#
.SYNOPSIS
Universal Master Bootstrap Script for Windows

.DESCRIPTION
One-command deployment for CIPHER-MCP:
1. Links 13 Agents, 9 Skills, Instructions.
2. Creates workspace directories.
3. Compiles the 24-server MCP ecosystem.
#>

$ErrorActionPreference = 'Stop'

Write-Host "🚀 Initializing CIPHER-MCP Master Environment for Windows..." -ForegroundColor Cyan

# 1. Check Prerequisites
Write-Host "Checking prerequisites..."
$Prereqs = @("node", "npm", "python", "pip")
foreach ($cmd in $Prereqs) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Error: $cmd is not installed. Please install it first." -ForegroundColor Red
        exit 1
    }
}

# Install python-dotenv for compiler
Write-Host "Ensuring python-dotenv is installed..."
pip install python-dotenv --quiet

# Define paths
$RepoRoot = $PSScriptRoot
$CopilotGlobalDir = "$env:USERPROFILE\.copilot"
$CopilotConfigDir = "$env:USERPROFILE\.config\copilot"
$TargetPromptsDir = "$env:USERPROFILE\vs-code-agents\.github\prompts"
$AgentOutputDir = "$env:USERPROFILE\agent-output"

# 2. Create target directories
Write-Host "Preparing workspace directories..."
if (-not (Test-Path "$CopilotConfigDir\agents")) { New-Item -ItemType Directory -Path "$CopilotConfigDir\agents" -Force | Out-Null }
if (-not (Test-Path "$CopilotGlobalDir\skills")) { New-Item -ItemType Directory -Path "$CopilotGlobalDir\skills" -Force | Out-Null }
if (-not (Test-Path $TargetPromptsDir)) { New-Item -ItemType Directory -Path $TargetPromptsDir -Force | Out-Null }
if (-not (Test-Path $AgentOutputDir)) { New-Item -ItemType Directory -Path $AgentOutputDir -Force | Out-Null }

# 3. Setup Global Instructions
Write-Host "Linking instructions..."
$SourceInstructions = "$RepoRoot\core\instructions\copilot-instructions.md"
$TargetInstructions = "$CopilotGlobalDir\copilot-instructions.md"
if (Test-Path $TargetInstructions) { Remove-Item -Path $TargetInstructions -Force }
New-Item -ItemType SymbolicLink -Path $TargetInstructions -Target $SourceInstructions -Force | Out-Null

# 4. Setup Agents
Write-Host "Linking 13 Specialist Agents..."
$Agents = Get-ChildItem -Path "$RepoRoot\core\agents\*.md"
foreach ($Agent in $Agents) {
    $TargetAgent = "$CopilotConfigDir\agents\$($Agent.Name)"
    if (Test-Path $TargetAgent) { Remove-Item -Path $TargetAgent -Force }
    New-Item -ItemType SymbolicLink -Path $TargetAgent -Target $Agent.FullName -Force | Out-Null
}

# 5. Setup Skills
Write-Host "Linking 9 Core Skills..."
$Skills = Get-ChildItem -Path "$RepoRoot\core\skills" -Directory
foreach ($Skill in $Skills) {
    $TargetSkill = "$CopilotGlobalDir\skills\$($Skill.Name)"
    if (Test-Path $TargetSkill) { Remove-Item -Path $TargetSkill -Recurse -Force }
    New-Item -ItemType Junction -Path $TargetSkill -Target $Skill.FullName -Force | Out-Null
}

# 6. Setup Prompts
Write-Host "Linking Prompt Templates..."
$Prompts = Get-ChildItem -Path "$RepoRoot\prompts\*.md"
foreach ($Prompt in $Prompts) {
    $TargetPrompt = "$TargetPromptsDir\$($Prompt.Name)"
    if (Test-Path $TargetPrompt) { Remove-Item -Path $TargetPrompt -Force }
    New-Item -ItemType SymbolicLink -Path $TargetPrompt -Target $Prompt.FullName -Force | Out-Null
}

# 7. Compile MCP Ecosystem
Write-Host "🛠️ Compiling 24-Server MCP Ecosystem (AOT Mode)..." -ForegroundColor Yellow
cd "$RepoRoot"
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env from template..."
    Copy-Item ".env.example" ".env"
}

python mcp_enterprise_compiler.py

Write-Host "✨ SUCCESS: Your Universal AI Master Repo is fully active." -ForegroundColor Cyan
Write-Host "   - 13 Agents Linked"
Write-Host "   - 9 Skills Linked"
Write-Host "   - 24 MCP Servers Compiled to mcp-compiled.json"
Write-Host "   - Workspace: $AgentOutputDir ready."
Write-Host "NOTE: Point your IDE/Host to $RepoRoot\mcp-compiled.json to use your tools." -ForegroundColor Yellow
