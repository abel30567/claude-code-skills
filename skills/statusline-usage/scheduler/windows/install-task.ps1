# ABOUTME: Windows Task Scheduler installer for Claude usage scraper.
# ABOUTME: Creates a reminder task since PTY automation is unsupported on Windows.

param(
    [string]$ScraperPath = "$env:USERPROFILE\.claude-statusline-usage\scrape-usage.py",
    [switch]$Uninstall
)

$TaskName = "ClaudeUsageScraper"

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Task removed."
    exit 0
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    Write-Error "Python not found. Install Python 3 first."
    exit 1
}

$CacheDir = "$env:USERPROFILE\.claude-statusline-usage"
if (-not (Test-Path $CacheDir)) {
    New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null
}

Write-Host "NOTE: PTY automation is not supported on Windows."
Write-Host "Run '/usage' manually in Claude Code to update limits."
Write-Host ""

$Action = New-ScheduledTaskAction -Execute $Python.Source -Argument $ScraperPath
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Force | Out-Null

Write-Host "Task '$TaskName' created. Runs every 15 minutes."
Write-Host "To uninstall: .\install-task.ps1 -Uninstall"
