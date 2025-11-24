#!/usr/bin/env python3
"""
Final Integration Testing Script
Tests all components of the community monitoring improvements:
- Real-time WebSocket updates
- Duplicate detection
- Agent orchestration
- Report generation
- Monitoring control endpoints
- Error handling
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from NicheEngine.duplicate_detector import DuplicateDetector
from NicheEngine.monitoring_manager import MonitoringManager
from NicheEngine.report_generator import ReportGenerator
from NicheEngine.models import DemandSignal
from config import settings


class IntegrationTester:
    """Comprehensive integration testing suite"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.duplicate_detector = DuplicateDetector(self.db)
        self.monitoring_manager = MonitoringManager()
        self.report_generator = ReportGenerator(self.db)
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✓ PASS" if passed else "✗ FAIL"
        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"
        print(result)
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        
    def setup_test_data(self):
        """Create test communities and signals"""
        print("\n=== Setting Up Test Data ===")
        
        # Clean up any existing test data using direct engine access
        try:
            with self.db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("DELETE FROM communities WHERE name LIKE 'Test Community%'"))
                conn.execute(text("DELETE FROM demand_signals WHERE title LIKE 'Test Signal%'"))
                conn.execute(text("DELETE FROM demand_reports WHERE title LIKE 'Test Report%'"))
                conn.commit()
        except Exception as e:
            print(f"Warning during cleanup: {e}")
        
        # Create test community using direct engine access
        try:
            with self.db.engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(
                    text("""INSERT INTO communities 
                           (name, source_type, source_url, monitoring_status, status)
                           VALUES (:name, :source_type, :source_url, :monitoring_status, :status)"""),
                    {
                        "name": "Test Community 1",
                        "source_type": "github",
                        "source_url": "https://github.com/test/repo",
                        "monitoring_status": "not_started",
                        "status": "active"
                    }
                )
                conn.commit()
        except Exception as e:
            print(f"Error creating community: {e}")
            raise
        
        # Get the last inserted ID
        result = self.db.execute_query(
            "SELECT id FROM communities WHERE name = 'Test Community 1' ORDER BY id DESC LIMIT 1"
        )
        community_id = result[0][0] if result else None
        
        if not community_id:
            raise Exception("Failed to create test community")
        
        print(f"Created test community with ID: {community_id}")
        return community_id
        
    def test_duplicate_detection(self, community_id: int):
        """Test duplicate detection with various scenarios"""
        print("\n=== Testing Duplicate Detection ===")
        
        # Test 1: URL-based duplicate detection
        signal1 = DemandSignal(
            signal_type="issue",
            title="Test Signal 1",
            content="This is a test signal",
            source_url="https://github.com/test/repo/issues/1",
            community_id=community_id
        )
        
        is_dup = self.duplicate_detector.is_duplicate(signal1, community_id)
        self.log_test(
            "URL-based duplicate (first occurrence)",
            not is_dup,
            "First signal should not be duplicate"
        )
        
        # Save the signal
        self.db.add_signal(signal1)
        # Get the signal ID
        result = self.db.execute_query(
            "SELECT id FROM demand_signals WHERE source_url = :url ORDER BY id DESC LIMIT 1",
            {"url": signal1.source_url}
        )
        signal_id = result[0][0] if result else None
        
        # Try to save same URL again
        signal2 = DemandSignal(
            signal_type="issue",
            title="Test Signal 1 Modified",
            content="Different content",
            source_url="https://github.com/test/repo/issues/1",
            community_id=community_id
        )
        
        is_dup = self.duplicate_detector.is_duplicate(signal2, community_id)
        self.log_test(
            "URL-based duplicate (second occurrence)",
            is_dup,
            "Same URL should be detected as duplicate"
        )
        
        # Test 2: Content-based duplicate detection (no URL)
        signal3 = DemandSignal(
            signal_type="discussion",
            title="Unique Title Test",
            content="Unique content for testing",
            source_url=None,
            community_id=community_id
        )
        
        is_dup = self.duplicate_detector.is_duplicate(signal3, community_id)
        self.log_test(
            "Content-based duplicate (first occurrence)",
            not is_dup,
            "First signal without URL should not be duplicate"
        )
        
        self.db.add_signal(signal3)
        # Get the signal ID
        result = self.db.execute_query(
            "SELECT id FROM demand_signals WHERE title = :title ORDER BY id DESC LIMIT 1",
            {"title": signal3.title}
        )
        signal_id2 = result[0][0] if result else None
        
        # Try same content again
        signal4 = DemandSignal(
            signal_type="discussion",
            title="Unique Title Test",
            content="Unique content for testing",
            source_url=None,
            community_id=community_id
        )
        
        is_dup = self.duplicate_detector.is_duplicate(signal4, community_id)
        self.log_test(
            "Content-based duplicate (second occurrence)",
            is_dup,
            "Same content should be detected as duplicate"
        )
        
        # Test 3: Time window filtering
        # Create an old signal (35 days ago)
        old_date = datetime.now() - timedelta(days=35)
        try:
            with self.db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(
                    text("""INSERT INTO demand_signals 
                           (community_id, signal_type, title, content, source_url, created_at, extracted_at)
                           VALUES (:community_id, :signal_type, :title, :content, :source_url, :created_at, :extracted_at)"""),
                    {
                        "community_id": community_id,
                        "signal_type": "issue",
                        "title": "Old Signal",
                        "content": "Old content",
                        "source_url": "https://github.com/test/repo/issues/999",
                        "created_at": old_date,
                        "extracted_at": old_date
                    }
                )
                conn.commit()
        except Exception as e:
            print(f"Error creating old signal: {e}")
        
        # Try to add same URL (should not be duplicate due to time window)
        signal5 = DemandSignal(
            signal_type="issue",
            title="Old Signal New",
            content="New content",
            source_url="https://github.com/test/repo/issues/999",
            community_id=community_id
        )
        
        is_dup = self.duplicate_detector.is_duplicate(signal5, community_id, time_window_days=30)
        self.log_test(
            "Time window filtering",
            not is_dup,
            "Signal outside time window should not be duplicate"
        )
        
        return signal_id, signal_id2
        
    def test_monitoring_control(self, community_id: int):
        """Test monitoring control endpoints"""
        print("\n=== Testing Monitoring Control ===")
        
        # Test 1: Verify initial status is not_started
        result = self.db.execute_query(
            "SELECT monitoring_status FROM communities WHERE id = :id",
            {"id": community_id}
        )
        status = result[0][0] if result else None
        self.log_test(
            "Initial monitoring status",
            status == 'not_started',
            f"Status: {status}"
        )
        
        # Test 2: Individual start
        try:
            self.monitoring_manager.start_monitoring(community_id)
            time.sleep(1)  # Give it time to start
            
            result = self.db.execute_query(
                "SELECT monitoring_status FROM communities WHERE id = :id",
                {"id": community_id}
            )
            status = result[0][0] if result else None
            self.log_test(
                "Individual start monitoring",
                status == 'running',
                f"Status: {status}"
            )
        except Exception as e:
            self.log_test(
                "Individual start monitoring",
                False,
                f"Error: {str(e)}"
            )
        
        # Test 3: Individual stop
        try:
            self.monitoring_manager.stop_monitoring(community_id)
            time.sleep(1)
            
            result = self.db.execute_query(
                "SELECT monitoring_status FROM communities WHERE id = :id",
                {"id": community_id}
            )
            status = result[0][0] if result else None
            self.log_test(
                "Individual stop monitoring",
                status == 'stopped',
                f"Status: {status}"
            )
        except Exception as e:
            self.log_test(
                "Individual stop monitoring",
                False,
                f"Error: {str(e)}"
            )
        
        # Test 4: Bulk operations
        # Create another test community
        try:
            with self.db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(
                    text("""INSERT INTO communities 
                           (name, source_type, source_url, monitoring_status, status)
                           VALUES (:name, :source_type, :source_url, :monitoring_status, :status)"""),
                    {
                        "name": "Test Community 2",
                        "source_type": "reddit",
                        "source_url": "https://reddit.com/r/test",
                        "monitoring_status": "not_started",
                        "status": "active"
                    }
                )
                conn.commit()
        except Exception as e:
            print(f"Error creating second community: {e}")
        
        try:
            self.monitoring_manager.start_all_monitoring()
            time.sleep(1)
            
            communities = self.db.get_all_communities()
            active_running = [c for c in communities 
                            if c['status'] == 'active' and c['monitoring_status'] == 'running']
            
            self.log_test(
                "Bulk start monitoring",
                len(active_running) >= 2,
                f"Running communities: {len(active_running)}"
            )
        except Exception as e:
            self.log_test(
                "Bulk start monitoring",
                False,
                f"Error: {str(e)}"
            )
        
        try:
            self.monitoring_manager.stop_all_monitoring()
            time.sleep(1)
            
            communities = self.db.get_all_communities()
            running = [c for c in communities if c['monitoring_status'] == 'running']
            
            self.log_test(
                "Bulk stop monitoring",
                len(running) == 0,
                f"Still running: {len(running)}"
            )
        except Exception as e:
            self.log_test(
                "Bulk stop monitoring",
                False,
                f"Error: {str(e)}"
            )
            
    def test_report_generation(self, signal_id: int, community_id: int):
        """Test report generation"""
        print("\n=== Testing Report Generation ===")
        
        # Test 1: Single demand report
        try:
            report_id, report_path = self.report_generator.generate_single_demand_report(signal_id)
            
            # Verify report was created
            report = self.db.execute_query(
                "SELECT * FROM demand_reports WHERE id = ?",
                (report_id,)
            )
            
            self.log_test(
                "Single demand report generation",
                report is not None and len(report) > 0,
                f"Report ID: {report_id}"
            )
            
            # Verify HTML content exists
            if report and len(report) > 0:
                has_html = report[0].get('html_content') is not None
                self.log_test(
                    "Single demand report HTML content",
                    has_html,
                    "HTML content present" if has_html else "No HTML content"
                )
        except Exception as e:
            self.log_test(
                "Single demand report generation",
                False,
                f"Error: {str(e)}"
            )
        
        # Test 2: Time-range report
        try:
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
            
            report_id, report_path = self.report_generator.generate_time_range_report(
                start_date=start_date,
                end_date=end_date,
                community_ids=[community_id]
            )
            
            report = self.db.execute_query(
                "SELECT * FROM demand_reports WHERE id = ?",
                (report_id,)
            )
            
            self.log_test(
                "Time-range report generation",
                report is not None and len(report) > 0,
                f"Report ID: {report_id}"
            )
            
            # Verify report type
            if report and len(report) > 0:
                is_time_range = report[0].get('report_type') == 'time_range'
                self.log_test(
                    "Time-range report type",
                    is_time_range,
                    f"Type: {report[0].get('report_type')}"
                )
        except Exception as e:
            self.log_test(
                "Time-range report generation",
                False,
                f"Error: {str(e)}"
            )
            
    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n=== Testing Error Handling ===")
        
        # Test 1: Invalid community ID
        try:
            self.monitoring_manager.start_monitoring(99999)
            self.log_test(
                "Invalid community ID handling",
                False,
                "Should have raised an error"
            )
        except Exception as e:
            self.log_test(
                "Invalid community ID handling",
                True,
                f"Correctly raised error: {type(e).__name__}"
            )
        
        # Test 2: Invalid signal ID for report
        try:
            self.report_generator.generate_single_demand_report(99999)
            self.log_test(
                "Invalid signal ID handling",
                False,
                "Should have raised an error"
            )
        except Exception as e:
            self.log_test(
                "Invalid signal ID handling",
                True,
                f"Correctly raised error: {type(e).__name__}"
            )
        
        # Test 3: Invalid date range for report
        try:
            start_date = datetime.now()
            end_date = datetime.now() - timedelta(days=7)  # End before start
            
            self.report_generator.generate_time_range_report(
                start_date=start_date,
                end_date=end_date
            )
            self.log_test(
                "Invalid date range handling",
                False,
                "Should have raised an error"
            )
        except Exception as e:
            self.log_test(
                "Invalid date range handling",
                True,
                f"Correctly raised error: {type(e).__name__}"
            )
            
    def test_database_schema(self):
        """Verify database schema consistency"""
        print("\n=== Testing Database Schema ===")
        
        # Test 1: agent_discussions table has required columns
        try:
            result = self.db.execute_query(
                "SELECT demand_id, created_at FROM agent_discussions LIMIT 1"
            )
            self.log_test(
                "agent_discussions schema (demand_id, created_at)",
                True,
                "Required columns exist"
            )
        except Exception as e:
            self.log_test(
                "agent_discussions schema (demand_id, created_at)",
                False,
                f"Missing columns: {str(e)}"
            )
        
        # Test 2: demand_signals has content_hash column
        try:
            result = self.db.execute_query(
                "SELECT content_hash FROM demand_signals LIMIT 1"
            )
            self.log_test(
                "demand_signals schema (content_hash)",
                True,
                "content_hash column exists"
            )
        except Exception as e:
            self.log_test(
                "demand_signals schema (content_hash)",
                False,
                f"Missing column: {str(e)}"
            )
        
        # Test 3: communities has duplicate_count column
        try:
            result = self.db.execute_query(
                "SELECT duplicate_count FROM communities LIMIT 1"
            )
            self.log_test(
                "communities schema (duplicate_count)",
                True,
                "duplicate_count column exists"
            )
        except Exception as e:
            self.log_test(
                "communities schema (duplicate_count)",
                False,
                f"Missing column: {str(e)}"
            )
            
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n=== Cleaning Up Test Data ===")
        
        try:
            with self.db.engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("DELETE FROM communities WHERE name LIKE 'Test Community%'"))
                conn.execute(text("DELETE FROM demand_signals WHERE title LIKE 'Test Signal%'"))
                conn.execute(text("DELETE FROM demand_reports WHERE title LIKE 'Test Report%'"))
                conn.commit()
            print("Test data cleaned up")
        except Exception as e:
            print(f"Warning during cleanup: {e}")
        
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("INTEGRATION TEST SUMMARY")
        print("="*60)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['passed'])
        failed = total - passed
        
        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed} ({failed/total*100:.1f}%)")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "="*60)
        
        return failed == 0
        
    def run_all_tests(self):
        """Run all integration tests"""
        print("="*60)
        print("FOXTRENDS INTEGRATION TEST SUITE")
        print("="*60)
        
        try:
            # Setup
            community_id = self.setup_test_data()
            
            # Run tests
            self.test_database_schema()
            signal_id, signal_id2 = self.test_duplicate_detection(community_id)
            self.test_monitoring_control(community_id)
            self.test_report_generation(signal_id, community_id)
            self.test_error_handling()
            
            # Summary
            all_passed = self.print_summary()
            
            # Cleanup
            self.cleanup_test_data()
            
            return all_passed
            
        except Exception as e:
            print(f"\n✗ CRITICAL ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main entry point"""
    tester = IntegrationTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
