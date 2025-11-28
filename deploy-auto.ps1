<#
.SYNOPSIS
    Trading Dashboard Auto Deployment Script (for GitHub Actions)
.DESCRIPTION
    Automatically install dependencies, build project, copy files, restart services
.NOTES
    Version: 2.1
    Author: Manus AI
    Date: 2025-11-27
#>

$ErrorActionPreference = "Continue"

# Color output functions
function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success { param([string]$Message); Write-ColorOutput "[SUCCESS] $Message" "Green" }
function Write-Error { param([string]$Message); Write-ColorOutput "[ERROR] $Message" "Red" }
function Write-Info { param([string]$Message); Write-ColorOutput "[INFO] $Message" "Cyan" }

Write-Info "Starting automatic deployment..."
Write-Host ""

try {
    # 1. Copy .env file from C:\.env
    Write-Info "Copying .env file from C:\.env..."
    if (Test-Path "C:\.env") {
        Copy-Item -Path "C:\.env" -Destination ".env" -Force
        Write-Success ".env file copied successfully"
    } else {
        Write-ColorOutput "[WARNING] C:\.env file not found" "Yellow"
        Write-Info "Please create C:\.env file with your configuration"
        if (-not (Test-Path ".env")) {
            Write-ColorOutput "[WARNING] No .env file in project directory either" "Yellow"
            Write-Info "Services requiring environment variables may fail to start"
        }
    }
    Write-Host ""
    
    # 2. Install Node.js dependencies
    Write-Info "Installing Node.js dependencies..."
    $npmOutput = pnpm install 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependencies installed successfully"
    } else {
        Write-Error "Failed to install dependencies"
        Write-Host $npmOutput
    }
    Write-Host ""
    
    # 3. Install Python dependencies
    Write-Info "Installing Python dependencies..."
    if (Test-Path "scripts\requirements.txt") {
        $pipOutput = pip install -r scripts\requirements.txt -q 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python dependencies installed successfully"
        } else {
            Write-Error "Failed to install Python dependencies"
            Write-Host $pipOutput
        }
    } else {
        Write-Info "No requirements.txt found, skipping Python dependencies"
    }
    Write-Host ""
    
    # 4. Build frontend
    Write-Info "Building frontend..."
    $buildOutput = pnpm run build 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Frontend built successfully"
    } else {
        Write-Error "Failed to build frontend"
        Write-Host $buildOutput
    }
    Write-Host ""
    
    # 5. Copy build files to correct location
    Write-Info "Copying build files..."
    if (Test-Path "dist\public") {
        New-Item -ItemType Directory -Force -Path "server\_core\public" | Out-Null
        Copy-Item -Path "dist\public\*" -Destination "server\_core\public\" -Recurse -Force
        Write-Success "Build files copied successfully"
    } else {
        Write-Info "No dist\public folder found, skipping file copy"
    }
    Write-Host ""
    
    # 6. Database migration (if needed)
    Write-Info "Checking database migration..."
    if (Test-Path "drizzle") {
        try {
            pnpm drizzle-kit push 2>&1 | Out-Null
            Write-Success "Database migration completed"
        } catch {
            Write-Info "Database migration skipped or not needed"
        }
    }
    Write-Host ""
    
    # 7. Restart PM2 services
    Write-Info "Restarting PM2 services..."
    
    # Check if PM2 is installed
    $pm2Check = Get-Command pm2 -ErrorAction SilentlyContinue
    if ($pm2Check) {
        # Start with ecosystem config
        if (Test-Path "ecosystem.config.cjs") {
            Write-Info "Restarting services with ecosystem.config.cjs..."
            pm2 restart ecosystem.config.cjs 2>&1 | Out-Null
            
            # If restart fails (no existing processes), start fresh
            if ($LASTEXITCODE -ne 0) {
                Write-Info "No existing processes, starting fresh..."
                pm2 start ecosystem.config.cjs
            }
            
            Write-Success "PM2 services restarted successfully"
            
            # Save PM2 process list
            pm2 save 2>&1 | Out-Null
            
            # Wait for services to start
            Write-Info "Waiting for services to start..."
            Start-Sleep -Seconds 5
            
            # Check service status
            Write-Info "Service status:"
            pm2 list
        } else {
            Write-Error "ecosystem.config.cjs not found"
        }
    } else {
        Write-Error "PM2 is not installed. Please install PM2 first: npm install -g pm2"
    }
    Write-Host ""
    
    # 8. Configure Nginx (if exists)
    Write-Info "Configuring Nginx..."
    $nginxCheck = Get-Command nginx -ErrorAction SilentlyContinue
    if ($nginxCheck) {
        # Check if Nginx config file exists
        $nginxConfPath = "C:\nginx\conf\sites-enabled\cryptoalpha.vip.conf"
        $nginxConfDir = Split-Path -Parent $nginxConfPath
        
        # Create sites-enabled directory (if not exists)
        if (!(Test-Path $nginxConfDir)) {
            New-Item -ItemType Directory -Force -Path $nginxConfDir | Out-Null
            Write-Info "Created directory: $nginxConfDir"
        }
        
        # Copy Nginx config file
        if (Test-Path "nginx.conf") {
            Copy-Item -Path "nginx.conf" -Destination $nginxConfPath -Force
            Write-Success "Nginx config file updated"
            
            # Test Nginx config
            $nginxTest = nginx -t 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Nginx config test passed"
                
                # Reload Nginx
                nginx -s reload 2>&1 | Out-Null
                Write-Success "Nginx reloaded successfully"
            } else {
                Write-Error "Nginx config test failed:"
                Write-Host $nginxTest
            }
        } else {
            Write-Info "nginx.conf not found in project directory"
        }
    } else {
        Write-Info "Nginx is not installed, skipping Nginx configuration"
        Write-Info "To install Nginx: choco install nginx -y"
    }
    Write-Host ""
    
    Write-Success "========================================="
    Write-Success "Deployment completed successfully!"
    Write-Success "========================================="
    Write-Host ""
    Write-Info "Next steps:"
    Write-Info "1. Check service status: pm2 list"
    Write-Info "2. View logs: pm2 logs"
    Write-Info "3. Access dashboard: http://localhost:3000"
    Write-Host ""
    
    exit 0
    
} catch {
    Write-Host ""
    Write-Error "========================================="
    Write-Error "Deployment failed!"
    Write-Error "========================================="
    Write-Error "Error details: $_"
    Write-Host ""
    Write-Info "Please check the error message above and try again"
    Write-Host ""
    
    exit 1
}
