# ===================================================================
# TA-Lib Automatic Installation Script for Windows
# Purpose: Download and install pre-compiled TA-Lib wheel for Windows
# ===================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TA-Lib Installation for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Detect Python version
Write-Host "Detecting Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  [OK] $pythonVersion" -ForegroundColor Green
    
    # Extract version numbers
    if ($pythonVersion -match 'Python (\d+)\.(\d+)\.(\d+)') {
        $majorVersion = $Matches[1]
        $minorVersion = $Matches[2]
        $pythonTag = "cp$majorVersion$minorVersion"
        Write-Host "  Python tag: $pythonTag" -ForegroundColor Cyan
    } else {
        Write-Host "  [ERROR] Cannot parse Python version" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  [ERROR] Python not found" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Detect system architecture
Write-Host "Detecting system architecture..." -ForegroundColor Yellow
$arch = if ([Environment]::Is64BitOperatingSystem) { "amd64" } else { "win32" }
Write-Host "  [OK] Architecture: $arch" -ForegroundColor Green
Write-Host ""

# Construct wheel filename
$wheelFilename = "TA_Lib-0.4.28-$pythonTag-$pythonTag-win_$arch.whl"
$downloadUrl = "https://github.com/cgohlke/talib-build/releases/download/v0.4.28/$wheelFilename"
$downloadPath = "$env:TEMP\$wheelFilename"

Write-Host "Downloading TA-Lib pre-compiled wheel..." -ForegroundColor Yellow
Write-Host "  URL: $downloadUrl" -ForegroundColor Gray
Write-Host "  Destination: $downloadPath" -ForegroundColor Gray

try {
    # Download wheel file
    Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath -UseBasicParsing
    Write-Host "  [OK] Download completed" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Download failed: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Alternative installation methods:" -ForegroundColor Yellow
    Write-Host "  1. Manual download from: https://github.com/cgohlke/talib-build/releases" -ForegroundColor Gray
    Write-Host "  2. Download the .whl file matching your Python version" -ForegroundColor Gray
    Write-Host "  3. Install using: pip install <downloaded-file>.whl" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Or install Visual Studio Build Tools:" -ForegroundColor Gray
    Write-Host "  https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Gray
    exit 1
}
Write-Host ""

# Install wheel file
Write-Host "Installing TA-Lib..." -ForegroundColor Yellow
try {
    pip install $downloadPath
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] TA-Lib installed successfully" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Installation failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  [ERROR] Installation failed: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Verify installation
Write-Host "Verifying installation..." -ForegroundColor Yellow
try {
    $result = python -c "import talib; print(talib.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] TA-Lib version: $result" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Verification failed, but installation may still be successful" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [WARNING] Verification failed, but installation may still be successful" -ForegroundColor Yellow
}
Write-Host ""

# Cleanup
Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
try {
    Remove-Item $downloadPath -ErrorAction SilentlyContinue
    Write-Host "  [OK] Cleanup completed" -ForegroundColor Green
} catch {
    Write-Host "  [WARNING] Cleanup failed (not critical)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TA-Lib Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
