#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据库连接

验证 FoxTrends 数据库配置和连接功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from config import settings
from database.db_manager import DatabaseManager


def test_database_connection():
    """测试数据库连接"""
    logger.info("=" * 60)
    logger.info("FoxTrends 数据库连接测试")
    logger.info("=" * 60)
    
    # 显示配置信息
    logger.info(f"\n数据库配置:")
    logger.info(f"  类型: {settings.DB_DIALECT}")
    logger.info(f"  主机: {settings.DB_HOST}")
    logger.info(f"  端口: {settings.DB_PORT}")
    logger.info(f"  数据库: {settings.DB_NAME}")
    logger.info(f"  用户: {settings.DB_USER}")
    
    # 测试连接
    logger.info(f"\n正在连接数据库...")
    
    try:
        db_manager = DatabaseManager()
        
        # 测试连接
        if db_manager.test_connection():
            logger.info("✅ 数据库连接成功！")
            
            # 显示表信息
            logger.info("\n查询数据库表...")
            db_manager.show_tables()
            
            return True
        else:
            logger.error("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库连接错误: {e}")
        return False
    finally:
        if 'db_manager' in locals():
            db_manager.close()


def main():
    """主函数"""
    success = test_database_connection()
    
    if success:
        logger.info("\n" + "=" * 60)
        logger.info("✅ 数据库连接测试通过")
        logger.info("=" * 60)
        return 0
    else:
        logger.error("\n" + "=" * 60)
        logger.error("❌ 数据库连接测试失败")
        logger.error("=" * 60)
        logger.error("\n请检查:")
        logger.error("1. 数据库服务是否运行")
        logger.error("2. .env 文件中的数据库配置是否正确")
        logger.error("3. 数据库用户是否有足够的权限")
        return 1


if __name__ == "__main__":
    sys.exit(main())
