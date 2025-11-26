# Forum Visualization Design Document

## Overview

The Forum Visualization feature transforms the ForumEngine's agent discussion process into an engaging, real-time visual experience. Agents are represented as participants seated around a virtual round table, with dynamic status indicators, speaking animations, and interactive elements that help users understand the collaborative AI discussion process.

## Integration with Existing Pages

The forum visualization will be integrated into the existing FoxTrends interface in the following ways:

### 1. Demand Detail Page Integration (Primary)

The visualization will be embedded directly in the **demand detail page** (`demand_detail.html`) as a new section:

**Location**: Between the "需求内容" section and the "Agent 分析讨论" section

**Integration Points**:
- Replace the current text-based "Agent 分析讨论" section with the interactive round table visualization
- Add a toggle button to switch between "Round Table View" and "Timeline View"
- The visualization will load automatically when the demand detail page opens
- Real-time updates will show live agent discussions as they happen

**User Flow**:
1. User clicks on a demand signal from the dashboard
2. Demand detail page loads with basic information
3. Forum visualization section shows:
   - If discussion is active: Live round table with real-time updates
   - If discussion is complete: Replay controls with final consensus
   - If no discussion yet: "Waiting for agent analysis" message

### 2. Standalone Visualization Page (Secondary)

A dedicated page for viewing forum discussions across multiple demands:

**URL**: `/forum-visualization`

**Features**:
- Session selector dropdown to choose which discussion to view
- Full-screen round table visualization
- Advanced replay controls
- Comparison view for multiple sessions

### 3. Dashboard Quick View (Optional)

Add a small "Live Discussion" indicator on the dashboard:

**Location**: Community cards or demand signal cards

**Features**:
- Small animated icon when agents are actively discussing
- Click to open demand detail with visualization
- Shows number of active discussions

## UI Layout in Demand Detail Page

```
┌─────────────────────────────────────────────────────────┐
│  Header: 需求详情                                        │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  Demand Header (existing)                                │
│  - Title, Meta, Stats, Action Buttons                    │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  需求内容 (existing)                                      │
│  - Full demand content                                   │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  🤖 Agent 讨论可视化 (NEW - replaces old section)        │
│  ┌─────────────────────────────────────────────────────┐│
│  │  [Round Table View] [Timeline View]  [⚙️ Settings] ││
│  └─────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────┐│
│  │                                                       ││
│  │         ┌─────────────────────┐                      ││
│  │         │   Forum Host        │                      ││
│  │         │   (Center)          │                      ││
│  │         └─────────────────────┘                      ││
│  │                                                       ││
│  │  ┌──────────┐         ┌──────────┐                  ││
│  │  │Community │         │ Content  │                  ││
│  │  │ Insight  │         │ Analysis │                  ││
│  │  └──────────┘         └──────────┘                  ││
│  │                                                       ││
│  │         ┌──────────┐                                 ││
│  │         │  Trend   │                                 ││
│  │         │Discovery │                                 ││
│  │         └──────────┘                                 ││
│  │                                                       ││
│  │  Progress: [████████░░] 80% - Discussing            ││
│  │  Consensus: [██████████] 95%                         ││
│  └─────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────┐│
│  │  Discussion Timeline (collapsible)                   ││
│  │  - Message 1: Community Insight Agent...             ││
│  │  - Message 2: Content Analysis Agent...              ││
│  │  - Message 3: Forum Host...                          ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## Architecture

### Component Structure

```
ForumVisualization/
├── frontend/
│   ├── components/
│   │   ├── RoundTableView.js       # Main circular layout component
│   │   ├── AgentAvatar.js          # Individual agent representation
│   │   ├── ForumHost.js            # Central moderator component
│   │   ├── DiscussionTimeline.js   # Message timeline panel
│   │   ├── ProgressIndicator.js    # Discussion progress bar
│   │   ├── ConsensusMe ter.js      # Agreement level visualization
│   │   └── InteractionLines.js     # Agent reference connections
│   ├── styles/
│   │   ├── round-table.css         # Round table layout styles
│   │   ├── agent-avatar.css        # Agent styling and animations
│   │   ├── timeline.css            # Timeline panel styles
│   │   └── animations.css          # Shared animation definitions
│   └── utils/
│       ├── websocket-client.js     # Real-time updates handler
│       ├── animation-engine.js     # Animation coordination
│       └── replay-controller.js    # Session replay logic
├── backend/
│   ├── forum_visualizer.py         # Visualization data provider
│   ├── session_recorder.py         # Discussion session recording
│   └── websocket_broadcaster.py    # Real-time event broadcasting
└── templates/
    └── forum_visualization.html    # Main visualization page
```

## Agent Discussion Flow (Pipeline Processing)

### Sequential Processing to Avoid API Overload

To prevent concurrent LLM API calls that could cause rate limiting and failures, the agent discussion follows a **pipeline processing model**:

```
Stage 1: CommunityInsightAgent
   ↓ (completes, extracts key insights)
Stage 2: ContentAnalysisAgent (can reference Stage 1 results)
   ↓ (completes, extracts pain points)
Stage 3: TrendDiscoveryAgent (can reference Stage 1 & 2 results)
   ↓ (completes)
Forum Discussion: All agents discuss based on their analyses
   ↓
Consensus: Forum Host generates summary
```

### Benefits of Pipeline Processing

1. **Reduced API Load**: Only one LLM call active at a time
2. **Lower Failure Rate**: No concurrent request conflicts
3. **Cost Control**: Predictable API usage
4. **Better Context**: Later agents can reference earlier analyses
5. **Graceful Degradation**: If one agent fails, others can still proceed

### Visualization Updates During Pipeline

The round table visualization will show the pipeline progress:

```
Stage 1 Active:
  Community Insight: 🔵 Analyzing...
  Content Analysis:  ⚪ Waiting...
  Trend Discovery:   ⚪ Waiting...

Stage 2 Active:
  Community Insight: ✅ Complete
  Content Analysis:  🔵 Analyzing...
  Trend Discovery:   ⚪ Waiting...

Stage 3 Active:
  Community Insight: ✅ Complete
  Content Analysis:  ✅ Complete
  Trend Discovery:   🔵 Analyzing...

Discussion Phase:
  Community Insight: 💬 Discussing...
  Content Analysis:  💬 Discussing...
  Trend Discovery:   💬 Discussing...
  Forum Host:        🎙️ Moderating...
```

## Components and Interfaces

### 1. RoundTableView Component

**Purpose**: Main container that arranges agents in a circular layout

**Props**:
- `agents`: Array of agent objects with status and position
- `forumHost`: Forum host object
- `sessionId`: Current discussion session ID
- `isActive`: Boolean indicating if discussion is ongoing

**State**:
- `agentPositions`: Calculated positions for circular layout
- `activeAgent`: Currently speaking agent
- `connections`: Array of active agent-to-agent connections

**Methods**:
```javascript
calculatePositions(agentCount, radius)
updateAgentStatus(agentId, status)
highlightSpeaker(agentId)
drawConnection(fromAgent, toAgent)
```

### 2. AgentAvatar Component

**Purpose**: Visual representation of an individual agent

**Props**:
- `agent`: Agent object (id, name, type, status)
- `position`: {x, y} coordinates
- `isActive`: Boolean for speaking state
- `onClick`: Callback for agent selection

**Visual States**:
- **Idle**: Gray, subtle pulse
- **Analyzing**: Blue, medium pulse
- **Speaking**: Green, bright glow with ripple effect
- **Complete**: Green with checkmark
- **Error**: Red with warning icon

**Animation**:
```css
@keyframes speaking-pulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 20px rgba(0,255,0,0.5); }
  50% { transform: scale(1.1); box-shadow: 0 0 40px rgba(0,255,0,0.8); }
}
```

### 3. DiscussionTimeline Component

**Purpose**: Scrollable panel showing chronological message history

**Props**:
- `messages`: Array of discussion messages
- `autoScroll`: Boolean for auto-scroll behavior
- `onMessageClick`: Callback for message interaction

**Message Format**:
```javascript
{
  id: "msg_123",
  agentId: "community_insight",
  agentName: "Community Insight Agent",
  timestamp: "2025-01-15T10:30:00Z",
  content: "Based on historical data...",
  type: "analysis" | "discussion" | "moderation",
  references: ["trend_discovery"] // Referenced agents
}
```

### 4. WebSocket Event System

**Event Types**:

```javascript
// Agent status change
{
  type: "agent_status_update",
  agentId: "community_insight",
  status: "speaking",
  timestamp: "2025-01-15T10:30:00Z"
}

// New message
{
  type: "new_message",
  message: {
    agentId: "content_analysis",
    content: "I agree with the sentiment analysis...",
    references: ["community_insight"]
  }
}

// Progress update
{
  type: "progress_update",
  phase: "discussing",
  percentage: 65,
  estimatedTimeRemaining: 120 // seconds
}

// Consensus reached
{
  type: "consensus_reached",
  consensusLevel: 95,
  summary: "All agents agree that..."
}
```

## Data Models

### Agent Model

```python
class AgentVisualization:
    id: str  # "community_insight", "content_analysis", "trend_discovery"
    name: str  # Display name
    type: str  # Agent type
    status: str  # "idle", "analyzing", "speaking", "complete", "error"
    position: int  # Position in circle (0-2)
    avatar_color: str  # Primary color for avatar
    message_count: int  # Number of messages posted
    last_active: datetime  # Last activity timestamp
```

### Discussion Session Model

```python
class DiscussionSession:
    id: str
    demand_signal_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str  # "active", "completed", "failed"
    participants: List[AgentVisualization]
    messages: List[DiscussionMessage]
    consensus_level: float  # 0.0 to 1.0
    consensus_summary: Optional[str]
```

### Discussion Message Model

```python
class DiscussionMessage:
    id: str
    session_id: str
    agent_id: str
    content: str
    timestamp: datetime
    message_type: str  # "analysis", "discussion", "moderation"
    references: List[str]  # IDs of referenced agents
    sentiment: Optional[str]  # "positive", "neutral", "negative"
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Agent Position Consistency
*For any* discussion session with N agents, the round table layout should position exactly N agents at evenly-spaced intervals around the circle, with no overlapping positions.
**Validates: Requirements 1.1, 1.2, 1.8**

### Property 2: Status Update Propagation
*For any* agent status change event, the visual indicator should update within 1 second, and the update should be reflected in both the avatar and the timeline.
**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

### Property 3: Single Speaker Constraint
*For any* point in time during an active discussion, at most one agent should be highlighted as currently speaking.
**Validates: Requirements 3.6**

### Property 4: Timeline Message Ordering
*For any* sequence of discussion messages, the timeline should display them in chronological order based on their timestamps.
**Validates: Requirements 4.1, 4.2, 4.3**

### Property 5: Progress Monotonicity
*For any* discussion session, the progress percentage should never decrease, and should reach 100% if and only if consensus is reached.
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 6: Connection Visibility Duration
*For any* agent reference connection, the visual line should be displayed for exactly 3 seconds before fading out.
**Validates: Requirements 6.3**

### Property 7: Consensus Meter Bounds
*For any* consensus meter value, it should always be between 0 and 100 inclusive, and should only reach 100 when all agents have expressed agreement.
**Validates: Requirements 7.1, 7.2, 7.3**

### Property 8: Replay Chronological Accuracy
*For any* replayed discussion session, events should occur in the exact same chronological order as the original session.
**Validates: Requirements 8.2, 8.3, 8.7**

### Property 9: Mobile Layout Transformation
*For any* screen width less than 768px, the round table layout should transform to a vertical stacked layout while preserving all agent information.
**Validates: Requirements 9.1, 9.2, 9.3**

### Property 10: Accessibility Announcement Completeness
*For any* visual status change, a corresponding text announcement should be generated for screen readers.
**Validates: Requirements 10.1, 10.2**

## Error Handling

### WebSocket Connection Failures
- **Detection**: Monitor WebSocket connection state
- **Recovery**: Implement automatic reconnection with exponential backoff
- **User Feedback**: Display connection status indicator
- **Fallback**: Poll REST API for updates if WebSocket unavailable

### Agent Timeout Handling
- **Detection**: No status update for > 60 seconds
- **Action**: Mark agent as "unresponsive" with warning indicator
- **Recovery**: Attempt to restart agent analysis
- **User Notification**: Show timeout message in timeline

### Animation Performance Issues
- **Detection**: Monitor frame rate (< 30 FPS)
- **Action**: Reduce animation complexity
- **Fallback**: Disable non-essential animations
- **User Control**: Provide "Reduce Motion" toggle

## Testing Strategy

### Unit Tests
- Test agent position calculation for various agent counts
- Test status indicator rendering for all status types
- Test message formatting and markdown rendering
- Test consensus meter calculation logic
- Test replay speed control functionality

### Property-Based Tests
- Use Hypothesis (Python) or fast-check (JavaScript) for property testing
- Generate random discussion sessions and verify properties hold
- Test with varying numbers of agents (1-10)
- Test with different message sequences and timings
- Verify layout calculations for all screen sizes

### Integration Tests
- Test WebSocket connection and event handling
- Test complete discussion flow from start to consensus
- Test replay functionality with recorded sessions
- Test mobile responsive behavior
- Test accessibility features with screen readers

### Performance Tests
- Measure rendering performance with 100+ messages
- Test WebSocket throughput with rapid updates
- Measure animation frame rates on various devices
- Test memory usage during long discussions

## Implementation Notes

### Technology Stack
- **Frontend**: Vanilla JavaScript or React.js
- **Styling**: CSS3 with CSS Grid and Flexbox
- **Real-time**: WebSocket (Socket.IO)
- **Animations**: CSS animations + requestAnimationFrame
- **Charts**: D3.js or Chart.js for consensus visualization

### Browser Compatibility
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Performance Optimizations
- Use CSS transforms for animations (GPU-accelerated)
- Implement virtual scrolling for long timelines
- Debounce WebSocket events to prevent flooding
- Use requestAnimationFrame for smooth animations
- Lazy load historical sessions

### Accessibility Considerations
- ARIA labels for all interactive elements
- Keyboard navigation support (Tab, Arrow keys)
- Focus indicators for keyboard users
- Screen reader announcements for status changes
- High contrast mode support
- Reduced motion mode for animations
