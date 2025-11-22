#!/bin/bash
# FoxTrends 快速启动脚本

echo "🚀 FoxTrends 快速启动"
echo "===================="

# 检查 UV 是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ UV 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ UV 安装完成"
fi

# 同步依赖
echo ""
echo "📦 安装依赖..."
uv sync

# 检查 .env 文件
if [ ! -f .env ]; then
    echo ""
    echo "📝 创建配置文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件（使用默认 SQLite 配置）"
fi

# 初始化数据库
echo ""
echo "🗄️  初始化数据库..."
uv run python database/init_database.py

# 启动应用
echo ""
echo "🎉 启动 FoxTrends..."
echo ""
echo "访问 Dashboard: http://localhost:5000/dashboard"
echo ""
uv run python app.py
