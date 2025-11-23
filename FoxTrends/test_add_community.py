#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试添加社区功能
"""

from NicheEngine.engine import NicheEngine

def test_add_and_list_communities():
    """测试添加和列出社区"""
    print("=" * 60)
    print("测试添加社区功能")
    print("=" * 60)
    
    # 创建引擎
    engine = NicheEngine()
    
    # 添加几个测试社区
    test_communities = [
        ('机器学习讨论区', 'reddit', {'keywords': ['AI', '机器学习']}),
        ('VS Code 开发动态', 'github', {'monitor_issues': True}),
        ('HN 技术热点', 'hackernews', {'min_score': 50}),
    ]
    
    print("\n添加测试社区...")
    for name, source_type, config in test_communities:
        try:
            community = engine.add_community(name, source_type, config)
            print(f"✓ 添加成功: {community.name} (ID: {community.id})")
        except Exception as e:
            print(f"✗ 添加失败: {name} - {e}")
    
    # 列出所有社区
    print("\n" + "=" * 60)
    print("当前所有社区:")
    print("=" * 60)
    
    communities = engine.list_communities()
    print(f"\n共有 {len(communities)} 个社区:\n")
    
    for c in communities:
        print(f"ID: {c.id}")
        print(f"名称: {c.name}")
        print(f"类型: {c.source_type}")
        print(f"状态: {c.status}")
        print(f"配置: {c.config}")
        print("-" * 60)

if __name__ == "__main__":
    test_add_and_list_communities()
