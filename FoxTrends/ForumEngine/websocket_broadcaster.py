"""
WebSocket Broadcaster

负责广播 Forum 可视化事件到前端
"""

from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger


class WebSocketBroadcaster:
    """
    WebSocket 事件广播器
    
    职责:
    - 广播 Agent 状态变化
    - 广播新消息
    - 广播进度更新
    - 广播共识达成
    """
    
    def __init__(self, socketio=None):
        """
        初始化广播器
        
        Args:
            socketio: Flask-SocketIO 实例
        """
        self.socketio = socketio
        self.namespace = '/forum-visualization'
    
    def set_socketio(self, socketio):
        """设置 SocketIO 实例"""
        self.socketio = socketio
    
    # ==================== 事件广播方法 ====================
    
    def broadcast_agent_status_update(self, session_id: str, agent_id: str, 
                                     status: str, current_stage: int = None,
                                     error_message: str = None):
        """
        广播 Agent 状态更新
        
        Args:
            session_id: 会话 ID
            agent_id: Agent ID
            status: 新状态
            current_stage: 当前阶段
            error_message: 错误消息
        """
        if not self.socketio:
            logger.warning("WebSocketBroadcaster: SocketIO 未初始化")
            return
        
        event_data = {
            'type': 'agent_status_update',
            'session_id': session_id,
            'agent_id': agent_id,
            'status': status,
            'current_stage': current_stage,
            'error_message': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            self.socketio.emit(
                'agent_status_update',
                event_data,
                namespace=self.namespace,
                room=session_id
            )
            logger.debug(f"WebSocketBroadcaster: 广播 Agent 状态更新 - {agent_id}: {status}")
        except Exception as e:
            logger.error(f"WebSocketBroadcaster: 广播失败: {e}")
    
    def broadcast_new_message(self, session_id: str, message: Dict[str, Any]):
        """
        广播新消息
        
        Args:
            session_id: 会话 ID
            message: 消息数据
        """
        if not self.socketio:
            logger.warning("WebSocketBroadcaster: SocketIO 未初始化")
            return
        
        event_data = {
            'type': 'new_message',
            'session_id': session_id,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            self.socketio.emit(
                'new_message',
                event_data,
                namespace=self.namespace,
                room=session_id
            )
            logger.debug(f"WebSocketBroadcaster: 广播新消息 - {message.get('agent_id')}")
        except Exception as e:
            logger.error(f"WebSocketBroadcaster: 广播失败: {e}")
    
    def broadcast_progress_update(self, session_id: str, phase: str, 
                                 percentage: int, estimated_time_remaining: int = None):
        """
        广播进度更新
        
        Args:
            session_id: 会话 ID
            phase: 当前阶段 (analyzing, discussing, consensus)
            percentage: 进度百分比 (0-100)
            estimated_time_remaining: 预计剩余时间（秒）
        """
        if not self.socketio:
            logger.warning("WebSocketBroadcaster: SocketIO 未初始化")
            return
        
        event_data = {
            'type': 'progress_update',
            'session_id': session_id,
            'phase': phase,
            'percentage': percentage,
            'estimated_time_remaining': estimated_time_remaining,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            self.socketio.emit(
                'progress_update',
                event_data,
                namespace=self.namespace,
                room=session_id
            )
            logger.debug(f"WebSocketBroadcaster: 广播进度更新 - {phase}: {percentage}%")
        except Exception as e:
            logger.error(f"WebSocketBroadcaster: 广播失败: {e}")
    
    def broadcast_consensus_reached(self, session_id: str, consensus_level: float,
                                   summary: str):
        """
        广播共识达成
        
        Args:
            session_id: 会话 ID
            consensus_level: 共识水平 (0.0-1.0)
            summary: 共识总结
        """
        if not self.socketio:
            logger.warning("WebSocketBroadcaster: SocketIO 未初始化")
            return
        
        event_data = {
            'type': 'consensus_reached',
            'session_id': session_id,
            'consensus_level': consensus_level,
            'summary': summary,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            self.socketio.emit(
                'consensus_reached',
                event_data,
                namespace=self.namespace,
                room=session_id
            )
            logger.info(f"WebSocketBroadcaster: 广播共识达成 - {consensus_level:.0%}")
        except Exception as e:
            logger.error(f"WebSocketBroadcaster: 广播失败: {e}")
    
    def broadcast_stage_change(self, session_id: str, stage: int, stage_name: str):
        """
        广播阶段变化
        
        Args:
            session_id: 会话 ID
            stage: 阶段编号 (1, 2, 3)
            stage_name: 阶段名称
        """
        if not self.socketio:
            logger.warning("WebSocketBroadcaster: SocketIO 未初始化")
            return
        
        event_data = {
            'type': 'stage_change',
            'session_id': session_id,
            'stage': stage,
            'stage_name': stage_name,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            self.socketio.emit(
                'stage_change',
                event_data,
                namespace=self.namespace,
                room=session_id
            )
            logger.info(f"WebSocketBroadcaster: 广播阶段变化 - Stage {stage}: {stage_name}")
        except Exception as e:
            logger.error(f"WebSocketBroadcaster: 广播失败: {e}")
    
    def broadcast_error(self, session_id: str, error_type: str, error_message: str):
        """
        广播错误
        
        Args:
            session_id: 会话 ID
            error_type: 错误类型
            error_message: 错误消息
        """
        if not self.socketio:
            logger.warning("WebSocketBroadcaster: SocketIO 未初始化")
            return
        
        event_data = {
            'type': 'error',
            'session_id': session_id,
            'error_type': error_type,
            'error_message': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            self.socketio.emit(
                'error',
                event_data,
                namespace=self.namespace,
                room=session_id
            )
            logger.error(f"WebSocketBroadcaster: 广播错误 - {error_type}: {error_message}")
        except Exception as e:
            logger.error(f"WebSocketBroadcaster: 广播失败: {e}")
    
    # ==================== 房间管理 ====================
    
    def join_session_room(self, session_id: str, sid: str):
        """
        加入会话房间
        
        Args:
            session_id: 会话 ID
            sid: Socket ID
        """
        if not self.socketio:
            return
        
        try:
            from flask_socketio import join_room
            join_room(session_id, sid=sid, namespace=self.namespace)
            logger.debug(f"WebSocketBroadcaster: 客户端 {sid} 加入房间 {session_id}")
        except Exception as e:
            logger.error(f"WebSocketBroadcaster: 加入房间失败: {e}")
    
    def leave_session_room(self, session_id: str, sid: str):
        """
        离开会话房间
        
        Args:
            session_id: 会话 ID
            sid: Socket ID
        """
        if not self.socketio:
            return
        
        try:
            from flask_socketio import leave_room
            leave_room(session_id, sid=sid, namespace=self.namespace)
            logger.debug(f"WebSocketBroadcaster: 客户端 {sid} 离开房间 {session_id}")
        except Exception as e:
            logger.error(f"WebSocketBroadcaster: 离开房间失败: {e}")


# 全局实例
_broadcaster_instance = None

def get_broadcaster() -> WebSocketBroadcaster:
    """获取全局 WebSocketBroadcaster 实例"""
    global _broadcaster_instance
    if _broadcaster_instance is None:
        _broadcaster_instance = WebSocketBroadcaster()
    return _broadcaster_instance

def init_broadcaster(socketio):
    """初始化广播器（在 app.py 中调用）"""
    broadcaster = get_broadcaster()
    broadcaster.set_socketio(socketio)
    logger.info("WebSocketBroadcaster: 已初始化")
    return broadcaster
