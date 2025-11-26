/**
 * Live Discussion Indicator
 * 
 * 显示活跃讨论的实时指示器
 */

class LiveDiscussionIndicator {
    constructor() {
        this.activeSessions = new Set();
        this.wsClient = null;
        this.updateInterval = null;
    }

    /**
     * 初始化
     */
    init() {
        // 连接 WebSocket 监听活跃会话
        this.wsClient = io('/forum-visualization', {
            transports: ['websocket', 'polling']
        });
        
        this.wsClient.on('connect', () => {
            console.log('[LiveIndicator] Connected');
        });
        
        // 监听所有会话的状态更新
        this.wsClient.on('agent_status_update', (data) => {
            if (data.status === 'analyzing' || data.status === 'speaking') {
                this.activeSessions.add(data.session_id);
                this.updateIndicators();
            }
        });
        
        this.wsClient.on('consensus_reached', (data) => {
            this.activeSessions.delete(data.session_id);
            this.updateIndicators();
        });
        
        // 定期更新活跃会话列表
        this.updateInterval = setInterval(() => {
            this.fetchActiveSessions();
        }, 30000); // 每30秒更新一次
        
        // 初始加载
        this.fetchActiveSessions();
    }

    /**
     * 获取活跃会话
     */
    async fetchActiveSessions() {
        try {
            const response = await fetch('/api/forum/active-sessions');
            const data = await response.json();
            
            if (data.success) {
                this.activeSessions = new Set(data.sessions.map(s => s.id));
                this.updateIndicators();
            }
        } catch (error) {
            console.error('[LiveIndicator] Failed to fetch active sessions:', error);
        }
    }

    /**
     * 更新所有指示器
     */
    updateIndicators() {
        // 更新需求卡片上的指示器
        document.querySelectorAll('[data-demand-id]').forEach(card => {
            const demandId = card.dataset.demandId;
            this.updateCardIndicator(card, demandId);
        });
        
        // 更新总计数
        this.updateTotalCount();
    }

    /**
     * 更新单个卡片的指示器
     */
    updateCardIndicator(card, demandId) {
        // 检查该需求是否有活跃讨论
        const hasActiveDiscussion = Array.from(this.activeSessions).some(sessionId => {
            // 这里需要根据实际情况判断 session 是否属于该 demand
            // 简化实现：假设 session 数据中包含 demand_id
            return true; // 实际应该查询 session 的 demand_id
        });
        
        let indicator = card.querySelector('.live-discussion-badge');
        
        if (hasActiveDiscussion) {
            if (!indicator) {
                indicator = this.createIndicator();
                card.appendChild(indicator);
            }
        } else {
            if (indicator) {
                indicator.remove();
            }
        }
    }

    /**
     * 创建指示器元素
     */
    createIndicator() {
        const badge = document.createElement('div');
        badge.className = 'live-discussion-badge';
        badge.innerHTML = `
            <span class="live-icon">🔴</span>
            <span class="live-text">Live Discussion</span>
        `;
        return badge;
    }

    /**
     * 更新总计数
     */
    updateTotalCount() {
        const count = this.activeSessions.size;
        const countElement = document.getElementById('live-discussion-count');
        
        if (countElement) {
            countElement.textContent = count;
            countElement.style.display = count > 0 ? 'inline-block' : 'none';
        }
    }

    /**
     * 清理
     */
    destroy() {
        if (this.wsClient) {
            this.wsClient.disconnect();
        }
        
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// 导出到全局
window.LiveDiscussionIndicator = LiveDiscussionIndicator;

// 自动初始化（如果在 dashboard 页面）
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (document.querySelector('.dashboard-container')) {
            const indicator = new LiveDiscussionIndicator();
            indicator.init();
        }
    });
} else {
    if (document.querySelector('.dashboard-container')) {
        const indicator = new LiveDiscussionIndicator();
        indicator.init();
    }
}
