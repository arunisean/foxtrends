# Implementation Plan

- [x] 1. Backend Infrastructure Setup
  - Create forum_visualizer.py module in ForumEngine/
  - Implement DiscussionSession model with SQLAlchemy
  - Implement DiscussionMessage model with agent references
  - Implement AgentState model for status tracking
  - Implement VisualizationEvent model for replay
  - Add database tables for visualization data
  - Create migration script for new tables
  - _Requirements: All backend data models_

- [ ]* 1.1 Write property test for agent position calculation
  - **Property 1: Agent Position Consistency**
  - **Validates: Requirements 1.1, 1.2, 1.8**

- [x] 2. WebSocket Broadcasting System
  - Create websocket_broadcaster.py in ForumEngine/
  - Implement event broadcasting for agent status changes
  - Implement event broadcasting for new messages
  - Implement event broadcasting for progress updates
  - Implement event broadcasting for consensus reached
  - Implement event broadcasting for stage changes
  - Implement event broadcasting for errors
  - Add WebSocket namespace for forum visualization
  - _Requirements: 2.6, 3.1, 4.3, 5.1, 7.6_

- [ ]* 2.1 Write property test for status update propagation
  - **Property 2: Status Update Propagation**
  - **Validates: Requirements 2.1-2.6**

- [x] 3. Frontend Project Structure
  - Create FoxTrends/static/js/forum-visualization/ directory
  - Create FoxTrends/static/css/forum-visualization/ directory
  - Set up module structure for components
  - _Requirements: All frontend components_

- [x] 4. WebSocket Client Implementation
  - Create websocket-client.js utility
  - Implement Socket.IO client connection
  - Implement event listeners for all event types
  - Implement automatic reconnection logic
  - Implement connection status indicator
  - Add error handling and fallback to polling
  - _Requirements: 2.6, Error Handling_

- [x] 5. RoundTableView Component
  - Create RoundTableView.js component
  - Implement circular layout with fixed positions
  - Implement agent positioning for 3 agents
  - Implement responsive layout resizing
  - Implement mobile vertical layout transformation
  - Add center position for Forum Host
  - Integrate with WebSocket for real-time updates
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 9.1, 9.2_

- [ ]* 5.1 Write property test for position consistency
  - **Property 1: Agent Position Consistency**
  - **Validates: Requirements 1.1, 1.2, 1.8**

- [ ]* 5.2 Write property test for mobile layout transformation
  - **Property 9: Mobile Layout Transformation**
  - **Validates: Requirements 9.1, 9.2, 9.3**

- [x] 6. AgentAvatar Component (Integrated in RoundTableView)
  - Implement avatar rendering with agent name and icon
  - Implement status indicator (idle, waiting, analyzing, speaking, complete, error)
  - Create CSS animations for each status state
  - Implement speaking pulse animation
  - Implement status transition animations
  - _Requirements: 1.7, 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 6.1 Write property test for status indicator rendering
  - **Property 2: Status Update Propagation**
  - **Validates: Requirements 2.1-2.6**

- [x] 7. ForumHost Component (Integrated in RoundTableView)
  - Implement central moderator avatar
  - Implement distinct visual styling for host
  - Add moderation status indicators
  - _Requirements: 1.6, 3.7, 4.7_

- [x] 8. Speaking Turn Visualization (Integrated in RoundTableView)
  - Implement spotlight highlight effect for active speaker
  - Implement smooth transition animations between speakers
  - Add constraint to ensure only one speaker highlighted
  - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6_

- [ ]* 8.1 Write property test for single speaker constraint
  - **Property 3: Single Speaker Constraint**
  - **Validates: Requirements 3.6**

- [x] 9. DiscussionTimeline Component
  - Create DiscussionTimeline.js component
  - Implement scrollable message list
  - Implement message rendering with agent info and timestamp
  - Add visual distinction for different agent messages
  - Implement auto-scroll to latest message
  - Add manual scroll control
  - Style Forum Host messages distinctly
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ]* 9.1 Write property test for message ordering
  - **Property 4: Timeline Message Ordering**
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 10. ProgressIndicator Component (Integrated in RoundTableView)
  - Implement progress bar visualization
  - Add phase labels (Analyzing, Discussing, Consensus)
  - Implement smooth progress transitions
  - _Requirements: 5.1, 5.2, 5.3, 5.6_

- [ ]* 10.1 Write property test for progress monotonicity
  - **Property 5: Progress Monotonicity**
  - **Validates: Requirements 5.1-5.5**

- [x] 11. ConsensusMeter Component (Integrated in RoundTableView)
  - Implement consensus level visualization (0-100%)
  - Implement consensus meter updates
  - Add celebration animation for consensus reached
  - _Requirements: 7.1, 7.2, 7.3, 7.6_

- [ ]* 11.1 Write property test for consensus meter bounds
  - **Property 7: Consensus Meter Bounds**
  - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 12. ForumVisualizationController
  - Create forum-controller.js main controller
  - Integrate RoundTableView and DiscussionTimeline
  - Setup WebSocket event handlers
  - Implement historical data loading
  - Add connection status management
  - _Requirements: All integration_

- [x] 13. Styling and CSS Animations
  - Create round-table.css for layout
  - Create timeline.css for message panel
  - Implement speaking pulse animation
  - Implement status transition animations
  - Add celebration animation
  - Optimize animations for mobile performance
  - _Requirements: All visual requirements_

- [x] 14. Flask API Endpoints



  - Add GET /api/forum/sessions endpoint to list sessions
  - Add GET /api/forum/sessions/<session_id> endpoint for session details
  - Add GET /api/forum/sessions/<session_id>/messages endpoint for messages
  - Add GET /api/forum/sessions/<session_id>/agent-states endpoint for agent states
  - Add GET /api/forum/sessions/<session_id>/replay endpoint for replay data
  - Add WebSocket namespace /forum-visualization with handlers
  - Initialize WebSocketBroadcaster in app.py
  - Implement error handling for missing sessions
  - _Requirements: Backend API_

- [x] 15. Integration with ForumEngine Monitor


  - Modify ForumEngine/monitor.py to create discussion sessions
  - Add session recording when forum starts
  - Emit visualization events via WebSocketBroadcaster
  - Record agent status changes to database
  - Record messages to database
  - Record visualization events for replay
  - Update consensus level when forum completes
  - _Requirements: All integration points_

- [x] 16. Create Standalone Visualization Page


  - Create forum_visualization.html template
  - Add HTML structure for round table and timeline containers
  - Include Socket.IO client library
  - Include all visualization JavaScript files
  - Include all visualization CSS files
  - Initialize ForumVisualizationController
  - Add session selector dropdown
  - Add loading states
  - _Requirements: Standalone page access_

- [x] 17. Integrate Visualization into Demand Detail Page


  - Modify demand_detail.html to add visualization section
  - Replace existing "Agent 分析讨论" section with visualization
  - Add view toggle buttons (Round Table / Timeline)
  - Add HTML containers for visualization components
  - Include visualization JavaScript and CSS files
  - Implement automatic session loading based on demand_id
  - Add error handling for missing or failed discussions
  - Style visualization to match existing page design
  - _Requirements: Integration with existing pages_

- [ ] 18. Session Replay Controller
  - Create replay-controller.js utility
  - Implement replay state management
  - Add play/pause/stop controls UI
  - Implement speed control (0.5x, 1x, 2x, 4x)
  - Add timeline scrubber for navigation
  - Implement event replay with timing
  - Maintain all visual effects during replay
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [ ]* 18.1 Write property test for replay chronological accuracy
  - **Property 8: Replay Chronological Accuracy**
  - **Validates: Requirements 8.2, 8.3, 8.7**

- [x] 19. InteractionLines Component


  - Create InteractionLines.js component
  - Implement SVG line drawing between agents
  - Add animation for line appearance
  - Implement 3-second fade-out timer
  - Support multiple simultaneous connections
  - Parse message content to detect agent references
  - Style Forum Host connections distinctly
  - Integrate into RoundTableView
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [ ]* 19.1 Write property test for connection visibility duration
  - **Property 6: Connection Visibility Duration**
  - **Validates: Requirements 6.3**



- [x] 20. Markdown Rendering for Messages


  - Add markdown library (e.g., marked.js)
  - Implement markdown parsing in DiscussionTimeline
  - Add syntax highlighting for code blocks
  - Sanitize HTML output for security
  - Style markdown content appropriately
  - _Requirements: 4.8_

- [ ] 21. Accessibility Implementation
  - Add ARIA labels to all interactive elements
  - Implement keyboard navigation (Tab, Arrow keys)
  - Add focus indicators for keyboard users
  - Implement screen reader announcements for status changes
  - Create high contrast mode toggle
  - Add "Reduce Motion" toggle
  - Ensure WCAG 2.1 Level AA compliance
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_



- [ ]* 21.1 Write property test for accessibility announcements
  - **Property 10: Accessibility Announcement Completeness**
  - **Validates: Requirements 10.1, 10.2**

- [ ] 22. Mobile Responsive Enhancements
  - Test viewport detection on real devices
  - Verify breakpoint at 768px works correctly



  - Test touch interactions
  - Implement swipe gestures for timeline
  - Optimize performance for mobile browsers
  - Test on iOS and Android devices
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [ ] 23. Add Dashboard Live Discussion Indicators
  - Add "Live Discussion" badge to demand signal cards
  - Implement animated icon for active discussions
  - Add click handler to open demand detail with visualization
  - Show active discussion count on dashboard
  - Add WebSocket listener for live discussion updates
  - _Requirements: Dashboard integration_

- [ ] 24. Performance Optimization
  - Implement virtual scrolling for long timelines
  - Add debouncing for WebSocket events
  - Optimize CSS animations with GPU acceleration
  - Implement lazy loading for historical sessions
  - Test with 100+ messages
  - Optimize for 60 FPS on target devices
  - Add performance monitoring
  - _Requirements: Performance_

- [ ] 25. Testing and Validation
  - Write unit tests for ForumVisualizer methods
  - Write unit tests for WebSocketBroadcaster methods
  - Write integration tests for WebSocket flow
  - Write property-based tests for correctness properties
  - Test replay functionality with recorded sessions
  - Test mobile responsive behavior on real devices
  - Perform cross-browser testing
  - Load test with multiple concurrent users
  - _Requirements: All_

- [ ] 26. Documentation
  - Document component API and props
  - Create user guide for forum visualization
  - Document WebSocket event format
  - Add developer guide for extending visualization
  - Document accessibility features
  - Create troubleshooting guide
  - Add inline code comments
  - _Requirements: All_

- [ ] 27. Final Integration and Polish
  - Ensure all tests pass
  - Fix any remaining bugs
  - Polish animations and transitions
  - Optimize performance
  - Validate accessibility compliance
  - Get user feedback and iterate
  - Prepare for deployment
  - _Requirements: All_
