# FoxTrends Quick Stop Script (PowerShell)
# Set console encoding to UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "FoxTrends Quick Stop" -ForegroundColor Red
Write-Host "====================" -ForegroundColor Red

# Find and stop FoxTrends main processes
Write-Host ""
Write-Host "Searching for FoxTrends processes..." -ForegroundColor Cyan

$foundProcesses = @()

# Find app.py related processes
try {
    $processes = Get-WmiObject Win32_Process -ErrorAction SilentlyContinue | Where-Object { 
        $_.CommandLine -like "*app.py*" -and 
        ($_.CommandLine -like "*python*" -or $_.CommandLine -like "*uv run*")
    }
    
    foreach ($process in $processes) {
        $foundProcesses += $process
        Write-Host "Found process PID: $($process.ProcessId)" -ForegroundColor Yellow
        Write-Host "  Command: $($process.CommandLine)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "Error searching for processes: $_" -ForegroundColor Yellow
}

if ($foundProcesses.Count -eq 0) {
    Write-Host "No running FoxTrends processes found" -ForegroundColor Gray
}
else {
    Write-Host ""
    Write-Host "Stopping processes..." -ForegroundColor Red
    
    foreach ($process in $foundProcesses) {
        try {
            Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
            Write-Host "  Stopped process $($process.ProcessId)" -ForegroundColor Green
        }
        catch {
            Write-Host "  Process $($process.ProcessId) may already be stopped" -ForegroundColor Yellow
        }
    }
    
    # Wait for processes to end
    Start-Sleep -Seconds 2
    
    # Check for remaining processes
    try {
        $remaining = Get-WmiObject Win32_Process -ErrorAction SilentlyContinue | Where-Object { 
            $_.CommandLine -like "*app.py*" -and 
            ($_.CommandLine -like "*python*" -or $_.CommandLine -like "*uv run*")
        }
        
        if ($remaining.Count -gt 0) {
            Write-Host ""
            Write-Host "Found remaining processes, forcing stop..." -ForegroundColor Yellow
            foreach ($process in $remaining) {
                try {
                    Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
                    Write-Host "  Force stopped process $($process.ProcessId)" -ForegroundColor Green
                }
                catch {
                    Write-Host "  Unable to stop process $($process.ProcessId)" -ForegroundColor Red
                }
            }
        }
    }
    catch {
        Write-Host "Error checking for remaining processes: $_" -ForegroundColor Yellow
    }
}

# Find and stop monitoring task processes
Write-Host ""
Write-Host "Searching for monitoring task processes..." -ForegroundColor Cyan

try {
    $monitorProcesses = Get-WmiObject Win32_Process -ErrorAction SilentlyContinue | Where-Object { 
        $_.CommandLine -like "*monitoring*" -and $_.CommandLine -like "*python*"
    }
    
    if ($monitorProcesses.Count -eq 0) {
        Write-Host "No monitoring task processes found" -ForegroundColor Gray
    }
    else {
        Write-Host "Found monitoring task processes:" -ForegroundColor Yellow
        foreach ($process in $monitorProcesses) {
            Write-Host "  PID: $($process.ProcessId) - $($process.CommandLine)" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "Stopping monitoring tasks..." -ForegroundColor Red
        foreach ($process in $monitorProcesses) {
            try {
                Stop-Process -Id $process.ProcessId -Force -ErrorAction Stop
                Write-Host "  Stopped process $($process.ProcessId)" -ForegroundColor Green
            }
            catch {
                Write-Host "  Process $($process.ProcessId) may already be stopped" -ForegroundColor Yellow
            }
        }
    }
}
catch {
    Write-Host "Error searching for monitoring processes: $_" -ForegroundColor Yellow
}

# Clean up zombie processes
Write-Host ""
Write-Host "Cleaning up zombie processes..." -ForegroundColor Cyan

try {
    # Clean all potentially related processes
    Get-Process -ErrorAction SilentlyContinue | Where-Object { 
        $_.ProcessName -eq "python" -and 
        $_.MainWindowTitle -like "*FoxTrends*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "Cleanup completed" -ForegroundColor Green
}
catch {
    Write-Host "Warning during cleanup: $_" -ForegroundColor Yellow
}

# Display final status
Write-Host ""
Write-Host "FoxTrends has been stopped" -ForegroundColor Green
Write-Host ""
Write-Host "Tips:" -ForegroundColor Cyan
Write-Host "  - To restart: .\quick_start.ps1" -ForegroundColor Gray
Write-Host "  - To clean data: uv run python scripts/clean_test_data.py" -ForegroundColor Gray
Write-Host "  - To view logs: Get-ChildItem logs\" -ForegroundColor Gray
Write-Host ""

# Pause in interactive mode
if ($Host.Name -eq "ConsoleHost") {
    Read-Host "Press Enter to exit"
}
