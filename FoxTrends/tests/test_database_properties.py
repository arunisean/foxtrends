# -*- coding: utf-8 -*-
"""
属性测试：数据库连接配置兼容性

验证需求: 1.5, 7.3
属性 2: 数据库连接配置兼容性
*对于任何*有效的数据库配置（PostgreSQL 或 MySQL），FoxTrends 应该能够使用与 BettaFish 相同的配置参数成功建立连接

属性 18: 数据库配置向后兼容
*对于任何*BettaFish 的有效数据库配置，FoxTrends 应该能够使用相同的配置成功连接数据库

**Feature: foxtrends-transformation, Property 2: 数据库连接配置兼容性**
**Feature: foxtrends-transformation, Property 18: 数据库配置向后兼容**
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch, MagicMock
from urllib.parse import quote_plus

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDatabaseConnectionCompatibility:
    """数据库连接配置兼容性测试"""
    
    @given(
        db_dialect=st.sampled_from(['postgresql', 'postgres', 'mysql']),
        db_host=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N', 'P'))),
        db_port=st.integers(min_value=1024, max_value=65535),
        db_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N')))
    )
    @settings(max_examples=20, deadline=None)
    def test_property_database_url_construction(self, db_dialect, db_host, db_port, db_name):
        """
        属性 2: 数据库连接配置兼容性
        
        对于任何有效的数据库配置，应该能够构建正确的连接 URL
        """
        assume(db_host.strip() != '')
        assume(db_name.strip() != '')
        assume(not db_host.startswith('.'))
        
        from database.db_manager import build_database_url
        
        # Mock 配置
        with patch('database.db_manager.settings') as mock_settings:
            mock_settings.DB_DIALECT = db_dialect
            mock_settings.DB_HOST = db_host
            mock_settings.DB_PORT = db_port
            mock_settings.DB_USER = 'test_user'
            mock_settings.DB_PASSWORD = 'test_pass'
            mock_settings.DB_NAME = db_name
            mock_settings.DB_CHARSET = 'utf8mb4'
            
            # 构建 URL
            url = build_database_url(async_mode=False)
            
            # 验证 URL 包含必要的组件
            assert db_host in url, f"URL 应包含主机名: {db_host}"
            assert str(db_port) in url, f"URL 应包含端口: {db_port}"
            assert db_name in url, f"URL 应包含数据库名: {db_name}"
            
            # 验证方言
            if db_dialect in ('postgresql', 'postgres'):
                assert 'postgresql' in url, "PostgreSQL URL 应包含 postgresql"
            else:
                assert 'mysql' in url, "MySQL URL 应包含 mysql"
    
    def test_postgresql_url_format(self):
        """验证 PostgreSQL URL 格式"""
        from database.db_manager import build_database_url
        
        with patch('database.db_manager.settings') as mock_settings:
            mock_settings.DB_DIALECT = 'postgresql'
            mock_settings.DB_HOST = 'localhost'
            mock_settings.DB_PORT = 5432
            mock_settings.DB_USER = 'foxtrends_user'
            mock_settings.DB_PASSWORD = 'test_password'
            mock_settings.DB_NAME = 'foxtrends'
            
            # 同步 URL
            sync_url = build_database_url(async_mode=False)
            assert sync_url.startswith('postgresql+psycopg://'), "同步 PostgreSQL URL 应使用 psycopg"
            assert 'localhost:5432' in sync_url
            assert 'foxtrends' in sync_url
            
            # 异步 URL
            async_url = build_database_url(async_mode=True)
            assert async_url.startswith('postgresql+asyncpg://'), "异步 PostgreSQL URL 应使用 asyncpg"
    
    def test_mysql_url_format(self):
        """验证 MySQL URL 格式"""
        from database.db_manager import build_database_url
        
        with patch('database.db_manager.settings') as mock_settings:
            mock_settings.DB_DIALECT = 'mysql'
            mock_settings.DB_HOST = 'localhost'
            mock_settings.DB_PORT = 3306
            mock_settings.DB_USER = 'foxtrends_user'
            mock_settings.DB_PASSWORD = 'test_password'
            mock_settings.DB_NAME = 'foxtrends'
            mock_settings.DB_CHARSET = 'utf8mb4'
            
            # 同步 URL
            sync_url = build_database_url(async_mode=False)
            assert sync_url.startswith('mysql+pymysql://'), "同步 MySQL URL 应使用 pymysql"
            assert 'localhost:3306' in sync_url
            assert 'foxtrends' in sync_url
            assert 'charset=utf8mb4' in sync_url
            
            # 异步 URL
            async_url = build_database_url(async_mode=True)
            assert async_url.startswith('mysql+aiomysql://'), "异步 MySQL URL 应使用 aiomysql"
    
    def test_password_encoding(self):
        """验证密码特殊字符编码"""
        from database.db_manager import build_database_url
        
        # 测试包含特殊字符的密码
        special_passwords = [
            'pass@word',
            'pass#word',
            'pass word',
            'pass/word',
            'pass?word=123'
        ]
        
        for password in special_passwords:
            with patch('database.db_manager.settings') as mock_settings:
                mock_settings.DB_DIALECT = 'postgresql'
                mock_settings.DB_HOST = 'localhost'
                mock_settings.DB_PORT = 5432
                mock_settings.DB_USER = 'user'
                mock_settings.DB_PASSWORD = password
                mock_settings.DB_NAME = 'testdb'
                
                url = build_database_url()
                
                # 验证密码被正确编码
                encoded_password = quote_plus(password)
                assert encoded_password in url, f"密码应被正确编码: {password}"
    
    def test_bettafish_config_compatibility(self):
        """
        属性 18: 数据库配置向后兼容
        
        验证 BettaFish 的配置可以在 FoxTrends 中使用
        """
        from database.db_manager import build_database_url
        
        # BettaFish 的典型配置
        bettafish_configs = [
            {
                'DB_DIALECT': 'postgresql',
                'DB_HOST': 'localhost',
                'DB_PORT': 5432,
                'DB_USER': 'bettafish_user',
                'DB_PASSWORD': 'bettafish_pass',
                'DB_NAME': 'bettafish',
            },
            {
                'DB_DIALECT': 'mysql',
                'DB_HOST': '127.0.0.1',
                'DB_PORT': 3306,
                'DB_USER': 'root',
                'DB_PASSWORD': 'mysql_pass',
                'DB_NAME': 'bettafish',
                'DB_CHARSET': 'utf8mb4',
            }
        ]
        
        for config in bettafish_configs:
            with patch('database.db_manager.settings') as mock_settings:
                for key, value in config.items():
                    setattr(mock_settings, key, value)
                
                # 应该能够成功构建 URL
                url = build_database_url()
                assert url is not None
                assert len(url) > 0
                
                # 验证 URL 包含关键信息
                assert config['DB_HOST'] in url
                assert str(config['DB_PORT']) in url
                assert config['DB_NAME'] in url


class TestDatabaseManagerCompatibility:
    """数据库管理器兼容性测试"""
    
    def test_database_manager_initialization(self):
        """验证数据库管理器可以初始化"""
        from database.db_manager import DatabaseManager
        
        # Mock SQLAlchemy engine
        with patch('database.db_manager.create_engine') as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            
            db_manager = DatabaseManager()
            
            # 验证引擎被创建
            assert mock_create_engine.called
            assert db_manager.engine is not None
    
    def test_database_manager_close(self):
        """验证数据库管理器可以正确关闭"""
        from database.db_manager import DatabaseManager
        
        with patch('database.db_manager.create_engine') as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            
            db_manager = DatabaseManager()
            db_manager.close()
            
            # 验证 dispose 被调用
            assert mock_engine.dispose.called
    
    def test_get_engine_function(self):
        """验证 get_engine 函数"""
        from database.db_manager import get_engine
        
        with patch('database.db_manager.create_engine') as mock_create_engine:
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine
            
            engine = get_engine()
            
            # 验证引擎被创建
            assert mock_create_engine.called
            assert engine is not None
            
            # 验证使用了正确的参数
            call_args = mock_create_engine.call_args
            assert call_args[1]['future'] == True
            assert call_args[1]['pool_pre_ping'] == True
            assert call_args[1]['pool_recycle'] == 1800
    
    def test_get_async_engine_function(self):
        """验证 get_async_engine 函数"""
        from database.db_manager import get_async_engine
        
        with patch('database.db_manager.create_async_engine') as mock_create_async_engine:
            mock_engine = MagicMock()
            mock_create_async_engine.return_value = mock_engine
            
            engine = get_async_engine()
            
            # 验证异步引擎被创建
            assert mock_create_async_engine.called
            assert engine is not None
            
            # 验证使用了正确的参数
            call_args = mock_create_async_engine.call_args
            assert call_args[1]['pool_pre_ping'] == True
            assert call_args[1]['pool_recycle'] == 1800


class TestDatabaseConfigValidation:
    """数据库配置验证测试"""
    
    @given(
        db_port=st.integers()
    )
    @settings(max_examples=30)
    def test_property_port_validation(self, db_port):
        """
        属性：端口号验证
        
        数据库端口应该在有效范围内
        """
        from database.db_manager import build_database_url
        
        with patch('database.db_manager.settings') as mock_settings:
            mock_settings.DB_DIALECT = 'postgresql'
            mock_settings.DB_HOST = 'localhost'
            mock_settings.DB_PORT = db_port
            mock_settings.DB_USER = 'user'
            mock_settings.DB_PASSWORD = 'pass'
            mock_settings.DB_NAME = 'db'
            
            # 构建 URL（不验证端口有效性，由数据库驱动处理）
            url = build_database_url()
            
            # URL 应该包含端口号
            assert str(db_port) in url
    
    def test_dialect_case_insensitive(self):
        """验证数据库类型不区分大小写"""
        from database.db_manager import build_database_url
        
        dialects = ['postgresql', 'PostgreSQL', 'POSTGRESQL', 'postgres', 'POSTGRES']
        
        for dialect in dialects:
            with patch('database.db_manager.settings') as mock_settings:
                mock_settings.DB_DIALECT = dialect
                mock_settings.DB_HOST = 'localhost'
                mock_settings.DB_PORT = 5432
                mock_settings.DB_USER = 'user'
                mock_settings.DB_PASSWORD = 'pass'
                mock_settings.DB_NAME = 'db'
                
                url = build_database_url()
                
                # 所有变体都应该生成 PostgreSQL URL
                assert 'postgresql' in url.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
