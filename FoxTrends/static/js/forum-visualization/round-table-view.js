/**
 * Round Table View Component
 * 
 * 圆桌布局可视化组件
 */

class RoundTableView {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container ${containerId} not found`);
        }
        
        this.agents = [];
        this.forumHost = null;
        this.currentStage = 0;
        this.currentPhase = 'idle';
        this.interactionLines = null;
        
        this._init();
    }

    /**
     * 初始化组件
     */
    _init() {
        this.container.innerHTML = `
            <div class="round-table-container" id="round-table-inner">
                <!-- 阶段指示器 -->
                <div class="stage-indicator">
                    <div class="stage-label">准备中...</div>
                    <div class="stage-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="progress-text">0%</div>
                    </div>
                </div>
                
                <!-- 圆桌布局 -->
                <div class="round-table">
                    <!-- Forum Host (中心) -->
                    <div class="agent-avatar forum-host" data-agent-id="forum_host">
                        <div class="avatar-circle">
                            <div class="avatar-icon">🎙️</div>
                            <div class="status-indicator"></div>
                        </div>
                        <div class="avatar-name">Forum Host</div>
                        <div class="avatar-status">等待中</div>
                    </div>
                    
                    <!-- Community Insight Agent (顶部) -->
                    <div class="agent-avatar agent-top" data-agent-id="community_insight">
                        <div class="avatar-circle">
                            <div class="avatar-icon">📊</div>
                            <div class="status-indicator"></div>
                        </div>
                        <div class="avatar-name">Community Insight</div>
                        <div class="avatar-status">等待中</div>
                    </div>
                    
                    <!-- Content Analysis Agent (右侧) -->
                    <div class="agent-avatar agent-right" data-agent-id="content_analysis">
                        <div class="avatar-circle">
                            <div class="avatar-icon">🔍</div>
                            <div class="status-indicator"></div>
                        </div>
                        <div class="avatar-name">Content Analysis</div>
                        <div class="avatar-status">等待中</div>
                    </div>
                    
                    <!-- Trend Discovery Agent (左侧) -->
                    <div class="agent-avatar agent-left" data-agent-id="trend_discovery">
                        <div class="avatar-circle">
                            <div class="avatar-icon">📈</div>
                            <div class="status-indicator"></div>
                        </div>
                        <div class="avatar-name">Trend Discovery</div>
                        <div class="avatar-status">等待中</div>
                    </div>
                </div>
                
                <!-- 共识指示器 -->
                <div class="consensus-meter">
                    <div class="consensus-label">共识度</div>
                    <div class="consensus-bar">
                        <div class="consensus-fill" style="width: 0%"></div>
                    </div>
                    <div class="consensus-text">0%</div>
                </div>
            </div>
        `;
        
        // 初始化交互线组件
        try {
            if (typeof InteractionLines !== 'undefined') {
                this.interactionLines = new InteractionLines('round-table-inner');
            }
        } catch (error) {
            console.warn('InteractionLines not available:', error);
        }
    }

    /**
     * 更新 Agent 状态
     */
    updateAgentStatus(agentId, status, stage = null) {
        const agentElement = this.container.querySelector(`[data-agent-id="${agentId}"]`);
        if (!agentElement) {
            console.warn(`Agent ${agentId} not found`);
            return;
        }

        // 移除所有状态类
        agentElement.classList.remove('idle', 'waiting', 'analyzing', 'speaking', 'complete', 'error');
        
        // 添加新状态类
        agentElement.classList.add(status);
        
        // 更新状态文本
        const statusText = this._getStatusText(status, stage);
        const statusElement = agentElement.querySelector('.avatar-status');
        if (statusElement) {
            statusElement.textContent = statusText;
        }
        
        // 更新状态指示器
        const indicator = agentElement.querySelector('.status-indicator');
        if (indicator) {
            indicator.className = 'status-indicator status-' + status;
        }
    }

    /**
     * 获取状态文本
     */
    _getStatusText(status, stage) {
        const statusMap = {
            'idle': '空闲',
            'waiting': stage ? `等待阶段 ${stage}` : '等待中',
            'analyzing': '分析中...',
            'speaking': '发言中...',
            'complete': '已完成',
            'error': '错误'
        };
        return statusMap[status] || status;
    }

    /**
     * 更新阶段
     */
    updateStage(stage, stageName) {
        this.currentStage = stage;
        
        const stageLabel = this.container.querySelector('.stage-label');
        if (stageLabel) {
            stageLabel.textContent = `阶段 ${stage}/3: ${stageName}`;
        }
    }

    /**
     * 更新进度
     */
    updateProgress(percentage, phase = null) {
        if (phase) {
            this.currentPhase = phase;
        }
        
        const progressFill = this.container.querySelector('.progress-fill');
        const progressText = this.container.querySelector('.progress-text');
        
        if (progressFill) {
            progressFill.style.width = `${percentage}%`;
        }
        
        if (progressText) {
            progressText.textContent = `${percentage}%`;
        }
    }

    /**
     * 更新共识度
     */
    updateConsensus(level) {
        const percentage = Math.round(level * 100);
        
        const consensusFill = this.container.querySelector('.consensus-fill');
        const consensusText = this.container.querySelector('.consensus-text');
        
        if (consensusFill) {
            consensusFill.style.width = `${percentage}%`;
            
            // 根据共识度改变颜色
            if (percentage >= 90) {
                consensusFill.style.backgroundColor = '#4caf50';
            } else if (percentage >= 70) {
                consensusFill.style.backgroundColor = '#8bc34a';
            } else if (percentage >= 50) {
                consensusFill.style.backgroundColor = '#ffc107';
            } else {
                consensusFill.style.backgroundColor = '#ff9800';
            }
        }
        
        if (consensusText) {
            consensusText.textContent = `${percentage}%`;
        }
    }

    /**
     * 高亮发言者
     */
    highlightSpeaker(agentId) {
        // 移除所有高亮
        this.container.querySelectorAll('.agent-avatar').forEach(el => {
            el.classList.remove('speaking-highlight');
        });
        
        // 添加新高亮
        const agentElement = this.container.querySelector(`[data-agent-id="${agentId}"]`);
        if (agentElement) {
            agentElement.classList.add('speaking-highlight');
        }
    }

    /**
     * 移除高亮
     */
    removeHighlight() {
        this.container.querySelectorAll('.agent-avatar').forEach(el => {
            el.classList.remove('speaking-highlight');
        });
    }

    /**
     * 显示庆祝动画（共识达成）
     */
    showCelebration() {
        const celebration = document.createElement('div');
        celebration.className = 'celebration-overlay';
        celebration.innerHTML = `
            <div class="celebration-content">
                <div class="celebration-icon">🎉</div>
                <div class="celebration-text">共识达成！</div>
            </div>
        `;
        
        this.container.appendChild(celebration);
        
        // 3秒后移除
        setTimeout(() => {
            celebration.remove();
        }, 3000);
    }

    /**
     * 处理消息（绘制交互线）
     */
    handleMessage(message) {
        if (this.interactionLines) {
            this.interactionLines.handleMessage(message);
        }
    }
    
    /**
     * 重置视图
     */
    reset() {
        this.currentStage = 0;
        this.currentPhase = 'idle';
        
        // 重置所有 Agent 状态
        this.container.querySelectorAll('.agent-avatar').forEach(el => {
            el.classList.remove('idle', 'waiting', 'analyzing', 'speaking', 'complete', 'error', 'speaking-highlight');
            el.classList.add('waiting');
            
            const statusElement = el.querySelector('.avatar-status');
            if (statusElement) {
                statusElement.textContent = '等待中';
            }
        });
        
        // 重置进度
        this.updateProgress(0);
        this.updateConsensus(0);
        
        const stageLabel = this.container.querySelector('.stage-label');
        if (stageLabel) {
            stageLabel.textContent = '准备中...';
        }
        
        // 清除交互线
        if (this.interactionLines) {
            this.interactionLines.clearAll();
        }
    }
}

// 导出到全局
window.RoundTableView = RoundTableView;
