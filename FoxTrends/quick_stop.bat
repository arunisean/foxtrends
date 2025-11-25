@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🛑 FoxTrends 快速停止
echo ====================

REM 查找并停止 FoxTrends 主进程
echo.
echo 🔍 查找 FoxTrends 进程...

REM 查找 app.py 进程
set "found_processes=0"

REM 使用 wmic 查找进程
for /f "tokens=2" %%i in ('wmic process where "CommandLine like '%%app.py%%' and CommandLine like '%%python%%'" get ProcessId /format:value 2^>nul ^| find "ProcessId"') do (
    set "pid=%%i"
    if not "!pid!"=="" (
        set /a found_processes+=1
        echo 📋 找到进程 PID: !pid!
        
        REM 获取进程详细信息
        for /f "tokens=*" %%j in ('wmic process where "ProcessId=!pid!" get CommandLine /format:value 2^>nul ^| find "CommandLine"') do (
            echo     %%j
        )
        
        REM 停止进程
        taskkill /PID !pid! /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✅ 已停止进程 !pid!
        ) else (
            echo   ⚠️  进程 !pid! 可能已停止
        )
    )
)

REM 查找 uv run 相关进程
for /f "tokens=2" %%i in ('wmic process where "CommandLine like '%%uv run%%' and CommandLine like '%%app.py%%'" get ProcessId /format:value 2^>nul ^| find "ProcessId"') do (
    set "pid=%%i"
    if not "!pid!"=="" (
        set /a found_processes+=1
        echo 📋 找到 UV 进程 PID: !pid!
        
        REM 停止进程
        taskkill /PID !pid! /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✅ 已停止进程 !pid!
        ) else (
            echo   ⚠️  进程 !pid! 可能已停止
        )
    )
)

if !found_processes! equ 0 (
    echo ℹ️  未找到运行中的 FoxTrends 进程
)

REM 查找并停止监控任务相关的后台进程
echo.
echo 🔍 查找监控任务进程...

set "monitor_found=0"
for /f "tokens=2" %%i in ('wmic process where "CommandLine like '%%monitoring%%' and CommandLine like '%%python%%'" get ProcessId /format:value 2^>nul ^| find "ProcessId"') do (
    set "pid=%%i"
    if not "!pid!"=="" (
        set /a monitor_found+=1
        echo 📋 找到监控任务进程 PID: !pid!
        
        REM 停止进程
        taskkill /PID !pid! /F >nul 2>&1
        if !errorlevel! equ 0 (
            echo   ✅ 已停止进程 !pid!
        ) else (
            echo   ⚠️  进程 !pid! 可能已停止
        )
    )
)

if !monitor_found! equ 0 (
    echo ℹ️  未找到监控任务进程
)

REM 清理可能的残留进程
echo.
echo 🧹 清理残留进程...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq FoxTrends*" >nul 2>&1
taskkill /F /IM python.exe /FI "COMMANDLINE eq *app.py*" >nul 2>&1

REM 等待进程结束
timeout /t 2 /nobreak >nul

REM 显示最终状态
echo.
echo ✅ FoxTrends 已停止
echo.
echo 提示:
echo   - 如需重新启动: quick_start.bat
echo   - 如需清理数据: uv run python scripts/clean_test_data.py
echo   - 如需查看日志: dir logs\
echo.
pause
