# Trading Dashboard Simple Deployment Script
# Simplified version for Windows Server 2022

# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trading Dashboard Deployment" -ForegroundColor Cyan
Write-Host "  Simplified Version" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check .env file
Write-Host "[1/6] Checking configuration file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "[OK] .env file found" -ForegroundColor Green
} else {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file first. See DEPLOYMENT_WITH_YOUR_CONFIG.md" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Check Python
Write-Host ""
Write-Host "[2/6] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 3: Check Node.js
Write-Host ""
Write-Host "[3/6] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found!" -ForegroundColor Red
    Write-Host "Please install Node.js 20+ first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 4: Install dependencies
Write-Host ""
Write-Host "[4/6] Installing dependencies..." -ForegroundColor Yellow

# Install pnpm if not exists
try {
    $pnpmVersion = pnpm --version 2>&1
    Write-Host "[OK] pnpm v$pnpmVersion already installed" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Installing pnpm..." -ForegroundColor Cyan
    npm install -g pnpm
}

# Install PM2 if not exists
try {
    $pm2Version = pm2 --version 2>&1
    Write-Host "[OK] PM2 v$pm2Version already installed" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Installing PM2..." -ForegroundColor Cyan
    npm install -g pm2
    npm install -g pm2-windows-startup
    pm2-startup install
}

# Install Node.js dependencies
Write-Host "[INFO] Installing Node.js dependencies (this may take a few minutes)..." -ForegroundColor Cyan
pnpm install

# Install Python dependencies
Write-Host "[INFO] Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

Write-Host "[OK] Dependencies installed successfully" -ForegroundColor Green

# Step 5: Initialize database
Write-Host ""
Write-Host "[5/6] Database initialization..." -ForegroundColor Yellow
Write-Host "[INFO] Please make sure MySQL database is ready:" -ForegroundColor Cyan
Write-Host "  - Database: trading_dashboard" -ForegroundColor Cyan
Write-Host "  - User: trading" -ForegroundColor Cyan
Write-Host "  - Password: Zdm351026" -ForegroundColor Cyan
Write-Host ""
$initDb = Read-Host "Initialize database schema? (y/n)"
if ($initDb -eq "y") {
    if (Test-Path "database\schema.sql") {
        Write-Host "[INFO] Importing database schema..." -ForegroundColor Cyan
        Get-Content "database\schema.sql" -Raw | mysql -u trading -pZdm351026 trading_dashboard
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Database initialized successfully" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] Database initialization may have failed" -ForegroundColor Yellow
            Write-Host "[INFO] You can manually run: mysql -u trading -pZdm351026 trading_dashboard < database\schema.sql" -ForegroundColor Cyan
        }
    } else {
        Write-Host "[WARNING] database\schema.sql not found, skipping..." -ForegroundColor Yellow
    }
} else {
    Write-Host "[INFO] Skipping database initialization" -ForegroundColor Cyan
}

# Step 6: Start services
Write-Host ""
Write-Host "[6/6] Starting services..." -ForegroundColor Yellow
Write-Host "[INFO] Starting all services with PM2..." -ForegroundColor Cyan

pm2 delete all 2>$null
pm2 start ecosystem.config.cjs
pm2 save

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Show status
pm2 list

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Check service status: pm2 list" -ForegroundColor White
Write-Host "  2. View logs: pm2 logs" -ForegroundColor White
Write-Host "  3. Access dashboard: http://localhost:3000" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
