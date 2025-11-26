/**
 * Discussion Timeline Component
 * 
 * 讨论时间线组件
 */

class DiscussionTimeline {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container ${containerId} not found`);
        }
        
        this.messages = [];
        this.autoScroll = true;
        
        this._init();
    }

    /**
     * 初始化组件
     */
    _init() {
        this.container.innerHTML = `
            <div class="timeline-container">
                <div class="timeline-header">
                    <h3>💬 讨论时间线</h3>
                    <div class="timeline-controls">
                        <button class="btn-auto-scroll active" title="自动滚动">
                            <span class="icon">📜</span>
                        </button>
                        <button class="btn-clear" title="清空">
                            <span class="icon">🗑️</span>
                        </button>
                    </div>
                </div>
                <div class="timeline-messages"></div>
                <div class="timeline-empty">
                    <div class="empty-icon">💭</div>
                    <div class="empty-text">暂无讨论消息</div>
                </div>
            </div>
        `;
        
        this._setupEventListeners();
    }

    /**
     * 设置事件监听
     */
    _setupEventListeners() {
        // 自动滚动按钮
        const autoScrollBtn = this.container.querySelector('.btn-auto-scroll');
        if (autoScrollBtn) {
            autoScrollBtn.addEventListener('click', () => {
                this.autoScroll = !this.autoScroll;
                autoScrollBtn.classList.toggle('active', this.autoScroll);
                
                if (this.autoScroll) {
                    this._scrollToBottom();
                }
            });
        }
        
        // 清空按钮
        const clearBtn = this.container.querySelector('.btn-clear');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                this.clear();
            });
        }
        
        // 触摸手势支持
        this._setupTouchGestures();
    }
    
    /**
     * 设置触摸手势
     */
    _setupTouchGestures() {
        const messagesContainer = this.container.querySelector('.timeline-messages');
        if (!messagesContainer) return;
        
        let touchStartY = 0;
        let touchStartTime = 0;
        
        messagesContainer.addEventListener('touchstart', (e) => {
            touchStartY = e.touches[0].clientY;
            touchStartTime = Date.now();
        }, { passive: true });
        
        messagesContainer.addEventListener('touchmove', (e) => {
            // 禁用自动滚动当用户手动滚动时
            if (this.autoScroll) {
                const touchY = e.touches[0].clientY;
                const deltaY = touchY - touchStartY;
                
                // 如果用户向上滑动（查看历史消息）
                if (deltaY < -10) {
                    this.setAutoScroll(false);
                }
            }
        }, { passive: true });
        
        messagesContainer.addEventListener('touchend', (e) => {
            const touchEndTime = Date.now();
            const touchDuration = touchEndTime - touchStartTime;
            
            // 快速下滑手势 = 滚动到底部
            if (touchDuration < 300) {
                const touchEndY = e.changedTouches[0].clientY;
                const deltaY = touchEndY - touchStartY;
                
                if (deltaY > 50) {
                    this.setAutoScroll(true);
                    this._scrollToBottom();
                }
            }
        }, { passive: true });
    }

    /**
     * 添加消息
     */
    addMessage(message) {
        this.messages.push(message);
        
        const messagesContainer = this.container.querySelector('.timeline-messages');
        const emptyState = this.container.querySelector('.timeline-empty');
        
        if (!messagesContainer) return;
        
        // 隐藏空状态
        if (emptyState) {
            emptyState.style.display = 'none';
        }
        
        // 创建消息元素
        const messageElement = this._createMessageElement(message);
        messagesContainer.appendChild(messageElement);
        
        // 自动滚动
        if (this.autoScroll) {
            this._scrollToBottom();
        }
        
        // 添加动画
        setTimeout(() => {
            messageElement.classList.add('message-appear');
        }, 10);
    }

    /**
     * 创建消息元素
     */
    _createMessageElement(message) {
        const div = document.createElement('div');
        div.className = `timeline-message message-${message.message_type || 'discussion'}`;
        div.dataset.agentId = message.agent_id;
        
        const agentClass = this._getAgentClass(message.agent_id);
        const agentIcon = this._getAgentIcon(message.agent_id);
        const timestamp = this._formatTimestamp(message.timestamp);
        
        div.innerHTML = `
            <div class="message-header">
                <div class="message-agent ${agentClass}">
                    <span class="agent-icon">${agentIcon}</span>
                    <span class="agent-name">${message.agent_name || message.agent_id}</span>
                </div>
                <div class="message-time">${timestamp}</div>
            </div>
            <div class="message-content">${this._formatContent(message.content)}</div>
            ${message.references && message.references.length > 0 ? `
                <div class="message-references">
                    <span class="ref-icon">🔗</span>
                    引用: ${message.references.join(', ')}
                </div>
            ` : ''}
        `;
        
        return div;
    }

    /**
     * 获取 Agent 类名
     */
    _getAgentClass(agentId) {
        const classMap = {
            'community_insight': 'agent-community',
            'content_analysis': 'agent-content',
            'trend_discovery': 'agent-trend',
            'forum_host': 'agent-host',
            'HOST': 'agent-host'
        };
        return classMap[agentId] || 'agent-default';
    }

    /**
     * 获取 Agent 图标
     */
    _getAgentIcon(agentId) {
        const iconMap = {
            'community_insight': '📊',
            'content_analysis': '🔍',
            'trend_discovery': '📈',
            'forum_host': '🎙️',
            'HOST': '🎙️'
        };
        return iconMap[agentId] || '🤖';
    }

    /**
     * 格式化时间戳
     */
    _formatTimestamp(timestamp) {
        if (!timestamp) return '';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        } catch (e) {
            return timestamp;
        }
    }

    /**
     * 格式化内容（支持基础 Markdown）
     */
    _formatContent(content) {
        if (!content) return '';
        
        // 转义 HTML
        let formatted = content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
        
        // 基础 Markdown 支持
        
        // 代码块 ```code```
        formatted = formatted.replace(/```([^`]+)```/g, '<pre><code>$1</code></pre>');
        
        // 行内代码 `code`
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // 粗体 **text** 或 __text__
        formatted = formatted.replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/__([^_]+)__/g, '<strong>$1</strong>');
        
        // 斜体 *text* 或 _text_
        formatted = formatted.replace(/\*([^\*]+)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/_([^_]+)_/g, '<em>$1</em>');
        
        // 链接 [text](url)
        formatted = formatted.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        
        // 列表项 - item 或 * item
        formatted = formatted.replace(/^[\-\*]\s+(.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        // 标题 # Heading
        formatted = formatted.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
        formatted = formatted.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
        formatted = formatted.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
        
        // 转换换行符
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }

    /**
     * 滚动到底部
     */
    _scrollToBottom() {
        const messagesContainer = this.container.querySelector('.timeline-messages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }

    /**
     * 清空消息
     */
    clear() {
        this.messages = [];
        
        const messagesContainer = this.container.querySelector('.timeline-messages');
        const emptyState = this.container.querySelector('.timeline-empty');
        
        if (messagesContainer) {
            messagesContainer.innerHTML = '';
        }
        
        if (emptyState) {
            emptyState.style.display = 'flex';
        }
    }

    /**
     * 加载历史消息
     */
    loadMessages(messages) {
        this.clear();
        messages.forEach(msg => this.addMessage(msg));
    }

    /**
     * 获取所有消息
     */
    getMessages() {
        return this.messages;
    }

    /**
     * 设置自动滚动
     */
    setAutoScroll(enabled) {
        this.autoScroll = enabled;
        
        const autoScrollBtn = this.container.querySelector('.btn-auto-scroll');
        if (autoScrollBtn) {
            autoScrollBtn.classList.toggle('active', enabled);
        }
    }
}

// 导出到全局
window.DiscussionTimeline = DiscussionTimeline;
