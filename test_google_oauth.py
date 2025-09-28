#!/usr/bin/env python3
"""
Google OAuth 2.0 登录测试脚本
用于测试Google登录功能是否正常工作
"""

import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_google_oauth_config():
    """测试Google OAuth配置"""
    print("🔍 检查Google OAuth配置...")
    
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not google_client_id:
        print("❌ GOOGLE_CLIENT_ID 未配置")
        return False
    
    if not google_client_secret:
        print("❌ GOOGLE_CLIENT_SECRET 未配置")
        return False
    
    if google_client_id == 'your-google-client-id.apps.googleusercontent.com':
        print("❌ GOOGLE_CLIENT_ID 仍为示例值，请设置真实的Client ID")
        return False
    
    if google_client_secret == 'your-google-client-secret':
        print("❌ GOOGLE_CLIENT_SECRET 仍为示例值，请设置真实的Client Secret")
        return False
    
    print(f"✅ GOOGLE_CLIENT_ID: {google_client_id[:20]}...")
    print(f"✅ GOOGLE_CLIENT_SECRET: {google_client_secret[:10]}...")
    
    return True

def test_flask_app_running():
    """测试Flask应用是否运行"""
    print("\n🔍 检查Flask应用状态...")
    
    try:
        response = requests.get('http://localhost:5001/', timeout=5)
        if response.status_code in [200, 302]:  # 200 OK 或 302 重定向都是正常的
            print("✅ Flask应用正在运行")
            return True
        else:
            print(f"❌ Flask应用响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask应用 (http://localhost:5001)")
        print("   请确保运行了: python app.py")
        return False
    except Exception as e:
        print(f"❌ 连接Flask应用时出错: {e}")
        return False

def test_register_page():
    """测试注册页面是否包含Google登录"""
    print("\n🔍 检查注册页面...")
    
    try:
        response = requests.get('http://localhost:5001/register', timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # 检查是否包含Google登录相关元素
            checks = [
                ('Google Client Script', 'accounts.google.com/gsi/client'),
                ('Google Login Button', 'google-btn'),
                ('Google Callback Function', 'handleGoogleSignup'),
                ('Client ID Configuration', 'data-client_id')
            ]
            
            all_passed = True
            for check_name, check_pattern in checks:
                if check_pattern in content:
                    print(f"✅ {check_name}: 已配置")
                else:
                    print(f"❌ {check_name}: 未找到")
                    all_passed = False
            
            return all_passed
        else:
            print(f"❌ 注册页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 访问注册页面时出错: {e}")
        return False

def test_login_page():
    """测试登录页面是否包含Google登录"""
    print("\n🔍 检查登录页面...")
    
    try:
        response = requests.get('http://localhost:5001/login', timeout=5)
        if response.status_code == 200:
            content = response.text
            
            # 检查是否包含Google登录相关元素
            checks = [
                ('Google Client Script', 'accounts.google.com/gsi/client'),
                ('Google Login Button', 'google-btn'),
                ('Google Callback Function', 'handleGoogleSignin'),
                ('Client ID Configuration', 'data-client_id')
            ]
            
            all_passed = True
            for check_name, check_pattern in checks:
                if check_pattern in content:
                    print(f"✅ {check_name}: 已配置")
                else:
                    print(f"❌ {check_name}: 未找到")
                    all_passed = False
            
            return all_passed
        else:
            print(f"❌ 登录页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 访问登录页面时出错: {e}")
        return False

def test_google_auth_endpoint():
    """测试Google认证端点"""
    print("\n🔍 检查Google认证端点...")
    
    try:
        # 测试没有token的情况
        response = requests.post('http://localhost:5001/auth/google', 
                               json={}, 
                               timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if not data.get('success') and 'token' in data.get('message', ''):
                print("✅ Google认证端点正常响应")
                return True
            else:
                print(f"❌ Google认证端点响应异常: {data}")
                return False
        else:
            print(f"❌ Google认证端点状态码异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试Google认证端点时出错: {e}")
        return False

def print_google_oauth_setup_guide():
    """打印Google OAuth设置指南"""
    print("\n" + "="*60)
    print("📋 Google OAuth 2.0 设置指南")
    print("="*60)
    
    print("\n1. 访问 Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print("\n2. 创建或选择项目")
    
    print("\n3. 启用 Google+ API:")
    print("   - 进入 APIs & Services > Library")
    print("   - 搜索 'Google+ API' 并启用")
    
    print("\n4. 创建 OAuth 2.0 凭据:")
    print("   - 进入 APIs & Services > Credentials")
    print("   - 点击 'Create Credentials' > 'OAuth 2.0 Client IDs'")
    print("   - 选择 'Web application'")
    
    print("\n5. 配置授权域名:")
    print("   - Authorized JavaScript origins:")
    print("     http://localhost:5001")
    print("   - Authorized redirect URIs:")
    print("     http://localhost:5001/auth/google")
    
    print("\n6. 复制凭据到 .env 文件:")
    print("   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com")
    print("   GOOGLE_CLIENT_SECRET=your-client-secret")
    
    print("\n7. 重启Flask应用:")
    print("   python app.py")

def main():
    """主测试函数"""
    print("🎵 蕾拉酱 Google OAuth 2.0 登录测试")
    print("="*50)
    
    # 测试步骤
    tests = [
        ("Google OAuth配置", test_google_oauth_config),
        ("Flask应用运行状态", test_flask_app_running),
        ("注册页面Google登录", test_register_page),
        ("登录页面Google登录", test_login_page),
        ("Google认证端点", test_google_auth_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed += 1
        else:
            print(f"💡 {test_name} 测试失败")
    
    # 测试结果总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！Google OAuth登录应该可以正常工作")
        print("\n🚀 现在您可以:")
        print("   1. 访问 http://localhost:5001/register")
        print("   2. 点击 'Google注册' 按钮")
        print("   3. 或访问 http://localhost:5001/login")
        print("   4. 点击 'Google登录' 按钮")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        if not test_google_oauth_config():
            print_google_oauth_setup_guide()
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
