# ===================================================================
# Database Initialization Script for Windows
# Purpose: Create MySQL database and user for Trading Dashboard
# ===================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Initialization" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Check if MySQL is installed
Write-Host "Checking MySQL installation..." -ForegroundColor Yellow
try {
    $mysqlVersion = mysql --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] MySQL is installed: $mysqlVersion" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] MySQL not found" -ForegroundColor Red
        Write-Host "  Please install MySQL first" -ForegroundColor Gray
        Write-Host "  Download from: https://dev.mysql.com/downloads/installer/" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "  [ERROR] MySQL not found: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if MySQL service is running
Write-Host "Checking MySQL service status..." -ForegroundColor Yellow
try {
    $mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue | Where-Object { $_.Status -eq 'Running' } | Select-Object -First 1
    if ($mysqlService) {
        Write-Host "  [OK] MySQL service is running: $($mysqlService.Name)" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] MySQL service not running" -ForegroundColor Yellow
        Write-Host "  Attempting to start MySQL service..." -ForegroundColor Cyan
        
        $mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($mysqlService) {
            Start-Service $mysqlService.Name
            Write-Host "  [OK] MySQL service started: $($mysqlService.Name)" -ForegroundColor Green
        } else {
            Write-Host "  [ERROR] MySQL service not found" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "  [WARNING] Cannot check MySQL service status: $_" -ForegroundColor Yellow
}
Write-Host ""

# Prompt for MySQL root password
Write-Host "Please enter MySQL root password:" -ForegroundColor Yellow
Write-Host "  (Press Enter if no password is set)" -ForegroundColor Gray
$rootPassword = Read-Host -AsSecureString "  Root Password"
$rootPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($rootPassword)
)
Write-Host ""

# Test MySQL connection
Write-Host "Testing MySQL connection..." -ForegroundColor Yellow
try {
    $ErrorActionPreference = "Continue"
    if ($rootPasswordPlain) {
        $testResult = mysql -u root -p"$rootPasswordPlain" -e "SELECT 1;" 2>&1 | Out-String
    } else {
        $testResult = mysql -u root -e "SELECT 1;" 2>&1 | Out-String
    }
    
    # Check if connection was successful (ignore warnings, check for actual errors)
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] MySQL connection successful" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] MySQL connection failed" -ForegroundColor Red
        if ($testResult -match "Access denied") {
            Write-Host "  Incorrect password. Please try again." -ForegroundColor Gray
        } else {
            Write-Host "  Error details: $testResult" -ForegroundColor Gray
        }
        exit 1
    }
} catch {
    Write-Host "  [ERROR] MySQL connection failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Execute initialization script
Write-Host "Initializing database..." -ForegroundColor Yellow
Write-Host "  Creating database: trading_dashboard" -ForegroundColor Cyan
Write-Host "  Creating user: trading" -ForegroundColor Cyan
Write-Host "  Default password: trading123" -ForegroundColor Cyan
Write-Host ""

try {
    $scriptPath = "$PSScriptRoot\init_database.sql"
    if (-not (Test-Path $scriptPath)) {
        Write-Host "  [ERROR] SQL script not found: $scriptPath" -ForegroundColor Red
        exit 1
    }
    
    # Read SQL script content
    $sqlContent = Get-Content -Path $scriptPath -Raw
    
    $ErrorActionPreference = "Continue"
    if ($rootPasswordPlain) {
        $sqlResult = $sqlContent | mysql -u root -p"$rootPasswordPlain" 2>&1 | Out-String
    } else {
        $sqlResult = $sqlContent | mysql -u root 2>&1 | Out-String
    }
    
    # Check if SQL execution was successful (ignore warnings)
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Database initialized successfully" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Database initialization failed" -ForegroundColor Red
        Write-Host "  Error details: $sqlResult" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "  [ERROR] Database initialization failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Verify database creation
Write-Host "Verifying database creation..." -ForegroundColor Yellow
try {
    $ErrorActionPreference = "Continue"
    if ($rootPasswordPlain) {
        $dbCheck = mysql -u root -p"$rootPasswordPlain" -e "SHOW DATABASES LIKE 'trading_dashboard';" 2>&1 | Out-String
    } else {
        $dbCheck = mysql -u root -e "SHOW DATABASES LIKE 'trading_dashboard';" 2>&1 | Out-String
    }
    
    if ($LASTEXITCODE -eq 0 -and $dbCheck -match "trading_dashboard") {
        Write-Host "  [OK] Database 'trading_dashboard' created" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Cannot verify database creation" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [WARNING] Cannot verify database creation: $_" -ForegroundColor Yellow
}
Write-Host ""

# Verify user creation
Write-Host "Verifying user creation..." -ForegroundColor Yellow
try {
    $ErrorActionPreference = "Continue"
    if ($rootPasswordPlain) {
        $userCheck = mysql -u root -p"$rootPasswordPlain" -e "SELECT User, Host FROM mysql.user WHERE User='trading';" 2>&1 | Out-String
    } else {
        $userCheck = mysql -u root -e "SELECT User, Host FROM mysql.user WHERE User='trading';" 2>&1 | Out-String
    }
    
    if ($LASTEXITCODE -eq 0 -and $userCheck -match "trading") {
        Write-Host "  [OK] User 'trading' created" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Cannot verify user creation" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [WARNING] Cannot verify user creation: $_" -ForegroundColor Yellow
}
Write-Host ""

# Test new user connection
Write-Host "Testing new user connection..." -ForegroundColor Yellow
try {
    $ErrorActionPreference = "Continue"
    $testNewUser = mysql -u trading -p"trading123" -e "USE trading_dashboard; SELECT 1;" 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] User 'trading' can access database" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] User connection test failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [WARNING] User connection test failed: $_" -ForegroundColor Yellow
}
Write-Host ""

# Display connection string
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Database Initialization Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database Configuration:" -ForegroundColor Yellow
Write-Host "  Database Name: trading_dashboard" -ForegroundColor Gray
Write-Host "  Username: trading" -ForegroundColor Gray
Write-Host "  Password: trading123" -ForegroundColor Gray
Write-Host "  Host: localhost" -ForegroundColor Gray
Write-Host "  Port: 3306" -ForegroundColor Gray
Write-Host ""
Write-Host "Connection String for .env file:" -ForegroundColor Yellow
Write-Host '  DATABASE_URL="mysql://trading:trading123@localhost:3306/trading_dashboard"' -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT SECURITY NOTE:" -ForegroundColor Red
Write-Host "  The default password 'trading123' is for development only." -ForegroundColor Yellow
Write-Host "  Please change it in production environment!" -ForegroundColor Yellow
Write-Host ""
Write-Host "To change password, run:" -ForegroundColor Gray
Write-Host "  mysql -u root -p" -ForegroundColor Gray
Write-Host "  ALTER USER 'trading'@'localhost' IDENTIFIED BY 'your_new_password';" -ForegroundColor Gray
Write-Host "  FLUSH PRIVILEGES;" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
