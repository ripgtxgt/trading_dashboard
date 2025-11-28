# Quick Diagnostic Script for Trading Dashboard
# Run this on Windows Server to check deployment status

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Trading Dashboard Diagnostic Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Check current directory
$projectPath = "C:\trading_dashboard_fixed"
if (-not (Test-Path $projectPath)) {
    Write-Host "`nERROR: Project directory not found: $projectPath" -ForegroundColor Red
    exit 1
}

Set-Location $projectPath

# 1. Check current version
Write-Host "`n=== Current Git Version ===" -ForegroundColor Yellow
try {
    $gitVersion = git log -1 --oneline
    Write-Host $gitVersion -ForegroundColor Green
    
    $shortSHA = ($gitVersion -split ' ')[0]
    Write-Host "Short SHA: $shortSHA" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: Failed to get git version" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# 2. Check Git status
Write-Host "`n=== Git Status ===" -ForegroundColor Yellow
try {
    git status --short
    $gitStatus = git status --porcelain
    if ([string]::IsNullOrEmpty($gitStatus)) {
        Write-Host "Working directory clean" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Uncommitted changes detected" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Failed to check git status" -ForegroundColor Red
}

# 3. Check PM2 services
Write-Host "`n=== PM2 Services Status ===" -ForegroundColor Yellow
try {
    pm2 list
    
    # Count online services
    $pm2Json = pm2 jlist | ConvertFrom-Json
    $onlineCount = ($pm2Json | Where-Object { $_.pm2_env.status -eq "online" }).Count
    $totalCount = $pm2Json.Count
    
    Write-Host "`nServices: $onlineCount/$totalCount online" -ForegroundColor $(if ($onlineCount -eq $totalCount) { "Green" } else { "Yellow" })
} catch {
    Write-Host "ERROR: Failed to check PM2 services" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# 4. Check Nginx status
Write-Host "`n=== Nginx Status ===" -ForegroundColor Yellow
try {
    $nginxProcess = Get-Process nginx -ErrorAction SilentlyContinue
    if ($nginxProcess) {
        Write-Host "Nginx is running" -ForegroundColor Green
        $nginxProcess | Select-Object Id, ProcessName, StartTime | Format-Table
    } else {
        Write-Host "WARNING: Nginx is not running" -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Nginx not found" -ForegroundColor Yellow
}

# 5. Check recent webhook logs
Write-Host "`n=== Recent Webhook Deployment Logs ===" -ForegroundColor Yellow
try {
    pm2 logs webhook-deploy-server --lines 20 --nostream
} catch {
    Write-Host "ERROR: Failed to get webhook logs" -ForegroundColor Red
}

# 6. Check deployment history
Write-Host "`n=== Recent Deployment History ===" -ForegroundColor Yellow
$historyFile = "$projectPath\deployment\deploy-history.json"
if (Test-Path $historyFile) {
    try {
        $history = Get-Content $historyFile | ConvertFrom-Json
        $recentDeployments = $history | Select-Object -Last 3
        $recentDeployments | ForEach-Object {
            $status = if ($_.success) { "SUCCESS" } else { "FAILED" }
            $color = if ($_.success) { "Green" } else { "Red" }
            Write-Host "$($_.timestamp) - $($_.version) - $status" -ForegroundColor $color
        }
    } catch {
        Write-Host "ERROR: Failed to read deployment history" -ForegroundColor Red
    }
} else {
    Write-Host "No deployment history file found" -ForegroundColor Yellow
}

# 7. Check if website is accessible
Write-Host "`n=== Website Accessibility Check ===" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "Website is accessible (HTTP 200)" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Website returned status code $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Website is not accessible" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}

# 8. Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Diagnostic Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Check GitHub Actions logs: https://github.com/ripgtxgt/trading_dashboard/actions"
Write-Host "2. View detailed service logs: pm2 logs <service-name>"
Write-Host "3. Manual deployment: .\deployment\deploy-auto.ps1"
Write-Host "4. Rollback if needed: .\deployment\rollback.ps1 -version <sha>"

Write-Host "`nFor more help, see: deployment\CHECK_VERSION.md" -ForegroundColor Cyan
