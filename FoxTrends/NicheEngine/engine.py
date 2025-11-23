"""
NicheEngine - 社区监控引擎主类
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings
from .models import Community, DemandSignal


class NicheEngine:
    """
    垂直社区监控引擎
    
    职责:
    - 管理多个垂直社区
    - 采集社区数据
    - 提取需求信号
    - 计算需求热度
    - 管理监控状态
    """
    
    def __init__(self, db_manager=None):
        """
        初始化引擎
        
        Args:
            db_manager: 数据库管理器实例
        """
        if db_manager is None:
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager()
        self.db_manager = db_manager
        self.communities: Dict[int, Community] = {}
        self.monitoring_status: Dict[int, str] = {}
    
    def add_community(self, name: str, source_type: str, config: Dict[str, Any]) -> Community:
        """
        添加监控社区
        
        Args:
            name: 社区名称
            source_type: 数据源类型 (reddit, github, hackernews)
            config: 社区特定配置
            
        Returns:
            创建的社区对象
        """
        import json
        from sqlalchemy import text
        
        # 保存到数据库
        config_json = json.dumps(config) if config else '{}'
        
        with self.db_manager.engine.begin() as conn:
            result = conn.execute(
                text("""
                    INSERT INTO communities (name, source_type, config, status)
                    VALUES (:name, :source_type, :config, :status)
                """),
                {
                    'name': name,
                    'source_type': source_type,
                    'config': config_json,
                    'status': 'active'
                }
            )
            
            # 获取插入的 ID
            community_id = result.lastrowid
        
        # 创建社区对象
        community = Community(
            name=name,
            source_type=source_type,
            config=config,
            status='active'
        )
        community.id = community_id
        
        # 缓存到内存
        self.communities[community_id] = community
        
        return community
    
    def start_monitoring(self, community_id: int) -> bool:
        """
        开始监控指定社区
        
        Args:
            community_id: 社区ID
            
        Returns:
            是否成功启动
        """
        if community_id not in self.communities:
            return False
        
        self.monitoring_status[community_id] = 'running'
        return True
    
    def extract_demand_signals(self, content: str) -> List[DemandSignal]:
        """
        从内容中提取需求信号
        
        Args:
            content: 社区内容
            
        Returns:
            需求信号列表
        """
        # 占位符实现 - 实际需要LLM分析
        signals = []
        
        # 简单的关键词匹配示例
        if any(word in content.lower() for word in ['need', 'want', 'wish', '需要', '希望']):
            signal = DemandSignal(
                signal_type='feature_request',
                title='Feature Request Detected',
                content=content[:200],
                sentiment_score=0.5
            )
            signals.append(signal)
        
        if any(word in content.lower() for word in ['problem', 'issue', 'bug', '问题', '错误']):
            signal = DemandSignal(
                signal_type='pain_point',
                title='Pain Point Detected',
                content=content[:200],
                sentiment_score=-0.3
            )
            signals.append(signal)
        
        return signals
    
    def get_monitoring_status(self, community_id: int) -> Optional[str]:
        """
        获取社区监控状态
        
        Args:
            community_id: 社区ID
            
        Returns:
            监控状态
        """
        return self.monitoring_status.get(community_id)
    
    def list_communities(self) -> List[Community]:
        """获取所有社区列表"""
        import json
        from sqlalchemy import text
        
        communities = []
        
        with self.db_manager.engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, name, source_type, config, status, created_at FROM communities ORDER BY created_at DESC")
            )
            
            for row in result:
                # 解析 config JSON
                try:
                    config = json.loads(row[3]) if row[3] else {}
                except:
                    config = {}
                
                community = Community(
                    name=row[1],
                    source_type=row[2],
                    config=config,
                    status=row[4]
                )
                community.id = row[0]
                communities.append(community)
        
        return communities
    
    def calculate_hotness(self, signal: DemandSignal, 
                         discussion_count: int = 0,
                         participant_count: int = 0) -> float:
        """
        计算需求热度分数
        
        Args:
            signal: 需求信号
            discussion_count: 讨论次数
            participant_count: 参与人数
            
        Returns:
            热度分数 (0.0 - 100.0)
        """
        # 基础分数
        base_score = 0.0
        
        # 情感分数贡献 (0-30分)
        if signal.sentiment_score is not None:
            # 将 -1.0~1.0 映射到 0~30
            sentiment_contribution = (signal.sentiment_score + 1.0) * 15
            base_score += sentiment_contribution
        
        # 讨论次数贡献 (0-40分)
        discussion_contribution = min(discussion_count * 2, 40)
        base_score += discussion_contribution
        
        # 参与人数贡献 (0-30分)
        participant_contribution = min(participant_count * 3, 30)
        base_score += participant_contribution
        
        # 确保分数在 0-100 范围内
        hotness_score = max(0.0, min(100.0, base_score))
        
        return hotness_score
