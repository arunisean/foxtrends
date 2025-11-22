"""
TrendDiscoveryAgent - 趋势发现Agent主类
发现新兴需求趋势，预测需求方向
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class TrendDiscoveryAgent:
    """
    需求发现Agent
    
    职责:
    - 发现当前需求热点
    - 分析需求优先级
    - 提供竞品对比分析
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Agent"""
        self.config = config or {}
        self.api_key = self.config.get('api_key') or settings.TREND_DISCOVERY_API_KEY
        self.base_url = self.config.get('base_url') or settings.TREND_DISCOVERY_BASE_URL
        self.model_name = self.config.get('model_name') or settings.TREND_DISCOVERY_MODEL_NAME
        
        self.state = {
            'query': None,
            'results': [],
            'summary': None
        }
    
    def run(self, query: str, **kwargs) -> Dict[str, Any]:
        """运行Agent主流程"""
        self.state['query'] = query
        
        result = {
            'success': True,
            'agent': 'TrendDiscoveryAgent',
            'query': query,
            'analysis': f'需求发现: {query}',
            'current_demands': ['当前需求1', '当前需求2'],
            'priority_analysis': ['高优先级需求', '中优先级需求']
        }
        
        self.state['results'].append(result)
        return result
    
    def get_state(self) -> Dict[str, Any]:
        """获取Agent状态"""
        return self.state.copy()
    
    def reset_state(self):
        """重置Agent状态"""
        self.state = {
            'query': None,
            'results': [],
            'summary': None
        }
