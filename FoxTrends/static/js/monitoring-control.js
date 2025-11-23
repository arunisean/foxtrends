/**
 * 监控控制和实时更新功能
 */

// WebSocket连接
let socket = null;

// 初始化WebSocket连接
function initWebSocket() {
    socket = io();
    
    // 连接成功
    socket.on('connect', function() {
        console.log('WebSocket连接成功');
        updateConnectionStatus(true);
    });
    
    // 连接断开
    socket.on('disconnect', function() {
        console.log('WebSocket连接断开');
        updateConnectionStatus(false);
    });
    
    // 监听社区更新事件
    socket.on('community_update', function(data) {
        console.log('收到社区更新:', data);
        updateCommunityCard(data);
    });
    
    // 监听新信号事件
    socket.on('new_signal', function(data) {
        console.log('收到新信号:', data);
        showNewSignalNotification(data);
        // 刷新需求列表
        if (typeof loadDemands === 'function') {
            loadDemands();
        }
    });
    
    // 监听监控状态变化
    socket.on('monitoring_status', function(data) {
        console.log('监控状态变化:', data);
        updateMonitoringStatus(data);
    });
    
    // 监听错误事件
    socket.on('error_occurred', function(data) {
        console.log('监控错误:', data);
        showErrorNotification(data);
        updateCommunityCard(data);
    });
}

// 更新连接状态显示
function updateConnectionStatus(connected) {
    const indicator = document.querySelector('.ws-status-indicator');
    const text = document.querySelector('.ws-status-text');
    
    if (indicator && text) {
        if (connected) {
            indicator.style.backgroundColor = '#10b981';
            text.textContent = '实时连接';
        } else {
            indicator.style.backgroundColor = '#ef4444';
            text.textContent = '连接断开';
        }
    }
}

// 更新社区卡片
function updateCommunityCard(data) {
    const card = document.querySelector(`[data-community-id="${data.community_id}"]`);
    if (!card) return;
    
    // 更新信号总数
    if (data.total_signals !== undefined) {
        const signalCount = card.querySelector('.signal-count');
        if (signalCount) {
            signalCount.textContent = data.total_signals;
        }
    }
    
    // 更新最后采集时间
    if (data.last_collection_time) {
        const lastCollection = card.querySelector('.last-collection-time');
        if (lastCollection) {
            const date = new Date(data.last_collection_time);
            lastCollection.textContent = formatDateTime(date);
        }
    }
    
    // 更新错误计数
    if (data.error_count !== undefined) {
        const errorCount = card.querySelector('.error-count');
        if (errorCount) {
            errorCount.textContent = data.error_count;
            errorCount.style.display = data.error_count > 0 ? 'inline' : 'none';
        }
    }
}

// 更新监控状态
function updateMonitoringStatus(data) {
    const card = document.querySelector(`[data-community-id="${data.community_id}"]`);
    if (!card) return;
    
    const statusBadge = card.querySelector('.monitoring-status-badge');
    if (statusBadge) {
        statusBadge.textContent = getStatusText(data.status);
        statusBadge.className = `monitoring-status-badge status-${data.status}`;
    }
    
    // 更新按钮状态
    updateControlButtons(card, data.status);
}

// 更新控制按钮状态
function updateControlButtons(card, status) {
    const startBtn = card.querySelector('.start-monitoring-btn');
    const stopBtn = card.querySelector('.stop-monitoring-btn');
    
    if (startBtn && stopBtn) {
        if (status === 'running' || status === 'collecting') {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
    }
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'not_started': '未开始',
        'running': '运行中',
        'collecting': '采集中',
        'idle': '空闲',
        'paused': '已暂停',
        'stopped': '已停止',
        'error': '错误'
    };
    return statusMap[status] || status;
}

// 显示新信号通知
function showNewSignalNotification(data) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-success';
    notification.innerHTML = `
        <strong>新需求信号</strong><br>
        ${data.community_name}: ${data.title.substring(0, 50)}...
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 显示错误通知
function showErrorNotification(data) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-error';
    notification.innerHTML = `
        <strong>监控错误</strong><br>
        社区ID ${data.community_id}: ${data.error}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// 启动单个社区监控
async function startCommunityMonitoring(communityId) {
    try {
        const response = await fetch(`/api/communities/${communityId}/monitoring`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action: 'start' })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(result.message);
        } else {
            showErrorMessage(result.message);
        }
        
        return result;
    } catch (error) {
        console.error('启动监控失败:', error);
        showErrorMessage('启动监控失败: ' + error.message);
        return { success: false };
    }
}

// 停止单个社区监控
async function stopCommunityMonitoring(communityId) {
    try {
        const response = await fetch(`/api/communities/${communityId}/monitoring`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action: 'stop' })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(result.message);
        } else {
            showErrorMessage(result.message);
        }
        
        return result;
    } catch (error) {
        console.error('停止监控失败:', error);
        showErrorMessage('停止监控失败: ' + error.message);
        return { success: false };
    }
}

// 启动所有监控
async function startAllMonitoring() {
    try {
        const response = await fetch('/api/monitoring/start-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(result.message);
            // 刷新社区列表
            if (typeof loadCommunities === 'function') {
                setTimeout(loadCommunities, 1000);
            }
        } else {
            showErrorMessage(result.message);
        }
        
        return result;
    } catch (error) {
        console.error('批量启动监控失败:', error);
        showErrorMessage('批量启动监控失败: ' + error.message);
        return { success: false };
    }
}

// 停止所有监控
async function stopAllMonitoring() {
    try {
        const response = await fetch('/api/monitoring/stop-all', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage(result.message);
            // 刷新社区列表
            if (typeof loadCommunities === 'function') {
                setTimeout(loadCommunities, 1000);
            }
        } else {
            showErrorMessage(result.message);
        }
        
        return result;
    } catch (error) {
        console.error('批量停止监控失败:', error);
        showErrorMessage('批量停止监控失败: ' + error.message);
        return { success: false };
    }
}

// 显示成功消息
function showSuccessMessage(message) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-success';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// 显示错误消息
function showErrorMessage(message) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-error';
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// 格式化日期时间
function formatDateTime(date) {
    const now = new Date();
    const diff = now - date;
    
    // 小于1分钟
    if (diff < 60000) {
        return '刚刚';
    }
    
    // 小于1小时
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes}分钟前`;
    }
    
    // 小于24小时
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours}小时前`;
    }
    
    // 否则显示完整日期
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化WebSocket
    initWebSocket();
    
    // 绑定全局控制按钮
    const startAllBtn = document.getElementById('start-all-monitoring-btn');
    const stopAllBtn = document.getElementById('stop-all-monitoring-btn');
    
    if (startAllBtn) {
        startAllBtn.addEventListener('click', startAllMonitoring);
    }
    
    if (stopAllBtn) {
        stopAllBtn.addEventListener('click', stopAllMonitoring);
    }
});
