# -*- coding: utf-8 -*-
"""
属性测试：UV 依赖安装完整性

验证需求: 1.4
属性 1: 依赖安装完整性
*对于任何*通过 UV 安装的依赖包，该包应该能够被成功导入并使用
"""

import pytest
import subprocess
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, HealthCheck


# 核心依赖列表 - 这些是 FoxTrends 必需的关键包
# 注意：某些包的导入名称与包名不同（如 beautifulsoup4 -> bs4）
CORE_DEPENDENCIES = [
    'flask',
    'pydantic',
    'pydantic_settings',
    'sqlalchemy',
    'openai',
    'playwright',
    'pandas',
    'numpy',
    'requests',
    'aiohttp',
    'bs4',  # beautifulsoup4 的导入名称
    'plotly',
    'streamlit',
    'loguru',
    'tenacity',
    'pytest',
    'hypothesis',
]


class TestUVDependencyInstallation:
    """UV 依赖安装完整性测试"""
    
    def test_core_dependencies_importable(self):
        """
        属性 1: 依赖安装完整性
        
        验证所有核心依赖都能被成功导入
        """
        failed_imports = []
        
        for package in CORE_DEPENDENCIES:
            try:
                # 尝试导入包
                __import__(package)
            except ImportError as e:
                failed_imports.append((package, str(e)))
        
        # 断言：所有核心依赖都应该能够导入
        assert len(failed_imports) == 0, (
            f"以下核心依赖无法导入:\n" +
            "\n".join([f"  - {pkg}: {err}" for pkg, err in failed_imports])
        )
    
    def test_uv_lock_exists(self):
        """验证 uv.lock 文件存在"""
        project_root = Path(__file__).parent.parent
        uv_lock = project_root / "uv.lock"
        
        assert uv_lock.exists(), "uv.lock 文件不存在，依赖未锁定"
        assert uv_lock.stat().st_size > 0, "uv.lock 文件为空"
    
    def test_pyproject_toml_exists(self):
        """验证 pyproject.toml 文件存在且格式正确"""
        project_root = Path(__file__).parent.parent
        pyproject = project_root / "pyproject.toml"
        
        assert pyproject.exists(), "pyproject.toml 文件不存在"
        
        # 尝试解析 pyproject.toml
        try:
            import tomli
        except ImportError:
            # 如果 tomli 不可用，使用 toml
            try:
                import toml
                with open(pyproject, 'r', encoding='utf-8') as f:
                    config = toml.load(f)
            except ImportError:
                pytest.skip("需要 tomli 或 toml 包来解析 pyproject.toml")
        else:
            with open(pyproject, 'rb') as f:
                import tomli
                config = tomli.load(f)
        
        # 验证必需的配置项
        assert 'project' in config, "pyproject.toml 缺少 [project] 部分"
        assert 'name' in config['project'], "pyproject.toml 缺少项目名称"
        assert 'dependencies' in config['project'], "pyproject.toml 缺少依赖列表"
    
    def test_dependency_versions_locked(self):
        """验证依赖版本已锁定"""
        project_root = Path(__file__).parent.parent
        uv_lock = project_root / "uv.lock"
        
        if not uv_lock.exists():
            pytest.skip("uv.lock 文件不存在")
        
        # 读取 uv.lock 内容
        with open(uv_lock, 'r', encoding='utf-8') as f:
            lock_content = f.read()
        
        # 验证锁文件包含版本信息
        # uv.lock 应该包含 "version" 字段
        assert 'version' in lock_content.lower(), "uv.lock 文件缺少版本信息"
    
    @given(package_name=st.sampled_from(CORE_DEPENDENCIES))
    @settings(max_examples=len(CORE_DEPENDENCIES), suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_package_import_property(self, package_name):
        """
        属性测试：对于任何核心依赖包，都应该能够成功导入
        
        这是一个基于属性的测试，验证所有核心依赖的可导入性
        """
        try:
            module = __import__(package_name)
            # 验证模块有基本属性
            assert hasattr(module, '__name__'), f"{package_name} 模块缺少 __name__ 属性"
            assert module.__name__ == package_name, f"{package_name} 模块名称不匹配"
        except ImportError as e:
            pytest.fail(f"无法导入核心依赖 {package_name}: {e}")
    
    def test_uv_command_available(self):
        """验证 UV 命令可用"""
        try:
            result = subprocess.run(
                ['uv', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0, "UV 命令执行失败"
            assert 'uv' in result.stdout.lower(), "UV 版本信息不正确"
        except FileNotFoundError:
            pytest.fail("UV 命令不可用，请确保已安装 UV")
        except subprocess.TimeoutExpired:
            pytest.fail("UV 命令执行超时")
    
    def test_virtual_environment_active(self):
        """验证虚拟环境已激活"""
        # 检查是否在虚拟环境中
        in_venv = (
            hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )
        
        # 在 CI 环境中可能不在虚拟环境，所以这个测试是可选的
        if not in_venv:
            pytest.skip("未在虚拟环境中运行，跳过此测试")
        
        # 验证虚拟环境路径
        venv_path = Path(sys.prefix)
        assert venv_path.exists(), "虚拟环境路径不存在"
    
    def test_dependency_compatibility(self):
        """验证依赖兼容性"""
        # 测试关键依赖的版本兼容性
        import flask
        import pydantic
        import sqlalchemy
        
        # Flask 版本应该 >= 2.3
        flask_version = tuple(map(int, flask.__version__.split('.')[:2]))
        assert flask_version >= (2, 3), f"Flask 版本过低: {flask.__version__}"
        
        # Pydantic 版本应该 >= 2.5
        pydantic_version = tuple(map(int, pydantic.__version__.split('.')[:2]))
        assert pydantic_version >= (2, 5), f"Pydantic 版本过低: {pydantic.__version__}"
        
        # SQLAlchemy 版本应该 >= 2.0
        sqlalchemy_version = tuple(map(int, sqlalchemy.__version__.split('.')[:2]))
        assert sqlalchemy_version >= (2, 0), f"SQLAlchemy 版本过低: {sqlalchemy.__version__}"


class TestDependencyIntegrity:
    """依赖完整性集成测试"""
    
    def test_all_agent_dependencies(self):
        """验证所有 Agent 相关依赖"""
        agent_dependencies = {
            'openai': 'LLM 接口',
            'tenacity': '重试机制',
            'loguru': '日志系统',
        }
        
        for package, description in agent_dependencies.items():
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"{description} 依赖 {package} 未安装")
    
    def test_all_database_dependencies(self):
        """验证所有数据库相关依赖"""
        db_dependencies = {
            'sqlalchemy': 'ORM',
            'asyncpg': 'PostgreSQL 异步驱动',
            'pymysql': 'MySQL 驱动',
            'aiomysql': 'MySQL 异步驱动',
        }
        
        for package, description in db_dependencies.items():
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"{description} 依赖 {package} 未安装")
    
    def test_all_crawler_dependencies(self):
        """验证所有爬虫相关依赖"""
        crawler_dependencies = {
            'playwright': '浏览器自动化',
            'aiohttp': '异步 HTTP 客户端',
            'bs4': 'HTML 解析',  # beautifulsoup4 的导入名称
            'lxml': 'XML 解析',
        }
        
        for package, description in crawler_dependencies.items():
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"{description} 依赖 {package} 未安装")
    
    def test_all_testing_dependencies(self):
        """验证所有测试相关依赖"""
        test_dependencies = {
            'pytest': '测试框架',
            'hypothesis': '属性测试',
            'pytest_cov': '覆盖率',
            'pytest_mock': 'Mock 工具',
        }
        
        for package, description in test_dependencies.items():
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"{description} 依赖 {package} 未安装")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
