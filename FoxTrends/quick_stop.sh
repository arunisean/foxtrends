#!/bin/bash
# FoxTrends 快速停止脚本

echo "🛑 FoxTrends 快速停止"
echo "===================="

# 查找并停止 FoxTrends 主进程
echo ""
echo "🔍 查找 FoxTrends 进程..."

# 查找 app.py 进程
APP_PIDS=$(ps aux | grep "[u]v run python app.py" | awk '{print $2}')
PYTHON_PIDS=$(ps aux | grep "[p]ython.*app.py" | awk '{print $2}')

# 合并所有进程ID
ALL_PIDS="$APP_PIDS $PYTHON_PIDS"

if [ -z "$ALL_PIDS" ]; then
    echo "ℹ️  未找到运行中的 FoxTrends 进程"
else
    echo "📋 找到以下进程:"
    for PID in $ALL_PIDS; do
        ps -p $PID -o pid,command | tail -n 1
    done
    
    echo ""
    echo "🔪 停止进程..."
    for PID in $ALL_PIDS; do
        kill $PID 2>/dev/null && echo "  ✅ 已停止进程 $PID" || echo "  ⚠️  进程 $PID 可能已停止"
    done
    
    # 等待进程结束
    sleep 2
    
    # 检查是否还有残留进程
    REMAINING=$(ps aux | grep -E "[u]v run python app.py|[p]ython.*app.py" | wc -l)
    if [ $REMAINING -gt 0 ]; then
        echo ""
        echo "⚠️  发现残留进程，使用强制停止..."
        for PID in $ALL_PIDS; do
            kill -9 $PID 2>/dev/null
        done
        echo "  ✅ 强制停止完成"
    fi
fi

# 查找并停止监控任务相关的后台进程
echo ""
echo "🔍 查找监控任务进程..."
MONITOR_PIDS=$(ps aux | grep "[p]ython.*monitoring" | awk '{print $2}')

if [ -z "$MONITOR_PIDS" ]; then
    echo "ℹ️  未找到监控任务进程"
else
    echo "📋 找到监控任务进程:"
    for PID in $MONITOR_PIDS; do
        ps -p $PID -o pid,command | tail -n 1
    done
    
    echo ""
    echo "🔪 停止监控任务..."
    for PID in $MONITOR_PIDS; do
        kill $PID 2>/dev/null && echo "  ✅ 已停止进程 $PID" || echo "  ⚠️  进程 $PID 可能已停止"
    done
fi

# 清理可能的僵尸进程
echo ""
echo "🧹 清理僵尸进程..."
pkill -f "uv run python app.py" 2>/dev/null
pkill -f "python.*app.py" 2>/dev/null

# 显示最终状态
echo ""
echo "✅ FoxTrends 已停止"
echo ""
echo "提示:"
echo "  - 如需重新启动: ./quick_start.sh"
echo "  - 如需清理数据: uv run python scripts/clean_test_data.py"
echo "  - 如需查看日志: ls -lh logs/"
echo ""
