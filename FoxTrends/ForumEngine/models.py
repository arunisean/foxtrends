"""
ForumEngine 数据模型

用于存储讨论会话、消息和可视化数据
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class SessionStatus(str, enum.Enum):
    """会话状态枚举"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageType(str, enum.Enum):
    """消息类型枚举"""
    ANALYSIS = "analysis"
    DISCUSSION = "discussion"
    MODERATION = "moderation"
    SYSTEM = "system"


class AgentStatus(str, enum.Enum):
    """Agent 状态枚举"""
    IDLE = "idle"
    WAITING = "waiting"
    ANALYZING = "analyzing"
    SPEAKING = "speaking"
    COMPLETE = "complete"
    ERROR = "error"


class DiscussionSession(Base):
    """讨论会话模型"""
    __tablename__ = 'discussion_sessions'
    
    id = Column(String(36), primary_key=True)  # UUID
    demand_signal_id = Column(Integer, ForeignKey('demand_signals.id'), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE, nullable=False)
    consensus_level = Column(Float, default=0.0)  # 0.0 to 1.0
    consensus_summary = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)  # 额外的元数据
    
    # 关系
    messages = relationship("DiscussionMessage", back_populates="session", cascade="all, delete-orphan")
    agent_states = relationship("AgentState", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DiscussionSession(id={self.id}, demand_id={self.demand_signal_id}, status={self.status})>"


class DiscussionMessage(Base):
    """讨论消息模型"""
    __tablename__ = 'discussion_messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey('discussion_sessions.id'), nullable=False)
    agent_id = Column(String(50), nullable=False)  # community_insight, content_analysis, etc.
    agent_name = Column(String(100), nullable=False)  # 显示名称
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.DISCUSSION, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    references = Column(JSON, nullable=True)  # 引用的其他 agent IDs
    sentiment = Column(String(20), nullable=True)  # positive, neutral, negative
    metadata = Column(JSON, nullable=True)
    
    # 关系
    session = relationship("DiscussionSession", back_populates="messages")
    
    def __repr__(self):
        return f"<DiscussionMessage(id={self.id}, agent={self.agent_id}, type={self.message_type})>"


class AgentState(Base):
    """Agent 状态模型（用于实时可视化）"""
    __tablename__ = 'agent_states'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey('discussion_sessions.id'), nullable=False)
    agent_id = Column(String(50), nullable=False)
    agent_name = Column(String(100), nullable=False)
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE, nullable=False)
    current_stage = Column(Integer, nullable=True)  # 1, 2, 3 for pipeline stages
    message_count = Column(Integer, default=0)
    last_active = Column(DateTime, default=datetime.utcnow, nullable=False)
    error_message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # 关系
    session = relationship("DiscussionSession", back_populates="agent_states")
    
    def __repr__(self):
        return f"<AgentState(agent={self.agent_id}, status={self.status}, stage={self.current_stage})>"


class VisualizationEvent(Base):
    """可视化事件模型（用于回放）"""
    __tablename__ = 'visualization_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey('discussion_sessions.id'), nullable=False)
    event_type = Column(String(50), nullable=False)  # agent_status_update, new_message, etc.
    event_data = Column(JSON, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<VisualizationEvent(type={self.event_type}, session={self.session_id})>"
