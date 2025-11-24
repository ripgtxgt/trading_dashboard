# ===================================================================
# Windows Server Environment Check Script
# Purpose: Automatically detect Windows server environment dependencies
# ===================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trading Dashboard - Environment Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allPassed = $true

# Detection functions
function Test-Command {
    param($CommandName)
    try {
        if (Get-Command $CommandName -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Get-Version {
    param($Command, $VersionArg = "--version")
    try {
        $output = & $Command $VersionArg 2>&1 | Out-String
        return $output.Trim()
    } catch {
        return "Unable to get version"
    }
}

# ===================================================================
# 1. Check Node.js
# ===================================================================
Write-Host "[1/8] Checking Node.js..." -ForegroundColor Yellow
if (Test-Command "node") {
    $nodeVersion = Get-Version "node" "-v"
    Write-Host "  [OK] Node.js installed: $nodeVersion" -ForegroundColor Green
    
    # Check if version >= 18
    $versionNumber = $nodeVersion -replace 'v', '' -replace '\..*', ''
    if ([int]$versionNumber -lt 18) {
        Write-Host "  [WARNING] Node.js version is too old, recommend v18 or higher" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [ERROR] Node.js not installed" -ForegroundColor Red
    Write-Host "    Download: https://nodejs.org/" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 2. Check npm/pnpm
# ===================================================================
Write-Host "[2/8] Checking npm/pnpm..." -ForegroundColor Yellow
if (Test-Command "npm") {
    $npmVersion = Get-Version "npm" "-v"
    Write-Host "  [OK] npm installed: v$npmVersion" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] npm not installed" -ForegroundColor Red
    $allPassed = $false
}

if (Test-Command "pnpm") {
    $pnpmVersion = Get-Version "pnpm" "-v"
    Write-Host "  [OK] pnpm installed: v$pnpmVersion" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] pnpm not installed (recommended)" -ForegroundColor Yellow
    Write-Host "    Install: npm install -g pnpm" -ForegroundColor Gray
}
Write-Host ""

# ===================================================================
# 3. Check Python
# ===================================================================
Write-Host "[3/8] Checking Python..." -ForegroundColor Yellow
if (Test-Command "python") {
    $pythonVersion = Get-Version "python" "--version"
    Write-Host "  [OK] Python installed: $pythonVersion" -ForegroundColor Green
    
    # Check if version >= 3.8
    $versionMatch = $pythonVersion -match 'Python (\d+)\.(\d+)'
    if ($versionMatch) {
        $majorVersion = [int]$Matches[1]
        $minorVersion = [int]$Matches[2]
        if ($majorVersion -lt 3 -or ($majorVersion -eq 3 -and $minorVersion -lt 8)) {
            Write-Host "  [WARNING] Python version is too old, recommend 3.8 or higher" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  [ERROR] Python not installed" -ForegroundColor Red
    Write-Host "    Download: https://www.python.org/downloads/" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 4. Check pip
# ===================================================================
Write-Host "[4/8] Checking pip..." -ForegroundColor Yellow
if (Test-Command "pip") {
    $pipVersion = Get-Version "pip" "--version"
    Write-Host "  [OK] pip installed: $pipVersion" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] pip not installed" -ForegroundColor Red
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 5. Check MySQL
# ===================================================================
Write-Host "[5/8] Checking MySQL..." -ForegroundColor Yellow
if (Test-Command "mysql") {
    $mysqlVersion = Get-Version "mysql" "--version"
    Write-Host "  [OK] MySQL client installed: $mysqlVersion" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] MySQL client not installed (optional)" -ForegroundColor Yellow
}

# Check MySQL service
$mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue
if ($mysqlService) {
    Write-Host "  [OK] MySQL service installed: $($mysqlService.DisplayName)" -ForegroundColor Green
    if ($mysqlService.Status -eq "Running") {
        Write-Host "    Status: Running" -ForegroundColor Green
    } else {
        Write-Host "    Status: Stopped" -ForegroundColor Yellow
        Write-Host "    Start command: Start-Service $($mysqlService.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "  [ERROR] MySQL service not installed" -ForegroundColor Red
    Write-Host "    Download: https://dev.mysql.com/downloads/mysql/" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 6. Check PM2
# ===================================================================
Write-Host "[6/8] Checking PM2..." -ForegroundColor Yellow
if (Test-Command "pm2") {
    $pm2Version = Get-Version "pm2" "-v"
    Write-Host "  [OK] PM2 installed: v$pm2Version" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] PM2 not installed (required for production)" -ForegroundColor Red
    Write-Host "    Install: npm install -g pm2" -ForegroundColor Gray
    Write-Host "    Install: npm install -g pm2-windows-startup" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# 7. Check Git
# ===================================================================
Write-Host "[7/8] Checking Git..." -ForegroundColor Yellow
if (Test-Command "git") {
    $gitVersion = Get-Version "git" "--version"
    Write-Host "  [OK] Git installed: $gitVersion" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] Git not installed (optional, for version control)" -ForegroundColor Yellow
    Write-Host "    Download: https://git-scm.com/download/win" -ForegroundColor Gray
}
Write-Host ""

# ===================================================================
# 8. Check Firewall and Ports
# ===================================================================
Write-Host "[8/8] Checking firewall and ports..." -ForegroundColor Yellow

# Check if port 3000 is in use
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
if ($port3000) {
    Write-Host "  [WARNING] Port 3000 is in use" -ForegroundColor Yellow
    Write-Host "    Process: PID $($port3000.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "  [OK] Port 3000 is available" -ForegroundColor Green
}

# Check if port 8765 is in use (WebSocket)
$port8765 = Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue
if ($port8765) {
    Write-Host "  [WARNING] Port 8765 is in use" -ForegroundColor Yellow
    Write-Host "    Process: PID $($port8765.OwningProcess)" -ForegroundColor Gray
} else {
    Write-Host "  [OK] Port 8765 is available" -ForegroundColor Green
}

# Check firewall status
$firewallProfile = Get-NetFirewallProfile -Profile Domain,Public,Private
$enabledProfiles = $firewallProfile | Where-Object { $_.Enabled -eq $true }
if ($enabledProfiles) {
    Write-Host "  [INFO] Firewall is enabled, need to open ports 3000 and 8765" -ForegroundColor Cyan
    Write-Host "    Command: New-NetFirewallRule -DisplayName 'Trading Dashboard' -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow" -ForegroundColor Gray
} else {
    Write-Host "  [WARNING] Firewall is disabled (not recommended)" -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# Check Python Dependencies
# ===================================================================
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
$pythonPackages = @("ccxt", "websocket-client", "requests", "pandas", "numpy")
$missingPackages = @()

foreach ($package in $pythonPackages) {
    try {
        $result = & pip show $package 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] $package installed" -ForegroundColor Green
        } else {
            Write-Host "  [ERROR] $package not installed" -ForegroundColor Red
            $missingPackages += $package
        }
    } catch {
        Write-Host "  [ERROR] $package not installed" -ForegroundColor Red
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "  Missing Python packages: $($missingPackages -join ', ')" -ForegroundColor Yellow
    Write-Host "  Install command: pip install $($missingPackages -join ' ')" -ForegroundColor Gray
    $allPassed = $false
}
Write-Host ""

# ===================================================================
# Summary
# ===================================================================
Write-Host "========================================" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host "  [OK] Environment check passed!" -ForegroundColor Green
    Write-Host "  Your server is ready for deployment" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Environment check failed" -ForegroundColor Red
    Write-Host "  Please install missing dependencies as indicated above" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Pause to view results
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
