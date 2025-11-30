#!/usr/bin/env python3
"""
清除需求信号数据，保留社区配置

这个脚本会：
1. 删除所有需求信号数据（demand_signals表）
2. 重置社区的采集统计（total_signals, last_collection_time）
3. 保留所有社区配置
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import DatabaseManager
from config import settings


def clear_demand_signals():
    """清除需求信号数据"""
    db = DatabaseManager()
    
    try:
        print("🗑️  开始清除需求信号数据...")
        
        from sqlalchemy import text
        
        # 1. 统计当前数据
        with db.engine.connect() as conn:
            # 统计需求信号数量
            result = conn.execute(text("SELECT COUNT(*) FROM demand_signals"))
            signal_count = result.scalar()
            
            # 统计社区数量
            result = conn.execute(text("SELECT COUNT(*) FROM communities"))
            community_count = result.scalar()
            
            print(f"\n📊 当前数据统计：")
            print(f"   - 社区数量: {community_count}")
            print(f"   - 需求信号: {signal_count}")
            
            if signal_count == 0:
                print("\n✅ 没有需求信号数据，无需清除")
                return
        
        # 2. 执行清除操作（使用事务）
        with db.engine.begin() as conn:
            # 删除所有需求信号
            print(f"\n🗑️  删除 {signal_count} 条需求信号...")
            conn.execute(text("DELETE FROM demand_signals"))
            
            # 重置社区统计
            print("🔄 重置社区采集统计...")
            conn.execute(text("""
                UPDATE communities 
                SET total_signals = 0,
                    last_collection_time = NULL
            """))
        
        print("\n✅ 清除完成！")
        print(f"   - 已删除 {signal_count} 条需求信号")
        print(f"   - 已重置 {community_count} 个社区的统计")
        print(f"   - 社区配置已保留")
            
    except Exception as e:
        print(f"\n❌ 清除失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("清除需求信号数据")
    print("=" * 60)
    
    # 确认操作
    response = input("\n⚠️  确定要清除所有需求信号数据吗？(输入 yes 确认): ")
    
    if response.lower() == 'yes':
        clear_demand_signals()
    else:
        print("\n❌ 操作已取消")
