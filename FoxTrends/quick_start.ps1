# FoxTrends Quick Start Script (PowerShell)
# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "FoxTrends Quick Start" -ForegroundColor Green
Write-Host "====================" -ForegroundColor Green

# Check if UV is installed
Write-Host ""
Write-Host "Checking UV installation..." -ForegroundColor Cyan

$uvInstalled = $false
try {
    $uvCheck = & uv --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $uvInstalled = $true
        Write-Host "UV is installed: $uvCheck" -ForegroundColor Green
    }
}
catch {
    $uvInstalled = $false
}

if (-not $uvInstalled) {
    Write-Host "UV not installed, installing..." -ForegroundColor Yellow
    try {
        Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        Write-Host "UV installation completed" -ForegroundColor Green
    }
    catch {
        Write-Host "UV installation failed, please install manually" -ForegroundColor Red
        Write-Host "Visit: https://docs.astral.sh/uv/getting-started/installation/" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Sync dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Cyan
& uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "Dependency installation failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Dependencies installed successfully" -ForegroundColor Green

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating configuration file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host ".env file created (using default SQLite configuration)" -ForegroundColor Green
}

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Cyan
& uv run python database/init_database.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Database initialization failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Database initialized successfully" -ForegroundColor Green

# Start application
Write-Host ""
Write-Host "Starting FoxTrends..." -ForegroundColor Green
Write-Host ""
Write-Host "Access Dashboard: http://localhost:5000/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

& uv run python app.py
