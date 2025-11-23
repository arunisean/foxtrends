# Design Document

## Overview

This design addresses critical improvements to the FoxTrends community monitoring system, focusing on real-time updates, database schema consistency, manual monitoring control, duplicate detection, and complete agent analysis with report generation capabilities.

The system follows a multi-layered architecture:
- **Frontend Layer**: WebSocket-enabled dashboard for real-time updates
- **API Layer**: Flask REST endpoints for CRUD operations and control
- **Service Layer**: MonitoringManager, NicheEngine, and Agent orchestration
- **Data Layer**: SQLite/PostgreSQL database with proper schema
- **Integration Layer**: Crawler adapters and Agent interfaces

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Browser)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Community    │  │ Demand       │  │ Report       │      │
│  │ Cards        │  │ List         │  │ Viewer       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    WebSocket + REST API                      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                      Flask Application                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ WebSocket    │  │ REST         │  │ Report       │      │
│  │ Handler      │  │ Endpoints    │  │ Generator    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                      Service Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Monitoring   │  │ Niche        │  │ Agent        │      │
│  │ Manager      │  │ Engine       │  │ Orchestrator │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
└────────────────────────────┴────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Database     │  │ Duplicate    │  │ Report       │      │
│  │ Manager      │  │ Detector     │  │ Storage      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Monitoring Start Flow**:
   - User clicks "Start" button → Frontend sends POST to `/api/communities/{id}/monitoring`
   - Flask endpoint validates request → MonitoringManager.start_monitoring()
   - MonitoringTask created → Crawler initialized → Data collection begins
   - WebSocket broadcasts status update → Frontend updates community card

2. **Signal Collection Flow**:
   - Crawler fetches content → DuplicateDetector checks for duplicates
   - New signals stored in database → AgentOrchestrator triggered
   - Agents analyze signal → Forum discussion initiated
   - Discussion stored → WebSocket broadcasts new signal count

3. **Report Generation Flow**:
   - User requests report → ReportGenerator gathers data
   - Agents provide insights → HTML report generated
   - Report stored in database → Download link provided

## Components and Interfaces

### 1. WebSocket Handler

**Purpose**: Push real-time updates to connected clients

**Interface**:
```python
class WebSocketHandler:
    def broadcast_community_update(self, community_id: int, update_data: Dict[str, Any])
    def broadcast_new_signal(self, signal_id: int, community_id: int)
    def broadcast_monitoring_status(self, community_id: int, status: str)
```

**Events Emitted**:
- `community_update`: Community card data changed
- `new_signal`: New demand signal collected
- `monitoring_status`: Monitoring status changed
- `error_occurred`: Error in monitoring task

### 2. DuplicateDetector

**Purpose**: Detect and prevent duplicate demand signals

**Interface**:
```python
class DuplicateDetector:
    def is_duplicate(self, signal: DemandSignal, time_window_days: int = 30) -> bool
    def check_by_url(self, source_url: str) -> Optional[int]
    def check_by_content(self, title: str, content: str, threshold: float = 0.95) -> Optional[int]
    def get_duplicate_stats(self, community_id: int) -> Dict[str, int]
```

**Algorithm**:
1. Check source_url in database (exact match)
2. If no URL, compute content hash (title + content)
3. Check hash in database within time window
4. If no exact match, compute similarity score using Levenshtein distance
5. Return duplicate if similarity > threshold

### 3. AgentOrchestrator

**Purpose**: Coordinate agent analysis and forum discussions

**Interface**:
```python
class AgentOrchestrator:
    def analyze_signal(self, signal_id: int) -> Dict[str, Any]
    def initiate_forum_discussion(self, signal_id: int) -> str  # Returns session_id
    def get_discussion_summary(self, session_id: str) -> str
    def store_discussion(self, session_id: str, demand_id: int)
```

**Workflow**:
1. Trigger analysis when new signal collected
2. Call each agent in parallel (CommunityInsight, ContentAnalysis, TrendDiscovery)
3. Collect agent responses
4. Initiate forum discussion via ForumEngine
5. Store discussion messages with demand_id link
6. Generate consensus summary

### 4. ReportGenerator

**Purpose**: Generate single-demand and time-range reports

**Interface**:
```python
class ReportGenerator:
    def generate_single_demand_report(self, demand_id: int) -> Tuple[int, str]
    def generate_time_range_report(self, start_date: datetime, end_date: datetime, 
                                   community_ids: List[int] = None) -> Tuple[int, str]
    def get_report_template(self, report_type: str) -> str
    def render_report(self, template: str, data: Dict[str, Any]) -> str
```

**Report Sections**:
- Executive Summary
- Demand Details / Aggregated Statistics
- Agent Analysis Results
- Discussion Transcript
- Trend Visualizations
- Recommendations

### 5. MonitoringTask (Enhanced)

**Purpose**: Execute monitoring for a single community with real-time updates

**Enhanced Methods**:
```python
class MonitoringTask:
    def _broadcast_update(self, update_type: str, data: Dict[str, Any])
    def _check_duplicate(self, signal: DemandSignal) -> bool
    def _trigger_agent_analysis(self, signal_id: int)
```

## Data Models

### Enhanced Database Schema

#### agent_discussions Table (Modified)
```sql
CREATE TABLE agent_discussions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id VARCHAR(255) NOT NULL,
    demand_id INTEGER,  -- NEW: Link to specific demand
    agent_name VARCHAR(50) NOT NULL,
    message_type VARCHAR(20),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- NEW: Renamed from timestamp
    metadata TEXT,
    FOREIGN KEY (demand_id) REFERENCES demand_signals(id)
);

CREATE INDEX idx_agent_discussions_demand ON agent_discussions(demand_id);
CREATE INDEX idx_agent_discussions_session ON agent_discussions(session_id);
```

#### demand_signals Table (Enhanced)
```sql
CREATE TABLE demand_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    community_id INTEGER,
    signal_type VARCHAR(50),
    title TEXT NOT NULL,
    content TEXT,
    source_url TEXT UNIQUE,  -- ENHANCED: Add unique constraint
    content_hash VARCHAR(64),  -- NEW: For duplicate detection
    author VARCHAR(255),
    sentiment_score REAL,
    hotness_score REAL,
    discussion_count INTEGER DEFAULT 0,
    participant_count INTEGER DEFAULT 0,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES communities(id)
);

CREATE INDEX idx_demand_signals_content_hash ON demand_signals(content_hash);
CREATE INDEX idx_demand_signals_url ON demand_signals(source_url);
```

#### communities Table (Enhanced)
```sql
CREATE TABLE communities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    source_url TEXT,
    config TEXT,
    status VARCHAR(20) DEFAULT 'active',
    monitoring_status VARCHAR(20) DEFAULT 'not_started',  -- ENHANCED: Default to not_started
    last_collection_time TIMESTAMP,
    total_signals INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    duplicate_count INTEGER DEFAULT 0,  -- NEW: Track duplicates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Python Models

```python
@dataclass
class DemandSignal:
    signal_type: str
    title: str
    content: str
    source_url: Optional[str] = None
    content_hash: Optional[str] = None
    author: Optional[str] = None
    sentiment_score: Optional[float] = None
    hotness_score: Optional[float] = None
    discussion_count: int = 0
    participant_count: int = 0
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[int] = None
    community_id: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class AgentDiscussion:
    session_id: str
    demand_id: int
    agent_name: str
    content: str
    message_type: Optional[str] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

@dataclass
class DemandReport:
    title: str
    report_type: str  # 'single_demand' or 'time_range'
    content: str
    html_content: str
    communities: List[Dict[str, Any]]
    demand_signals: List[Dict[str, Any]]
    generated_by: str
    id: Optional[int] = None
    created_at: Optional[datetime] = None
```

## Error Handling

### Error Categories

1. **Database Errors**:
   - Connection failures → Retry with exponential backoff
   - Schema mismatches → Log error and alert admin
   - Constraint violations → Skip duplicate, log warning

2. **Crawler Errors**:
   - Network timeouts → Retry up to 3 times
   - Rate limiting → Implement backoff strategy
   - Invalid responses → Log and skip

3. **Agent Errors**:
   - API failures → Retry with different endpoint
   - Timeout → Use cached analysis if available
   - Invalid responses → Log and use fallback

4. **WebSocket Errors**:
   - Connection lost → Client auto-reconnects
   - Broadcast failures → Queue for retry
   - Invalid messages → Log and ignore

### Error Recovery Strategies

- **Graceful Degradation**: System continues without real-time updates if WebSocket fails
- **Retry Logic**: Exponential backoff for transient failures
- **Fallback Mechanisms**: Use cached data when live data unavailable
- **Error Logging**: All errors logged to monitoring_logs table
- **User Notification**: Critical errors shown in UI

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Real-Time Updates Properties

**Property 1: Signal collection triggers updates**
*For any* monitoring task that collects a new demand signal, a WebSocket message should be broadcast with the updated signal count for that community.
**Validates: Requirements 1.1**

**Property 2: Error increments are reflected**
*For any* monitoring task that encounters an error, the error_count field should be incremented and a WebSocket update should be broadcast.
**Validates: Requirements 1.3**

**Property 3: Collection time updates**
*For any* successful signal collection, the last_collection_time field should be updated to the current timestamp.
**Validates: Requirements 1.4**

### Database Schema Properties

**Property 4: Schema validation detects missing columns**
*For any* database schema that is missing required columns (demand_id, created_at in agent_discussions), the validation function should return False and list the missing columns.
**Validates: Requirements 2.5**

### Monitoring Control Properties

**Property 5: Bulk start affects all active communities**
*For any* set of active communities, calling start_all_monitoring() should result in all active communities having monitoring_status = 'running'.
**Validates: Requirements 3.2**

**Property 6: New communities default to not_started**
*For any* newly created community, its monitoring_status should be 'not_started' and no monitoring task should be running for it.
**Validates: Requirements 3.3**

**Property 7: Individual start is isolated**
*For any* community in a set of communities, starting monitoring for that community should not change the monitoring status of other communities.
**Validates: Requirements 3.4**

**Property 8: Individual stop is isolated**
*For any* community in a set of communities, stopping monitoring for that community should not change the monitoring status of other communities.
**Validates: Requirements 3.5**

**Property 9: Bulk stop affects all communities**
*For any* set of communities with running monitoring, calling stop_all_monitoring() should result in all communities having monitoring_status = 'stopped'.
**Validates: Requirements 3.6**

### Duplicate Detection Properties

**Property 10: URL-based duplicate detection**
*For any* two demand signals with the same non-null source_url, the second signal should be detected as a duplicate and not stored.
**Validates: Requirements 5.1, 5.2**

**Property 11: Content-based duplicate detection for signals without URLs**
*For any* two demand signals without source_url but with identical title and content, the second signal should be detected as a duplicate.
**Validates: Requirements 5.3, 5.4**

**Property 12: Time window limits duplicate detection**
*For any* two demand signals with the same source_url but created more than 30 days apart, the second signal should not be detected as a duplicate.
**Validates: Requirements 5.5**

**Property 13: Duplicate counting**
*For any* community, the duplicate_count field should equal the number of signals that were detected as duplicates and not stored.
**Validates: Requirements 5.7**

### Agent Analysis Properties

**Property 14: Signal collection triggers agent analysis**
*For any* newly collected demand signal, the agent orchestrator should be called to initiate analysis.
**Validates: Requirements 6.1**

**Property 15: All agents are invoked**
*For any* demand signal analysis, all three agents (CommunityInsightAgent, ContentAnalysisAgent, TrendDiscoveryAgent) should be invoked.
**Validates: Requirements 6.2, 6.3, 6.4**

**Property 16: Forum discussion follows agent analysis**
*For any* demand signal where all agents have completed analysis, a forum discussion should be initiated.
**Validates: Requirements 6.5**

**Property 17: Discussion messages are persisted**
*For any* forum discussion, all discussion messages should be stored in the agent_discussions table with the correct demand_id.
**Validates: Requirements 6.6, 6.8**

**Property 18: Discussion produces summary**
*For any* completed forum discussion, a consensus summary should be generated and stored.
**Validates: Requirements 6.7**

### Single Demand Report Properties

**Property 19: Report includes demand details**
*For any* single demand report, the report should include the demand signal's title, content, and metadata.
**Validates: Requirements 7.1**

**Property 20: Report includes all discussions**
*For any* single demand report, the report should include all agent discussion messages linked to that demand_id.
**Validates: Requirements 7.2**

**Property 21: Report includes sentiment data**
*For any* single demand report, the report should include the sentiment_score and sentiment analysis results.
**Validates: Requirements 7.3**

**Property 22: Report includes related signals**
*For any* single demand report, the report should include a list of related demand signals based on similarity.
**Validates: Requirements 7.4**

**Property 23: Report includes trend data**
*For any* single demand report, the report should include trend analysis data if available.
**Validates: Requirements 7.5**

**Property 24: Report contains visualizations**
*For any* single demand report HTML, the document should contain chart elements for sentiment and trends.
**Validates: Requirements 7.7**

**Property 25: Report is persisted**
*For any* generated single demand report, a record should be created in the demand_reports table with report_type = 'single_demand'.
**Validates: Requirements 7.8**

### Time-Range Report Properties

**Property 26: Time filtering is accurate**
*For any* time-range report with start and end dates, only demand signals with created_at between those dates should be included.
**Validates: Requirements 8.2**

**Property 27: Trend statistics are calculated**
*For any* time-range report, the report should include calculated growth_rate and hotness_change statistics.
**Validates: Requirements 8.3**

**Property 28: Top items are ranked correctly**
*For any* time-range report, the top pain points and feature requests should be ordered by hotness_score descending.
**Validates: Requirements 8.4**

**Property 29: Community breakdowns are complete**
*For any* time-range report, the report should include statistics grouped by each community that has signals in the time range.
**Validates: Requirements 8.5**

**Property 30: Agent insights are included**
*For any* time-range report, the report should include agent consensus insights from forum discussions.
**Validates: Requirements 8.6**

**Property 31: Report structure is complete**
*For any* time-range report HTML, the document should contain sections for executive summary, detailed analysis, and recommendations.
**Validates: Requirements 8.8**

**Property 32: Time-range report is persisted**
*For any* generated time-range report, a record should be created in the demand_reports table with report_type = 'time_range'.
**Validates: Requirements 8.9**

## Testing Strategy

### Unit Testing

- Test duplicate detection with various content types
- Test content hash generation consistency
- Test agent orchestration workflow
- Test report generation with mock data
- Test WebSocket message formatting
- Test database migration scripts

### Property-Based Testing

Property-based tests will be implemented using the `hypothesis` library for Python. Each correctness property listed above will be implemented as a separate property-based test. Tests will run a minimum of 100 iterations to ensure robustness.

**Test Configuration**:
- Library: hypothesis (Python)
- Minimum iterations: 100
- Random seed: Configurable for reproducibility
- Shrinking: Enabled for minimal failing examples

**Generator Strategies**:
- Community generators: Random communities with various source types
- Signal generators: Random demand signals with/without URLs
- Date generators: Random dates within reasonable ranges
- Content generators: Random text with controlled similarity

### Integration Testing

- Test end-to-end monitoring flow
- Test WebSocket communication
- Test agent forum integration
- Test report generation pipeline
- Test database schema migrations

### Manual Testing

- Test UI responsiveness with real-time updates
- Test monitoring control buttons
- Test report viewing and downloading
- Test error handling and recovery
