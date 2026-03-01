<#
.SYNOPSIS
Universal Fleet Bootstrap Script for Windows

.DESCRIPTION
This script automatically maps the CIPHER-MCP repository to your system's global GitHub Copilot 
agent directories. By using symlinks, any changes made to an agent or skill by you (or an AI) 
are automatically synced back to this repository, making it easy to git commit your brain.

.EXAMPLE
.\setup.ps1
#>

$ErrorActionPreference = 'Stop'

Write-Host "🚀 Initializing CIPHER-MCP Fleet Environment for Windows..." -ForegroundColor Cyan

# Define paths
$RepoRoot = $PSScriptRoot
$CopilotGlobalDir = "$env:USERPROFILE\.copilot"
$CopilotConfigDir = "$env:USERPROFILE\.config\copilot"

# 1. Create necessary target directories
$TargetAgentsDir = "$CopilotConfigDir\agents"
$TargetSkillsDir = "$CopilotGlobalDir\skills"
$TargetPromptsDir = "$env:USERPROFILE\vs-code-agents\.github\prompts"

Write-Host "Creating target directories if they don't exist..."
if (-not (Test-Path $TargetAgentsDir)) { New-Item -ItemType Directory -Path $TargetAgentsDir -Force | Out-Null }
if (-not (Test-Path $TargetSkillsDir)) { New-Item -ItemType Directory -Path $TargetSkillsDir -Force | Out-Null }
if (-not (Test-Path $TargetPromptsDir)) { New-Item -ItemType Directory -Path $TargetPromptsDir -Force | Out-Null }

# 2. Setup Global Instructions (Hard Copy or Symlink)
$SourceInstructions = "$RepoRoot\core\instructions\copilot-instructions.md"
$TargetInstructions = "$CopilotGlobalDir\copilot-instructions.md"

if (Test-Path $TargetInstructions) { Remove-Item -Path $TargetInstructions -Force }
New-Item -ItemType SymbolicLink -Path $TargetInstructions -Target $SourceInstructions -Force | Out-Null
Write-Host "✅ Linked copilot-instructions.md" -ForegroundColor Green

# 3. Setup Agents
Write-Host "Linking Agents..."
$Agents = Get-ChildItem -Path "$RepoRoot\core\agents\*.md"
foreach ($Agent in $Agents) {
    $TargetAgent = "$TargetAgentsDir\$($Agent.Name)"
    if (Test-Path $TargetAgent) { Remove-Item -Path $TargetAgent -Force }
    New-Item -ItemType SymbolicLink -Path $TargetAgent -Target $Agent.FullName -Force | Out-Null
}
Write-Host "✅ Linked $(@($Agents).Count) Agents" -ForegroundColor Green

# 4. Setup Skills
Write-Host "Linking Skills..."
$Skills = Get-ChildItem -Path "$RepoRoot\core\skills" -Directory
foreach ($Skill in $Skills) {
    $TargetSkill = "$TargetSkillsDir\$($Skill.Name)"
    if (Test-Path $TargetSkill) { Remove-Item -Path $TargetSkill -Recurse -Force }
    # Create directory junction for skills
    New-Item -ItemType Junction -Path $TargetSkill -Target $Skill.FullName -Force | Out-Null
}
Write-Host "✅ Linked $(@($Skills).Count) Skills" -ForegroundColor Green

# 5. Setup Prompts
Write-Host "Linking Prompts..."
$Prompts = Get-ChildItem -Path "$RepoRoot\prompts\*.md"
foreach ($Prompt in $Prompts) {
    $TargetPrompt = "$TargetPromptsDir\$($Prompt.Name)"
    if (Test-Path $TargetPrompt) { Remove-Item -Path $TargetPrompt -Force }
    New-Item -ItemType SymbolicLink -Path $TargetPrompt -Target $Prompt.FullName -Force | Out-Null
}
Write-Host "✅ Linked $(@($Prompts).Count) Prompts" -ForegroundColor Green

Write-Host "✨ Bootstrap Complete! Your Fleet is now globally active." -ForegroundColor Magenta
Write-Host "NOTE: If you edit any agent or skill, it will directly update the files in this repository." -ForegroundColor Yellow
