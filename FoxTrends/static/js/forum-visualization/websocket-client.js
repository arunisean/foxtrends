/**
 * WebSocket Client for Forum Visualization
 * 
 * 处理与后端的 WebSocket 连接和事件监听
 */

class ForumWebSocketClient {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.socket = null;
        this.namespace = '/forum-visualization';
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        this.eventHandlers = {};
        this.isConnected = false;
    }

    /**
     * 连接到 WebSocket 服务器
     */
    connect() {
        console.log(`[ForumWS] 连接到会话: ${this.sessionId}`);
        
        try {
            // 使用 Socket.IO 连接
            this.socket = io(this.namespace, {
                transports: ['websocket', 'polling'],
                reconnection: true,
                reconnectionDelay: this.reconnectDelay,
                reconnectionAttempts: this.maxReconnectAttempts
            });

            this._setupEventListeners();
            
        } catch (error) {
            console.error('[ForumWS] 连接失败:', error);
            this._handleConnectionError(error);
        }
    }

    /**
     * 设置事件监听器
     */
    _setupEventListeners() {
        // 连接成功
        this.socket.on('connect', () => {
            console.log('[ForumWS] 已连接');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            
            // 加入会话房间
            this.socket.emit('join_session', { session_id: this.sessionId });
            
            this._trigger('connected');
        });

        // 连接断开
        this.socket.on('disconnect', (reason) => {
            console.log('[ForumWS] 连接断开:', reason);
            this.isConnected = false;
            this._trigger('disconnected', { reason });
        });

        // 连接错误
        this.socket.on('connect_error', (error) => {
            console.error('[ForumWS] 连接错误:', error);
            this._handleConnectionError(error);
        });

        // Agent 状态更新
        this.socket.on('agent_status_update', (data) => {
            console.log('[ForumWS] Agent 状态更新:', data);
            this._trigger('agent_status_update', data);
        });

        // 新消息
        this.socket.on('new_message', (data) => {
            console.log('[ForumWS] 新消息:', data);
            this._trigger('new_message', data);
        });

        // 进度更新
        this.socket.on('progress_update', (data) => {
            console.log('[ForumWS] 进度更新:', data);
            this._trigger('progress_update', data);
        });

        // 共识达成
        this.socket.on('consensus_reached', (data) => {
            console.log('[ForumWS] 共识达成:', data);
            this._trigger('consensus_reached', data);
        });

        // 阶段变化
        this.socket.on('stage_change', (data) => {
            console.log('[ForumWS] 阶段变化:', data);
            this._trigger('stage_change', data);
        });

        // 错误
        this.socket.on('error', (data) => {
            console.error('[ForumWS] 错误:', data);
            this._trigger('error', data);
        });
    }

    /**
     * 处理连接错误
     */
    _handleConnectionError(error) {
        this.reconnectAttempts++;
        
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[ForumWS] 达到最大重连次数，放弃重连');
            this._trigger('connection_failed', { error });
        } else {
            console.log(`[ForumWS] 将在 ${this.reconnectDelay}ms 后重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        }
    }

    /**
     * 注册事件处理器
     */
    on(eventName, handler) {
        if (!this.eventHandlers[eventName]) {
            this.eventHandlers[eventName] = [];
        }
        this.eventHandlers[eventName].push(handler);
    }

    /**
     * 移除事件处理器
     */
    off(eventName, handler) {
        if (!this.eventHandlers[eventName]) return;
        
        if (handler) {
            this.eventHandlers[eventName] = this.eventHandlers[eventName]
                .filter(h => h !== handler);
        } else {
            delete this.eventHandlers[eventName];
        }
    }

    /**
     * 触发事件
     */
    _trigger(eventName, data) {
        const handlers = this.eventHandlers[eventName];
        if (!handlers) return;
        
        handlers.forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                console.error(`[ForumWS] 事件处理器错误 (${eventName}):`, error);
            }
        });
    }

    /**
     * 断开连接
     */
    disconnect() {
        if (this.socket) {
            console.log('[ForumWS] 断开连接');
            this.socket.disconnect();
            this.socket = null;
            this.isConnected = false;
        }
    }

    /**
     * 获取连接状态
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            sessionId: this.sessionId
        };
    }
}

// 导出到全局
window.ForumWebSocketClient = ForumWebSocketClient;
