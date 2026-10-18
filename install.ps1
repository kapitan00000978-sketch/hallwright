# ==============================================================================
# Artisan PowerShell Bootstrap Installer
# Usage:
#   # Recommended secure installation:
#   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/kapitan00000978-sketch/hallwright/main/install.ps1" -OutFile "install.ps1"
#   .\install.ps1
#
#   # Quick pipe mode:
#   irm https://raw.githubusercontent.com/kapitan00000978-sketch/hallwright/main/install.ps1 | iex
# ==============================================================================

$RepoRaw = "https://raw.githubusercontent.com/kapitan00000978-sketch/hallwright/main"
$TargetDir = Get-Location

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  🛡️  ARTISAN POWERSHELL BOOTSTRAP INSTALLER" -ForegroundColor Cyan
Write-Host "      Autonomous AI Agent Quality & Craftsmanship Protocol" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "[*] Target Directory: $TargetDir" -ForegroundColor Yellow

# Ensure directories
New-Item -ItemType Directory -Force -Path "$TargetDir\.hallwright" | Out-Null
New-Item -ItemType Directory -Force -Path "$TargetDir\.cursor\rules" | Out-Null
New-Item -ItemType Directory -Force -Path "$TargetDir\.github" | Out-Null

Write-Host "[+] Downloading core Artisan protocol..." -ForegroundColor Green
Invoke-RestMethod -Uri "$RepoRaw/AGENTS.md" -OutFile "$TargetDir\AGENTS.md"

# Safe memory preservation: never overwrite existing user memory
if (-not (Test-Path "$TargetDir\.hallwright\memory.json")) {
    Write-Host "[+] Initializing clean starter memory template..." -ForegroundColor Green
    Invoke-RestMethod -Uri "$RepoRaw/.hallwright/memory.json" -OutFile "$TargetDir\.hallwright\memory.json"
} else {
    Write-Host "[*] Preserving existing .hallwright\memory.json (not overwritten)." -ForegroundColor Yellow
}

if (-not (Test-Path "$TargetDir\.hallwright\memory.md")) {
    Invoke-RestMethod -Uri "$RepoRaw/.hallwright/memory.md" -OutFile "$TargetDir\.hallwright\memory.md"
}

Write-Host "[+] Installing Cursor AI Rules..." -ForegroundColor Green
Invoke-RestMethod -Uri "$RepoRaw/.cursorrules" -OutFile "$TargetDir\.cursorrules"
Invoke-RestMethod -Uri "$RepoRaw/.cursor/rules/01-craftsman.mdc" -OutFile "$TargetDir\.cursor\rules\01-craftsman.mdc"
Invoke-RestMethod -Uri "$RepoRaw/.cursor/rules/02-architecture-standards.mdc" -OutFile "$TargetDir\.cursor\rules\02-architecture-standards.mdc"
Invoke-RestMethod -Uri "$RepoRaw/.cursor/rules/03-security-directives.mdc" -OutFile "$TargetDir\.cursor\rules\03-security-directives.mdc"
Invoke-RestMethod -Uri "$RepoRaw/.cursor/rules/04-testing-tdd.mdc" -OutFile "$TargetDir\.cursor\rules\04-testing-tdd.mdc"
Invoke-RestMethod -Uri "$RepoRaw/.cursor/rules/05-design-standards.mdc" -OutFile "$TargetDir\.cursor\rules\05-design-standards.mdc"

Write-Host "[+] Installing Claude Code Directives..." -ForegroundColor Green
Invoke-RestMethod -Uri "$RepoRaw/CLAUDE.md" -OutFile "$TargetDir\CLAUDE.md"

Write-Host "[+] Installing GitHub Copilot & Windsurf Directives..." -ForegroundColor Green
Invoke-RestMethod -Uri "$RepoRaw/.github/copilot-instructions.md" -OutFile "$TargetDir\.github\copilot-instructions.md"
Invoke-RestMethod -Uri "$RepoRaw/.windsurfrules" -OutFile "$TargetDir\.windsurfrules"

Write-Host "[+] Installing Cline, Kimi & Kilo Directives..." -ForegroundColor Green
Invoke-RestMethod -Uri "$RepoRaw/.clinerules" -OutFile "$TargetDir\.clinerules"
Invoke-RestMethod -Uri "$RepoRaw/kimi-agent/KIMI.md" -OutFile "$TargetDir\KIMI.md"
Invoke-RestMethod -Uri "$RepoRaw/kilo-agent/KILO.md" -OutFile "$TargetDir\KILO.md"

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "  ✅ Artisan successfully installed!" -ForegroundColor Green
Write-Host "     Quality and craftsmanship rules are now active." -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
