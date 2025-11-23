#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
监控任务

单个社区的监控任务实现
"""

import sys
import time
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from NicheEngine.models import Community, DemandSignal
from utils.safe_logger import safe_log_info, safe_log_error


class MonitoringTask:
    """
    单个社区的监控任务
    
    职责:
    - 定期采集社区数据
    - 提取需求信号
    - 更新监控状态
    - 报告错误和异常
    """
    
    MAX_RETRIES = 3
    COLLECTION_INTERVAL = 60  # 秒
    
    def __init__(self, community: Community, manager, db_manager=None, socketio=None):
        """
        初始化监控任务
        
        Args:
            community: 社区对象
            manager: MonitoringManager 实例
            db_manager: 数据库管理器
            socketio: SocketIO实例用于实时更新
        """
        self.community = community
        self.manager = manager
        self.db_manager = db_manager
        self.socketio = socketio
        
        self.status = 'idle'
        self.last_run: Optional[datetime] = None
        self.error_count = 0
        self.signals_collected = 0
        self._should_stop = False
        self._is_paused = False
        
        # 初始化重复检测器
        self.duplicate_detector = None
        self._init_duplicate_detector()
    
    def run(self):
        """执行监控任务（主循环）"""
        if self.status == 'running':
            return
        
        self.status = 'running'
        self._should_stop = False
        
        # 记录启动信息
        self.manager.add_log(
            'INFO',
            f'监控任务已启动: {self.community.name}',
            self.community.id
        )
        safe_log_info(f"监控任务已启动: {self.community.name}")
        
        try:
            while not self._should_stop:
                if self._is_paused:
                    time.sleep(1)
                    continue
                
                try:
                    # 执行一次数据采集
                    self._run_once()
                    
                    # 重置错误计数
                    self.error_count = 0
                    
                    # 等待下次采集
                    time.sleep(self.COLLECTION_INTERVAL)
                    
                except Exception as e:
                    self.error_count += 1
                    self.manager.add_log(
                        'ERROR',
                        f'监控任务执行失败: {str(e)}',
                        self.community.id,
                        {'error': str(e), 'error_count': self.error_count}
                    )
                    safe_log_error(f"监控任务执行失败 ({self.community.name}): {e}")
                    
                    # 广播错误事件
                    self._broadcast_update('error_occurred', {
                        'community_id': self.community.id,
                        'error': str(e),
                        'error_count': self.error_count
                    })
                    
                    # 更新数据库中的错误计数
                    self._update_error_count()
                    
                    # 检查是否超过最大重试次数
                    if self.error_count >= self.MAX_RETRIES:
                        self.status = 'error'
                        self.manager.add_log(
                            'ERROR',
                            f'监控任务连续失败 {self.MAX_RETRIES} 次，已暂停',
                            self.community.id
                        )
                        safe_log_error(f"监控任务已暂停 ({self.community.name}): 连续失败 {self.MAX_RETRIES} 次")
                        self._update_community_status('error')
                        break
                    
                    # 等待后重试
                    time.sleep(10)
        
        finally:
            if self.status != 'error':
                self.status = 'stopped'
    
    def _run_once(self):
        """执行一次监控任务"""
        self.manager.add_log(
            'INFO',
            f'开始采集数据: {self.community.name}',
            self.community.id
        )
        
        # 广播监控状态更新
        self._broadcast_update('monitoring_status', {
            'community_id': self.community.id,
            'status': 'collecting'
        })
        
        # 1. 采集社区数据
        data = self.collect_data()
        
        self.manager.add_log(
            'INFO',
            f'采集到 {len(data)} 条原始数据',
            self.community.id,
            {'data_count': len(data)}
        )
        
        # 2. 提取需求信号
        signals = self.extract_signals(data)
        
        self.manager.add_log(
            'INFO',
            f'提取到 {len(signals)} 个需求信号',
            self.community.id,
            {
                'signal_count': len(signals),
                'pain_points': sum(1 for s in signals if s.signal_type == 'pain_point'),
                'feature_requests': sum(1 for s in signals if s.signal_type == 'feature_request'),
                'bug_reports': sum(1 for s in signals if s.signal_type == 'bug_report')
            }
        )
        
        # 3. 保存需求信号（包含重复检测和实时更新）
        if signals:
            self.save_signals(signals)
            self.signals_collected += len(signals)
        
        # 4. 更新最后采集时间
        self.last_run = datetime.now()
        self._update_community_last_collection()
        
        # 广播监控状态更新
        self._broadcast_update('monitoring_status', {
            'community_id': self.community.id,
            'status': 'idle'
        })
        
        self.manager.add_log(
            'INFO',
            f'数据采集完成: {self.community.name}',
            self.community.id
        )
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        采集社区数据（使用真实爬虫）
        
        Returns:
            原始数据列表
        """
        try:
            from NicheEngine.crawlers.factory import CrawlerFactory
            
            # 创建对应的爬虫
            crawler = CrawlerFactory.create_crawler(
                self.community.source_type,
                self.community.source_url,
                self.community.config or {}
            )
            
            # 执行爬取
            data = crawler.crawl(limit=50)
            
            safe_log_info(f"成功采集 {len(data)} 条数据: {self.community.name}")
            return data
            
        except Exception as e:
            safe_log_error(f"采集数据失败 ({self.community.name}): {e}")
            # 如果爬取失败，返回空列表
            return []
    
    def extract_signals(self, data: List[Dict[str, Any]]) -> List[DemandSignal]:
        """
        从数据中提取需求信号（真实数据）
        
        Args:
            data: 原始数据列表
            
        Returns:
            需求信号列表
        """
        signals = []
        
        for item in data:
            try:
                # 根据标题和内容判断信号类型
                title = item.get('title', '').lower()
                content = item.get('content', '').lower()
                
                # 简单的关键词匹配来判断类型
                signal_type = 'discussion'  # 默认类型
                sentiment_score = 0.0
                
                if any(word in title or word in content for word in ['bug', 'error', 'issue', 'problem', 'broken', 'fail']):
                    signal_type = 'bug_report'
                    sentiment_score = random.uniform(-0.8, -0.2)
                elif any(word in title or word in content for word in ['feature', 'request', 'enhancement', 'add', 'support', 'would like']):
                    signal_type = 'feature_request'
                    sentiment_score = random.uniform(0.0, 0.6)
                elif any(word in title or word in content for word in ['pain', 'difficult', 'hard', 'frustrat', 'annoying']):
                    signal_type = 'pain_point'
                    sentiment_score = random.uniform(-0.7, -0.1)
                else:
                    sentiment_score = random.uniform(-0.3, 0.3)
                
                signal = DemandSignal(
                    signal_type=signal_type,
                    title=item.get('title', ''),
                    content=item.get('content', ''),
                    sentiment_score=sentiment_score
                )
                
                # 设置额外属性
                signal.source_url = item.get('url', '')
                signal.author = item.get('author', 'unknown')
                signal.discussion_count = item.get('comments_count', 0)
                signal.participant_count = max(1, item.get('comments_count', 0) // 2)  # 估算参与人数
                
                signals.append(signal)
                
            except Exception as e:
                safe_log_error(f"提取信号失败: {e}")
                continue
        
        return signals
    
    def save_signals(self, signals: List[DemandSignal]):
        """
        保存需求信号到数据库（带重复检测和实时更新）
        
        Args:
            signals: 需求信号列表
        """
        try:
            from database.db_manager import DatabaseManager
            from sqlalchemy import text
            import json
            
            if self.db_manager is None:
                db = DatabaseManager()
            else:
                db = self.db_manager
            
            # 计算热度分数
            from NicheEngine.engine import NicheEngine
            engine = NicheEngine(db)
            
            saved_count = 0
            duplicate_count = 0
            
            with db.engine.begin() as conn:
                for signal in signals:
                    # 检查重复
                    if self._check_duplicate(signal):
                        duplicate_count += 1
                        continue
                    
                    # 计算内容哈希
                    if self.duplicate_detector and signal.title and signal.content:
                        content_hash = self.duplicate_detector.compute_content_hash(
                            signal.title, 
                            signal.content
                        )
                    else:
                        content_hash = None
                    
                    # 计算热度分数
                    hotness_score = engine.calculate_hotness(
                        signal,
                        signal.discussion_count or 0,
                        signal.participant_count or 0
                    )
                    
                    # 保存到数据库
                    result = conn.execute(
                        text("""
                            INSERT INTO demand_signals 
                            (community_id, signal_type, title, content, source_url, content_hash, author,
                             sentiment_score, hotness_score, discussion_count, participant_count, metadata)
                            VALUES 
                            (:community_id, :signal_type, :title, :content, :source_url, :content_hash, :author,
                             :sentiment_score, :hotness_score, :discussion_count, :participant_count, :metadata)
                        """),
                        {
                            'community_id': self.community.id,
                            'signal_type': signal.signal_type,
                            'title': signal.title,
                            'content': signal.content,
                            'source_url': signal.source_url,
                            'content_hash': content_hash,
                            'author': signal.author,
                            'sentiment_score': signal.sentiment_score,
                            'hotness_score': hotness_score,
                            'discussion_count': signal.discussion_count,
                            'participant_count': signal.participant_count,
                            'metadata': json.dumps({})
                        }
                    )
                    
                    saved_count += 1
                    
                    # 广播新信号事件
                    signal_id = result.lastrowid
                    self._broadcast_update('new_signal', {
                        'signal_id': signal_id,
                        'community_id': self.community.id,
                        'community_name': self.community.name,
                        'title': signal.title,
                        'signal_type': signal.signal_type,
                        'hotness_score': hotness_score
                    })
                
                # 更新社区的总信号数
                result = conn.execute(
                    text("SELECT COUNT(*) FROM demand_signals WHERE community_id = :community_id"),
                    {'community_id': self.community.id}
                )
                total_signals = result.scalar_one()
                
                conn.execute(
                    text("UPDATE communities SET total_signals = :total WHERE id = :id"),
                    {'total': total_signals, 'id': self.community.id}
                )
                
                # 广播社区更新事件
                self._broadcast_update('community_update', {
                    'community_id': self.community.id,
                    'total_signals': total_signals,
                    'last_collection_time': datetime.now().isoformat()
                })
            
            if self.db_manager is None:
                db.close()
            
            safe_log_info(f"保存了 {saved_count} 个需求信号到数据库，跳过 {duplicate_count} 个重复信号")
            
        except Exception as e:
            safe_log_error(f"保存需求信号失败: {e}")
            # 广播错误事件
            self._broadcast_update('error_occurred', {
                'community_id': self.community.id,
                'error': str(e)
            })
            raise
    
    def _update_community_last_collection(self):
        """更新社区的最后采集时间"""
        try:
            from database.db_manager import DatabaseManager
            from sqlalchemy import text
            
            if self.db_manager is None:
                db = DatabaseManager()
            else:
                db = self.db_manager
            
            with db.engine.begin() as conn:
                conn.execute(
                    text("""
                        UPDATE communities 
                        SET last_collection_time = :time
                        WHERE id = :id
                    """),
                    {
                        'time': datetime.now().isoformat(),
                        'id': self.community.id
                    }
                )
            
            if self.db_manager is None:
                db.close()
                
        except Exception as e:
            safe_log_error(f"更新最后采集时间失败: {e}")
    
    def _update_community_status(self, status: str):
        """更新社区的监控状态"""
        try:
            from database.db_manager import DatabaseManager
            from sqlalchemy import text
            
            if self.db_manager is None:
                db = DatabaseManager()
            else:
                db = self.db_manager
            
            with db.engine.begin() as conn:
                conn.execute(
                    text("UPDATE communities SET monitoring_status = :status WHERE id = :id"),
                    {'status': status, 'id': self.community.id}
                )
            
            if self.db_manager is None:
                db.close()
                
        except Exception as e:
            safe_log_error(f"更新社区状态失败: {e}")
    
    def _update_error_count(self):
        """更新社区的错误计数"""
        try:
            from database.db_manager import DatabaseManager
            from sqlalchemy import text
            
            if self.db_manager is None:
                db = DatabaseManager()
            else:
                db = self.db_manager
            
            with db.engine.begin() as conn:
                conn.execute(
                    text("UPDATE communities SET error_count = :count WHERE id = :id"),
                    {'count': self.error_count, 'id': self.community.id}
                )
            
            # 广播社区更新
            self._broadcast_update('community_update', {
                'community_id': self.community.id,
                'error_count': self.error_count
            })
            
            if self.db_manager is None:
                db.close()
                
        except Exception as e:
            safe_log_error(f"更新错误计数失败: {e}")
    

    
    def stop(self):
        """停止监控任务"""
        self._should_stop = True
        self.status = 'stopped'
        self._update_community_status('idle')
    
    def pause(self):
        """暂停监控任务"""
        self._is_paused = True
        self.status = 'paused'
        self._update_community_status('paused')
    
    def resume(self):
        """恢复监控任务"""
        self._is_paused = False
        self.status = 'running'
        self.error_count = 0  # 重置错误计数
        self._update_community_status('active')
    
    def _init_duplicate_detector(self):
        """初始化重复检测器"""
        try:
            from NicheEngine.duplicate_detector import DuplicateDetector
            self.duplicate_detector = DuplicateDetector(self.db_manager)
        except Exception as e:
            safe_log_error(f"初始化重复检测器失败: {e}")
            self.duplicate_detector = None
    
    def _broadcast_update(self, update_type: str, data: Dict[str, Any]):
        """
        广播实时更新到前端
        
        Args:
            update_type: 更新类型 (community_update, new_signal, monitoring_status, error_occurred)
            data: 更新数据
        """
        if self.socketio is None:
            return
        
        try:
            self.socketio.emit(update_type, data)
            safe_log_info(f"广播更新: {update_type} - {data}")
        except Exception as e:
            safe_log_error(f"广播更新失败: {e}")
    
    def _check_duplicate(self, signal: DemandSignal) -> bool:
        """
        检查信号是否重复
        
        Args:
            signal: 需求信号
            
        Returns:
            是否为重复信号
        """
        if self.duplicate_detector is None:
            return False
        
        try:
            is_dup = self.duplicate_detector.is_duplicate(
                signal, 
                self.community.id,
                time_window_days=30
            )
            
            if is_dup:
                # 增加重复计数
                self.duplicate_detector.increment_duplicate_count(self.community.id)
                safe_log_info(f"检测到重复信号: {signal.title[:50]}...")
            
            return is_dup
            
        except Exception as e:
            safe_log_error(f"重复检测失败: {e}")
            return False
