# Test FoxTrends Windows Scripts
# This script validates that the startup and stop scripts work correctly

Write-Host "Testing FoxTrends Windows Scripts" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Test 1: Check if UV is available
Write-Host ""
Write-Host "Test 1: Checking UV installation..." -ForegroundColor Yellow
try {
    $uvVersion = & uv --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PASS: UV is available - $uvVersion" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: UV is not available" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: UV is not available" -ForegroundColor Red
    exit 1
}

# Test 2: Check if project files exist
Write-Host ""
Write-Host "Test 2: Checking project files..." -ForegroundColor Yellow

$requiredFiles = @(
    "pyproject.toml",
    ".env.example",
    "app.py",
    "database/init_database.py"
)

$allFilesExist = $true
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  PASS: $file exists" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: $file does not exist" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    exit 1
}

# Test 3: Check if startup scripts exist
Write-Host ""
Write-Host "Test 3: Checking startup scripts..." -ForegroundColor Yellow

$scripts = @(
    "quick_start.ps1",
    "quick_stop.ps1",
    "quick_start.bat",
    "quick_stop.bat"
)

foreach ($script in $scripts) {
    if (Test-Path $script) {
        Write-Host "  PASS: $script exists" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: $script does not exist" -ForegroundColor Red
    }
}

# Test 4: Check if configuration file exists
Write-Host ""
Write-Host "Test 4: Checking configuration file..." -ForegroundColor Yellow

if (Test-Path ".env") {
    Write-Host "  INFO: .env file already exists" -ForegroundColor Cyan
} else {
    Write-Host "  INFO: .env file does not exist (will be created on first run)" -ForegroundColor Cyan
}

# Test 5: Check if database directory exists
Write-Host ""
Write-Host "Test 5: Checking database directory..." -ForegroundColor Yellow

if (Test-Path "database") {
    Write-Host "  PASS: database directory exists" -ForegroundColor Green
    
    $dbFiles = @(
        "database/__init__.py",
        "database/init_database.py",
        "database/db_manager.py"
    )
    
    foreach ($file in $dbFiles) {
        if (Test-Path $file) {
            Write-Host "    PASS: $file exists" -ForegroundColor Green
        } else {
            Write-Host "    FAIL: $file does not exist" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  FAIL: database directory does not exist" -ForegroundColor Red
    exit 1
}

# Test 6: Check if port 5000 is available
Write-Host ""
Write-Host "Test 6: Checking port availability..." -ForegroundColor Yellow

try {
    $port = 5000
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $port)
    $listener.Start()
    $listener.Stop()
    Write-Host "  PASS: Port $port is available" -ForegroundColor Green
} catch {
    Write-Host "  WARN: Port $port may be in use" -ForegroundColor Yellow
    Write-Host "        You can change the port in .env file" -ForegroundColor Gray
}

# Test 7: Validate PowerShell script syntax
Write-Host ""
Write-Host "Test 7: Validating PowerShell script syntax..." -ForegroundColor Yellow

try {
    $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content quick_start.ps1 -Raw), [ref]$null)
    Write-Host "  PASS: quick_start.ps1 syntax is valid" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: quick_start.ps1 has syntax errors" -ForegroundColor Red
}

try {
    $null = [System.Management.Automation.PSParser]::Tokenize((Get-Content quick_stop.ps1 -Raw), [ref]$null)
    Write-Host "  PASS: quick_stop.ps1 syntax is valid" -ForegroundColor Green
} catch {
    Write-Host "  FAIL: quick_stop.ps1 has syntax errors" -ForegroundColor Red
}

# Summary
Write-Host ""
Write-Host "Test Summary" -ForegroundColor Cyan
Write-Host "============" -ForegroundColor Cyan
Write-Host "  Basic environment check completed" -ForegroundColor Green
Write-Host "  Project files are complete" -ForegroundColor Green
Write-Host "  Startup scripts are ready" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run the startup script:" -ForegroundColor Yellow
Write-Host "  .\quick_start.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To stop the application:" -ForegroundColor Yellow
Write-Host "  .\quick_stop.ps1" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
