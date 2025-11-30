/**
 * Forum Visualization Controller
 * 
 * 主控制器，整合所有组件
 */

class ForumVisualizationController {
    constructor(config) {
        this.sessionId = config.sessionId;
        this.demandId = config.demandId;
        
        // 初始化组件
        this.roundTable = new RoundTableView(config.roundTableContainerId);
        this.timeline = new DiscussionTimeline(config.timelineContainerId);
        this.wsClient = new ForumWebSocketClient(this.sessionId);
        
        this.isActive = false;
        
        this._setupWebSocketHandlers();
    }

    /**
     * 设置 WebSocket 事件处理器
     */
    _setupWebSocketHandlers() {
        // 连接成功
        this.wsClient.on('connected', () => {
            console.log('[ForumController] WebSocket 已连接');
            this.isActive = true;
            this._showConnectionStatus('connected');
        });

        // 连接断开
        this.wsClient.on('disconnected', (data) => {
            console.log('[ForumController] WebSocket 已断开');
            this.isActive = false;
            this._showConnectionStatus('disconnected');
        });

        // 连接失败
        this.wsClient.on('connection_failed', (data) => {
            console.error('[ForumController] WebSocket 连接失败');
            this._showConnectionStatus('failed');
        });

        // Agent 状态更新
        this.wsClient.on('agent_status_update', (data) => {
            this.roundTable.updateAgentStatus(
                data.agent_id,
                data.status,
                data.current_stage
            );
            
            // 如果是发言状态，高亮显示
            if (data.status === 'speaking') {
                this.roundTable.highlightSpeaker(data.agent_id);
            }
        });

        // 新消息
        this.wsClient.on('new_message', (data) => {
            this.timeline.addMessage(data.message);
            
            // 绘制交互线
            this.roundTable.handleMessage(data.message);
            
            // 高亮发言者
            if (data.message.agent_id) {
                this.roundTable.highlightSpeaker(data.message.agent_id);
                
                // 3秒后移除高亮
                setTimeout(() => {
                    this.roundTable.removeHighlight();
                }, 3000);
            }
        });

        // 进度更新
        this.wsClient.on('progress_update', (data) => {
            this.roundTable.updateProgress(data.percentage, data.phase);
        });

        // 阶段变化
        this.wsClient.on('stage_change', (data) => {
            this.roundTable.updateStage(data.stage, data.stage_name);
        });

        // 共识达成
        this.wsClient.on('consensus_reached', (data) => {
            this.roundTable.updateConsensus(data.consensus_level);
            this.roundTable.showCelebration();
            
            // 添加共识消息到时间线
            this.timeline.addMessage({
                agent_id: 'system',
                agent_name: '系统',
                content: `共识达成！共识度: ${(data.consensus_level * 100).toFixed(0)}%\n\n${data.summary}`,
                message_type: 'system',
                timestamp: data.timestamp
            });
        });

        // 错误
        this.wsClient.on('error', (data) => {
            console.error('[ForumController] 错误:', data);
            this._showError(data.error_message);
        });
    }

    /**
     * 启动可视化
     */
    start() {
        console.log('[ForumController] 启动可视化');
        
        // 连接 WebSocket
        this.wsClient.connect();
        
        // 加载历史数据
        this._loadHistoricalData();
    }

    /**
     * 停止可视化
     */
    stop() {
        console.log('[ForumController] 停止可视化');
        
        this.isActive = false;
        this.wsClient.disconnect();
    }

    /**
     * 重置可视化
     */
    reset() {
        console.log('[ForumController] 重置可视化');
        
        this.roundTable.reset();
        this.timeline.clear();
    }

    /**
     * 加载历史数据
     */
    async _loadHistoricalData() {
        try {
            // 如果有 demandId，从需求讨论API加载
            if (this.demandId) {
                const response = await fetch(`/api/demands/${this.demandId}/discussions`);
                if (response.ok) {
                    const data = await response.json();
                    console.log('[ForumController] 历史讨论:', data);
                    
                    if (data.discussions && data.discussions.length > 0) {
                        // 转换为时间线消息格式
                        const messages = data.discussions.map(disc => ({
                            agent_id: disc.agent_name || 'unknown',
                            agent_name: this._getAgentDisplayName(disc.agent_name),
                            content: disc.content,
                            message_type: disc.message_type || 'speech',
                            timestamp: disc.created_at
                        }));
                        
                        this.timeline.loadMessages(messages);
                        
                        // 在圆桌视图中显示Agent状态
                        const uniqueAgents = [...new Set(messages.map(m => m.agent_id))];
                        uniqueAgents.forEach(agentId => {
                            this.roundTable.updateAgentStatus(agentId, 'complete', null);
                        });
                    }
                }
            }
            
            // 尝试加载会话信息（如果API存在）
            try {
                const sessionResponse = await fetch(`/api/forum/sessions/${this.sessionId}`);
                if (sessionResponse.ok) {
                    const sessionData = await sessionResponse.json();
                    console.log('[ForumController] 会话数据:', sessionData);
                    
                    if (sessionData.consensus_level) {
                        this.roundTable.updateConsensus(sessionData.consensus_level);
                    }
                }
            } catch (e) {
                // 会话API可能不存在，忽略错误
                console.log('[ForumController] 会话API不可用');
            }
            
        } catch (error) {
            console.error('[ForumController] 加载历史数据失败:', error);
        }
    }
    
    /**
     * 获取Agent显示名称
     */
    _getAgentDisplayName(agentName) {
        const nameMap = {
            'community_insight': '社区洞察',
            'content_analysis': '内容分析',
            'trend_discovery': '趋势发现',
            'forum_host': '论坛主持人'
        };
        return nameMap[agentName] || agentName;
    }

    /**
     * 显示连接状态
     */
    _showConnectionStatus(status) {
        const statusMap = {
            'connected': { text: '已连接', color: '#4caf50' },
            'disconnected': { text: '已断开', color: '#ff9800' },
            'failed': { text: '连接失败', color: '#f44336' }
        };
        
        const statusInfo = statusMap[status] || { text: status, color: '#999' };
        
        // 可以在这里显示一个状态指示器
        console.log(`[ForumController] 连接状态: ${statusInfo.text}`);
    }

    /**
     * 显示错误
     */
    _showError(message) {
        // 可以在这里显示一个错误提示
        console.error(`[ForumController] 错误: ${message}`);
        
        // 添加错误消息到时间线
        this.timeline.addMessage({
            agent_id: 'system',
            agent_name: '系统',
            content: `❌ 错误: ${message}`,
            message_type: 'system',
            timestamp: new Date().toISOString()
        });
    }

    /**
     * 获取状态
     */
    getStatus() {
        return {
            isActive: this.isActive,
            sessionId: this.sessionId,
            demandId: this.demandId,
            wsStatus: this.wsClient.getConnectionStatus()
        };
    }
}

// 导出到全局
window.ForumVisualizationController = ForumVisualizationController;
