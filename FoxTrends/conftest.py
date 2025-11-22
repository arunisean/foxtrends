# -*- coding: utf-8 -*-
"""
Pytest 配置文件

确保测试使用 FoxTrends 目录下的模块
"""

import sys
import os
from pathlib import Path
import pytest

# 将 FoxTrends 目录添加到 Python 路径的最前面
# 这样可以确保导入 FoxTrends 的 config 而不是根目录的 config
foxtrends_dir = Path(__file__).parent
if str(foxtrends_dir) not in sys.path:
    sys.path.insert(0, str(foxtrends_dir))


@pytest.fixture(autouse=True, scope='session')
def setup_test_environment():
    """设置测试环境 - 使用 SQLite 内存数据库"""
    # 在所有测试开始前设置环境变量
    os.environ['DB_DIALECT'] = 'sqlite'
    os.environ['DB_NAME'] = ':memory:'
    
    yield
    
    # 清理
    pass


@pytest.fixture(autouse=True)
def reset_config_after_test():
    """在每个测试后重置配置，避免测试间的环境变量污染"""
    # 保存原始环境变量
    original_env = os.environ.copy()
    
    yield
    
    # 恢复原始环境变量（但保留测试环境的数据库配置）
    test_db_config = {
        'DB_DIALECT': os.environ.get('DB_DIALECT'),
        'DB_NAME': os.environ.get('DB_NAME')
    }
    os.environ.clear()
    os.environ.update(original_env)
    # 重新应用测试数据库配置
    if test_db_config['DB_DIALECT']:
        os.environ['DB_DIALECT'] = test_db_config['DB_DIALECT']
        os.environ['DB_NAME'] = test_db_config['DB_NAME']
    
    # 重新加载配置模块
    if 'config' in sys.modules:
        import importlib
        import config
        importlib.reload(config)
