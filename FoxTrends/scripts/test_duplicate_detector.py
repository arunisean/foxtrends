#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试DuplicateDetector组件
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from NicheEngine.duplicate_detector import DuplicateDetector
from NicheEngine.models import DemandSignal
from database.db_manager import DatabaseManager
from loguru import logger


def test_content_hash():
    """测试内容哈希计算"""
    logger.info("=" * 60)
    logger.info("测试内容哈希计算")
    logger.info("=" * 60)
    
    detector = DuplicateDetector()
    
    # 测试1: 相同内容应该产生相同哈希
    hash1 = detector.compute_content_hash("Test Title", "Test content here")
    hash2 = detector.compute_content_hash("Test Title", "Test content here")
    
    assert hash1 == hash2, "相同内容应该产生相同哈希"
    logger.info(f"✅ 测试1通过: 相同内容产生相同哈希")
    
    # 测试2: 不同内容应该产生不同哈希
    hash3 = detector.compute_content_hash("Different Title", "Different content")
    
    assert hash1 != hash3, "不同内容应该产生不同哈希"
    logger.info(f"✅ 测试2通过: 不同内容产生不同哈希")
    
    # 测试3: 空白字符标准化
    hash4 = detector.compute_content_hash("  Test   Title  ", "  Test   content   here  ")
    
    assert hash1 == hash4, "空白字符应该被标准化"
    logger.info(f"✅ 测试3通过: 空白字符标准化")
    
    # 测试4: 大小写标准化
    hash5 = detector.compute_content_hash("TEST TITLE", "TEST CONTENT HERE")
    
    assert hash1 == hash5, "大小写应该被标准化"
    logger.info(f"✅ 测试4通过: 大小写标准化")


def test_similarity_calculation():
    """测试相似度计算"""
    logger.info("=" * 60)
    logger.info("测试相似度计算")
    logger.info("=" * 60)
    
    detector = DuplicateDetector()
    
    # 测试1: 完全相同的文本
    sim1 = detector.calculate_similarity(
        "Test Title", "Test content",
        "Test Title", "Test content"
    )
    assert sim1 == 1.0, "完全相同的文本相似度应该为1.0"
    logger.info(f"✅ 测试1通过: 完全相同文本相似度 = {sim1}")
    
    # 测试2: 完全不同的文本
    sim2 = detector.calculate_similarity(
        "Apple Banana", "Orange Grape",
        "Cat Dog", "Bird Fish"
    )
    assert sim2 == 0.0, "完全不同的文本相似度应该为0.0"
    logger.info(f"✅ 测试2通过: 完全不同文本相似度 = {sim2}")
    
    # 测试3: 部分重叠的文本
    sim3 = detector.calculate_similarity(
        "Python Programming", "Learn Python",
        "Python Tutorial", "Python Basics"
    )
    assert 0.0 < sim3 < 1.0, "部分重叠的文本相似度应该在0和1之间"
    logger.info(f"✅ 测试3通过: 部分重叠文本相似度 = {sim3:.2f}")


def test_url_duplicate_detection():
    """测试基于URL的重复检测"""
    logger.info("=" * 60)
    logger.info("测试基于URL的重复检测")
    logger.info("=" * 60)
    
    db = DatabaseManager()
    detector = DuplicateDetector(db)
    
    # 创建测试信号
    signal1 = DemandSignal(
        signal_type='feature_request',
        title='Test Signal 1',
        content='This is a test signal',
        source_url='https://example.com/test1'
    )
    
    signal2 = DemandSignal(
        signal_type='feature_request',
        title='Test Signal 2',
        content='This is another test signal',
        source_url='https://example.com/test1'  # 相同URL
    )
    
    # 第一个信号不应该是重复
    is_dup1 = detector.is_duplicate(signal1, community_id=1)
    logger.info(f"第一个信号重复检测: {is_dup1}")
    
    # 插入第一个信号到数据库
    from sqlalchemy import text
    content_hash = detector.compute_content_hash(signal1.title, signal1.content or '')
    
    with db.engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO demand_signals 
                (community_id, signal_type, title, content, source_url, content_hash)
                VALUES (:community_id, :signal_type, :title, :content, :source_url, :content_hash)
            """),
            {
                'community_id': 1,
                'signal_type': signal1.signal_type,
                'title': signal1.title,
                'content': signal1.content,
                'source_url': signal1.source_url,
                'content_hash': content_hash
            }
        )
    
    # 第二个信号应该被检测为重复（相同URL）
    is_dup2 = detector.is_duplicate(signal2, community_id=1)
    
    assert is_dup2, "相同URL的信号应该被检测为重复"
    logger.info(f"✅ 测试通过: 相同URL被检测为重复")
    
    # 清理测试数据
    with db.engine.begin() as conn:
        conn.execute(
            text("DELETE FROM demand_signals WHERE source_url = :url"),
            {'url': 'https://example.com/test1'}
        )
    
    db.close()


def test_content_duplicate_detection():
    """测试基于内容的重复检测"""
    logger.info("=" * 60)
    logger.info("测试基于内容的重复检测")
    logger.info("=" * 60)
    
    db = DatabaseManager()
    detector = DuplicateDetector(db)
    
    # 创建测试信号（没有URL）
    signal1 = DemandSignal(
        signal_type='pain_point',
        title='Need better documentation',
        content='The current documentation is hard to understand and needs improvement'
    )
    
    signal2 = DemandSignal(
        signal_type='pain_point',
        title='Need better documentation',
        content='The current documentation is hard to understand and needs improvement'
    )
    
    # 第一个信号不应该是重复
    is_dup1 = detector.is_duplicate(signal1, community_id=2)
    logger.info(f"第一个信号重复检测: {is_dup1}")
    
    # 插入第一个信号到数据库
    from sqlalchemy import text
    content_hash = detector.compute_content_hash(signal1.title, signal1.content or '')
    
    with db.engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO demand_signals 
                (community_id, signal_type, title, content, content_hash)
                VALUES (:community_id, :signal_type, :title, :content, :content_hash)
            """),
            {
                'community_id': 2,
                'signal_type': signal1.signal_type,
                'title': signal1.title,
                'content': signal1.content,
                'content_hash': content_hash
            }
        )
    
    # 第二个信号应该被检测为重复（相同内容）
    is_dup2 = detector.is_duplicate(signal2, community_id=2)
    
    assert is_dup2, "相同内容的信号应该被检测为重复"
    logger.info(f"✅ 测试通过: 相同内容被检测为重复")
    
    # 清理测试数据
    with db.engine.begin() as conn:
        conn.execute(
            text("DELETE FROM demand_signals WHERE community_id = 2")
        )
    
    db.close()


def test_duplicate_stats():
    """测试重复统计"""
    logger.info("=" * 60)
    logger.info("测试重复统计")
    logger.info("=" * 60)
    
    db = DatabaseManager()
    detector = DuplicateDetector(db)
    
    # 获取统计
    stats = detector.get_duplicate_stats(community_id=1)
    
    logger.info(f"重复统计: {stats}")
    logger.info(f"✅ 测试通过: 成功获取重复统计")
    
    db.close()


if __name__ == '__main__':
    try:
        test_content_hash()
        test_similarity_calculation()
        test_url_duplicate_detection()
        test_content_duplicate_detection()
        test_duplicate_stats()
        
        logger.info("=" * 60)
        logger.info("✅ 所有测试通过！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        logger.exception(e)
        sys.exit(1)
