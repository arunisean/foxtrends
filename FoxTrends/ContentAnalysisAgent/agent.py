"""
ContentAnalysisAgent - 内容分析Agent主类
多模态内容分析，理解用户表达的需求
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings


class ContentAnalysisAgent:
    """
    内容分析Agent
    
    职责:
    - 多模态内容分析
    - 理解用户表达的需求
    - 提取痛点和功能请求
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化Agent"""
        self.config = config or {}
        self.api_key = self.config.get('api_key') or settings.CONTENT_ANALYSIS_API_KEY
        self.base_url = self.config.get('base_url') or settings.CONTENT_ANALYSIS_BASE_URL
        self.model_name = self.config.get('model_name') or settings.CONTENT_ANALYSIS_MODEL_NAME
        
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
            'agent': 'ContentAnalysisAgent',
            'query': query,
            'analysis': f'内容分析: {query}',
            'pain_points': ['痛点1', '痛点2'],
            'feature_requests': ['功能请求1', '功能请求2']
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
