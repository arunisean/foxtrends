# -*- coding: utf-8 -*-
"""
Pytest 配置文件

确保测试使用 FoxTrends 目录下的模块
"""

import sys
from pathlib import Path

# 将 FoxTrends 目录添加到 Python 路径的最前面
# 这样可以确保导入 FoxTrends 的 config 而不是根目录的 config
foxtrends_dir = Path(__file__).parent
if str(foxtrends_dir) not in sys.path:
    sys.path.insert(0, str(foxtrends_dir))
