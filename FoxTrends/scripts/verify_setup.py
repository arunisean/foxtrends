#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证 FoxTrends 基础设置

检查配置加载、依赖安装和基本功能。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def verify_config():
    """验证配置系统"""
    print("🔍 验证配置系统...")
    try:
        from config import settings, reload_settings
        
        # 测试配置加载
        assert settings is not None, "配置实例创建失败"
        assert hasattr(settings, 'HOST'), "缺少 HOST 配置"
        assert hasattr(settings, 'PORT'), "缺少 PORT 配置"
        assert hasattr(settings, 'DB_DIALECT'), "缺少 DB_DIALECT 配置"
        
        # 测试配置重载
        new_settings = reload_settings()
        assert new_settings is not None, "配置重载失败"
        
        print(f"✅ 配置系统正常")
        print(f"   - 主机: {settings.HOST}:{settings.PORT}")
        print(f"   - 数据库类型: {settings.DB_DIALECT}")
        print(f"   - 数据库名称: {settings.DB_NAME}")
        return True
    except Exception as e:
        print(f"❌ 配置系统错误: {e}")
        return False


def verify_dependencies():
    """验证关键依赖"""
    print("\n🔍 验证关键依赖...")
    dependencies = {
        'flask': 'Flask',
        'pydantic': 'Pydantic',
        'sqlalchemy': 'SQLAlchemy',
        'openai': 'OpenAI',
        'playwright': 'Playwright',
        'pandas': 'Pandas',
        'pytest': 'Pytest',
        'hypothesis': 'Hypothesis',
    }
    
    all_ok = True
    for module_name, display_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"✅ {display_name} 已安装")
        except ImportError:
            print(f"❌ {display_name} 未安装")
            all_ok = False
    
    return all_ok


def verify_project_structure():
    """验证项目结构"""
    print("\n🔍 验证项目结构...")
    required_dirs = [
        'CommunityInsightAgent',
        'ContentAnalysisAgent',
        'TrendDiscoveryAgent',
        'NicheEngine',
        'TrendEngine',
        'ForumEngine',
        'ReportEngine',
        'Dashboard',
        'tests',
        'scripts',
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ {dir_name}/ 目录缺失")
            all_ok = False
    
    # 检查关键文件
    required_files = [
        'config.py',
        '.env.example',
        'pyproject.toml',
        'uv.lock',
        'README.md',
    ]
    
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"✅ {file_name} 文件存在")
        else:
            print(f"❌ {file_name} 文件缺失")
            all_ok = False
    
    return all_ok


def main():
    """主函数"""
    print("=" * 60)
    print("FoxTrends 基础设置验证")
    print("=" * 60)
    
    results = []
    
    # 验证项目结构
    results.append(("项目结构", verify_project_structure()))
    
    # 验证依赖
    results.append(("依赖安装", verify_dependencies()))
    
    # 验证配置
    results.append(("配置系统", verify_config()))
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有验证通过！FoxTrends 基础设置完成。")
        print("\n下一步:")
        print("1. 复制 .env.example 为 .env 并填写配置")
        print("2. 初始化数据库")
        print("3. 开始开发或运行测试")
        return 0
    else:
        print("\n⚠️  部分验证失败，请检查上述错误。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
