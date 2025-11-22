# -*- coding: utf-8 -*-
"""
FoxTrends 数据库管理器

基于 BettaFish 的数据库连接代码改造，支持 PostgreSQL 和 MySQL
"""

import sys
from pathlib import Path
from urllib.parse import quote_plus
from typing import Optional
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.engine import Engine
from loguru import logger

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import settings


class DatabaseManager:
    """
    数据库管理器
    
    提供数据库连接、查询和管理功能
    继承自 BettaFish 的 DatabaseManager，适配 FoxTrends 需求
    """
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.connect()
    
    def connect(self):
        """
        连接数据库
        
        支持 PostgreSQL 和 MySQL，与 BettaFish 保持兼容
        """
        try:
            url = build_database_url()
            self.engine = create_engine(url, future=True, pool_pre_ping=True, pool_recycle=1800)
            logger.info(f"成功连接到数据库: {settings.DB_NAME} ({settings.DB_DIALECT})")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            bool: 连接是否成功
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("数据库连接测试成功")
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def show_tables(self):
        """显示所有表"""
        logger.info("=" * 60)
        logger.info("数据库表列表")
        logger.info("=" * 60)
        
        inspector = inspect(self.engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.info("数据库中没有表")
            return
        
        # 分类显示表
        foxtrends_tables = []
        other_tables = []
        
        for table_name in tables:
            if table_name in ['communities', 'demand_signals', 'trend_analysis', 
                            'agent_discussions', 'demand_reports']:
                foxtrends_tables.append(table_name)
            else:
                other_tables.append(table_name)
        
        if foxtrends_tables:
            logger.info("\nFoxTrends 核心表:")
            for table in foxtrends_tables:
                with self.engine.connect() as conn:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
                logger.info(f"  - {table:<25} ({count:>6} 条记录)")
        
        if other_tables:
            logger.info("\n其他表:")
            for table in other_tables:
                try:
                    with self.engine.connect() as conn:
                        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
                    logger.info(f"  - {table:<25} ({count:>6} 条记录)")
                except Exception as e:
                    logger.info(f"  - {table:<25} (查询失败: {e})")
    
    def get_table_info(self, table_name: str):
        """
        获取表信息
        
        Args:
            table_name: 表名
        """
        inspector = inspect(self.engine)
        
        if table_name not in inspector.get_table_names():
            logger.error(f"表 {table_name} 不存在")
            return
        
        logger.info(f"\n表 {table_name} 的结构:")
        columns = inspector.get_columns(table_name)
        for col in columns:
            logger.info(f"  - {col['name']:<20} {col['type']}")
    
    def execute_query(self, query: str, params=None):
        """
        执行查询
        
        Args:
            query: SQL 查询语句（使用 ? 或 %s 占位符）
            params: 查询参数（字典、元组或列表）
            
        Returns:
            查询结果
        """
        try:
            with self.engine.connect() as conn:
                # 如果 params 是元组或列表，转换为字典
                if params and isinstance(params, (tuple, list)):
                    # 将 ? 或 %s 占位符替换为命名参数
                    param_dict = {}
                    query_with_names = query
                    for i, val in enumerate(params):
                        param_name = f'param{i}'
                        param_dict[param_name] = val
                        # 替换 ? 或 %s 为命名参数（只替换第一个）
                        if '?' in query_with_names:
                            query_with_names = query_with_names.replace('?', f':{param_name}', 1)
                        elif '%s' in query_with_names:
                            query_with_names = query_with_names.replace('%s', f':{param_name}', 1)
                    result = conn.execute(text(query_with_names), param_dict)
                else:
                    # 字典参数或无参数
                    result = conn.execute(text(query), params or {})
                return result.fetchall()
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise


def build_database_url(async_mode: bool = False) -> str:
    """
    构建数据库连接 URL
    
    Args:
        async_mode: 是否使用异步驱动
        
    Returns:
        str: 数据库连接 URL
    """
    dialect = (settings.DB_DIALECT or "sqlite").lower()
    
    # SQLite 配置
    if dialect == "sqlite":
        db_name = settings.DB_NAME
        # SQLite 使用相对路径或绝对路径
        if async_mode:
            return f"sqlite+aiosqlite:///{db_name}"
        else:
            return f"sqlite:///{db_name}"
    
    # PostgreSQL/MySQL 配置
    host = settings.DB_HOST
    port = settings.DB_PORT
    user = settings.DB_USER
    password = quote_plus(settings.DB_PASSWORD)
    db_name = settings.DB_NAME
    
    if dialect in ("postgresql", "postgres"):
        if async_mode:
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
        else:
            return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"
    else:  # mysql
        charset = settings.DB_CHARSET
        if async_mode:
            return f"mysql+aiomysql://{user}:{password}@{host}:{port}/{db_name}?charset={charset}"
        else:
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset={charset}"


def get_engine() -> Engine:
    """
    获取同步数据库引擎
    
    Returns:
        Engine: SQLAlchemy 引擎实例
    """
    url = build_database_url(async_mode=False)
    return create_engine(url, future=True, pool_pre_ping=True, pool_recycle=1800)


def get_async_engine() -> AsyncEngine:
    """
    获取异步数据库引擎
    
    Returns:
        AsyncEngine: SQLAlchemy 异步引擎实例
    """
    url = build_database_url(async_mode=True)
    return create_async_engine(url, pool_pre_ping=True, pool_recycle=1800)


if __name__ == "__main__":
    # 测试数据库连接
    db_manager = DatabaseManager()
    try:
        if db_manager.test_connection():
            db_manager.show_tables()
    finally:
        db_manager.close()
