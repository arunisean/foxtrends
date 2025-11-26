"""
Forum Visualizer

提供 Forum 讨论的可视化数据和 API
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import text
from loguru import logger

from database.db_manager import DatabaseManager


class ForumVisualizer:
    """
    Forum 可视化数据提供器
    
    职责:
    - 创建和管理讨论会话
    - 记录讨论消息
    - 跟踪 Agent 状态
    - 记录可视化事件
    - 提供查询接口
    """
    
    def __init__(self, db_manager: DatabaseManager = None):
        """初始化 Forum Visualizer"""
        if db_manager is None:
            db_manager = DatabaseManager()
        self.db_manager = db_manager
    
    # ==================== 会话管理 ====================
    
    def create_session(self, demand_signal_id: int) -> str:
        """
        创建新的讨论会话
        
        Args:
            demand_signal_id: 需求信号 ID
            
        Returns:
            会话 ID (UUID)
        """
        session_id = str(uuid.uuid4())
        
        try:
            with self.db_manager.engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO discussion_sessions 
                        (id, demand_signal_id, start_time, status)
                        VALUES (:id, :demand_id, :start_time, :status)
                    """),
                    {
                        'id': session_id,
                        'demand_id': demand_signal_id,
                        'start_time': datetime.utcnow(),
                        'status': 'active'
                    }
                )
            
            logger.info(f"ForumVisualizer: 创建会话 {session_id} for demand {demand_signal_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"ForumVisualizer: 创建会话失败: {e}")
            raise
    
    def update_session_status(self, session_id: str, status: str, 
                            consensus_level: float = None, 
                            consensus_summary: str = None):
        """
        更新会话状态
        
        Args:
            session_id: 会话 ID
            status: 新状态 (active, completed, failed)
            consensus_level: 共识水平 (0.0-1.0)
            consensus_summary: 共识总结
        """
        try:
            with self.db_manager.engine.begin() as conn:
                updates = {'status': status}
                
                if status in ['completed', 'failed']:
                    updates['end_time'] = datetime.utcnow()
                
                if consensus_level is not None:
                    updates['consensus_level'] = consensus_level
                
                if consensus_summary is not None:
                    updates['consensus_summary'] = consensus_summary
                
                set_clause = ', '.join([f"{k} = :{k}" for k in updates.keys()])
                
                conn.execute(
                    text(f"""
                        UPDATE discussion_sessions 
                        SET {set_clause}
                        WHERE id = :session_id
                    """),
                    {**updates, 'session_id': session_id}
                )
            
            logger.info(f"ForumVisualizer: 更新会话 {session_id} 状态为 {status}")
            
        except Exception as e:
            logger.error(f"ForumVisualizer: 更新会话状态失败: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话详情
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话数据字典
        """
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT * FROM discussion_sessions 
                        WHERE id = :session_id
                    """),
                    {'session_id': session_id}
                )
                
                row = result.fetchone()
                if row:
                    return dict(row._mapping)
                return None
                
        except Exception as e:
            logger.error(f"ForumVisualizer: 获取会话失败: {e}")
            return None
    
    def get_sessions_by_demand(self, demand_signal_id: int) -> List[Dict[str, Any]]:
        """
        获取需求信号的所有讨论会话
        
        Args:
            demand_signal_id: 需求信号 ID
            
        Returns:
            会话列表
        """
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT * FROM discussion_sessions 
                        WHERE demand_signal_id = :demand_id
                        ORDER BY start_time DESC
                    """),
                    {'demand_id': demand_signal_id}
                )
                
                return [dict(row._mapping) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"ForumVisualizer: 获取会话列表失败: {e}")
            return []
    
    # ==================== 消息管理 ====================
    
    def add_message(self, session_id: str, agent_id: str, agent_name: str,
                   content: str, message_type: str = 'discussion',
                   references: List[str] = None, sentiment: str = None) -> int:
        """
        添加讨论消息
        
        Args:
            session_id: 会话 ID
            agent_id: Agent ID
            agent_name: Agent 显示名称
            content: 消息内容
            message_type: 消息类型
            references: 引用的其他 agent IDs
            sentiment: 情感倾向
            
        Returns:
            消息 ID
        """
        try:
            import json
            
            with self.db_manager.engine.begin() as conn:
                result = conn.execute(
                    text("""
                        INSERT INTO discussion_messages 
                        (session_id, agent_id, agent_name, content, message_type, 
                         timestamp, agent_references, sentiment)
                        VALUES (:session_id, :agent_id, :agent_name, :content, :message_type,
                                :timestamp, :agent_references, :sentiment)
                    """),
                    {
                        'session_id': session_id,
                        'agent_id': agent_id,
                        'agent_name': agent_name,
                        'content': content,
                        'message_type': message_type,
                        'timestamp': datetime.utcnow(),
                        'agent_references': json.dumps(references) if references else None,
                        'sentiment': sentiment
                    }
                )
                
                message_id = result.lastrowid
            
            logger.debug(f"ForumVisualizer: 添加消息 {message_id} from {agent_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"ForumVisualizer: 添加消息失败: {e}")
            raise
    
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话的所有消息
        
        Args:
            session_id: 会话 ID
            
        Returns:
            消息列表
        """
        try:
            import json
            
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT * FROM discussion_messages 
                        WHERE session_id = :session_id
                        ORDER BY timestamp ASC
                    """),
                    {'session_id': session_id}
                )
                
                messages = []
                for row in result.fetchall():
                    msg = dict(row._mapping)
                    # 解析 JSON 字段
                    if msg.get('agent_references'):
                        try:
                            msg['references'] = json.loads(msg['agent_references'])
                        except:
                            msg['references'] = []
                        # 移除原始字段
                        del msg['agent_references']
                    else:
                        msg['references'] = []
                    messages.append(msg)
                
                return messages
                
        except Exception as e:
            logger.error(f"ForumVisualizer: 获取消息失败: {e}")
            return []
    
    # ==================== Agent 状态管理 ====================
    
    def update_agent_state(self, session_id: str, agent_id: str, agent_name: str,
                          status: str, current_stage: int = None, 
                          error_message: str = None):
        """
        更新 Agent 状态
        
        Args:
            session_id: 会话 ID
            agent_id: Agent ID
            agent_name: Agent 显示名称
            status: 状态 (idle, waiting, analyzing, speaking, complete, error)
            current_stage: 当前阶段 (1, 2, 3)
            error_message: 错误消息
        """
        try:
            with self.db_manager.engine.begin() as conn:
                # 检查是否已存在
                result = conn.execute(
                    text("""
                        SELECT id FROM agent_states 
                        WHERE session_id = :session_id AND agent_id = :agent_id
                    """),
                    {'session_id': session_id, 'agent_id': agent_id}
                )
                
                existing = result.fetchone()
                
                if existing:
                    # 更新
                    conn.execute(
                        text("""
                            UPDATE agent_states 
                            SET status = :status, 
                                current_stage = :stage,
                                last_active = :last_active,
                                error_message = :error_message
                            WHERE session_id = :session_id AND agent_id = :agent_id
                        """),
                        {
                            'status': status,
                            'stage': current_stage,
                            'last_active': datetime.utcnow(),
                            'error_message': error_message,
                            'session_id': session_id,
                            'agent_id': agent_id
                        }
                    )
                else:
                    # 插入
                    conn.execute(
                        text("""
                            INSERT INTO agent_states 
                            (session_id, agent_id, agent_name, status, current_stage, 
                             last_active, error_message)
                            VALUES (:session_id, :agent_id, :agent_name, :status, :stage,
                                    :last_active, :error_message)
                        """),
                        {
                            'session_id': session_id,
                            'agent_id': agent_id,
                            'agent_name': agent_name,
                            'status': status,
                            'stage': current_stage,
                            'last_active': datetime.utcnow(),
                            'error_message': error_message
                        }
                    )
            
            logger.debug(f"ForumVisualizer: 更新 Agent {agent_id} 状态为 {status}")
            
        except Exception as e:
            logger.error(f"ForumVisualizer: 更新 Agent 状态失败: {e}")
            raise
    
    def get_agent_states(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话的所有 Agent 状态
        
        Args:
            session_id: 会话 ID
            
        Returns:
            Agent 状态列表
        """
        try:
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT * FROM agent_states 
                        WHERE session_id = :session_id
                        ORDER BY agent_id
                    """),
                    {'session_id': session_id}
                )
                
                return [dict(row._mapping) for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"ForumVisualizer: 获取 Agent 状态失败: {e}")
            return []
    
    # ==================== 可视化事件管理 ====================
    
    def record_event(self, session_id: str, event_type: str, event_data: Dict[str, Any]):
        """
        记录可视化事件（用于回放）
        
        Args:
            session_id: 会话 ID
            event_type: 事件类型
            event_data: 事件数据
        """
        try:
            import json
            
            with self.db_manager.engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO visualization_events 
                        (session_id, event_type, event_data, timestamp)
                        VALUES (:session_id, :event_type, :event_data, :timestamp)
                    """),
                    {
                        'session_id': session_id,
                        'event_type': event_type,
                        'event_data': json.dumps(event_data),
                        'timestamp': datetime.utcnow()
                    }
                )
            
            logger.debug(f"ForumVisualizer: 记录事件 {event_type}")
            
        except Exception as e:
            logger.error(f"ForumVisualizer: 记录事件失败: {e}")
    
    def get_events(self, session_id: str) -> List[Dict[str, Any]]:
        """
        获取会话的所有可视化事件
        
        Args:
            session_id: 会话 ID
            
        Returns:
            事件列表
        """
        try:
            import json
            
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT * FROM visualization_events 
                        WHERE session_id = :session_id
                        ORDER BY timestamp ASC
                    """),
                    {'session_id': session_id}
                )
                
                events = []
                for row in result.fetchall():
                    event = dict(row._mapping)
                    # 解析 JSON 字段
                    if event.get('event_data'):
                        try:
                            event['event_data'] = json.loads(event['event_data'])
                        except:
                            event['event_data'] = {}
                    events.append(event)
                
                return events
                
        except Exception as e:
            logger.error(f"ForumVisualizer: 获取事件失败: {e}")
            return []


# 全局实例
_visualizer_instance = None

def get_visualizer() -> ForumVisualizer:
    """获取全局 ForumVisualizer 实例"""
    global _visualizer_instance
    if _visualizer_instance is None:
        _visualizer_instance = ForumVisualizer()
    return _visualizer_instance
