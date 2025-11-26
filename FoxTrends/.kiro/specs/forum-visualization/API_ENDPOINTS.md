# Forum Visualization API Endpoints

## REST API Endpoints

### Session Management

#### GET /api/forum/sessions
获取讨论会话列表

**Query Parameters:**
- `limit` (int, optional): 返回数量限制，默认 50
- `demand_id` (int, optional): 筛选特定需求的会话

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "uuid-string",
      "demand_signal_id": 123,
      "start_time": "2025-01-15T10:30:00Z",
      "end_time": "2025-01-15T10:45:00Z",
      "status": "completed",
      "consensus_level": 0.95,
      "consensus_summary": "All agents agree..."
    }
  ]
}
```

#### GET /api/forum/sessions/<session_id>
获取会话详情

**Response:**
```json
{
  "success": true,
  "session": {
    "id": "uuid-string",
    "demand_signal_id": 123,
    "start_time": "2025-01-15T10:30:00Z",
    "end_time": "2025-01-15T10:45:00Z",
    "status": "completed",
    "consensus_level": 0.95,
    "consensus_summary": "All agents agree..."
  }
}
```

#### GET /api/forum/sessions/<session_id>/messages
获取会话的所有消息

**Response:**
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "session_id": "uuid-string",
      "agent_id": "community_insight",
      "agent_name": "Community Insight Agent",
      "content": "Based on historical data...",
      "message_type": "analysis",
      "timestamp": "2025-01-15T10:30:00Z",
      "references": ["trend_discovery"],
      "sentiment": "positive"
    }
  ]
}
```

#### GET /api/forum/sessions/<session_id>/agent-states
获取会话的 Agent 状态

**Response:**
```json
{
  "success": true,
  "states": [
    {
      "id": 1,
      "session_id": "uuid-string",
      "agent_id": "community_insight",
      "agent_name": "Community Insight Agent",
      "status": "complete",
      "current_stage": 1,
      "message_count": 3,
      "last_active": "2025-01-15T10:35:00Z",
      "error_message": null
    }
  ]
}
```

#### GET /api/forum/sessions/<session_id>/replay
获取会话的回放数据（所有可视化事件）

**Response:**
```json
{
  "success": true,
  "events": [
    {
      "id": 1,
      "session_id": "uuid-string",
      "event_type": "agent_status_update",
      "event_data": {
        "agent_id": "community_insight",
        "status": "analyzing"
      },
      "timestamp": "2025-01-15T10:30:00Z"
    }
  ]
}
```

## WebSocket Events

### Namespace: /forum-visualization

#### Client → Server Events

##### connect
客户端连接到 WebSocket

**Response:**
```json
{
  "message": "已连接到 Forum 可视化服务"
}
```

##### join_session
加入会话房间以接收实时更新

**Payload:**
```json
{
  "session_id": "uuid-string"
}
```

**Response:**
```json
{
  "session_id": "uuid-string"
}
```

##### leave_session
离开会话房间

**Payload:**
```json
{
  "session_id": "uuid-string"
}
```

**Response:**
```json
{
  "session_id": "uuid-string"
}
```

#### Server → Client Events

##### agent_status_update
Agent 状态更新

**Payload:**
```json
{
  "type": "agent_status_update",
  "session_id": "uuid-string",
  "agent_id": "community_insight",
  "status": "analyzing",
  "current_stage": 1,
  "error_message": null,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

##### new_message
新消息

**Payload:**
```json
{
  "type": "new_message",
  "session_id": "uuid-string",
  "message": {
    "agent_id": "community_insight",
    "agent_name": "Community Insight Agent",
    "content": "Based on historical data...",
    "message_type": "analysis",
    "timestamp": "2025-01-15T10:30:00Z",
    "references": ["trend_discovery"]
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

##### progress_update
进度更新

**Payload:**
```json
{
  "type": "progress_update",
  "session_id": "uuid-string",
  "phase": "discussing",
  "percentage": 65,
  "estimated_time_remaining": 120,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

##### stage_change
阶段变化

**Payload:**
```json
{
  "type": "stage_change",
  "session_id": "uuid-string",
  "stage": 2,
  "stage_name": "Content Analysis",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

##### consensus_reached
共识达成

**Payload:**
```json
{
  "type": "consensus_reached",
  "session_id": "uuid-string",
  "consensus_level": 0.95,
  "summary": "All agents agree that...",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

##### error
错误事件

**Payload:**
```json
{
  "type": "error",
  "session_id": "uuid-string",
  "error_type": "agent_timeout",
  "error_message": "Agent did not respond within timeout",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Usage Example

### JavaScript Client

```javascript
// Initialize controller
const controller = new ForumVisualizationController({
    sessionId: 'your-session-id',
    demandId: 123,
    roundTableContainerId: 'round-table-container',
    timelineContainerId: 'timeline-container'
});

// Start visualization
controller.start();

// The controller will:
// 1. Connect to WebSocket
// 2. Load historical data via REST API
// 3. Listen for real-time updates
// 4. Update UI components automatically
```

### REST API Usage

```javascript
// Get session list
const sessions = await fetch('/api/forum/sessions?demand_id=123')
    .then(r => r.json());

// Get session details
const session = await fetch('/api/forum/sessions/uuid-string')
    .then(r => r.json());

// Get messages
const messages = await fetch('/api/forum/sessions/uuid-string/messages')
    .then(r => r.json());

// Get agent states
const states = await fetch('/api/forum/sessions/uuid-string/agent-states')
    .then(r => r.json());

// Get replay data
const events = await fetch('/api/forum/sessions/uuid-string/replay')
    .then(r => r.json());
```

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "message": "Error description"
}
```

HTTP Status Codes:
- 200: Success
- 400: Bad Request
- 404: Not Found
- 500: Internal Server Error
