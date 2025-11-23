#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
监控管理器

负责管理所有社区的监控任务
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent.parent))
from NicheEngine.monitoring_task import MonitoringTask
from NicheEngine.models import Community
from utils.safe_logger import safe_log_info, safe_log_error


class MonitoringManager:
    """
    监控任务管理器
    
    职责:
    - 管理所有监控任务的生命周期
    - 调度任务执行
    - 收集和分发日志
    - 跟踪任务状态
    """
    
    _instance = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化监控管理器"""
        if hasattr(self, '_initialized'):
            return
        
        self.tasks: Dict[int, MonitoringTask] = {}
        self.logs: List[Dict[str, Any]] = []
        self.executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="monitor")
        self._initialized = True
        self._log_id_counter = 0
        
        safe_log_info("MonitoringManager 初始化完成")
    
    def start_monitoring(self, community: Community, db_manager=None) -> bool:
        """
        启动社区监控
        
        Args:
            community: 社区对象
            db_manager: 数据库管理器
            
        Returns:
            是否成功启动
        """
        community_id = community.id
        
        # 检查是否已经在监控
        if community_id in self.tasks:
            existing_task = self.tasks[community_id]
            if existing_task.status == 'running':
                self.add_log('WARNING', f'社区 {community.name} 已在监控中', community_id)
                return False
        
        # 创建新的监控任务
        task = MonitoringTask(community, self, db_manager)
        self.tasks[community_id] = task
        
        # 在线程池中启动任务
        self.executor.submit(task.run)
        
        self.add_log('INFO', f'开始监控社区: {community.name}', community_id)
        safe_log_info(f"启动监控任务: {community.name} (ID: {community_id})")
        
        return True
    
    def stop_monitoring(self, community_id: int) -> bool:
        """
        停止社区监控
        
        Args:
            community_id: 社区ID
            
        Returns:
            是否成功停止
        """
        if community_id not in self.tasks:
            self.add_log('WARNING', f'社区 ID {community_id} 没有监控任务', community_id)
            return False
        
        task = self.tasks[community_id]
        task.stop()
        
        self.add_log('INFO', f'停止监控社区: {task.community.name}', community_id)
        safe_log_info(f"停止监控任务: {task.community.name} (ID: {community_id})")
        
        return True
    
    def pause_monitoring(self, community_id: int) -> bool:
        """
        暂停社区监控
        
        Args:
            community_id: 社区ID
            
        Returns:
            是否成功暂停
        """
        if community_id not in self.tasks:
            return False
        
        task = self.tasks[community_id]
        task.pause()
        
        self.add_log('INFO', f'暂停监控社区: {task.community.name}', community_id)
        safe_log_info(f"暂停监控任务: {task.community.name} (ID: {community_id})")
        
        return True
    
    def resume_monitoring(self, community_id: int) -> bool:
        """
        恢复社区监控
        
        Args:
            community_id: 社区ID
            
        Returns:
            是否成功恢复
        """
        if community_id not in self.tasks:
            return False
        
        task = self.tasks[community_id]
        task.resume()
        
        # 重新提交任务到线程池
        self.executor.submit(task.run)
        
        self.add_log('INFO', f'恢复监控社区: {task.community.name}', community_id)
        safe_log_info(f"恢复监控任务: {task.community.name} (ID: {community_id})")
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取所有监控任务状态
        
        Returns:
            状态信息字典
        """
        active_count = sum(1 for task in self.tasks.values() if task.status == 'running')
        paused_count = sum(1 for task in self.tasks.values() if task.status == 'paused')
        error_count = sum(1 for task in self.tasks.values() if task.status == 'error')
        
        return {
            'total_tasks': len(self.tasks),
            'active_tasks': active_count,
            'paused_tasks': paused_count,
            'error_tasks': error_count,
            'tasks': [
                {
                    'community_id': task.community.id,
                    'community_name': task.community.name,
                    'status': task.status,
                    'last_run': task.last_run.isoformat() if task.last_run else None,
                    'error_count': task.error_count,
                    'signals_collected': task.signals_collected
                }
                for task in self.tasks.values()
            ]
        }
    
    def get_logs(self, limit: int = 50, level: Optional[str] = None, 
                 community_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取监控日志
        
        Args:
            limit: 返回日志数量
            level: 过滤日志级别
            community_id: 过滤特定社区
            
        Returns:
            日志列表
        """
        filtered_logs = self.logs
        
        # 按级别过滤
        if level:
            filtered_logs = [log for log in filtered_logs if log['level'] == level]
        
        # 按社区过滤
        if community_id is not None:
            filtered_logs = [log for log in filtered_logs if log.get('community_id') == community_id]
        
        # 按时间倒序排列，返回最新的 limit 条
        sorted_logs = sorted(filtered_logs, key=lambda x: x['timestamp'], reverse=True)
        return sorted_logs[:limit]
    
    def add_log(self, level: str, message: str, community_id: Optional[int] = None, 
                metadata: Optional[Dict[str, Any]] = None):
        """
        添加日志条目
        
        Args:
            level: 日志级别 (INFO/WARNING/ERROR)
            message: 日志消息
            community_id: 社区ID（可选）
            metadata: 额外的元数据（可选）
        """
        self._log_id_counter += 1
        
        log_entry = {
            'id': self._log_id_counter,
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'community_id': community_id,
            'metadata': metadata or {}
        }
        
        self.logs.append(log_entry)
        
        # 限制日志数量，避免内存溢出
        if len(self.logs) > 1000:
            self.logs = self.logs[-500:]  # 保留最新的 500 条
        
        # 同时保存到数据库（如果需要持久化）
        self._save_log_to_db(log_entry)
    
    def _save_log_to_db(self, log_entry: Dict[str, Any]):
        """
        保存日志到数据库
        
        Args:
            log_entry: 日志条目
        """
        try:
            from database.db_manager import DatabaseManager
            from sqlalchemy import text
            import json
            
            db = DatabaseManager()
            with db.engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO monitoring_logs (timestamp, level, message, community_id, metadata)
                        VALUES (:timestamp, :level, :message, :community_id, :metadata)
                    """),
                    {
                        'timestamp': log_entry['timestamp'],
                        'level': log_entry['level'],
                        'message': log_entry['message'],
                        'community_id': log_entry.get('community_id'),
                        'metadata': json.dumps(log_entry.get('metadata', {}))
                    }
                )
            db.close()
        except Exception as e:
            safe_log_error(f"保存日志到数据库失败: {e}")
    
    def clear_logs(self):
        """清空内存中的日志"""
        self.logs = []
        self._log_id_counter = 0
        safe_log_info("已清空监控日志")
    
    def shutdown(self):
        """关闭监控管理器"""
        safe_log_info("正在关闭 MonitoringManager...")
        
        # 停止所有任务
        for community_id in list(self.tasks.keys()):
            self.stop_monitoring(community_id)
        
        # 关闭线程池
        self.executor.shutdown(wait=True)
        
        safe_log_info("MonitoringManager 已关闭")
