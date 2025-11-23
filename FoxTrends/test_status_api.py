#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试系统状态 API
"""

import requests
import json

def test_system_status():
    """测试系统状态 API"""
    print("=" * 60)
    print("测试系统状态 API")
    print("=" * 60)
    
    try:
        # 测试系统状态 API
        response = requests.get('http://localhost:5000/api/system/status')
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ API 调用成功")
            print(f"\n返回数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 检查数据库连接状态
            if 'database_connected' in data:
                if data['database_connected']:
                    print("\n✓ 数据库连接状态: 已连接")
                else:
                    print("\n✗ 数据库连接状态: 未连接")
            else:
                print("\n⚠ 警告: API 响应中没有 database_connected 字段")
        else:
            print(f"\n✗ API 调用失败，状态码: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到服务器，请确保应用正在运行 (python app.py)")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")

if __name__ == "__main__":
    test_system_status()
