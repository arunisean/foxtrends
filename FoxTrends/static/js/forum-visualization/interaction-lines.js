/**
 * Interaction Lines Component
 * 
 * 绘制 Agent 之间的交互连接线
 */

class InteractionLines {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container ${containerId} not found`);
        }
        
        this.svg = null;
        this.activeLines = new Map(); // lineId -> {element, timeout}
        this.lineIdCounter = 0;
        
        this._init();
    }

    /**
     * 初始化 SVG 容器
     */
    _init() {
        // 创建 SVG 元素
        this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        this.svg.setAttribute('class', 'interaction-lines-svg');
        this.svg.style.position = 'absolute';
        this.svg.style.top = '0';
        this.svg.style.left = '0';
        this.svg.style.width = '100%';
        this.svg.style.height = '100%';
        this.svg.style.pointerEvents = 'none';
        this.svg.style.zIndex = '1';
        
        // 添加到容器
        this.container.style.position = 'relative';
        this.container.appendChild(this.svg);
        
        // 创建 defs 用于箭头标记
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        
        // 普通箭头
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '10');
        marker.setAttribute('markerHeight', '10');
        marker.setAttribute('refX', '9');
        marker.setAttribute('refY', '3');
        marker.setAttribute('orient', 'auto');
        
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 10 3, 0 6');
        polygon.setAttribute('fill', '#667eea');
        
        marker.appendChild(polygon);
        defs.appendChild(marker);
        
        // Host 箭头
        const hostMarker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        hostMarker.setAttribute('id', 'arrowhead-host');
        hostMarker.setAttribute('markerWidth', '10');
        hostMarker.setAttribute('markerHeight', '10');
        hostMarker.setAttribute('refX', '9');
        hostMarker.setAttribute('refY', '3');
        hostMarker.setAttribute('orient', 'auto');
        
        const hostPolygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        hostPolygon.setAttribute('points', '0 0, 10 3, 0 6');
        hostPolygon.setAttribute('fill', '#9c27b0');
        
        hostMarker.appendChild(hostPolygon);
        defs.appendChild(hostMarker);
        
        this.svg.appendChild(defs);
    }

    /**
     * 绘制连接线
     */
    drawLine(fromAgentId, toAgentId, isHostConnection = false) {
        // 获取 Agent 元素位置
        const fromElement = this.container.querySelector(`[data-agent-id="${fromAgentId}"]`);
        const toElement = this.container.querySelector(`[data-agent-id="${toAgentId}"]`);
        
        if (!fromElement || !toElement) {
            console.warn(`Agent elements not found: ${fromAgentId} -> ${toAgentId}`);
            return null;
        }
        
        // 计算中心点
        const fromRect = fromElement.getBoundingClientRect();
        const toRect = toElement.getBoundingClientRect();
        const containerRect = this.container.getBoundingClientRect();
        
        const fromX = fromRect.left + fromRect.width / 2 - containerRect.left;
        const fromY = fromRect.top + fromRect.height / 2 - containerRect.top;
        const toX = toRect.left + toRect.width / 2 - containerRect.left;
        const toY = toRect.top + toRect.height / 2 - containerRect.top;
        
        // 创建线条
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', fromX);
        line.setAttribute('y1', fromY);
        line.setAttribute('x2', toX);
        line.setAttribute('y2', toY);
        line.setAttribute('stroke', isHostConnection ? '#9c27b0' : '#667eea');
        line.setAttribute('stroke-width', '3');
        line.setAttribute('stroke-dasharray', isHostConnection ? '5,5' : '0');
        line.setAttribute('marker-end', isHostConnection ? 'url(#arrowhead-host)' : 'url(#arrowhead)');
        line.setAttribute('opacity', '0');
        line.setAttribute('class', 'interaction-line');
        
        this.svg.appendChild(line);
        
        // 动画出现
        setTimeout(() => {
            line.setAttribute('opacity', '0.8');
        }, 10);
        
        // 生成唯一 ID
        const lineId = `line-${this.lineIdCounter++}`;
        
        // 3秒后淡出并移除
        const timeout = setTimeout(() => {
            this._removeLine(lineId);
        }, 3000);
        
        // 保存引用
        this.activeLines.set(lineId, {
            element: line,
            timeout: timeout
        });
        
        return lineId;
    }

    /**
     * 移除连接线
     */
    _removeLine(lineId) {
        const lineData = this.activeLines.get(lineId);
        if (!lineData) return;
        
        const { element, timeout } = lineData;
        
        // 淡出动画
        element.setAttribute('opacity', '0');
        
        // 动画完成后移除
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
        }, 300);
        
        // 清理
        clearTimeout(timeout);
        this.activeLines.delete(lineId);
    }

    /**
     * 解析消息内容，检测 Agent 引用
     */
    detectReferences(message) {
        const references = [];
        const content = message.content.toLowerCase();
        
        // Agent 名称映射
        const agentPatterns = {
            'community_insight': ['community insight', 'community', '社区洞察'],
            'content_analysis': ['content analysis', 'content', '内容分析'],
            'trend_discovery': ['trend discovery', 'trend', '趋势发现'],
            'forum_host': ['forum host', 'host', '主持人', '论坛主持']
        };
        
        // 检测引用
        for (const [agentId, patterns] of Object.entries(agentPatterns)) {
            if (agentId === message.agent_id) continue; // 跳过自己
            
            for (const pattern of patterns) {
                if (content.includes(pattern)) {
                    references.push(agentId);
                    break;
                }
            }
        }
        
        // 也检查 message.references 字段
        if (message.references && Array.isArray(message.references)) {
            message.references.forEach(ref => {
                if (!references.includes(ref)) {
                    references.push(ref);
                }
            });
        }
        
        return references;
    }

    /**
     * 处理新消息，绘制引用线
     */
    handleMessage(message) {
        const references = this.detectReferences(message);
        
        if (references.length === 0) return;
        
        const isHostConnection = message.agent_id === 'forum_host';
        
        // 为每个引用绘制线条
        references.forEach(toAgentId => {
            this.drawLine(message.agent_id, toAgentId, isHostConnection);
        });
    }

    /**
     * 清除所有连接线
     */
    clearAll() {
        this.activeLines.forEach((lineData, lineId) => {
            this._removeLine(lineId);
        });
    }

    /**
     * 调整大小（窗口 resize 时调用）
     */
    resize() {
        // SVG 会自动调整，但可能需要重新计算线条位置
        // 当前实现中线条是静态的，不需要重新计算
    }
}

// 导出到全局
window.InteractionLines = InteractionLines;
