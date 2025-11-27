# Fix SQLite issue by disabling it and using MySQL only
Write-Host "=== Fixing SQLite Issue ===" -ForegroundColor Green

# Navigate to project directory
Set-Location C:\trading_dashboard_fixed

# Backup original db.ts
Write-Host "Backing up server\db.ts..." -ForegroundColor Yellow
Copy-Item "server\db.ts" "server\db.ts.backup" -Force

# Read the file
$dbFile = "server\db.ts"
$content = Get-Content $dbFile -Raw

# Find and replace getSqliteDb function
Write-Host "Disabling SQLite..." -ForegroundColor Yellow

# Pattern to match the getSqliteDb function
$oldFunction = @'
export async function getSqliteDb() {
  if (!_sqliteDb) {
    try {
      const dbPath = path.join(process.cwd(), 'trading.db');
      _sqliteDb = new Database(dbPath);
      console.log('[SQLite] Connected to database:', dbPath);
    } catch (error) {
      console.error('[SQLite] Failed to connect:', error);
      _sqliteDb = null;
    }
  }
  return _sqliteDb;
}
'@

$newFunction = @'
export async function getSqliteDb() {
  // SQLite disabled on Windows - using MySQL only
  if (!_sqliteDb) {
    console.warn('[SQLite] Disabled - using MySQL database instead');
    _sqliteDb = null;
  }
  return _sqliteDb;
}
'@

# Replace the function
if ($content -match 'export async function getSqliteDb') {
    $content = $content -replace [regex]::Escape($oldFunction), $newFunction
    Set-Content $dbFile $content -NoNewline
    Write-Host "SQLite disabled successfully!" -ForegroundColor Green
} else {
    Write-Host "Could not find getSqliteDb function, trying alternative method..." -ForegroundColor Yellow
    
    # Alternative: Comment out Database import and replace function
    $content = $content -replace "import Database from 'better-sqlite3';", "// import Database from 'better-sqlite3'; // Disabled"
    $content = $content -replace "(?s)export async function getSqliteDb\(\) \{.*?\n\}", $newFunction
    Set-Content $dbFile $content -NoNewline
    Write-Host "SQLite disabled using alternative method!" -ForegroundColor Green
}

# Rebuild the project
Write-Host "`nRebuilding project..." -ForegroundColor Yellow
pnpm run build

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build successful!" -ForegroundColor Green
    
    # Restart trading-dashboard
    Write-Host "`nRestarting trading-dashboard..." -ForegroundColor Yellow
    pm2 restart trading-dashboard
    
    Write-Host "`n=== Fix Complete ===" -ForegroundColor Green
    Write-Host "Waiting 3 seconds for service to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    
    Write-Host "`nChecking logs..." -ForegroundColor Yellow
    pm2 logs trading-dashboard --lines 30
} else {
    Write-Host "Build failed! Check errors above." -ForegroundColor Red
    Write-Host "Restoring backup..." -ForegroundColor Yellow
    Copy-Item "server\db.ts.backup" "server\db.ts" -Force
    Write-Host "Backup restored." -ForegroundColor Green
}
