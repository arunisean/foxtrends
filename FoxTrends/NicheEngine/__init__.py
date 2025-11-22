"""
NicheEngine - 垂直社区监控引擎
负责社区数据采集、需求信号提取、热度分析和监控状态管理
"""

from .engine import NicheEngine
from .models import Community, DemandSignal

__all__ = ['NicheEngine', 'Community', 'DemandSignal']
__version__ = "0.1.0"
