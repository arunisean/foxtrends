/**
 * 资源监控显示模块
 * 实时显示监控任务的资源使用情况
 */

class ResourceMonitor {
    constructor() {
        this.updateInterval = 2000; // 2秒更新一次
        this.intervalId = null;
    }

    /**
     * 启动资源监控
     */
    start() {
        this.update();
        this.intervalId = setInterval(() => this.update(), this.updateInterval);
    }

    /**
     * 停止资源监控
     */
    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * 更新资源监控数据
     */
    async update() {
        try {
            const response = await fetch('/api/monitoring/status');
            const data = await response.json();

            if (data.success) {
                this.updateResourceDisplay(data);
            }
        } catch (error) {
            console.error('更新资源监控失败:', error);
        }
    }

    /**
     * 更新资源显示
     */
    updateResourceDisplay(data) {
        const tasks = data.tasks || [];

        tasks.forEach(task => {
            const cardEl = document.querySelector(`[data-community-id="${task.community_id}"]`);
            if (cardEl) {
                this.updateTaskCard(cardEl, task);
            }
        });
    }

    /**
     * 更新单个任务卡片
     */
    updateTaskCard(cardEl, task) {
        // 更新或创建资源进度条
        let resourceBar = cardEl.querySelector('.resource-progress-bar');
        if (!resourceBar) {
            resourceBar = this.createResourceBar();
            const statsEl = cardEl.querySelector('.community-stats');
            if (statsEl) {
                statsEl.insertAdjacentElement('afterend', resourceBar);
            }
        }

        // 更新进度数据
        this.updateResourceBar(resourceBar, task);
    }

    /**
     * 创建资源进度条
     */
    createResourceBar() {
        const container = document.createElement('div');
        container.className = 'resource-progress-bar';
        container.innerHTML = `
            <div class="resource-section">
                <div class="resource-label">
                    <span class="resource-icon">🔄</span>
                    <span class="resource-name">采集周期</span>
                    <span class="resource-value">0/0</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill cycles-fill" style="width: 0%"></div>
                </div>
            </div>
            <div class="resource-section">
                <div class="resource-label">
                    <span class="resource-icon">📊</span>
                    <span class="resource-name">信号数量</span>
                    <span class="resource-value">0/0</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill signals-fill" style="width: 0%"></div>
                </div>
            </div>
            <div class="resource-section">
                <div class="resource-label">
                    <span class="resource-icon">🤖</span>
                    <span class="resource-name">Agent分析</span>
                    <span class="resource-status">待启动</span>
                </div>
            </div>
        `;
        return container;
    }

    /**
     * 更新资源进度条数据
     */
    updateResourceBar(resourceBar, task) {
        const {
            collection_cycles = 0,
            max_collection_cycles = 100,
            signals_collected = 0,
            max_signals_per_session = 500,
            agent_analysis_enabled = false,
            agent_analysis_count = 0,
            status = 'idle'
        } = task;

        // 更新周期进度
        const cyclesPercent = max_collection_cycles > 0 
            ? Math.min(100, (collection_cycles / max_collection_cycles) * 100)
            : 0;
        
        const cyclesFill = resourceBar.querySelector('.cycles-fill');
        const cyclesValue = resourceBar.querySelector('.resource-section:nth-child(1) .resource-value');
        
        if (cyclesFill && cyclesValue) {
            cyclesFill.style.width = `${cyclesPercent}%`;
            cyclesFill.className = `progress-fill cycles-fill ${this.getProgressClass(cyclesPercent)}`;
            
            if (max_collection_cycles > 0) {
                cyclesValue.textContent = `${collection_cycles}/${max_collection_cycles}`;
            } else {
                cyclesValue.textContent = `${collection_cycles}/∞`;
            }
        }

        // 更新信号进度
        const signalsPercent = max_signals_per_session > 0
            ? Math.min(100, (signals_collected / max_signals_per_session) * 100)
            : 0;
        
        const signalsFill = resourceBar.querySelector('.signals-fill');
        const signalsValue = resourceBar.querySelector('.resource-section:nth-child(2) .resource-value');
        
        if (signalsFill && signalsValue) {
            signalsFill.style.width = `${signalsPercent}%`;
            signalsFill.className = `progress-fill signals-fill ${this.getProgressClass(signalsPercent)}`;
            
            if (max_signals_per_session > 0) {
                signalsValue.textContent = `${signals_collected}/${max_signals_per_session}`;
            } else {
                signalsValue.textContent = `${signals_collected}/∞`;
            }
        }

        // 更新Agent分析状态
        const agentStatus = resourceBar.querySelector('.resource-status');
        if (agentStatus) {
            if (!agent_analysis_enabled) {
                agentStatus.textContent = '已禁用';
                agentStatus.className = 'resource-status status-disabled';
            } else if (status === 'running') {
                agentStatus.textContent = `已分析 ${agent_analysis_count} 个`;
                agentStatus.className = 'resource-status status-active';
            } else {
                agentStatus.textContent = '待启动';
                agentStatus.className = 'resource-status status-idle';
            }
        }
    }

    /**
     * 根据进度百分比获取样式类
     */
    getProgressClass(percent) {
        if (percent >= 90) return 'progress-danger';
        if (percent >= 70) return 'progress-warning';
        return 'progress-normal';
    }
}

// 创建全局实例
window.resourceMonitor = new ResourceMonitor();

// 页面加载完成后自动启动
document.addEventListener('DOMContentLoaded', () => {
    window.resourceMonitor.start();
});

// 页面卸载时停止
window.addEventListener('beforeunload', () => {
    window.resourceMonitor.stop();
});
