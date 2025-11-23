#!/usr/bin/env python3
"""
清理测试数据
删除所有测试产生的数据
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from loguru import logger

def clean_test_data():
    """清理测试数据"""
    logger.info("开始清理测试数据...")
    
    db = DatabaseManager()
    
    try:
        # 1. 删除测试社区和相关需求
        logger.info("删除测试社区...")
        
        # 查找测试社区
        test_communities = db.execute_query("""
            SELECT id, name FROM communities 
            WHERE name LIKE '%Test%' OR name LIKE '%test%'
        """)
        
        if test_communities:
            logger.info(f"找到 {len(test_communities)} 个测试社区")
            for community in test_communities:
                community_id, name = community
                logger.info(f"  - 删除社区: {name} (ID: {community_id})")
                
                # 删除相关需求
                db.execute_query("""
                    DELETE FROM demand_signals WHERE community_id = %s
                """, (community_id,))
                
                # 删除社区
                db.execute_query("""
                    DELETE FROM communities WHERE id = %s
                """, (community_id,))
        else:
            logger.info("未找到测试社区")
        
        # 2. 删除错误的需求数据（source_url 包含 example.com）
        logger.info("删除错误的需求数据...")
        
        error_demands = db.execute_query("""
            SELECT id, title, source_url FROM demand_signals 
            WHERE source_url LIKE '%example.com%' 
               OR source_url LIKE '%test%'
               OR source_url IS NULL
               OR source_url = ''
        """)
        
        if error_demands:
            logger.info(f"找到 {len(error_demands)} 条错误需求")
            for demand in error_demands:
                demand_id, title, url = demand
                logger.info(f"  - 删除需求: {title} (URL: {url})")
                
                db.execute_query("""
                    DELETE FROM demand_signals WHERE id = %s
                """, (demand_id,))
        else:
            logger.info("未找到错误需求")
        
        # 3. 删除测试讨论记录
        logger.info("删除测试讨论记录...")
        
        test_discussions = db.execute_query("""
            SELECT COUNT(*) FROM agent_discussions 
            WHERE agent_name LIKE '%Test%' OR content LIKE '%test%'
        """)
        
        if test_discussions and test_discussions[0][0] > 0:
            count = test_discussions[0][0]
            logger.info(f"找到 {count} 条测试讨论")
            
            db.execute_query("""
                DELETE FROM agent_discussions 
                WHERE agent_name LIKE '%Test%' OR content LIKE '%test%'
            """)
        else:
            logger.info("未找到测试讨论")
        
        # 4. 删除所有假的需求信号（source_url 包含错误格式）
        logger.info("删除所有假的需求信号...")
        
        # 查找所有假数据（URL格式错误的）
        fake_demands = db.execute_query("""
            SELECT COUNT(*) FROM demand_signals 
            WHERE source_url LIKE '%/post/%_%_%'
               OR source_url LIKE '%example.com%'
               OR source_url LIKE '%test%'
               OR source_url IS NULL
               OR source_url = ''
        """)
        
        if fake_demands and fake_demands[0][0] > 0:
            count = fake_demands[0][0]
            logger.info(f"找到 {count} 条假需求信号，全部删除")
            
            from sqlalchemy import text
            with db.engine.begin() as conn:
                conn.execute(text("""
                    DELETE FROM demand_signals 
                    WHERE source_url LIKE '%/post/%_%_%'
                       OR source_url LIKE '%example.com%'
                       OR source_url LIKE '%test%'
                       OR source_url IS NULL
                       OR source_url = ''
                """))
        else:
            logger.info("未找到假需求信号")
        
        # 5. 删除所有监控日志（因为都是错误的）
        logger.info("删除所有监控日志...")
        
        all_logs = db.execute_query("""
            SELECT COUNT(*) FROM monitoring_logs
        """)
        
        if all_logs and all_logs[0][0] > 0:
            count = all_logs[0][0]
            logger.info(f"找到 {count} 条监控日志，全部删除")
            
            from sqlalchemy import text
            with db.engine.begin() as conn:
                conn.execute(text("DELETE FROM monitoring_logs"))
        else:
            logger.info("未找到监控日志")
        
        # 6. 清理日志文件
        logger.info("清理日志文件...")
        
        import os
        logs_dir = Path(__file__).parent.parent / "logs"
        
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            if log_files:
                logger.info(f"找到 {len(log_files)} 个日志文件")
                for log_file in log_files:
                    try:
                        log_file.unlink()
                        logger.info(f"  - 删除日志: {log_file.name}")
                    except Exception as e:
                        logger.error(f"  - 删除失败 {log_file.name}: {e}")
            else:
                logger.info("未找到日志文件")
        else:
            logger.info("logs 目录不存在")
        
        logger.info("✅ 测试数据清理完成！")
        
        # 显示剩余数据统计
        logger.info("\n当前数据库统计:")
        
        communities = db.execute_query("SELECT COUNT(*) FROM communities")
        demands = db.execute_query("SELECT COUNT(*) FROM demand_signals")
        discussions = db.execute_query("SELECT COUNT(*) FROM agent_discussions")
        
        logger.info(f"  - 社区数: {communities[0][0] if communities else 0}")
        logger.info(f"  - 需求数: {demands[0][0] if demands else 0}")
        logger.info(f"  - 讨论数: {discussions[0][0] if discussions else 0}")
        
        return True
        
    except Exception as e:
        logger.error(f"清理失败: {e}")
        return False
    finally:
        db.close()

def main():
    """主函数"""
    print("=" * 60)
    print("FoxTrends 测试数据清理工具")
    print("=" * 60)
    print()
    
    # 确认操作
    response = input("⚠️  这将删除所有测试数据，确定继续吗？(yes/no): ")
    
    if response.lower() != 'yes':
        print("操作已取消")
        return
    
    print()
    success = clean_test_data()
    
    print()
    print("=" * 60)
    if success:
        print("✅ 清理成功！")
        print()
        print("建议:")
        print("1. 重启应用: uv run python app.py")
        print("2. 添加真实社区")
        print("3. 启动监控采集真实数据")
    else:
        print("❌ 清理失败，请检查日志")
    print("=" * 60)

if __name__ == "__main__":
    main()
