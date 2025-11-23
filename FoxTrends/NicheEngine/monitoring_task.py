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
    USE_MOCK_DATA = False  # 是否使用mock数据（生产环境应设为False）
    
    def __init__(self, community: Community, manager, db_manager=None):
        """
        初始化监控任务
        
        Args:
            community: 社区对象
            manager: MonitoringManager 实例
            db_manager: 数据库管理器
        """
        self.community = community
        self.manager = manager
        self.db_manager = db_manager
        
        self.status = 'idle'
        self.last_run: Optional[datetime] = None
        self.error_count = 0
        self.signals_collected = 0
        self._should_stop = False
        self._is_paused = False
    
    def run(self):
        """执行监控任务（主循环）"""
        if self.status == 'running':
            return
        
        # 如果禁用了mock数据，直接返回不启动监控
        if not self.USE_MOCK_DATA:
            self.status = 'disabled'
            self.manager.add_log(
                'WARNING',
                f'真实数据采集功能尚未实现，监控已禁用: {self.community.name}',
                self.community.id
            )
            safe_log_info(f"真实数据采集功能尚未实现，监控已禁用: {self.community.name}")
            self._update_community_status('idle')
            return
        
        self.status = 'running'
        self._should_stop = False
        
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
        
        # 1. 采集社区数据（模拟实现）
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
        
        # 3. 保存需求信号
        if signals:
            self.save_signals(signals)
            self.signals_collected += len(signals)
        
        # 4. 更新最后采集时间
        self.last_run = datetime.now()
        self._update_community_last_collection()
        
        self.manager.add_log(
            'INFO',
            f'数据采集完成: {self.community.name}',
            self.community.id
        )
    
    def collect_data(self) -> List[Dict[str, Any]]:
        """
        采集社区数据（模拟实现）
        
        Returns:
            原始数据列表
        """
        # 模拟采集 5-15 条数据
        data_count = random.randint(5, 15)
        data = []
        
        for i in range(data_count):
            data.append({
                'id': f'{self.community.id}_{int(time.time())}_{i}',
                'title': self._generate_random_title(),
                'content': self._generate_random_content(),
                'author': f'user_{random.randint(1000, 9999)}',
                'upvotes': random.randint(0, 100),
                'comments': random.randint(0, 50),
                'timestamp': datetime.now().isoformat()
            })
        
        return data
    
    def extract_signals(self, data: List[Dict[str, Any]]) -> List[DemandSignal]:
        """
        从数据中提取需求信号（模拟实现）
        
        Args:
            data: 原始数据列表
            
        Returns:
            需求信号列表
        """
        signals = []
        
        signal_types = ['pain_point', 'feature_request', 'bug_report']
        
        for item in data:
            # 随机决定是否为需求信号（60% 概率）
            if random.random() < 0.6:
                signal_type = random.choice(signal_types)
                
                # 计算情感分数
                sentiment_score = random.uniform(-1.0, 1.0)
                if signal_type == 'pain_point':
                    sentiment_score = random.uniform(-1.0, -0.2)  # 负面情感
                elif signal_type == 'feature_request':
                    sentiment_score = random.uniform(0.0, 0.8)  # 中性到正面
                elif signal_type == 'bug_report':
                    sentiment_score = random.uniform(-0.8, -0.1)  # 负面情感
                
                signal = DemandSignal(
                    signal_type=signal_type,
                    title=item['title'],
                    content=item['content'],
                    sentiment_score=sentiment_score
                )
                
                # 设置额外属性
                signal.source_url = f"https://{self.community.source_type}.com/post/{item['id']}"
                signal.author = item['author']
                signal.discussion_count = item['comments']
                signal.participant_count = random.randint(1, item['comments'] + 1)
                
                signals.append(signal)
        
        return signals
    
    def save_signals(self, signals: List[DemandSignal]):
        """
        保存需求信号到数据库
        
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
            
            with db.engine.begin() as conn:
                for signal in signals:
                    # 计算热度分数
                    hotness_score = engine.calculate_hotness(
                        signal,
                        signal.discussion_count or 0,
                        signal.participant_count or 0
                    )
                    
                    # 保存到数据库
                    conn.execute(
                        text("""
                            INSERT INTO demand_signals 
                            (community_id, signal_type, title, content, source_url, author,
                             sentiment_score, hotness_score, discussion_count, participant_count, metadata)
                            VALUES 
                            (:community_id, :signal_type, :title, :content, :source_url, :author,
                             :sentiment_score, :hotness_score, :discussion_count, :participant_count, :metadata)
                        """),
                        {
                            'community_id': self.community.id,
                            'signal_type': signal.signal_type,
                            'title': signal.title,
                            'content': signal.content,
                            'source_url': signal.source_url,
                            'author': signal.author,
                            'sentiment_score': signal.sentiment_score,
                            'hotness_score': hotness_score,
                            'discussion_count': signal.discussion_count,
                            'participant_count': signal.participant_count,
                            'metadata': json.dumps({})
                        }
                    )
                
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
            
            if self.db_manager is None:
                db.close()
            
            safe_log_info(f"保存了 {len(signals)} 个需求信号到数据库")
            
        except Exception as e:
            safe_log_error(f"保存需求信号失败: {e}")
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
    
    def _generate_random_title(self) -> str:
        """生成随机标题"""
        titles = [
            "如何解决 API 调用超时问题？",
            "希望增加批量导出功能",
            "发现一个严重的内存泄漏 bug",
            "建议优化搜索性能",
            "登录功能在移动端无法使用",
            "能否支持暗黑模式？",
            "数据同步经常失败",
            "希望添加多语言支持",
            "界面加载速度太慢",
            "能否提供 API 文档？"
        ]
        return random.choice(titles)
    
    def _generate_random_content(self) -> str:
        """生成随机内容"""
        contents = [
            "我在使用过程中遇到了这个问题，希望能够得到解决。",
            "这个功能对我们的业务非常重要，希望能够尽快实现。",
            "这个 bug 严重影响了用户体验，需要紧急修复。",
            "建议参考竞品的实现方式，可以提升用户满意度。",
            "已经尝试了多种方法，但问题依然存在。",
            "这个功能如果能实现，将大大提升工作效率。",
            "问题复现步骤：1. 打开页面 2. 点击按钮 3. 出现错误。",
            "希望团队能够重视这个需求，很多用户都在期待。",
            "性能问题在数据量大的时候特别明显。",
            "文档不够详细，希望能够补充更多示例。"
        ]
        return random.choice(contents)
    
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
