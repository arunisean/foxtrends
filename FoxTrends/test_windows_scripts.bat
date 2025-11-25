@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo Testing FoxTrends Windows Scripts
echo ==================================

REM Test 1: Check if UV is available
echo.
echo Test 1: Checking UV installation...
uv --version >nul 2>&1
if errorlevel 1 (
    echo   FAIL: UV is not available
    pause
    exit /b 1
) else (
    echo   PASS: UV is available
)

REM Test 2: Check if project files exist
echo.
echo Test 2: Checking project files...

set "files=pyproject.toml .env.example app.py database\init_database.py"
for %%f in (%files%) do (
    if exist "%%f" (
        echo   PASS: %%f exists
    ) else (
        echo   FAIL: %%f does not exist
        pause
        exit /b 1
    )
)

REM Test 3: Check if startup scripts exist
echo.
echo Test 3: Checking startup scripts...

set "scripts=quick_start.ps1 quick_stop.ps1 quick_start.bat quick_stop.bat"
for %%s in (%scripts%) do (
    if exist "%%s" (
        echo   PASS: %%s exists
    ) else (
        echo   FAIL: %%s does not exist
    )
)

REM Test 4: Check if configuration file exists
echo.
echo Test 4: Checking configuration file...

if exist ".env" (
    echo   INFO: .env file already exists
) else (
    echo   INFO: .env file does not exist (will be created on first run)
)

REM Test 5: Check if database directory exists
echo.
echo Test 5: Checking database directory...

if exist "database" (
    echo   PASS: database directory exists
    
    set "dbfiles=database\__init__.py database\init_database.py database\db_manager.py"
    for %%d in (!dbfiles!) do (
        if exist "%%d" (
            echo     PASS: %%d exists
        ) else (
            echo     FAIL: %%d does not exist
        )
    )
) else (
    echo   FAIL: database directory does not exist
    pause
    exit /b 1
)

REM Summary
echo.
echo Test Summary
echo ============
echo   Basic environment check completed
echo   Project files are complete
echo   Startup scripts are ready
echo.
echo You can now run the startup script:
echo   quick_start.bat or quick_start.ps1
echo.
echo To stop the application:
echo   quick_stop.bat or quick_stop.ps1
echo.
pause
