# ===================================================================
# Windows Server Automated Deployment Script
# Purpose: Automatically deploy Trading Dashboard to Windows Server
# ===================================================================

param(
    [string]$ProjectPath = "C:\trading_dashboard",
    [switch]$SkipBuild = $false,
    [switch]$SkipDB = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trading Dashboard - Auto Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# ===================================================================
# 1. Check Project Path
# ===================================================================
Write-Host "[1/10] Checking project path..." -ForegroundColor Yellow
if (-not (Test-Path $ProjectPath)) {
    Write-Host "  [ERROR] Project path does not exist: $ProjectPath" -ForegroundColor Red
    Write-Host "  Please copy project files to the server first" -ForegroundColor Yellow
    exit 1
}
Write-Host "  [OK] Project path exists: $ProjectPath" -ForegroundColor Green
Set-Location $ProjectPath
Write-Host ""

# ===================================================================
# 2. Check .env File
# ===================================================================
Write-Host "[2/10] Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "  [WARNING] .env file does not exist, copying from .env.example..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
        Write-Host "  [OK] .env file created" -ForegroundColor Green
        Write-Host "  [WARNING] Please edit .env file and fill in correct configuration" -ForegroundColor Yellow
        Write-Host "  Configuration file path: $ProjectPath\.env" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Press any key to continue..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    } else {
        Write-Host "  [ERROR] Neither .env nor .env.example file exists" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  [OK] .env file exists" -ForegroundColor Green
}
Write-Host ""

# ===================================================================
# 3. Install Node.js Dependencies
# ===================================================================
Write-Host "[3/10] Installing Node.js dependencies..." -ForegroundColor Yellow
if (Get-Command "pnpm" -ErrorAction SilentlyContinue) {
    Write-Host "  Using pnpm to install dependencies..." -ForegroundColor Cyan
    pnpm install
} else {
    Write-Host "  Using npm to install dependencies..." -ForegroundColor Cyan
    npm install
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [ERROR] Dependency installation failed" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Node.js dependencies installed" -ForegroundColor Green
Write-Host ""

# ===================================================================
# 4. Install TA-Lib (Windows pre-compiled)
# ===================================================================
Write-Host "[4/10] Installing TA-Lib..." -ForegroundColor Yellow
try {
    # Check if TA-Lib is already installed
    $talibInstalled = python -c "import talib" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] TA-Lib already installed" -ForegroundColor Green
    } else {
        Write-Host "  Installing TA-Lib pre-compiled wheel..." -ForegroundColor Cyan
        & ".\scripts\install_talib_windows.ps1"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [WARNING] TA-Lib installation failed, continuing anyway..." -ForegroundColor Yellow
            Write-Host "  You can install it manually later using: .\install_talib.bat" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "  [WARNING] TA-Lib check failed, continuing anyway..." -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# 5. Install Python Dependencies
# ===================================================================
Write-Host "[5/10] Installing Python dependencies..." -ForegroundColor Yellow
if (Test-Path "scripts\requirements.txt") {
    pip install -r scripts\requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  [ERROR] Python dependency installation failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] Python dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] requirements.txt not found, skipping Python dependencies" -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# 6. Database Migration
# ===================================================================
if (-not $SkipDB) {
    Write-Host "[6/10] Running database migration..." -ForegroundColor Yellow
    try {
        if (Get-Command "pnpm" -ErrorAction SilentlyContinue) {
            pnpm db:push
        } else {
            npm run db:push
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [ERROR] Database migration failed" -ForegroundColor Red
            Write-Host "  Please check if DATABASE_URL configuration is correct" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "  [OK] Database migration completed" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Database migration failed: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[6/10] Skipping database migration..." -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# 7. Build Frontend
# ===================================================================
if (-not $SkipBuild) {
    Write-Host "[7/10] Building frontend..." -ForegroundColor Yellow
    try {
        if (Get-Command "pnpm" -ErrorAction SilentlyContinue) {
            pnpm build
        } else {
            npm run build
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [ERROR] Frontend build failed" -ForegroundColor Red
            exit 1
        }
        Write-Host "  [OK] Frontend build completed" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Frontend build failed: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[7/10] Skipping frontend build..." -ForegroundColor Yellow
}
Write-Host ""

# ===================================================================
# 8. Configure PM2
# ===================================================================
Write-Host "[8/10] Configuring PM2..." -ForegroundColor Yellow
if (-not (Get-Command "pm2" -ErrorAction SilentlyContinue)) {
    Write-Host "  [ERROR] PM2 not installed" -ForegroundColor Red
    Write-Host "  Install command: npm install -g pm2" -ForegroundColor Gray
    exit 1
}

# Stop old processes
Write-Host "  Stopping old processes..." -ForegroundColor Cyan
$ErrorActionPreference = "Continue"
try {
    pm2 delete trading-dashboard 2>&1 | Out-Null
} catch {}
try {
    pm2 delete trading-bot 2>&1 | Out-Null
} catch {}
try {
    pm2 delete websocket-server 2>&1 | Out-Null
} catch {}
Write-Host "  [OK] Old processes stopped (if any)" -ForegroundColor Green

Write-Host "  [OK] PM2 configured" -ForegroundColor Green
Write-Host ""

# ===================================================================
# 9. Start Services
# ===================================================================
Write-Host "[9/10] Starting services..." -ForegroundColor Yellow

# Start services using PM2 ecosystem config
Write-Host "  Starting services using PM2 ecosystem config..." -ForegroundColor Cyan
pm2 start ecosystem.config.cjs

Write-Host "  [INFO] Trading bot can be started manually if needed" -ForegroundColor Cyan
Write-Host "    Start command: pm2 start python --name trading-bot -- scripts/kucoin_api.py" -ForegroundColor Gray

Write-Host "  [OK] Services started" -ForegroundColor Green
Write-Host ""

# ===================================================================
# 10. Save PM2 Configuration
# ===================================================================
Write-Host "[10/10] Saving PM2 configuration..." -ForegroundColor Yellow
pm2 save
Write-Host "  [OK] PM2 configuration saved" -ForegroundColor Green
Write-Host ""

# ===================================================================
# 11. Configure Startup
# ===================================================================
Write-Host "[11/11] Configuring startup..." -ForegroundColor Yellow
if (Get-Command "pm2-startup" -ErrorAction SilentlyContinue) {
    Write-Host "  Configuring PM2 startup..." -ForegroundColor Cyan
    pm2-startup install
    Write-Host "  [OK] Startup configuration completed" -ForegroundColor Green
} else {
    Write-Host "  [WARNING] pm2-startup not installed" -ForegroundColor Yellow
    Write-Host "    Install command: npm install -g pm2-windows-startup" -ForegroundColor Gray
    Write-Host "    Configure command: pm2-startup install" -ForegroundColor Gray
}
Write-Host ""

# ===================================================================
# Configure Firewall
# ===================================================================
Write-Host "Configuring firewall..." -ForegroundColor Yellow
try {
    # Check if firewall rule already exists
    $existingRule = Get-NetFirewallRule -DisplayName "Trading Dashboard" -ErrorAction SilentlyContinue
    if ($existingRule) {
        Write-Host "  [INFO] Firewall rule already exists" -ForegroundColor Cyan
    } else {
        Write-Host "  Adding firewall rule..." -ForegroundColor Cyan
        New-NetFirewallRule -DisplayName "Trading Dashboard" -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow
        Write-Host "  [OK] Firewall rule added successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "  [WARNING] Firewall configuration failed (may need administrator privileges)" -ForegroundColor Yellow
    Write-Host "    Manual command: New-NetFirewallRule -DisplayName 'Trading Dashboard' -Direction Inbound -LocalPort 3000,8765 -Protocol TCP -Action Allow" -ForegroundColor Gray
}
Write-Host ""

# ===================================================================
# Display Service Status
# ===================================================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Service Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
pm2 list
Write-Host ""

# ===================================================================
# Display Access Information
# ===================================================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow

# Get local IP addresses
$ipAddresses = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }
foreach ($ip in $ipAddresses) {
    Write-Host "  http://$($ip.IPAddress):3000" -ForegroundColor Cyan
}
Write-Host ""

Write-Host "Common Commands:" -ForegroundColor Yellow
Write-Host "  Check service status:    pm2 list" -ForegroundColor Gray
Write-Host "  View logs:               pm2 logs" -ForegroundColor Gray
Write-Host "  Restart services:        pm2 restart all" -ForegroundColor Gray
Write-Host "  Stop services:           pm2 stop all" -ForegroundColor Gray
Write-Host "  Start trading bot:       pm2 start python --name trading-bot -- scripts/kucoin_api.py" -ForegroundColor Gray
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Access the URL above in your browser" -ForegroundColor Gray
Write-Host "  2. Check if .env configuration is correct" -ForegroundColor Gray
Write-Host "  3. Configure KuCoin API keys" -ForegroundColor Gray
Write-Host "  4. Configure Telegram Bot Token" -ForegroundColor Gray
Write-Host "  5. Start trading bot" -ForegroundColor Gray
Write-Host ""

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
