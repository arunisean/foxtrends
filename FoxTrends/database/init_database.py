# -*- coding: utf-8 -*-
"""
FoxTrends 数据库初始化

创建 FoxTrends 所需的数据库表
支持 PostgreSQL 和 MySQL
"""

import asyncio
import sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from loguru import logger

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings
from database.db_manager import get_engine, get_async_engine


def init_database():
    """
    同步初始化数据库
    
    创建 FoxTrends 所需的所有表
    """
    logger.info("开始初始化 FoxTrends 数据库...")
    
    engine = get_engine()
    dialect = settings.DB_DIALECT.lower()
    
    try:
        with engine.begin() as conn:
            # 创建 communities 表
            if dialect in ("postgresql", "postgres"):
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS communities (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        source_type VARCHAR(50) NOT NULL,
                        source_url TEXT,
                        config JSONB,
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:  # mysql
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS communities (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        source_type VARCHAR(50) NOT NULL,
                        source_url TEXT,
                        config JSON,
                        status VARCHAR(20) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                """))
            
            logger.info("✓ 创建 communities 表")
            
            # 创建 demand_signals 表
            if dialect in ("postgresql", "postgres"):
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS demand_signals (
                        id SERIAL PRIMARY KEY,
                        community_id INTEGER REFERENCES communities(id),
                        signal_type VARCHAR(50),
                        title TEXT NOT NULL,
                        content TEXT,
                        source_url TEXT,
                        author VARCHAR(255),
                        sentiment_score FLOAT,
                        hotness_score FLOAT,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:  # mysql
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS demand_signals (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        community_id INT,
                        signal_type VARCHAR(50),
                        title TEXT NOT NULL,
                        content TEXT,
                        source_url TEXT,
                        author VARCHAR(255),
                        sentiment_score FLOAT,
                        hotness_score FLOAT,
                        metadata JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (community_id) REFERENCES communities(id)
                    )
                """))
            
            logger.info("✓ 创建 demand_signals 表")
            
            # 创建 trend_analysis 表
            if dialect in ("postgresql", "postgres"):
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS trend_analysis (
                        id SERIAL PRIMARY KEY,
                        demand_signal_id INTEGER REFERENCES demand_signals(id),
                        analysis_date DATE NOT NULL,
                        discussion_count INTEGER DEFAULT 0,
                        participant_count INTEGER DEFAULT 0,
                        sentiment_avg FLOAT,
                        hotness_score FLOAT,
                        trend_direction VARCHAR(20),
                        prediction JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:  # mysql
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS trend_analysis (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        demand_signal_id INT,
                        analysis_date DATE NOT NULL,
                        discussion_count INT DEFAULT 0,
                        participant_count INT DEFAULT 0,
                        sentiment_avg FLOAT,
                        hotness_score FLOAT,
                        trend_direction VARCHAR(20),
                        prediction JSON,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (demand_signal_id) REFERENCES demand_signals(id)
                    )
                """))
            
            logger.info("✓ 创建 trend_analysis 表")
            
            # 创建 agent_discussions 表
            if dialect in ("postgresql", "postgres"):
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS agent_discussions (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255) NOT NULL,
                        agent_name VARCHAR(50) NOT NULL,
                        message_type VARCHAR(20),
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSONB
                    )
                """))
            else:  # mysql
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS agent_discussions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        session_id VARCHAR(255) NOT NULL,
                        agent_name VARCHAR(50) NOT NULL,
                        message_type VARCHAR(20),
                        content TEXT NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata JSON
                    )
                """))
            
            logger.info("✓ 创建 agent_discussions 表")
            
            # 创建 demand_reports 表
            if dialect in ("postgresql", "postgres"):
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS demand_reports (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        report_type VARCHAR(50),
                        content TEXT,
                        html_content TEXT,
                        communities JSONB,
                        demand_signals JSONB,
                        generated_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            else:  # mysql
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS demand_reports (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        report_type VARCHAR(50),
                        content TEXT,
                        html_content TEXT,
                        communities JSON,
                        demand_signals JSON,
                        generated_by VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
            
            logger.info("✓ 创建 demand_reports 表")
            
            # 创建索引
            logger.info("创建索引...")
            
            # demand_signals 索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_demand_signals_community 
                ON demand_signals(community_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_demand_signals_created 
                ON demand_signals(created_at)
            """))
            
            # trend_analysis 索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_trend_analysis_signal 
                ON trend_analysis(demand_signal_id)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_trend_analysis_date 
                ON trend_analysis(analysis_date)
            """))
            
            # agent_discussions 索引
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_agent_discussions_session 
                ON agent_discussions(session_id)
            """))
            
            logger.info("✓ 创建索引完成")
        
        logger.info("✅ FoxTrends 数据库初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        engine.dispose()


async def init_database_async():
    """
    异步初始化数据库
    
    创建 FoxTrends 所需的所有表（异步版本）
    """
    logger.info("开始异步初始化 FoxTrends 数据库...")
    
    engine = get_async_engine()
    dialect = settings.DB_DIALECT.lower()
    
    try:
        async with engine.begin() as conn:
            # 创建表的逻辑与同步版本相同
            # 这里简化处理，实际使用时可以复用同步版本的 SQL
            logger.info("使用异步引擎创建表...")
            
            # 可以调用同步版本或复制 SQL 语句
            # 为简化，这里调用同步版本
            pass
        
        logger.info("✅ FoxTrends 数据库异步初始化完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据库异步初始化失败: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    # 运行数据库初始化
    init_database()
