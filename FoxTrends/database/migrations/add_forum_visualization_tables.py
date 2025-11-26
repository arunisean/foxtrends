"""
添加 Forum Visualization 相关表

创建讨论会话、消息、Agent状态和可视化事件表
"""

from sqlalchemy import text
from loguru import logger


def upgrade(engine):
    """升级数据库：添加 Forum Visualization 表"""
    
    logger.info("开始添加 Forum Visualization 表...")
    
    with engine.begin() as conn:
        # 1. 创建 discussion_sessions 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS discussion_sessions (
                id VARCHAR(36) PRIMARY KEY,
                demand_signal_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                consensus_level FLOAT DEFAULT 0.0,
                consensus_summary TEXT,
                metadata JSON,
                FOREIGN KEY (demand_signal_id) REFERENCES demand_signals(id) ON DELETE CASCADE
            )
        """))
        logger.info("✓ 创建 discussion_sessions 表")
        
        # 2. 创建 discussion_messages 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS discussion_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(36) NOT NULL,
                agent_id VARCHAR(50) NOT NULL,
                agent_name VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                message_type VARCHAR(20) NOT NULL DEFAULT 'discussion',
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                agent_references JSON,
                sentiment VARCHAR(20),
                metadata JSON,
                FOREIGN KEY (session_id) REFERENCES discussion_sessions(id) ON DELETE CASCADE
            )
        """))
        logger.info("✓ 创建 discussion_messages 表")
        
        # 3. 创建 agent_states 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agent_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(36) NOT NULL,
                agent_id VARCHAR(50) NOT NULL,
                agent_name VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'idle',
                current_stage INTEGER,
                message_count INTEGER DEFAULT 0,
                last_active TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT,
                metadata JSON,
                FOREIGN KEY (session_id) REFERENCES discussion_sessions(id) ON DELETE CASCADE
            )
        """))
        logger.info("✓ 创建 agent_states 表")
        
        # 4. 创建 visualization_events 表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS visualization_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(36) NOT NULL,
                event_type VARCHAR(50) NOT NULL,
                event_data JSON NOT NULL,
                timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES discussion_sessions(id) ON DELETE CASCADE
            )
        """))
        logger.info("✓ 创建 visualization_events 表")
        
        # 5. 创建索引
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_discussion_sessions_demand 
            ON discussion_sessions(demand_signal_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_discussion_messages_session 
            ON discussion_messages(session_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_discussion_messages_timestamp 
            ON discussion_messages(timestamp)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_agent_states_session 
            ON agent_states(session_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_visualization_events_session 
            ON visualization_events(session_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_visualization_events_timestamp 
            ON visualization_events(timestamp)
        """))
        
        logger.info("✓ 创建索引")
    
    logger.info("✅ Forum Visualization 表创建完成")


def downgrade(engine):
    """降级数据库：删除 Forum Visualization 表"""
    
    logger.info("开始删除 Forum Visualization 表...")
    
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS visualization_events"))
        conn.execute(text("DROP TABLE IF EXISTS agent_states"))
        conn.execute(text("DROP TABLE IF EXISTS discussion_messages"))
        conn.execute(text("DROP TABLE IF EXISTS discussion_sessions"))
        
    logger.info("✅ Forum Visualization 表删除完成")


if __name__ == "__main__":
    # 测试迁移
    from database.db_manager import DatabaseManager
    
    db_manager = DatabaseManager()
    
    print("执行升级...")
    upgrade(db_manager.engine)
    
    print("\n数据库迁移完成！")
