# SSL Certificate Setup Script for Windows Server
# Domain: cryptoalpha.vip
# Uses win-acme (formerly letsencrypt-win-simple) for Let's Encrypt certificates

param(
    [string]$Domain = "cryptoalpha.vip",
    [string]$Email = "admin@cryptoalpha.vip",
    [string]$NginxPath = "C:\nginx"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SSL Certificate Setup for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "[INFO] Running as Administrator" -ForegroundColor Green
Write-Host ""

# Create SSL directory
$sslDir = "$NginxPath\ssl\$Domain"
Write-Host "[INFO] Creating SSL directory: $sslDir" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $sslDir | Out-Null

# Check if win-acme is installed
$winAcmePath = "$env:ProgramFiles\win-acme"
$winAcmeExe = "$winAcmePath\wacs.exe"

if (-not (Test-Path $winAcmeExe)) {
    Write-Host "[INFO] win-acme not found. Downloading..." -ForegroundColor Yellow
    
    # Download win-acme
    $downloadUrl = "https://github.com/win-acme/win-acme/releases/latest/download/win-acme.v2.2.9.1701.x64.pluggable.zip"
    $zipFile = "$env:TEMP\win-acme.zip"
    
    try {
        Write-Host "[INFO] Downloading from: $downloadUrl" -ForegroundColor Cyan
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing
        
        Write-Host "[INFO] Extracting to: $winAcmePath" -ForegroundColor Cyan
        New-Item -ItemType Directory -Force -Path $winAcmePath | Out-Null
        Expand-Archive -Path $zipFile -DestinationPath $winAcmePath -Force
        
        Remove-Item $zipFile -Force
        Write-Host "[SUCCESS] win-acme installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to download win-acme: $_" -ForegroundColor Red
        Write-Host "[INFO] Please download manually from: https://github.com/win-acme/win-acme/releases" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SSL Certificate Options" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Option 1: Automatic Certificate (Recommended)" -ForegroundColor Green
Write-Host "  - Uses win-acme to obtain Let's Encrypt certificate" -ForegroundColor Gray
Write-Host "  - Requires port 80 to be accessible from internet" -ForegroundColor Gray
Write-Host "  - Automatic renewal every 60 days" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Manual Certificate" -ForegroundColor Yellow
Write-Host "  - Use your own SSL certificate files" -ForegroundColor Gray
Write-Host "  - Place fullchain.pem and privkey.pem in: $sslDir" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 3: Self-Signed Certificate (Testing Only)" -ForegroundColor Magenta
Write-Host "  - Generate self-signed certificate" -ForegroundColor Gray
Write-Host "  - Browser will show security warning" -ForegroundColor Gray
Write-Host "  - Only for testing, NOT for production" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Select option (1/2/3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "[INFO] Starting automatic certificate setup..." -ForegroundColor Cyan
        Write-Host ""
        Write-Host "IMPORTANT REQUIREMENTS:" -ForegroundColor Yellow
        Write-Host "1. DNS A record for $Domain must point to your server IP (13.113.194.218)" -ForegroundColor Yellow
        Write-Host "2. Port 80 must be open in Windows Firewall" -ForegroundColor Yellow
        Write-Host "3. Port 80 must be accessible from the internet" -ForegroundColor Yellow
        Write-Host "4. Nginx must be stopped during certificate issuance" -ForegroundColor Yellow
        Write-Host ""
        
        $confirm = Read-Host "Have you completed all requirements? (yes/no)"
        if ($confirm -ne "yes") {
            Write-Host "[INFO] Please complete the requirements and run this script again" -ForegroundColor Yellow
            exit 0
        }
        
        # Stop Nginx if running
        Write-Host ""
        Write-Host "[INFO] Stopping Nginx..." -ForegroundColor Cyan
        $nginxProcess = Get-Process nginx -ErrorAction SilentlyContinue
        if ($nginxProcess) {
            Stop-Process -Name nginx -Force
            Start-Sleep -Seconds 2
            Write-Host "[SUCCESS] Nginx stopped" -ForegroundColor Green
        }
        
        # Run win-acme
        Write-Host ""
        Write-Host "[INFO] Running win-acme..." -ForegroundColor Cyan
        Write-Host "[INFO] Follow the prompts to obtain your certificate" -ForegroundColor Yellow
        Write-Host ""
        
        & $winAcmeExe
        
        Write-Host ""
        Write-Host "[INFO] Certificate files should be located in:" -ForegroundColor Cyan
        Write-Host "  C:\ProgramData\win-acme\httpsacme-v02.api.letsencrypt.org\Certificates" -ForegroundColor Gray
        Write-Host ""
        Write-Host "[INFO] Copy the certificate files to: $sslDir" -ForegroundColor Yellow
        Write-Host "  - fullchain.pem (certificate)" -ForegroundColor Gray
        Write-Host "  - privkey.pem (private key)" -ForegroundColor Gray
    }
    
    "2" {
        Write-Host ""
        Write-Host "[INFO] Manual certificate setup selected" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Please place your certificate files in:" -ForegroundColor Yellow
        Write-Host "  $sslDir" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Required files:" -ForegroundColor Yellow
        Write-Host "  - fullchain.pem (full certificate chain)" -ForegroundColor Gray
        Write-Host "  - privkey.pem (private key)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Press Enter when files are ready..." -ForegroundColor Yellow
        Read-Host
    }
    
    "3" {
        Write-Host ""
        Write-Host "[WARNING] Generating self-signed certificate (TESTING ONLY)" -ForegroundColor Magenta
        Write-Host ""
        
        # Check if OpenSSL is available
        $opensslPath = "C:\Program Files\Git\usr\bin\openssl.exe"
        if (-not (Test-Path $opensslPath)) {
            $opensslPath = "openssl.exe"
        }
        
        try {
            # Generate self-signed certificate
            $certFile = "$sslDir\fullchain.pem"
            $keyFile = "$sslDir\privkey.pem"
            
            & $opensslPath req -x509 -nodes -days 365 -newkey rsa:2048 `
                -keyout $keyFile `
                -out $certFile `
                -subj "/C=US/ST=State/L=City/O=Organization/CN=$Domain"
            
            Write-Host "[SUCCESS] Self-signed certificate generated" -ForegroundColor Green
            Write-Host "[WARNING] This certificate will show security warnings in browsers" -ForegroundColor Yellow
        } catch {
            Write-Host "[ERROR] Failed to generate certificate: $_" -ForegroundColor Red
            Write-Host "[INFO] Please install OpenSSL or use Option 1/2" -ForegroundColor Yellow
            exit 1
        }
    }
    
    default {
        Write-Host "[ERROR] Invalid option selected" -ForegroundColor Red
        exit 1
    }
}

# Verify certificate files exist
Write-Host ""
Write-Host "[INFO] Verifying certificate files..." -ForegroundColor Cyan
$certFile = "$sslDir\fullchain.pem"
$keyFile = "$sslDir\privkey.pem"

if ((Test-Path $certFile) -and (Test-Path $keyFile)) {
    Write-Host "[SUCCESS] Certificate files found:" -ForegroundColor Green
    Write-Host "  Certificate: $certFile" -ForegroundColor Gray
    Write-Host "  Private Key: $keyFile" -ForegroundColor Gray
} else {
    Write-Host "[WARNING] Certificate files not found in: $sslDir" -ForegroundColor Yellow
    Write-Host "Please place the files manually before starting Nginx" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SSL Setup Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update Nginx configuration with correct certificate paths" -ForegroundColor Gray
Write-Host "2. Test Nginx configuration: nginx -t" -ForegroundColor Gray
Write-Host "3. Start Nginx: nginx" -ForegroundColor Gray
Write-Host "4. Test HTTPS access: https://$Domain" -ForegroundColor Gray
Write-Host ""
