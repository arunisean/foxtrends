# Forum Visualization Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- FoxTrends application running
- Database initialized
- ForumEngine configured

### Step 1: Run Database Migration

```bash
cd FoxTrends
uv run python database/migrations/add_forum_visualization_tables.py
```

This creates the necessary tables:
- `discussion_sessions`
- `discussion_messages`
- `agent_states`
- `visualization_events`

### Step 2: Start the Application

```bash
cd FoxTrends
uv run python app.py
```

The application will start on `http://localhost:5000`

### Step 3: Access Visualization

#### Option A: Standalone Page
Navigate to: `http://localhost:5000/forum-visualization`

#### Option B: Demand Detail Page
1. Go to dashboard: `http://localhost:5000`
2. Click on any demand signal
3. Scroll to "Agent 讨论可视化" section

## 📖 Usage Guide

### Viewing Live Discussions

1. **Start a Forum Discussion**
   - The ForumEngine monitor automatically creates a session when agents start analyzing
   - Sessions are linked to demand signals

2. **Watch Real-Time Updates**
   - Agent avatars show current status (idle, analyzing, speaking, complete)
   - Messages appear in the timeline as agents contribute
   - Progress bar shows overall completion
   - Consensus meter tracks agreement level

3. **Understand Agent States**
   - 🔵 **Analyzing**: Agent is processing data
   - 🟢 **Speaking**: Agent is contributing to discussion
   - ✅ **Complete**: Agent has finished
   - ⚪ **Waiting**: Agent is waiting for its turn
   - 🔴 **Error**: Agent encountered an issue

### Pipeline Stages

The visualization shows three sequential stages:

1. **Stage 1/3: Community Analysis**
   - Community Insight Agent analyzes historical data
   
2. **Stage 2/3: Content Analysis**
   - Content Analysis Agent examines content patterns
   
3. **Stage 3/3: Trend Discovery**
   - Trend Discovery Agent identifies emerging trends

4. **Discussion Phase**
   - All agents discuss findings
   - Forum Host moderates and summarizes

### View Modes

#### Round Table View
- Circular layout with agents around a table
- Forum Host in the center
- Visual status indicators
- Speaking highlights

#### Timeline View
- Chronological message list
- Agent identification
- Timestamps
- Auto-scroll to latest

## 🔧 Configuration

### Customizing Agent Names

Edit `FoxTrends/ForumEngine/monitor.py`:

```python
agent_names = {
    'community_insight': 'Your Custom Name',
    'content_analysis': 'Your Custom Name',
    'trend_discovery': 'Your Custom Name'
}
```

### Adjusting Stage Names

Edit `FoxTrends/ForumEngine/monitor.py`:

```python
self.stage_names = {
    1: "Your Stage 1 Name",
    2: "Your Stage 2 Name",
    3: "Your Stage 3 Name"
}
```

### Customizing Colors

Edit `FoxTrends/static/css/forum-visualization/round-table.css`:

```css
/* Change primary color */
.stage-indicator {
    background: linear-gradient(135deg, #your-color 0%, #your-color 100%);
}

/* Change agent colors */
.agent-community { color: #your-color; }
.agent-content { color: #your-color; }
.agent-trend { color: #your-color; }
```

## 🐛 Troubleshooting

### No Sessions Appearing

**Problem**: Session selector shows "No sessions available"

**Solutions**:
1. Check if ForumEngine is running: `GET /api/status`
2. Verify database tables exist: Check `discussion_sessions` table
3. Ensure agents have started analyzing: Check agent logs

### WebSocket Not Connecting

**Problem**: Connection status shows "Disconnected"

**Solutions**:
1. Check if Flask-SocketIO is installed: `uv run pip list | grep socketio`
2. Verify port is not blocked: Check firewall settings
3. Check browser console for errors: F12 → Console tab

### Visualization Not Loading

**Problem**: Loading spinner never disappears

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify all JS files are loaded: Network tab in DevTools
3. Check API endpoints are responding: Test `/api/forum/sessions`

### Messages Not Appearing

**Problem**: Timeline is empty despite active discussion

**Solutions**:
1. Check ForumEngine monitor is running: Look for log entries
2. Verify WebSocket events are being emitted: Check server logs
3. Ensure session ID is correct: Check URL or session selector

## 📊 Monitoring

### Check Session Status

```bash
# Using curl
curl http://localhost:5000/api/forum/sessions

# Using Python
import requests
response = requests.get('http://localhost:5000/api/forum/sessions')
print(response.json())
```

### View Session Details

```bash
curl http://localhost:5000/api/forum/sessions/<session-id>
```

### Get Messages

```bash
curl http://localhost:5000/api/forum/sessions/<session-id>/messages
```

### Check Agent States

```bash
curl http://localhost:5000/api/forum/sessions/<session-id>/agent-states
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] Database migration runs successfully
- [ ] Standalone page loads without errors
- [ ] Session selector populates with sessions
- [ ] Selecting a session loads visualization
- [ ] Round table shows all agents
- [ ] Timeline displays messages
- [ ] WebSocket connects successfully
- [ ] Real-time updates work
- [ ] Progress bar updates
- [ ] Consensus meter updates
- [ ] Mobile layout works
- [ ] Demand detail page integration works

### Test with Mock Data

Create a test session:

```python
from ForumEngine.forum_visualizer import get_visualizer

visualizer = get_visualizer()
session_id = visualizer.create_session(demand_signal_id=1)

# Add test messages
visualizer.add_message(
    session_id,
    'community_insight',
    'Community Insight Agent',
    'Test message content',
    'analysis'
)
```

## 📚 API Reference

See `API_ENDPOINTS.md` for complete API documentation.

### Quick Reference

```javascript
// Get sessions
GET /api/forum/sessions?demand_id=123

// Get session details
GET /api/forum/sessions/<session-id>

// Get messages
GET /api/forum/sessions/<session-id>/messages

// Get agent states
GET /api/forum/sessions/<session-id>/agent-states

// WebSocket namespace
/forum-visualization
```

## 🎯 Best Practices

### For Developers

1. **Always check session exists** before initializing visualization
2. **Handle WebSocket disconnections** gracefully
3. **Clean up controllers** on page unload
4. **Use error boundaries** to catch component errors
5. **Test on multiple browsers** and devices

### For Users

1. **Refresh page** if visualization stops updating
2. **Check connection status** indicator
3. **Use timeline view** for detailed message review
4. **Switch to mobile layout** on small screens
5. **Report issues** with session ID for debugging

## 🔗 Related Documentation

- [API Endpoints](./API_ENDPOINTS.md) - Complete API reference
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Technical details
- [Design Document](./design.md) - Architecture and design decisions
- [Requirements](./requirements.md) - Feature requirements

## 💡 Tips & Tricks

### Keyboard Shortcuts
- `Ctrl+R` - Refresh visualization
- `F12` - Open browser DevTools
- `Esc` - Close modals (if any)

### Performance Tips
- Close unused browser tabs
- Use Chrome/Firefox for best performance
- Disable browser extensions if issues occur
- Clear browser cache if visualization doesn't update

### Debugging Tips
- Check browser console for errors
- Monitor Network tab for failed requests
- Use WebSocket frame inspector
- Check server logs for backend errors

## 🆘 Getting Help

### Check Logs
```bash
# Server logs
tail -f FoxTrends/logs/forum.log

# Agent logs
tail -f FoxTrends/logs/community_insight.log
tail -f FoxTrends/logs/content_analysis.log
tail -f FoxTrends/logs/trend_discovery.log
```

### Common Issues

1. **"Session not found"** - Session may have expired or been deleted
2. **"WebSocket connection failed"** - Check if server is running
3. **"No messages"** - Discussion may not have started yet
4. **"Visualization frozen"** - Refresh page or check connection

### Support Resources
- GitHub Issues: Report bugs and feature requests
- Documentation: Check all .md files in specs folder
- Code Comments: Inline documentation in source files

## ✅ Success Checklist

After setup, verify:
- [ ] Database tables created
- [ ] Application starts without errors
- [ ] Standalone page accessible
- [ ] Sessions load in selector
- [ ] Visualization displays correctly
- [ ] WebSocket connects
- [ ] Real-time updates work
- [ ] Demand detail integration works
- [ ] Mobile layout responsive
- [ ] No console errors

**If all checked**: ✅ **You're ready to use Forum Visualization!**
