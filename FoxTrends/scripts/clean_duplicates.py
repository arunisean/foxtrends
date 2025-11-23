#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理数据库中的重复需求信号
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from sqlalchemy import text
from loguru import logger


def clean_duplicate_urls():
    """清理重复的URL"""
    logger.info("=" * 60)
    logger.info("开始清理重复的URL")
    logger.info("=" * 60)
    
    db = DatabaseManager()
    
    try:
        with db.engine.begin() as conn:
            # 查找所有重复的URL
            result = conn.execute(text("""
                SELECT source_url, MIN(id) as keep_id, COUNT(*) as count
                FROM demand_signals
                WHERE source_url IS NOT NULL AND source_url != ''
                GROUP BY source_url
                HAVING COUNT(*) > 1
            """))
            
            duplicates = result.fetchall()
            
            if not duplicates:
                logger.info("没有发现重复的URL")
                return 0
            
            logger.info(f"发现 {len(duplicates)} 个重复的URL")
            
            total_deleted = 0
            
            for url, keep_id, count in duplicates:
                # 删除除了最早的记录之外的所有重复记录
                result = conn.execute(
                    text("""
                        DELETE FROM demand_signals
                        WHERE source_url = :url AND id != :keep_id
                    """),
                    {'url': url, 'keep_id': keep_id}
                )
                
                deleted = result.rowcount
                total_deleted += deleted
                
                logger.info(f"URL: {url[:60]}... - 保留ID {keep_id}, 删除 {deleted} 条重复")
            
            logger.info(f"总共删除了 {total_deleted} 条重复记录")
            
            return total_deleted
            
    except Exception as e:
        logger.error(f"清理失败: {e}")
        raise
    finally:
        db.close()


def clean_duplicate_content():
    """清理重复的内容（基于content_hash）"""
    logger.info("=" * 60)
    logger.info("开始清理重复的内容")
    logger.info("=" * 60)
    
    db = DatabaseManager()
    
    try:
        with db.engine.begin() as conn:
            # 查找所有重复的content_hash
            result = conn.execute(text("""
                SELECT content_hash, MIN(id) as keep_id, COUNT(*) as count
                FROM demand_signals
                WHERE content_hash IS NOT NULL AND content_hash != ''
                GROUP BY content_hash
                HAVING COUNT(*) > 1
            """))
            
            duplicates = result.fetchall()
            
            if not duplicates:
                logger.info("没有发现重复的内容")
                return 0
            
            logger.info(f"发现 {len(duplicates)} 个重复的内容")
            
            total_deleted = 0
            
            for content_hash, keep_id, count in duplicates:
                # 删除除了最早的记录之外的所有重复记录
                result = conn.execute(
                    text("""
                        DELETE FROM demand_signals
                        WHERE content_hash = :hash AND id != :keep_id
                    """),
                    {'hash': content_hash, 'keep_id': keep_id}
                )
                
                deleted = result.rowcount
                total_deleted += deleted
                
                logger.info(f"Content Hash: {content_hash[:16]}... - 保留ID {keep_id}, 删除 {deleted} 条重复")
            
            logger.info(f"总共删除了 {total_deleted} 条重复记录")
            
            return total_deleted
            
    except Exception as e:
        logger.error(f"清理失败: {e}")
        raise
    finally:
        db.close()


def update_community_stats():
    """更新社区的统计信息"""
    logger.info("=" * 60)
    logger.info("更新社区统计信息")
    logger.info("=" * 60)
    
    db = DatabaseManager()
    
    try:
        with db.engine.begin() as conn:
            # 获取所有社区
            result = conn.execute(text("SELECT id, name FROM communities"))
            communities = result.fetchall()
            
            for community_id, name in communities:
                # 计算实际的信号数
                result = conn.execute(
                    text("SELECT COUNT(*) FROM demand_signals WHERE community_id = :id"),
                    {'id': community_id}
                )
                actual_count = result.scalar()
                
                # 更新社区的total_signals
                conn.execute(
                    text("UPDATE communities SET total_signals = :count WHERE id = :id"),
                    {'count': actual_count, 'id': community_id}
                )
                
                logger.info(f"社区 {name} (ID: {community_id}): {actual_count} 个信号")
            
    except Exception as e:
        logger.error(f"更新统计失败: {e}")
        raise
    finally:
        db.close()


def show_statistics():
    """显示清理后的统计信息"""
    logger.info("=" * 60)
    logger.info("数据库统计信息")
    logger.info("=" * 60)
    
    db = DatabaseManager()
    
    try:
        with db.engine.connect() as conn:
            # 总信号数
            result = conn.execute(text("SELECT COUNT(*) FROM demand_signals"))
            total_signals = result.scalar()
            
            # 有URL的信号数
            result = conn.execute(text("""
                SELECT COUNT(*) FROM demand_signals 
                WHERE source_url IS NOT NULL AND source_url != ''
            """))
            signals_with_url = result.scalar()
            
            # 有content_hash的信号数
            result = conn.execute(text("""
                SELECT COUNT(*) FROM demand_signals 
                WHERE content_hash IS NOT NULL AND content_hash != ''
            """))
            signals_with_hash = result.scalar()
            
            # 按社区统计
            result = conn.execute(text("""
                SELECT c.name, COUNT(ds.id) as signal_count
                FROM communities c
                LEFT JOIN demand_signals ds ON c.id = ds.community_id
                GROUP BY c.id, c.name
                ORDER BY signal_count DESC
            """))
            
            logger.info(f"总信号数: {total_signals}")
            logger.info(f"有URL的信号: {signals_with_url}")
            logger.info(f"有content_hash的信号: {signals_with_hash}")
            logger.info("\n按社区统计:")
            
            for name, count in result:
                logger.info(f"  {name}: {count} 个信号")
            
    except Exception as e:
        logger.error(f"获取统计失败: {e}")
    finally:
        db.close()


if __name__ == '__main__':
    try:
        # 显示清理前的统计
        logger.info("清理前:")
        show_statistics()
        
        # 清理重复的URL
        url_deleted = clean_duplicate_urls()
        
        # 清理重复的内容
        content_deleted = clean_duplicate_content()
        
        # 更新社区统计
        update_community_stats()
        
        # 显示清理后的统计
        logger.info("\n清理后:")
        show_statistics()
        
        logger.info("=" * 60)
        logger.info(f"✅ 清理完成！共删除 {url_deleted + content_deleted} 条重复记录")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 清理失败: {e}")
        logger.exception(e)
        sys.exit(1)
