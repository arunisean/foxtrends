#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重复检测器

负责检测和防止重复的需求信号
"""

import sys
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))
from NicheEngine.models import DemandSignal


class DuplicateDetector:
    """
    重复检测器
    
    职责:
    - 基于URL检测重复
    - 基于内容哈希检测重复
    - 基于相似度检测重复
    - 跟踪重复统计
    """
    
    def __init__(self, db_manager=None):
        """
        初始化重复检测器
        
        Args:
            db_manager: 数据库管理器实例
        """
        if db_manager is None:
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager()
        
        self.db_manager = db_manager
    
    def is_duplicate(self, signal: DemandSignal, community_id: int, 
                    time_window_days: int = 30) -> bool:
        """
        检查需求信号是否重复
        
        Args:
            signal: 需求信号对象
            community_id: 社区ID
            time_window_days: 时间窗口（天）
            
        Returns:
            是否为重复信号
        """
        # 首先检查基于URL的重复
        if signal.source_url:
            duplicate_id = self.check_by_url(signal.source_url, time_window_days)
            if duplicate_id:
                logger.debug(f"检测到URL重复: {signal.source_url} (原始ID: {duplicate_id})")
                return True
        
        # 如果没有URL或URL不重复，检查基于内容的重复
        if signal.title and signal.content:
            duplicate_id = self.check_by_content(
                signal.title, 
                signal.content, 
                community_id,
                time_window_days
            )
            if duplicate_id:
                logger.debug(f"检测到内容重复: {signal.title[:50]}... (原始ID: {duplicate_id})")
                return True
        
        return False
    
    def check_by_url(self, source_url: str, time_window_days: int = 30) -> Optional[int]:
        """
        基于URL检查重复
        
        Args:
            source_url: 源URL
            time_window_days: 时间窗口（天）
            
        Returns:
            如果重复，返回原始信号ID；否则返回None
        """
        if not source_url:
            return None
        
        try:
            from sqlalchemy import text
            
            # 计算时间窗口
            cutoff_date = datetime.now() - timedelta(days=time_window_days)
            
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT id 
                        FROM demand_signals 
                        WHERE source_url = :url 
                        AND created_at >= :cutoff_date
                        LIMIT 1
                    """),
                    {'url': source_url, 'cutoff_date': cutoff_date}
                )
                
                row = result.fetchone()
                if row:
                    return row[0]
            
            return None
            
        except Exception as e:
            logger.error(f"URL重复检查失败: {e}")
            return None
    
    def check_by_content(self, title: str, content: str, community_id: int,
                        time_window_days: int = 30, threshold: float = 0.95) -> Optional[int]:
        """
        基于内容检查重复
        
        Args:
            title: 标题
            content: 内容
            community_id: 社区ID
            time_window_days: 时间窗口（天）
            threshold: 相似度阈值（0.0-1.0）
            
        Returns:
            如果重复，返回原始信号ID；否则返回None
        """
        if not title or not content:
            return None
        
        try:
            # 计算内容哈希
            content_hash = self.compute_content_hash(title, content)
            
            from sqlalchemy import text
            
            # 计算时间窗口
            cutoff_date = datetime.now() - timedelta(days=time_window_days)
            
            with self.db_manager.engine.connect() as conn:
                # 首先检查完全相同的哈希
                result = conn.execute(
                    text("""
                        SELECT id 
                        FROM demand_signals 
                        WHERE content_hash = :hash 
                        AND community_id = :community_id
                        AND created_at >= :cutoff_date
                        LIMIT 1
                    """),
                    {
                        'hash': content_hash, 
                        'community_id': community_id,
                        'cutoff_date': cutoff_date
                    }
                )
                
                row = result.fetchone()
                if row:
                    return row[0]
                
                # 如果没有完全匹配，检查相似内容
                # 获取同一社区在时间窗口内的所有信号
                result = conn.execute(
                    text("""
                        SELECT id, title, content 
                        FROM demand_signals 
                        WHERE community_id = :community_id
                        AND created_at >= :cutoff_date
                        AND content_hash IS NOT NULL
                        ORDER BY created_at DESC
                        LIMIT 100
                    """),
                    {'community_id': community_id, 'cutoff_date': cutoff_date}
                )
                
                # 计算相似度
                for row in result:
                    existing_id, existing_title, existing_content = row
                    similarity = self.calculate_similarity(
                        title, content,
                        existing_title or '', existing_content or ''
                    )
                    
                    if similarity >= threshold:
                        logger.debug(f"检测到高相似度内容: {similarity:.2f}")
                        return existing_id
            
            return None
            
        except Exception as e:
            logger.error(f"内容重复检查失败: {e}")
            return None
    
    def compute_content_hash(self, title: str, content: str) -> str:
        """
        计算内容哈希
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            SHA256哈希值
        """
        # 标准化文本：去除多余空白，转小写
        normalized_title = ' '.join(title.strip().lower().split())
        normalized_content = ' '.join(content.strip().lower().split())
        
        # 组合标题和内容
        combined = f"{normalized_title}|{normalized_content}"
        
        # 计算SHA256哈希
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def calculate_similarity(self, title1: str, content1: str, 
                           title2: str, content2: str) -> float:
        """
        计算两个信号的相似度
        
        使用简单的Jaccard相似度（基于词集合）
        
        Args:
            title1: 第一个信号的标题
            content1: 第一个信号的内容
            title2: 第二个信号的标题
            content2: 第二个信号的内容
            
        Returns:
            相似度分数（0.0-1.0）
        """
        # 组合标题和内容
        text1 = f"{title1} {content1}".lower()
        text2 = f"{title2} {content2}".lower()
        
        # 分词（简单按空格分割）
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # 计算Jaccard相似度
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def get_duplicate_stats(self, community_id: int) -> Dict[str, int]:
        """
        获取社区的重复统计
        
        Args:
            community_id: 社区ID
            
        Returns:
            统计信息字典
        """
        try:
            from sqlalchemy import text
            
            with self.db_manager.engine.connect() as conn:
                # 获取duplicate_count
                result = conn.execute(
                    text("""
                        SELECT duplicate_count 
                        FROM communities 
                        WHERE id = :community_id
                    """),
                    {'community_id': community_id}
                )
                
                row = result.fetchone()
                duplicate_count = row[0] if row else 0
                
                # 获取总信号数
                result = conn.execute(
                    text("""
                        SELECT COUNT(*) 
                        FROM demand_signals 
                        WHERE community_id = :community_id
                    """),
                    {'community_id': community_id}
                )
                
                row = result.fetchone()
                total_signals = row[0] if row else 0
                
                return {
                    'duplicate_count': duplicate_count,
                    'total_signals': total_signals,
                    'unique_signals': total_signals,
                    'duplicate_rate': duplicate_count / (total_signals + duplicate_count) if (total_signals + duplicate_count) > 0 else 0.0
                }
            
        except Exception as e:
            logger.error(f"获取重复统计失败: {e}")
            return {
                'duplicate_count': 0,
                'total_signals': 0,
                'unique_signals': 0,
                'duplicate_rate': 0.0
            }
    
    def increment_duplicate_count(self, community_id: int):
        """
        增加社区的重复计数
        
        Args:
            community_id: 社区ID
        """
        try:
            from sqlalchemy import text
            
            with self.db_manager.engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE communities 
                        SET duplicate_count = duplicate_count + 1 
                        WHERE id = :community_id
                    """),
                    {'community_id': community_id}
                )
            
            logger.debug(f"社区 {community_id} 重复计数已增加")
            
        except Exception as e:
            logger.error(f"增加重复计数失败: {e}")
