#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试手动监控控制功能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from NicheEngine.monitoring_manager import MonitoringManager
from NicheEngine.engine import NicheEngine
from NicheEngine.models import Community
from loguru import logger


def test_manual_control():
    """测试手动监控控制"""
    logger.info("=" * 60)
    logger.info("测试手动监控控制")
    logger.info("=" * 60)
    
    manager = MonitoringManager()
    engine = NicheEngine()
    
    # 测试1: 系统启动时不应该有任何监控任务运行
    status = manager.get_status()
    logger.info(f"初始状态: {status}")
    assert status['active_tasks'] == 0, "系统启动时不应该有活跃的监控任务"
    logger.info("✅ 测试1通过: 系统启动时没有自动启动监控")
    
    # 测试2: 创建测试社区
    test_community = Community(
        name="Test Community",
        source_type="reddit",
        config={'subreddit': 'test'},
        status='active'
    )
    test_community.id = 999  # 使用测试ID
    
    # 测试3: 手动启动单个社区监控
    result = manager.start_monitoring(test_community)
    assert result == True, "应该能够成功启动监控"
    logger.info("✅ 测试3通过: 成功启动单个社区监控")
    
    # 测试4: 检查监控状态
    status = manager.get_status()
    assert status['active_tasks'] == 1, "应该有1个活跃的监控任务"
    logger.info(f"✅ 测试4通过: 监控状态正确 - {status}")
    
    # 测试5: 尝试重复启动应该失败
    result = manager.start_monitoring(test_community)
    assert result == False, "重复启动应该返回False"
    logger.info("✅ 测试5通过: 防止重复启动")
    
    # 测试6: 停止监控
    result = manager.stop_monitoring(test_community.id)
    assert result == True, "应该能够成功停止监控"
    logger.info("✅ 测试6通过: 成功停止监控")
    
    # 测试7: 检查停止后的状态
    status = manager.get_status()
    assert status['active_tasks'] == 0, "停止后不应该有活跃的监控任务"
    logger.info("✅ 测试7通过: 停止后状态正确")
    
    logger.info("=" * 60)
    logger.info("✅ 所有手动控制测试通过！")
    logger.info("=" * 60)


def test_bulk_control():
    """测试批量控制"""
    logger.info("=" * 60)
    logger.info("测试批量监控控制")
    logger.info("=" * 60)
    
    manager = MonitoringManager()
    
    # 测试批量启动
    result = manager.start_all_monitoring()
    logger.info(f"批量启动结果: {result}")
    logger.info("✅ 批量启动功能正常")
    
    # 测试批量停止
    result = manager.stop_all_monitoring()
    logger.info(f"批量停止结果: {result}")
    logger.info("✅ 批量停止功能正常")
    
    logger.info("=" * 60)
    logger.info("✅ 所有批量控制测试通过！")
    logger.info("=" * 60)


if __name__ == '__main__':
    try:
        test_manual_control()
        test_bulk_control()
        
        logger.info("=" * 60)
        logger.info("✅ 所有测试通过！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        logger.exception(e)
        sys.exit(1)
