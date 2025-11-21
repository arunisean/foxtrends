# -*- coding: utf-8 -*-
"""
FoxTrends 数据库模块

提供数据库连接、初始化和管理功能
"""

from .db_manager import DatabaseManager, get_engine, get_async_engine
from .init_database import init_database, init_database_async

__all__ = [
    'DatabaseManager',
    'get_engine',
    'get_async_engine',
    'init_database',
    'init_database_async',
]
