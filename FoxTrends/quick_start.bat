@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo 🚀 FoxTrends 快速启动
echo ====================

REM 检查 UV 是否安装
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ UV 未安装，请先安装 UV
    echo 请访问: https://docs.astral.sh/uv/getting-started/installation/
    echo 或运行: powershell -c "irm https://astral.sh/uv/install.ps1 ^| iex"
    pause
    exit /b 1
)

REM 同步依赖
echo.
echo 📦 安装依赖...
uv sync
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist ".env" (
    echo.
    echo 📝 创建配置文件...
    copy ".env.example" ".env" >nul
    echo ✅ 已创建 .env 文件（使用默认 SQLite 配置）
)

REM 初始化数据库
echo.
echo 🗄️  初始化数据库...
uv run python database/init_database.py
if errorlevel 1 (
    echo ❌ 数据库初始化失败
    pause
    exit /b 1
)

REM 启动应用
echo.
echo 🎉 启动 FoxTrends...
echo.
echo 访问 Dashboard: http://localhost:5000/
echo.
echo 按 Ctrl+C 停止应用
echo.
uv run python app.py
