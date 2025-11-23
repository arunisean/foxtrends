#!/usr/bin/env python3
"""检查爬虫配置状态"""
import sys
sys.path.insert(0, '.')

from config import settings

def check_config():
    """检查所有爬虫的配置状态"""
    print("=" * 60)
    print("爬虫配置状态检查")
    print("=" * 60)
    
    # Reddit 配置
    print("\n【Reddit 爬虫】")
    print(f"  Client ID: {'✓ 已配置' if settings.REDDIT_CLIENT_ID else '✗ 未配置（使用 Playwright 无需配置）'}")
    print(f"  Client Secret: {'✓ 已配置' if settings.REDDIT_CLIENT_SECRET else '✗ 未配置（使用 Playwright 无需配置）'}")
    print(f"  User Agent: {settings.REDDIT_USER_AGENT}")
    print(f"  推荐方式: Playwright（无需 API 凭证）")
    
    # GitHub 配置
    print("\n【GitHub 爬虫】")
    if settings.GITHUB_TOKEN:
        token_preview = settings.GITHUB_TOKEN[:10] + "..." + settings.GITHUB_TOKEN[-4:]
        print(f"  Token: ✓ 已配置 ({token_preview})")
        print(f"  速率限制: 5000次/小时")
    else:
        print(f"  Token: ✗ 未配置")
        print(f"  速率限制: 60次/小时（未认证模式）")
    
    # HackerNews 配置
    print("\n【HackerNews 爬虫】")
    print(f"  API Base: {settings.HACKERNEWS_API_BASE}")
    print(f"  认证: 无需认证")
    print(f"  速率限制: 无限制")
    
    # 总结
    print("\n" + "=" * 60)
    print("配置建议")
    print("=" * 60)
    
    recommendations = []
    
    if not settings.GITHUB_TOKEN:
        recommendations.append("• 建议配置 GITHUB_TOKEN 以提高速率限制（60 → 5000次/小时）")
    
    if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET:
        recommendations.append("• Reddit 已配置 API 凭证，但推荐使用 Playwright（更稳定）")
    
    if recommendations:
        for rec in recommendations:
            print(rec)
    else:
        print("✓ 所有配置都已优化！")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    check_config()
