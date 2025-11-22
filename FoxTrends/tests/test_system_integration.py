"""
系统集成测试
测试 Dashboard 的完整功能
"""
import pytest


class TestSystemIntegration:
    """系统集成测试"""
    
    def test_homepage_loads(self, client):
        """测试首页加载"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'FoxTrends' in response.data
    
    def test_dashboard_loads(self, client):
        """测试 Dashboard 页面加载"""
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data
    
    def test_analysis_page_loads(self, client):
        """测试分析页面加载"""
        response = client.get('/analysis')
        assert response.status_code == 200
        assert 'analysis' in response.data.decode('utf-8').lower()
    
    def test_api_status_endpoint(self, client):
        """测试状态 API"""
        response = client.get('/api/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'forum' in data
        assert 'community_insight' in data or 'insight' in data
    
    def test_api_config_get(self, client):
        """测试获取配置"""
        response = client.get('/api/config')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'config' in data
    
    def test_system_status(self, client):
        """测试系统状态"""
        response = client.get('/api/system/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'started' in data
        assert 'starting' in data


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def app():
    """创建测试应用"""
    from app import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app
