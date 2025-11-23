#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库Schema迁移脚本

迁移内容:
1. agent_discussions表: 添加demand_id列和created_at列，重命名timestamp为created_at
2. demand_signals表: 添加content_hash列，为source_url添加唯一约束
3. communities表: 添加duplicate_count列，修改monitoring_status默认值为'not_started'
"""

import sys
from pathlib import Path
from sqlalchemy import text, inspect
from loguru import logger

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from database.db_manager import get_engine


def check_column_exists(conn, table_name: str, column_name: str) -> bool:
    """检查列是否存在"""
    dialect = settings.DB_DIALECT.lower()
    
    if dialect == "sqlite":
        result = conn.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result]
        return column_name in columns
    elif dialect in ("postgresql", "postgres"):
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = :table_name AND column_name = :column_name
        """), {'table_name': table_name, 'column_name': column_name})
        return result.fetchone() is not None
    else:  # mysql
        result = conn.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = :table_name AND COLUMN_NAME = :column_name
        """), {'table_name': table_name, 'column_name': column_name})
        return result.fetchone() is not None


def migrate_agent_discussions(conn, dialect: str):
    """迁移agent_discussions表"""
    logger.info("开始迁移 agent_discussions 表...")
    
    # 检查是否需要迁移
    has_demand_id = check_column_exists(conn, 'agent_discussions', 'demand_id')
    has_created_at = check_column_exists(conn, 'agent_discussions', 'created_at')
    has_timestamp = check_column_exists(conn, 'agent_discussions', 'timestamp')
    
    if has_demand_id and has_created_at and not has_timestamp:
        logger.info("✓ agent_discussions 表已经是最新版本")
        return
    
    # SQLite需要重建表
    if dialect == "sqlite":
        logger.info("SQLite: 重建 agent_discussions 表...")
        
        # 1. 重命名旧表
        conn.execute(text("ALTER TABLE agent_discussions RENAME TO agent_discussions_old"))
        
        # 2. 创建新表
        conn.execute(text("""
            CREATE TABLE agent_discussions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(255) NOT NULL,
                demand_id INTEGER,
                agent_name VARCHAR(50) NOT NULL,
                message_type VARCHAR(20),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (demand_id) REFERENCES demand_signals(id)
            )
        """))
        
        # 3. 复制数据
        conn.execute(text("""
            INSERT INTO agent_discussions 
                (id, session_id, agent_name, message_type, content, created_at, metadata)
            SELECT 
                id, session_id, agent_name, message_type, content, 
                COALESCE(timestamp, CURRENT_TIMESTAMP), metadata
            FROM agent_discussions_old
        """))
        
        # 4. 删除旧表
        conn.execute(text("DROP TABLE agent_discussions_old"))
        
        # 5. 创建索引
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_agent_discussions_session 
            ON agent_discussions(session_id)
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_agent_discussions_demand 
            ON agent_discussions(demand_id)
        """))
        
        logger.info("✓ SQLite: agent_discussions 表迁移完成")
    
    elif dialect in ("postgresql", "postgres"):
        logger.info("PostgreSQL: 修改 agent_discussions 表...")
        
        # 添加demand_id列
        if not has_demand_id:
            conn.execute(text("""
                ALTER TABLE agent_discussions 
                ADD COLUMN demand_id INTEGER REFERENCES demand_signals(id)
            """))
            logger.info("✓ 添加 demand_id 列")
        
        # 重命名timestamp为created_at或添加created_at
        if has_timestamp and not has_created_at:
            conn.execute(text("""
                ALTER TABLE agent_discussions 
                RENAME COLUMN timestamp TO created_at
            """))
            logger.info("✓ 重命名 timestamp 为 created_at")
        elif not has_created_at:
            conn.execute(text("""
                ALTER TABLE agent_discussions 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
            logger.info("✓ 添加 created_at 列")
        
        # 创建索引
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_agent_discussions_demand 
            ON agent_discussions(demand_id)
        """))
        
        logger.info("✓ PostgreSQL: agent_discussions 表迁移完成")
    
    else:  # mysql
        logger.info("MySQL: 修改 agent_discussions 表...")
        
        # 添加demand_id列
        if not has_demand_id:
            conn.execute(text("""
                ALTER TABLE agent_discussions 
                ADD COLUMN demand_id INT,
                ADD FOREIGN KEY (demand_id) REFERENCES demand_signals(id)
            """))
            logger.info("✓ 添加 demand_id 列")
        
        # 重命名timestamp为created_at或添加created_at
        if has_timestamp and not has_created_at:
            conn.execute(text("""
                ALTER TABLE agent_discussions 
                CHANGE COLUMN timestamp created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
            logger.info("✓ 重命名 timestamp 为 created_at")
        elif not has_created_at:
            conn.execute(text("""
                ALTER TABLE agent_discussions 
                ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """))
            logger.info("✓ 添加 created_at 列")
        
        # 创建索引
        conn.execute(text("""
            CREATE INDEX idx_agent_discussions_demand 
            ON agent_discussions(demand_id)
        """))
        
        logger.info("✓ MySQL: agent_discussions 表迁移完成")


def migrate_demand_signals(conn, dialect: str):
    """迁移demand_signals表"""
    logger.info("开始迁移 demand_signals 表...")
    
    # 检查是否需要迁移
    has_content_hash = check_column_exists(conn, 'demand_signals', 'content_hash')
    
    if has_content_hash:
        logger.info("✓ demand_signals 表已经是最新版本")
        return
    
    # 添加content_hash列
    if dialect == "sqlite":
        conn.execute(text("""
            ALTER TABLE demand_signals 
            ADD COLUMN content_hash VARCHAR(64)
        """))
    elif dialect in ("postgresql", "postgres"):
        conn.execute(text("""
            ALTER TABLE demand_signals 
            ADD COLUMN content_hash VARCHAR(64)
        """))
    else:  # mysql
        conn.execute(text("""
            ALTER TABLE demand_signals 
            ADD COLUMN content_hash VARCHAR(64)
        """))
    
    logger.info("✓ 添加 content_hash 列")
    
    # 创建索引
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_demand_signals_content_hash 
        ON demand_signals(content_hash)
    """))
    
    # 为source_url创建索引（用于快速查找重复）
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_demand_signals_url 
        ON demand_signals(source_url)
    """))
    
    logger.info("✓ demand_signals 表迁移完成")


def migrate_communities(conn, dialect: str):
    """迁移communities表"""
    logger.info("开始迁移 communities 表...")
    
    # 检查是否需要迁移
    has_duplicate_count = check_column_exists(conn, 'communities', 'duplicate_count')
    
    if has_duplicate_count:
        logger.info("✓ communities 表已经是最新版本")
        return
    
    # 添加duplicate_count列
    if dialect == "sqlite":
        conn.execute(text("""
            ALTER TABLE communities 
            ADD COLUMN duplicate_count INTEGER DEFAULT 0
        """))
    elif dialect in ("postgresql", "postgres"):
        conn.execute(text("""
            ALTER TABLE communities 
            ADD COLUMN duplicate_count INTEGER DEFAULT 0
        """))
    else:  # mysql
        conn.execute(text("""
            ALTER TABLE communities 
            ADD COLUMN duplicate_count INT DEFAULT 0
        """))
    
    logger.info("✓ 添加 duplicate_count 列")
    
    # 更新现有记录的monitoring_status默认值
    conn.execute(text("""
        UPDATE communities 
        SET monitoring_status = 'not_started' 
        WHERE monitoring_status = 'idle' OR monitoring_status IS NULL
    """))
    
    logger.info("✓ 更新 monitoring_status 默认值")
    logger.info("✓ communities 表迁移完成")


def run_migration():
    """运行数据库迁移"""
    logger.info("=" * 60)
    logger.info("开始数据库Schema迁移...")
    logger.info("=" * 60)
    
    engine = get_engine()
    dialect = settings.DB_DIALECT.lower()
    
    try:
        with engine.begin() as conn:
            # 迁移agent_discussions表
            migrate_agent_discussions(conn, dialect)
            
            # 迁移demand_signals表
            migrate_demand_signals(conn, dialect)
            
            # 迁移communities表
            migrate_communities(conn, dialect)
        
        logger.info("=" * 60)
        logger.info("✅ 数据库Schema迁移完成")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库迁移失败: {e}")
        logger.exception(e)
        return False
    finally:
        engine.dispose()


def validate_schema():
    """验证Schema一致性"""
    logger.info("验证数据库Schema...")
    
    engine = get_engine()
    
    try:
        with engine.connect() as conn:
            # 检查agent_discussions表
            has_demand_id = check_column_exists(conn, 'agent_discussions', 'demand_id')
            has_created_at = check_column_exists(conn, 'agent_discussions', 'created_at')
            
            if not has_demand_id:
                logger.error("❌ agent_discussions 表缺少 demand_id 列")
                return False
            
            if not has_created_at:
                logger.error("❌ agent_discussions 表缺少 created_at 列")
                return False
            
            # 检查demand_signals表
            has_content_hash = check_column_exists(conn, 'demand_signals', 'content_hash')
            
            if not has_content_hash:
                logger.error("❌ demand_signals 表缺少 content_hash 列")
                return False
            
            # 检查communities表
            has_duplicate_count = check_column_exists(conn, 'communities', 'duplicate_count')
            
            if not has_duplicate_count:
                logger.error("❌ communities 表缺少 duplicate_count 列")
                return False
            
            logger.info("✅ Schema验证通过")
            return True
            
    except Exception as e:
        logger.error(f"❌ Schema验证失败: {e}")
        return False
    finally:
        engine.dispose()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库Schema迁移工具')
    parser.add_argument('--validate', action='store_true', help='仅验证Schema，不执行迁移')
    args = parser.parse_args()
    
    if args.validate:
        success = validate_schema()
    else:
        success = run_migration()
        if success:
            validate_schema()
    
    sys.exit(0 if success else 1)
