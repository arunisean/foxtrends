# Dashboard 增强设计文档

## 概述

本设计文档描述了 FoxTrends Dashboard 的增强方案，包括页面整合、UI 美化、完整的监控功能实现。设计目标是创建一个统一、美观、功能完整的监控界面。

## 架构

### 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Frontend)                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Unified Dashboard Page                      │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │  System Status Bar (Fixed Top)               │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  │  ┌──────────────┐  ┌──────────────────────────┐  │ │
│  │  │ Stats Cards  │  │  Monitoring Logs         │  │ │
│  │  └──────────────┘  └──────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │  Community Cards Grid                        │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │  Demand Signals List                         │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/WebSocket
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Flask Backend (app.py)                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │  API Routes                                         │ │
│  │  - /api/system/status                              │ │
│  │  - /api/monitoring/logs                            │ │
│  │  - /api/communities (GET/POST/PATCH/DELETE)        │ │
│  │  - /api/demands                                    │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  MonitoringManager                                  │ │
│  │  - Task scheduling                                  │ │
│  │  - Log management                                   │ │
│  │  - Status tracking                                  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    NicheEngine                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │  MonitoringTask (per community)                     │ │
│  │  - Data collection                                  │ │
│  │  - Signal extraction                                │ │
│  │  - Status updates                                   │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Database (SQLite)                     │
│  - communities                                           │
│  - demand_signals                                        │
│  - monitoring_logs                                       │
└─────────────────────────────────────────────────────────┘
```

## 组件和接口

### 1. Frontend Components

#### 1.1 SystemStatusBar
固定在页面顶部的状态栏组件

**Props:**
- `databaseStatus`: string - 数据库连接状态
- `systemStatus`: string - 系统运行状态
- `activeTasksCount`: number - 活跃监控任务数
- `lastUpdate`: string - 最后更新时间

**Methods:**
- `updateStatus()`: 更新状态信息
- `refresh()`: 手动刷新状态

#### 1.2 MonitoringLogPanel
显示实时监控日志的面板

**Props:**
- `logs`: Array<LogEntry> - 日志条目数组
- `maxLogs`: number - 最大显示日志数（默认 50）

**Methods:**
- `addLog(entry)`: 添加新日志
- `clearLogs()`: 清空日志
- `filterByLevel(level)`: 按级别过滤日志

#### 1.3 CommunityCard
增强的社区卡片组件

**Props:**
- `community`: Community - 社区对象
- `stats`: CommunityStats - 统计信息

**Methods:**
- `toggleMonitoring()`: 切换监控状态
- `showDetails()`: 显示详细信息
- `deleteCommunity()`: 删除社区

### 2. Backend Components

#### 2.1 MonitoringManager
监控任务管理器

```python
class MonitoringManager:
    """
    监控任务管理器
    
    职责:
    - 管理所有监控任务的生命周期
    - 调度任务执行
    - 收集和分发日志
    - 跟踪任务状态
    """
    
    def __init__(self):
        self.tasks: Dict[int, MonitoringTask] = {}
        self.logs: List[LogEntry] = []
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def start_monitoring(self, community_id: int) -> bool:
        """启动社区监控"""
        pass
    
    def stop_monitoring(self, community_id: int) -> bool:
        """停止社区监控"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有监控任务状态"""
        pass
    
    def get_logs(self, limit: int = 50) -> List[LogEntry]:
        """获取最新日志"""
        pass
    
    def add_log(self, level: str, message: str, community_id: int = None):
        """添加日志条目"""
        pass
```

#### 2.2 MonitoringTask
单个社区的监控任务

```python
class MonitoringTask:
    """
    单个社区的监控任务
    
    职责:
    - 定期采集社区数据
    - 提取需求信号
    - 更新监控状态
    - 报告错误和异常
    """
    
    def __init__(self, community: Community, manager: MonitoringManager):
        self.community = community
        self.manager = manager
        self.status = 'idle'
        self.last_run = None
        self.error_count = 0
    
    def run(self):
        """执行一次监控任务"""
        pass
    
    def collect_data(self) -> List[Dict]:
        """采集社区数据（模拟实现）"""
        pass
    
    def extract_signals(self, data: List[Dict]) -> List[DemandSignal]:
        """提取需求信号"""
        pass
    
    def save_signals(self, signals: List[DemandSignal]):
        """保存需求信号到数据库"""
        pass
```

### 3. API Endpoints

#### 3.1 GET /api/monitoring/logs
获取监控日志

**Query Parameters:**
- `limit`: int - 返回日志数量（默认 50）
- `level`: string - 过滤日志级别（可选）
- `community_id`: int - 过滤特定社区（可选）

**Response:**
```json
{
  "success": true,
  "logs": [
    {
      "id": 1,
      "timestamp": "2025-11-22 20:30:00",
      "level": "INFO",
      "message": "开始监控社区: 机器学习讨论区",
      "community_id": 1
    }
  ]
}
```

#### 3.2 POST /api/communities/:id/monitoring
控制社区监控状态

**Request Body:**
```json
{
  "action": "start" | "stop" | "pause"
}
```

**Response:**
```json
{
  "success": true,
  "message": "监控已启动",
  "status": "running"
}
```

#### 3.3 GET /api/communities/:id/stats
获取社区统计信息

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_signals": 45,
    "last_collection": "2025-11-22 20:25:00",
    "status": "running",
    "error_count": 0
  }
}
```

## 数据模型

### monitoring_logs 表

```sql
CREATE TABLE monitoring_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(20) NOT NULL,  -- INFO, WARNING, ERROR
    message TEXT NOT NULL,
    community_id INTEGER,
    metadata TEXT,  -- JSON格式的额外信息
    FOREIGN KEY (community_id) REFERENCES communities(id)
);
```

### communities 表扩展

添加监控相关字段：

```sql
ALTER TABLE communities ADD COLUMN last_collection_time TIMESTAMP;
ALTER TABLE communities ADD COLUMN total_signals INTEGER DEFAULT 0;
ALTER TABLE communities ADD COLUMN error_count INTEGER DEFAULT 0;
ALTER TABLE communities ADD COLUMN monitoring_status VARCHAR(20) DEFAULT 'idle';
```

## 正确性属性

*属性是应该在所有有效执行中保持为真的特征或行为——本质上是关于系统应该做什么的正式陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: 系统状态 API 完整性
*对于任何*系统状态查询，返回的数据应该包含 database_connected、system_status、active_tasks_count 和 last_update 字段
**验证: 需求 2.1, 2.2, 2.3, 2.4**

### 属性 2: 添加社区自动启动监控
*对于任何*新添加的社区，系统应该自动创建监控任务并在日志中记录"开始监控 [社区名称]"
**验证: 需求 3.1, 3.2, 6.2**

### 属性 3: 监控任务生成日志
*对于任何*运行中的监控任务，应该定期产生采集进度和状态信息的日志条目
**验证: 需求 3.3**

### 属性 4: 信号提取记录日志
*对于任何*需求信号提取操作，应该在日志中记录提取的需求数量和类型
**验证: 需求 3.4**

### 属性 5: 错误处理更新状态
*对于任何*监控错误，系统应该记录错误日志并将社区状态标记为异常
**验证: 需求 3.5**

### 属性 6: 日志时间倒序排列
*对于任何*日志查询，返回的日志条目应该按时间戳降序排列
**验证: 需求 4.3**

### 属性 7: 日志数量限制
*对于任何*日志查询，返回的日志数量不应超过请求的 limit 参数
**验证: 需求 4.3**

### 属性 8: 日志级别样式映射
*对于任何*日志条目，不同的日志级别（INFO/WARNING/ERROR）应该映射到不同的 CSS 类
**验证: 需求 4.5**

### 属性 9: 社区数据完整性
*对于任何*社区查询，返回的数据应该包含 name、source_type、status、last_collection_time 和 total_signals 字段
**验证: 需求 5.1, 5.2, 5.3**

### 属性 10: 系统启动加载社区
*对于任何*系统启动，应该为所有状态为 'active' 的社区创建监控任务
**验证: 需求 6.1**

### 属性 11: 监控任务唯一性
*对于任何*社区，系统中最多只能有一个活跃的监控任务在运行
**验证: 需求 6.2**

### 属性 12: 失败重试限制
*对于任何*监控任务失败，系统应该自动重试，但连续失败次数不应超过 3 次
**验证: 需求 6.4**

### 属性 13: 暂停停止任务
*对于任何*社区暂停操作，相关的监控任务应该被停止
**验证: 需求 6.5**

### 属性 14: 模拟数据生成
*对于任何*监控任务运行，应该生成包含 pain_point、feature_request、bug_report 三种类型的需求信号
**验证: 需求 7.1, 7.2**

### 属性 15: 信号数据持久化
*对于任何*生成的需求信号，应该被保存到 demand_signals 表中
**验证: 需求 7.3**

### 属性 16: 热度分数计算
*对于任何*需求信号，应该有一个 0-100 范围内的热度分数
**验证: 需求 7.4**

### 属性 17: 采集时间更新
*对于任何*完成的数据采集，社区的 last_collection_time 应该被更新为当前时间
**验证: 需求 7.5**

### 属性 18: 操作结果消息
*对于任何*API 操作（成功或失败），响应应该包含 success 字段和 message 字段
**验证: 需求 8.5**

## 错误处理

### 监控任务错误
- 数据采集失败：记录错误日志，增加 error_count，3 次失败后暂停任务
- 信号提取失败：记录警告日志，跳过该批数据，继续下一次采集
- 数据库保存失败：记录错误日志，重试最多 3 次

### API 错误
- 社区不存在：返回 404 错误
- 监控任务冲突：返回 409 错误
- 参数验证失败：返回 400 错误

### 前端错误
- API 调用失败：显示错误提示，提供重试按钮
- WebSocket 断开：自动重连，最多重试 5 次
- 数据加载超时：显示超时提示，提供刷新按钮

## 测试策略

### 单元测试
- MonitoringManager 的任务管理逻辑
- MonitoringTask 的数据采集和信号提取
- API 端点的参数验证和响应格式
- 前端组件的渲染和交互

### 集成测试
- 完整的监控流程：添加社区 → 启动监控 → 采集数据 → 显示日志
- 状态同步：后端状态变化 → 前端状态更新
- 错误恢复：任务失败 → 重试 → 恢复或暂停

### 性能测试
- 多个监控任务并发运行
- 大量日志的查询和显示性能
- 前端页面在大量数据下的响应速度

## UI 设计规范

### 配色方案
- 主色：`#667eea` (紫蓝色)
- 辅色：`#764ba2` (深紫色)
- 成功：`#28a745` (绿色)
- 警告：`#ffc107` (黄色)
- 错误：`#dc3545` (红色)
- 背景：`#f5f7fa` (浅灰)

### 组件样式
- 卡片：白色背景，8px 圆角，轻微阴影
- 按钮：渐变背景，悬停时上移 2px
- 状态指示器：圆点 + 文字，颜色对应状态
- 日志面板：等宽字体，深色背景，彩色文字

### 响应式断点
- 移动设备：< 768px
- 平板设备：768px - 1024px
- 桌面设备：> 1024px

## 实现阶段

### 阶段 1: 基础架构（优先）
1. 创建 MonitoringManager 和 MonitoringTask 类
2. 实现 monitoring_logs 表和相关 API
3. 添加社区监控状态字段

### 阶段 2: 模拟监控（优先）
1. 实现模拟数据采集逻辑
2. 生成随机需求信号
3. 记录监控日志

### 阶段 3: UI 整合（优先）
1. 合并首页和 Dashboard
2. 实现系统状态栏
3. 添加监控日志面板

### 阶段 4: 增强功能
1. 实现社区卡片增强
2. 添加监控控制功能
3. 优化性能和用户体验

### 阶段 5: 真实监控（后期）
1. 集成真实爬虫
2. 实现 LLM 需求分析
3. 完善错误处理和重试机制
