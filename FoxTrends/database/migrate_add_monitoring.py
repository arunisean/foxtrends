#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本：添加监控相关字段和表

为现有数据库添加：
1. communities 表的监控相关字段
2. monitoring_logs 表
"""

import sys
from pathlib import Path
from sqlalchemy import text
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from database.db_manager import get_engine


def migrate_database():
    """执行数据库迁移"""
    logger.info("开始数据库迁移：添加监控功能...")
    
    engine = get_engine()
    dialect = settings.DB_DIALECT.lower()
    
    try:
        with engine.begin() as conn:
            # 1. 为 communities 表添加新字段
            logger.info("为 communities 表添加监控相关字段...")
            
            try:
                if dialect == "sqlite":
                    # SQLite 不支持 ADD COLUMN IF NOT EXISTS，需要逐个尝试
                    fields = [
                        ("last_collection_time", "TIMESTAMP"),
                        ("total_signals", "INTEGER DEFAULT 0"),
                        ("error_count", "INTEGER DEFAULT 0"),
                        ("monitoring_status", "VARCHAR(20) DEFAULT 'idle'")
                    ]
                    
                    for field_name, field_type in fields:
                        try:
                            conn.execute(text(f"""
                                ALTER TABLE communities 
                                ADD COLUMN {field_name} {field_type}
                            """))
                            logger.info(f"  ✓ 添加字段: {field_name}")
                        except Exception as e:
                            if "duplicate column name" in str(e).lower():
                                logger.info(f"  - 字段已存在: {field_name}")
                            else:
                                raise
                
                elif dialect in ("postgresql", "postgres"):
                    conn.execute(text("""
                        ALTER TABLE communities 
                        ADD COLUMN IF NOT EXISTS last_collection_time TIMESTAMP,
                        ADD COLUMN IF NOT EXISTS total_signals INTEGER DEFAULT 0,
                        ADD COLUMN IF NOT EXISTS error_count INTEGER DEFAULT 0,
                        ADD COLUMN IF NOT EXISTS monitoring_status VARCHAR(20) DEFAULT 'idle'
                    """))
                    logger.info("  ✓ 添加所有监控字段")
                
                else:  # mysql
                    # MySQL 需要逐个添加
                    fields = [
                        ("last_collection_time", "TIMESTAMP NULL"),
                        ("total_signals", "INT DEFAULT 0"),
                        ("error_count", "INT DEFAULT 0"),
                        ("monitoring_status", "VARCHAR(20) DEFAULT 'idle'")
                    ]
                    
                    for field_name, field_type in fields:
                        try:
                            conn.execute(text(f"""
                                ALTER TABLE communities 
                                ADD COLUMN {field_name} {field_type}
                            """))
                            logger.info(f"  ✓ 添加字段: {field_name}")
                        except Exception as e:
                            if "duplicate column" in str(e).lower():
                                logger.info(f"  - 字段已存在: {field_name}")
                            else:
                                raise
            
            except Exception as e:
                logger.warning(f"添加 communities 字段时出现问题: {e}")
            
            # 2. 创建 monitoring_logs 表
            logger.info("创建 monitoring_logs 表...")
            
            try:
                if dialect == "sqlite":
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS monitoring_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            level VARCHAR(20) NOT NULL,
                            message TEXT NOT NULL,
                            community_id INTEGER,
                            metadata TEXT,
                            FOREIGN KEY (community_id) REFERENCES communities(id)
                        )
                    """))
                elif dialect in ("postgresql", "postgres"):
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS monitoring_logs (
                            id SERIAL PRIMARY KEY,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            level VARCHAR(20) NOT NULL,
                            message TEXT NOT NULL,
                            community_id INTEGER REFERENCES communities(id),
                            metadata JSONB
                        )
                    """))
                else:  # mysql
                    conn.execute(text("""
                        CREATE TABLE IF NOT EXISTS monitoring_logs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            level VARCHAR(20) NOT NULL,
                            message TEXT NOT NULL,
                            community_id INT,
                            metadata JSON,
                            FOREIGN KEY (community_id) REFERENCES communities(id)
                        )
                    """))
                
                logger.info("  ✓ 创建 monitoring_logs 表")
            
            except Exception as e:
                logger.warning(f"创建 monitoring_logs 表时出现问题: {e}")
            
            # 3. 创建索引
            logger.info("创建索引...")
            
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_monitoring_logs_community 
                    ON monitoring_logs(community_id)
                """))
                logger.info("  ✓ 创建 monitoring_logs 社区索引")
            except Exception as e:
                logger.warning(f"创建索引时出现问题: {e}")
            
            try:
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_monitoring_logs_timestamp 
                    ON monitoring_logs(timestamp)
                """))
                logger.info("  ✓ 创建 monitoring_logs 时间索引")
            except Exception as e:
                logger.warning(f"创建索引时出现问题: {e}")
        
        logger.info("✅ 数据库迁移完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    migrate_database()
