#!/usr/bin/env python3
"""验证模板文件的改进"""

import os

template_path = 'templates/unified_dashboard.html'

if os.path.exists(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 检查关键函数是否存在
        functions = [
            'updateCommunityForm',
            'fillRedditSubreddit',
            'updateRedditUrl',
            'updateGithubUrl',
            'updateDiscourseUrl',
            'updateCustomUrl',
            'submitAddCommunity'
        ]
        
        print("=== 检查JavaScript函数 ===")
        for func in functions:
            if func in content:
                print(f'✓ {func} 函数存在')
            else:
                print(f'✗ {func} 函数缺失')
        
        # 检查表单元素
        elements = [
            'reddit-subreddit-group',
            'github-repo-group',
            'hackernews-note',
            'discourse-url-group',
            'custom-url-group'
        ]
        
        print("\n=== 检查表单元素 ===")
        for elem in elements:
            if elem in content:
                print(f'✓ {elem} 元素存在')
            else:
                print(f'✗ {elem} 元素缺失')
        
        print('\n✅ 模板文件验证完成')
else:
    print('❌ 模板文件不存在')
