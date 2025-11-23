# Implementation Plan

- [x] 1. Database Schema Migration
  - Create migration script to add missing columns to agent_discussions table
  - Add demand_id column with foreign key to demand_signals
  - Rename timestamp column to created_at
  - Add content_hash column to demand_signals table
  - Add duplicate_count column to communities table
  - Update monitoring_status default value to 'not_started'
  - Create indexes for performance optimization
  - _Requirements: 2.1, 2.2, 5.6_

- [ ]* 1.1 Write property test for schema validation
  - **Property 4: Schema validation detects missing columns**
  - **Validates: Requirements 2.5**

- [x] 2. Implement DuplicateDetector Component
  - Create DuplicateDetector class with URL-based detection
  - Implement content-based duplicate detection using content hashing
  - Add time window filtering (30 days)
  - Implement similarity calculation for fuzzy matching
  - Add duplicate statistics tracking
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.7_

- [ ]* 2.1 Write property test for URL-based duplicate detection
  - **Property 10: URL-based duplicate detection**
  - **Validates: Requirements 5.1, 5.2**

- [ ]* 2.2 Write property test for content-based duplicate detection
  - **Property 11: Content-based duplicate detection for signals without URLs**
  - **Validates: Requirements 5.3, 5.4**

- [ ]* 2.3 Write property test for time window filtering
  - **Property 12: Time window limits duplicate detection**
  - **Validates: Requirements 5.5**

- [ ]* 2.4 Write property test for duplicate counting
  - **Property 13: Duplicate counting**
  - **Validates: Requirements 5.7**

- [x] 3. Enhance MonitoringTask with Real-Time Updates
  - Add WebSocket broadcast method to MonitoringTask
  - Integrate DuplicateDetector into signal collection flow
  - Emit WebSocket events on signal collection
  - Emit WebSocket events on status changes
  - Emit WebSocket events on errors
  - Update last_collection_time on successful collection
  - _Requirements: 1.1, 1.3, 1.4, 5.1, 5.2_

- [ ]* 3.1 Write property test for signal collection updates
  - **Property 1: Signal collection triggers updates**
  - **Validates: Requirements 1.1**

- [ ]* 3.2 Write property test for error increments
  - **Property 2: Error increments are reflected**
  - **Validates: Requirements 1.3**

- [ ]* 3.3 Write property test for collection time updates
  - **Property 3: Collection time updates**
  - **Validates: Requirements 1.4**

- [x] 4. Implement Manual Monitoring Control
  - Update system startup to NOT auto-start monitoring
  - Implement start_all_monitoring() method in MonitoringManager
  - Implement stop_all_monitoring() method in MonitoringManager
  - Update add_community() to set monitoring_status = 'not_started'
  - Ensure individual start/stop operations are isolated
  - Add Flask endpoints for bulk start/stop operations
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ]* 4.1 Write property test for bulk start
  - **Property 5: Bulk start affects all active communities**
  - **Validates: Requirements 3.2**

- [ ]* 4.2 Write property test for new community defaults
  - **Property 6: New communities default to not_started**
  - **Validates: Requirements 3.3**

- [ ]* 4.3 Write property test for individual start isolation
  - **Property 7: Individual start is isolated**
  - **Validates: Requirements 3.4**

- [ ]* 4.4 Write property test for individual stop isolation
  - **Property 8: Individual stop is isolated**
  - **Validates: Requirements 3.5**

- [ ]* 4.5 Write property test for bulk stop
  - **Property 9: Bulk stop affects all communities**
  - **Validates: Requirements 3.6**

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement AgentOrchestrator Component
  - Create AgentOrchestrator class
  - Implement analyze_signal() method to call all three agents
  - Implement initiate_forum_discussion() method
  - Implement store_discussion() method with demand_id linking
  - Implement get_discussion_summary() method
  - Integrate with ForumEngine for agent discussions
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [ ]* 6.1 Write property test for agent analysis trigger
  - **Property 14: Signal collection triggers agent analysis**
  - **Validates: Requirements 6.1**

- [ ]* 6.2 Write property test for all agents invoked
  - **Property 15: All agents are invoked**
  - **Validates: Requirements 6.2, 6.3, 6.4**

- [ ]* 6.3 Write property test for forum discussion sequencing
  - **Property 16: Forum discussion follows agent analysis**
  - **Validates: Requirements 6.5**

- [ ]* 6.4 Write property test for discussion persistence
  - **Property 17: Discussion messages are persisted**
  - **Validates: Requirements 6.6, 6.8**

- [ ]* 6.5 Write property test for discussion summary
  - **Property 18: Discussion produces summary**
  - **Validates: Requirements 6.7**

- [ ] 7. Integrate AgentOrchestrator with MonitoringTask
  - Add agent analysis trigger after signal collection
  - Handle agent analysis errors gracefully
  - Log agent analysis progress
  - Update signal metadata with analysis results
  - _Requirements: 6.1_

- [ ] 8. Implement ReportGenerator Component
  - Create ReportGenerator class
  - Implement generate_single_demand_report() method
  - Implement generate_time_range_report() method
  - Create HTML report templates
  - Implement data gathering for reports
  - Implement visualization generation (charts)
  - Implement report persistence to demand_reports table
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9_

- [ ]* 8.1 Write property test for single demand report completeness
  - **Property 19: Report includes demand details**
  - **Validates: Requirements 7.1**

- [ ]* 8.2 Write property test for report discussion inclusion
  - **Property 20: Report includes all discussions**
  - **Validates: Requirements 7.2**

- [ ]* 8.3 Write property test for report sentiment data
  - **Property 21: Report includes sentiment data**
  - **Validates: Requirements 7.3**

- [ ]* 8.4 Write property test for report related signals
  - **Property 22: Report includes related signals**
  - **Validates: Requirements 7.4**

- [ ]* 8.5 Write property test for report trend data
  - **Property 23: Report includes trend data**
  - **Validates: Requirements 7.5**

- [ ]* 8.6 Write property test for report visualizations
  - **Property 24: Report contains visualizations**
  - **Validates: Requirements 7.7**

- [ ]* 8.7 Write property test for single report persistence
  - **Property 25: Report is persisted**
  - **Validates: Requirements 7.8**

- [ ]* 8.8 Write property test for time filtering accuracy
  - **Property 26: Time filtering is accurate**
  - **Validates: Requirements 8.2**

- [ ]* 8.9 Write property test for trend statistics
  - **Property 27: Trend statistics are calculated**
  - **Validates: Requirements 8.3**

- [ ]* 8.10 Write property test for top items ranking
  - **Property 28: Top items are ranked correctly**
  - **Validates: Requirements 8.4**

- [ ]* 8.11 Write property test for community breakdowns
  - **Property 29: Community breakdowns are complete**
  - **Validates: Requirements 8.5**

- [ ]* 8.12 Write property test for agent insights inclusion
  - **Property 30: Agent insights are included**
  - **Validates: Requirements 8.6**

- [ ]* 8.13 Write property test for report structure
  - **Property 31: Report structure is complete**
  - **Validates: Requirements 8.8**

- [ ]* 8.14 Write property test for time-range report persistence
  - **Property 32: Time-range report is persisted**
  - **Validates: Requirements 8.9**

- [ ] 9. Add Flask API Endpoints for Reports
  - Add POST /api/demands/{id}/report endpoint for single demand reports
  - Add POST /api/reports/time-range endpoint for time-range reports
  - Add GET /api/reports/{id} endpoint to retrieve reports
  - Add error handling for report generation failures
  - _Requirements: 7.1, 8.1_

- [x] 10. Update Frontend Dashboard
  - Add WebSocket connection handling
  - Update community cards to show real-time updates
  - Replace "Details" button with "Start" and "Stop" buttons
  - Add global "Start All" and "Stop All" buttons
  - Add "Generate Report" button for single demands
  - Add "Generate Time-Range Report" form
  - Update UI to show monitoring status clearly
  - Handle WebSocket reconnection on connection loss
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.2, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 11. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Integration and End-to-End Testing
  - Test complete monitoring flow with real-time updates
  - Test duplicate detection with various scenarios
  - Test agent analysis and forum discussion flow
  - Test single demand report generation
  - Test time-range report generation
  - Test WebSocket communication under load
  - Test error handling and recovery
  - _Requirements: All_

- [ ] 13. Documentation and Deployment
  - Update README with new features
  - Document API endpoints
  - Document WebSocket events
  - Document report generation usage
  - Update database migration instructions
  - Create user guide for monitoring controls
  - _Requirements: All_
