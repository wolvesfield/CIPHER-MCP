# =============================================================================
# CIPHER-MCP — One-Liner Bootstrap (Windows PowerShell)
# Clones the repo and runs full setup in a single command.
#
# Usage — paste this in any PowerShell window (run as Admin):
#   irm https://raw.githubusercontent.com/wolvesfield/CIPHER-MCP/main/setup/windows-bootstrap.ps1 | iex
#
# Or with a custom install path:
#   $env:INSTALL_DIR = "C:\cipher-mcp"; irm .../windows-bootstrap.ps1 | iex
# =============================================================================

$RepoUrl    = "https://github.com/wolvesfield/CIPHER-MCP.git"
$InstallDir = if ($env:INSTALL_DIR) { $env:INSTALL_DIR } else { "$env:USERPROFILE\cipher-mcp" }

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   CIPHER-MCP — Universal Machine Bootstrap       ║" -ForegroundColor Cyan
Write-Host "║   For Littli 💙                                  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ git not found. Install Git from https://git-scm.com and rerun." -ForegroundColor Red
    exit 1
}

# Clone or update
if (Test-Path "$InstallDir\.git") {
    Write-Host "📦 Repo exists at $InstallDir — pulling latest..."
    Set-Location $InstallDir
    git pull --rebase origin main
} else {
    Write-Host "📦 Cloning CIPHER-MCP to $InstallDir..."
    git clone $RepoUrl $InstallDir
    Set-Location $InstallDir
}

Write-Host ""
Write-Host "🔧 Running setup..."
powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host ""
Write-Host "✅ Bootstrap complete. Repo at: $InstallDir" -ForegroundColor Green
