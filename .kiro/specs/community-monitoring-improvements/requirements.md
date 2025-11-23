# Requirements Document

## Introduction

This specification addresses three critical issues in the FoxTrends community monitoring system:
1. Community cards not displaying real-time content updates after monitoring starts
2. Database schema mismatch causing demand discussion queries to fail
3. Monitoring control flow requiring improvement for better user control

## Glossary

- **Community Card**: UI component displaying a monitored community's status and statistics
- **Monitoring Task**: Background process that collects demand signals from a community
- **Demand Signal**: A piece of content (post, issue, comment) extracted from a community
- **Agent Discussion**: Conversation records between AI agents analyzing demands
- **Monitoring Status**: Current state of a monitoring task (idle, running, paused, stopped)
- **Dashboard**: Web interface for managing communities and viewing demand signals

## Requirements

### Requirement 1: Real-time Community Card Updates

**User Story:** As a user, I want to see real-time updates on community cards when monitoring is active, so that I can track data collection progress without refreshing the page.

#### Acceptance Criteria

1. WHEN a monitoring task collects new demand signals THEN the system SHALL update the community card's signal count immediately
2. WHEN a monitoring task changes status THEN the system SHALL reflect the new status on the community card within 2 seconds
3. WHEN monitoring errors occur THEN the system SHALL display the error count on the community card
4. WHEN the last collection time updates THEN the system SHALL show the updated timestamp on the community card
5. THE system SHALL use WebSocket connections to push real-time updates to connected clients

### Requirement 2: Database Schema Consistency

**User Story:** As a developer, I want the database schema to match the application queries, so that demand discussion retrieval does not fail with column errors.

#### Acceptance Criteria

1. WHEN the agent_discussions table is created THEN the system SHALL include a demand_id column with foreign key reference to demand_signals
2. WHEN the agent_discussions table is created THEN the system SHALL include a created_at column for timestamp tracking
3. WHEN querying agent discussions by demand_id THEN the system SHALL return results without column errors
4. THE system SHALL provide a database migration script to add missing columns to existing tables
5. THE system SHALL validate schema consistency on application startup

### Requirement 3: Manual Monitoring Control

**User Story:** As a user, I want explicit control over when monitoring starts and stops, so that I can manage system resources and avoid unwanted automatic monitoring.

#### Acceptance Criteria

1. WHEN the system starts THEN the system SHALL NOT automatically begin monitoring any communities
2. WHEN a user clicks the global "Start Monitoring" button THEN the system SHALL begin monitoring all active communities
3. WHEN a user adds a new community THEN the system SHALL set its monitoring status to "not_started" and SHALL NOT automatically begin monitoring
4. WHEN a user clicks "Start" on a community card THEN the system SHALL begin monitoring only that specific community
5. WHEN a user clicks "Stop" on a community card THEN the system SHALL stop monitoring only that specific community
6. WHEN a user clicks the global "Stop Monitoring" button THEN the system SHALL stop monitoring all communities
7. THE community card SHALL display "Start" and "Stop" buttons instead of a "Details" button
8. THE community card SHALL show monitoring status (not_started, running, paused, stopped) clearly

### Requirement 4: Simplified Community Card UI

**User Story:** As a user, I want a cleaner community card interface with essential controls, so that I can quickly manage monitoring without unnecessary details.

#### Acceptance Criteria

1. THE community card SHALL display community name, source type, and monitoring status
2. THE community card SHALL display total signals collected and last collection time
3. THE community card SHALL display error count if errors have occurred
4. THE community card SHALL provide "Start" and "Stop" buttons for monitoring control
5. THE community card SHALL NOT include a "Details" button or detailed view
6. WHEN monitoring is running THEN the "Start" button SHALL be disabled
7. WHEN monitoring is stopped or not started THEN the "Stop" button SHALL be disabled

### Requirement 5: Duplicate Content Detection and Prevention

**User Story:** As a user, I want the system to avoid storing duplicate demand signals, so that I see unique content and avoid wasting storage space.

#### Acceptance Criteria

1. WHEN crawling demand signals THEN the system SHALL check for duplicates based on source URL
2. WHEN a demand signal with an existing source URL is found THEN the system SHALL skip storing it
3. WHEN a demand signal has no source URL THEN the system SHALL check for duplicates based on title and content similarity
4. WHEN two demand signals have identical titles and content THEN the system SHALL treat them as duplicates
5. THE system SHALL use a time window of 30 days when checking for duplicates
6. THE database SHALL enforce unique constraints on source_url column where applicable
7. WHEN duplicate detection occurs THEN the system SHALL log the duplicate count for monitoring purposes

### Requirement 6: Complete Agent Analysis and Discussion

**User Story:** As a user, I want AI agents to analyze demand signals and engage in collaborative discussions, so that I receive intelligent insights about community needs.

#### Acceptance Criteria

1. WHEN a new demand signal is collected THEN the system SHALL trigger agent analysis within 5 minutes
2. WHEN agent analysis begins THEN the CommunityInsightAgent SHALL analyze historical context and trends
3. WHEN agent analysis begins THEN the ContentAnalysisAgent SHALL analyze content sentiment and key themes
4. WHEN agent analysis begins THEN the TrendDiscoveryAgent SHALL identify related trends and patterns
5. WHEN all agents complete initial analysis THEN the system SHALL initiate a forum discussion
6. WHEN forum discussion occurs THEN the system SHALL store discussion messages in the agent_discussions table
7. WHEN forum discussion completes THEN the system SHALL generate a consensus summary
8. THE agent_discussions table SHALL link discussions to specific demand signals via demand_id

### Requirement 7: Single Demand Report Generation

**User Story:** As a user, I want to generate a detailed report for a single demand signal, so that I can understand its significance and agent insights.

#### Acceptance Criteria

1. WHEN a user requests a single demand report THEN the system SHALL gather the demand signal details
2. WHEN generating a single demand report THEN the system SHALL include all agent discussion messages
3. WHEN generating a single demand report THEN the system SHALL include sentiment analysis results
4. WHEN generating a single demand report THEN the system SHALL include related demand signals
5. WHEN generating a single demand report THEN the system SHALL include trend analysis data
6. THE single demand report SHALL be formatted as an HTML document
7. THE single demand report SHALL include visualizations for sentiment and trends
8. WHEN report generation completes THEN the system SHALL store the report in the demand_reports table

### Requirement 8: Time-Range Comprehensive Report Generation

**User Story:** As a user, I want to generate comprehensive reports for a specific time period, so that I can analyze demand trends and patterns over time.

#### Acceptance Criteria

1. WHEN a user requests a time-range report THEN the system SHALL accept start and end date parameters
2. WHEN generating a time-range report THEN the system SHALL aggregate all demand signals within the period
3. WHEN generating a time-range report THEN the system SHALL calculate trend statistics (growth rate, hotness changes)
4. WHEN generating a time-range report THEN the system SHALL identify top pain points and feature requests
5. WHEN generating a time-range report THEN the system SHALL include community-level breakdowns
6. WHEN generating a time-range report THEN the system SHALL include agent consensus insights
7. THE time-range report SHALL be formatted as an HTML document with interactive charts
8. THE time-range report SHALL include executive summary, detailed analysis, and recommendations sections
9. WHEN report generation completes THEN the system SHALL store the report in the demand_reports table
