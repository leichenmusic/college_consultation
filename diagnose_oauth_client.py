#!/usr/bin/env python3
"""
Google OAuth客户端诊断工具
检查Client ID配置和状态
"""

import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_client_id_format():
    """检查Client ID格式"""
    print("🔍 检查Google Client ID格式...")
    
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    
    if not client_id:
        print("❌ GOOGLE_CLIENT_ID 环境变量未设置")
        return False, None
    
    print(f"📋 Client ID: {client_id}")
    
    # 检查格式
    if not client_id.endswith('.apps.googleusercontent.com'):
        print("❌ Client ID格式不正确，应该以 .apps.googleusercontent.com 结尾")
        return False, client_id
    
    # 检查长度和格式
    parts = client_id.split('-')
    if len(parts) < 2:
        print("❌ Client ID格式不正确，应该包含连字符")
        return False, client_id
    
    project_number = parts[0]
    if not project_number.isdigit() or len(project_number) != 12:
        print("❌ 项目编号格式不正确，应该是12位数字")
        return False, client_id
    
    print("✅ Client ID格式正确")
    return True, client_id

def check_google_discovery():
    """检查Google OAuth发现端点"""
    print("\n🔍 检查Google OAuth服务状态...")
    
    try:
        discovery_url = "https://accounts.google.com/.well-known/openid_configuration"
        response = requests.get(discovery_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Google OAuth服务正常")
            config = response.json()
            print(f"📋 授权端点: {config.get('authorization_endpoint', 'N/A')}")
            print(f"📋 Token端点: {config.get('token_endpoint', 'N/A')}")
            return True
        else:
            print(f"❌ Google OAuth服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到Google OAuth服务: {e}")
        return False

def generate_test_urls():
    """生成测试URL"""
    print("\n🔗 生成测试和配置URL...")
    
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    
    if not client_id:
        print("❌ 无法生成URL，Client ID未设置")
        return
    
    # 提取项目编号
    project_number = client_id.split('-')[0] if '-' in client_id else 'unknown'
    
    urls = {
        "Google Cloud Console": "https://console.cloud.google.com/",
        "APIs & Services": f"https://console.cloud.google.com/apis/credentials?project={project_number}",
        "OAuth同意屏幕": f"https://console.cloud.google.com/apis/credentials/consent?project={project_number}",
        "API库": f"https://console.cloud.google.com/apis/library?project={project_number}",
    }
    
    for name, url in urls.items():
        print(f"🔗 {name}: {url}")

def check_oauth_consent_screen():
    """检查OAuth同意屏幕配置提示"""
    print("\n📋 OAuth同意屏幕检查清单:")
    
    checklist = [
        "✓ 应用名称已设置",
        "✓ 用户支持邮箱已设置", 
        "✓ 开发者联系信息已设置",
        "✓ 应用域名已配置（如果有）",
        "✓ 授权域名包含 localhost（用于测试）",
        "✓ 发布状态设置正确（测试/生产）"
    ]
    
    for item in checklist:
        print(f"  {item}")

def provide_solutions():
    """提供解决方案"""
    print("\n" + "="*60)
    print("🔧 解决方案指南")
    print("="*60)
    
    print("\n1. 检查Google Cloud Console配置:")
    print("   - 确认项目存在且可访问")
    print("   - 确认OAuth 2.0客户端ID存在")
    print("   - 确认客户端ID状态为启用")
    
    print("\n2. 重新创建OAuth客户端ID:")
    print("   - 删除现有的客户端ID")
    print("   - 创建新的Web应用程序客户端ID")
    print("   - 更新.env文件中的GOOGLE_CLIENT_ID")
    
    print("\n3. 检查OAuth同意屏幕:")
    print("   - 确保已配置OAuth同意屏幕")
    print("   - 检查发布状态（测试用户vs公开发布）")
    print("   - 添加测试用户（如果是测试状态）")
    
    print("\n4. 检查授权域名:")
    print("   - 在OAuth客户端配置中添加:")
    print("     * http://localhost:8080")
    print("     * http://localhost:5001")
    print("     * http://127.0.0.1:8080")
    
    print("\n5. 启用必要的API:")
    print("   - Google+ API")
    print("   - Google Identity Services")

def main():
    """主诊断函数"""
    print("🎵 Google OAuth客户端诊断工具")
    print("="*50)
    
    # 检查Client ID格式
    format_ok, client_id = check_client_id_format()
    
    # 检查Google服务状态
    service_ok = check_google_discovery()
    
    # 生成有用的URL
    generate_test_urls()
    
    # 显示检查清单
    check_oauth_consent_screen()
    
    # 结果总结
    print("\n" + "="*60)
    print("📊 诊断结果")
    print("="*60)
    
    if format_ok and service_ok:
        print("✅ Client ID格式正确，Google服务正常")
        print("❌ 但是客户端未找到，可能是配置问题")
        print("\n🎯 建议操作:")
        print("1. 检查Google Cloud Console中的OAuth客户端配置")
        print("2. 确认客户端ID是否被意外删除或禁用")
        print("3. 检查项目权限和访问状态")
    else:
        print("❌ 发现配置问题")
        if not format_ok:
            print("  - Client ID格式不正确")
        if not service_ok:
            print("  - Google OAuth服务连接失败")
    
    provide_solutions()
    
    print(f"\n🔑 当前Client ID: {client_id}")
    print("请访问上述Google Cloud Console链接检查配置")

if __name__ == "__main__":
    main()



