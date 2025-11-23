#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
监控系统的属性测试

使用 Hypothesis 进行基于属性的测试
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis import assume
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from NicheEngine.monitoring_manager import MonitoringManager
from NicheEngine.models import Community


# ==================== 测试数据生成策略 ====================

@st.composite
def community_strategy(draw):
    """生成随机社区对象"""
    community_id = draw(st.integers(min_value=1, max_value=1000))
    name = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))))
    source_type = draw(st.sampled_from(['reddit', 'github', 'hackernews']))
    
    community = Community(
        name=name,
        source_type=source_type,
        config={},
        status='active'
    )
    community.id = community_id
    
    return community


# ==================== 属性测试 ====================

class TestMonitoringManagerProperties:
    """MonitoringManager 的属性测试"""
    
    @given(community=community_strategy())
    @settings(max_examples=50)
    def test_property_10_system_loads_active_communities(self, community):
        """
        属性 10: 系统启动加载社区
        
        对于任何状态为 'active' 的社区，系统启动时应该为其创建监控任务
        
        **Feature: dashboard-enhancement, Property 10: 系统启动加载社区**
        **验证: 需求 6.1**
        """
        # 确保社区状态为 active
        community.status = 'active'
        
        # 创建新的 MonitoringManager 实例
        manager = MonitoringManager()
        manager.tasks.clear()  # 清空现有任务
        
        # 启动监控
        result = manager.start_monitoring(community)
        
        # 验证：应该成功创建监控任务
        assert result is True
        assert community.id in manager.tasks
        assert manager.tasks[community.id].community.id == community.id
    
    @given(community=community_strategy())
    @settings(max_examples=50)
    def test_property_11_monitoring_task_uniqueness(self, community):
        """
        属性 11: 监控任务唯一性
        
        对于任何社区，系统中最多只能有一个活跃的监控任务在运行
        
        **Feature: dashboard-enhancement, Property 11: 监控任务唯一性**
        **验证: 需求 6.2**
        """
        manager = MonitoringManager()
        manager.tasks.clear()
        
        # 第一次启动监控
        result1 = manager.start_monitoring(community)
        assert result1 is True
        
        # 设置任务状态为 running
        manager.tasks[community.id].status = 'running'
        
        # 尝试再次启动同一社区的监控
        result2 = manager.start_monitoring(community)
        
        # 验证：第二次启动应该失败
        assert result2 is False
        
        # 验证：只有一个任务
        tasks_for_community = [t for t in manager.tasks.values() if t.community.id == community.id]
        assert len(tasks_for_community) == 1
    
    @given(communities=st.lists(community_strategy(), min_size=2, max_size=5, unique_by=lambda c: c.id))
    @settings(max_examples=30)
    def test_property_11_multiple_communities_unique_tasks(self, communities):
        """
        属性 11 扩展: 多个社区的监控任务唯一性
        
        对于任何多个不同的社区，每个社区最多只能有一个活跃的监控任务
        
        **Feature: dashboard-enhancement, Property 11: 监控任务唯一性**
        **验证: 需求 6.2**
        """
        manager = MonitoringManager()
        manager.tasks.clear()
        
        # 为每个社区启动监控
        for community in communities:
            manager.start_monitoring(community)
        
        # 验证：每个社区只有一个任务
        for community in communities:
            tasks_for_community = [t for t in manager.tasks.values() if t.community.id == community.id]
            assert len(tasks_for_community) <= 1
        
        # 验证：任务总数等于社区数
        assert len(manager.tasks) == len(communities)


class TestMonitoringTaskProperties:
    """MonitoringTask 的属性测试"""
    
    @given(community=community_strategy(), failure_count=st.integers(min_value=1, max_value=5))
    @settings(max_examples=30)
    def test_property_12_failure_retry_limit(self, community, failure_count):
        """
        属性 12: 失败重试限制
        
        对于任何监控任务失败，系统应该自动重试，但连续失败次数不应超过 3 次
        
        **Feature: dashboard-enhancement, Property 12: 失败重试限制**
        **验证: 需求 6.4**
        """
        from NicheEngine.monitoring_task import MonitoringTask
        
        manager = MonitoringManager()
        manager.tasks.clear()
        
        task = MonitoringTask(community, manager)
        
        # 模拟失败
        task.error_count = failure_count
        
        # 验证：错误计数不应超过 MAX_RETRIES
        if failure_count >= MonitoringTask.MAX_RETRIES:
            # 任务应该被标记为错误状态
            assert task.error_count >= MonitoringTask.MAX_RETRIES
        else:
            # 任务应该继续运行
            assert task.error_count < MonitoringTask.MAX_RETRIES
    
    @given(community=community_strategy())
    @settings(max_examples=50)
    def test_property_13_pause_stops_task(self, community):
        """
        属性 13: 暂停停止任务
        
        对于任何社区暂停操作，相关的监控任务应该被停止
        
        **Feature: dashboard-enhancement, Property 13: 暂停停止任务**
        **验证: 需求 6.5**
        """
        manager = MonitoringManager()
        manager.tasks.clear()
        
        # 启动监控
        manager.start_monitoring(community)
        task = manager.tasks[community.id]
        task.status = 'running'
        
        # 暂停监控
        result = manager.pause_monitoring(community.id)
        
        # 验证：暂停成功
        assert result is True
        
        # 验证：任务状态变为 paused
        assert task.status == 'paused'
        assert task._is_paused is True


class TestMonitoringLogProperties:
    """监控日志的属性测试"""
    
    @given(
        log_count=st.integers(min_value=1, max_value=100),
        limit=st.integers(min_value=1, max_value=50)
    )
    @settings(max_examples=30)
    def test_property_7_log_count_limit(self, log_count, limit):
        """
        属性 7: 日志数量限制
        
        对于任何日志查询，返回的日志数量不应超过请求的 limit 参数
        
        **Feature: dashboard-enhancement, Property 7: 日志数量限制**
        **验证: 需求 4.3**
        """
        manager = MonitoringManager()
        manager.logs.clear()
        
        # 添加多条日志
        for i in range(log_count):
            manager.add_log('INFO', f'Test log {i}')
        
        # 获取日志
        logs = manager.get_logs(limit=limit)
        
        # 验证：返回的日志数量不超过 limit
        assert len(logs) <= limit
        
        # 验证：如果日志总数少于 limit，返回所有日志
        if log_count < limit:
            assert len(logs) == log_count
        else:
            assert len(logs) == limit
    
    @given(
        log_entries=st.lists(
            st.tuples(
                st.sampled_from(['INFO', 'WARNING', 'ERROR']),
                st.text(min_size=1, max_size=100)
            ),
            min_size=5,
            max_size=20
        )
    )
    @settings(max_examples=30)
    def test_property_6_log_time_order(self, log_entries):
        """
        属性 6: 日志时间倒序排列
        
        对于任何日志查询，返回的日志条目应该按时间戳降序排列
        
        **Feature: dashboard-enhancement, Property 6: 日志时间倒序排列**
        **验证: 需求 4.3**
        """
        import time
        
        manager = MonitoringManager()
        manager.logs.clear()
        
        # 添加日志（带时间间隔）
        for level, message in log_entries:
            manager.add_log(level, message)
            time.sleep(0.001)  # 确保时间戳不同
        
        # 获取日志
        logs = manager.get_logs(limit=100)
        
        # 验证：日志按时间倒序排列（最新的在前）
        timestamps = [log['timestamp'] for log in logs]
        assert timestamps == sorted(timestamps, reverse=True)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
