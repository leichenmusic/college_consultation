#!/usr/bin/env python3
"""
Google登录问题诊断脚本
"""

import os
import requests
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_flask_app():
    """检查Flask应用是否运行"""
    print("🔍 检查Flask应用状态...")
    
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:5001/', timeout=5)
            if response.status_code in [200, 302]:
                print("✅ Flask应用正在运行")
                return True
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                print(f"⏳ 等待Flask应用启动... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("❌ Flask应用未运行")
                return False
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            return False
    
    return False

def check_google_client_id():
    """检查Google Client ID配置"""
    print("\n🔍 检查Google Client ID配置...")
    
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    
    if not google_client_id:
        print("❌ GOOGLE_CLIENT_ID 环境变量未设置")
        return False, None
    
    if google_client_id == 'your-google-client-id.apps.googleusercontent.com':
        print("❌ GOOGLE_CLIENT_ID 仍为示例值")
        return False, None
    
    print(f"✅ GOOGLE_CLIENT_ID: {google_client_id[:20]}...")
    return True, google_client_id

def check_register_page_rendering():
    """检查注册页面Google Client ID渲染"""
    print("\n🔍 检查注册页面Google Client ID渲染...")
    
    try:
        response = requests.get('http://localhost:5001/register', timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # 查找data-client_id
            import re
            client_id_match = re.search(r'data-client_id="([^"]*)"', content)
            
            if client_id_match:
                client_id_in_html = client_id_match.group(1)
                if client_id_in_html:
                    print(f"✅ 注册页面Client ID: {client_id_in_html[:20]}...")
                    return True, client_id_in_html
                else:
                    print("❌ 注册页面Client ID为空")
                    return False, None
            else:
                print("❌ 注册页面未找到data-client_id")
                return False, None
        else:
            print(f"❌ 注册页面访问失败: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ 访问注册页面出错: {e}")
        return False, None

def check_google_script_loading():
    """检查Google脚本加载"""
    print("\n🔍 检查Google Identity Services脚本...")
    
    try:
        response = requests.get('http://localhost:5001/register', timeout=10)
        if response.status_code == 200:
            content = response.text
            
            if 'accounts.google.com/gsi/client' in content:
                print("✅ Google Identity Services脚本已包含")
                return True
            else:
                print("❌ Google Identity Services脚本未找到")
                return False
        else:
            print(f"❌ 无法检查脚本: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 检查脚本出错: {e}")
        return False

def check_google_callback():
    """检查Google回调函数"""
    print("\n🔍 检查Google回调函数...")
    
    try:
        response = requests.get('http://localhost:5001/register', timeout=10)
        if response.status_code == 200:
            content = response.text
            
            callbacks = ['handleGoogleSignup', 'handleGoogleSignin']
            found_callbacks = []
            
            for callback in callbacks:
                if callback in content:
                    found_callbacks.append(callback)
            
            if found_callbacks:
                print(f"✅ 找到回调函数: {', '.join(found_callbacks)}")
                return True
            else:
                print("❌ 未找到Google回调函数")
                return False
        else:
            print(f"❌ 无法检查回调函数: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 检查回调函数出错: {e}")
        return False

def provide_solutions():
    """提供解决方案"""
    print("\n" + "="*60)
    print("🔧 Google登录问题解决方案")
    print("="*60)
    
    print("\n1. 检查.env文件配置:")
    print("   确保GOOGLE_CLIENT_ID已正确设置")
    print("   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com")
    
    print("\n2. 重启Flask应用:")
    print("   pkill -f 'python.*app.py'")
    print("   python app.py")
    
    print("\n3. 检查浏览器控制台:")
    print("   - 打开浏览器开发者工具 (F12)")
    print("   - 查看Console标签页的错误信息")
    print("   - 查看Network标签页的网络请求")
    
    print("\n4. 检查Google Cloud Console配置:")
    print("   - 确保OAuth 2.0客户端ID已创建")
    print("   - 确保授权的JavaScript来源包含: http://localhost:5001")
    
    print("\n5. 测试页面:")
    print("   访问: http://localhost:5001/test_google_login")
    print("   这个页面有更详细的调试信息")

def main():
    """主诊断函数"""
    print("🎵 Google登录问题诊断")
    print("="*40)
    
    # 检查步骤
    checks = [
        ("Flask应用运行", check_flask_app),
        ("Google Client ID配置", lambda: check_google_client_id()[0]),
        ("注册页面渲染", lambda: check_register_page_rendering()[0]),
        ("Google脚本加载", check_google_script_loading),
        ("Google回调函数", check_google_callback),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            if check_func():
                passed += 1
                print(f"✅ {check_name}: 通过")
            else:
                print(f"❌ {check_name}: 失败")
        except Exception as e:
            print(f"❌ {check_name}: 错误 - {e}")
    
    # 结果总结
    print("\n" + "="*60)
    print("📊 诊断结果")
    print("="*60)
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有检查都通过了！")
        print("如果Google登录仍然没有反应，请检查浏览器控制台的错误信息。")
    else:
        provide_solutions()
    
    # 显示详细的Client ID信息
    success, client_id = check_google_client_id()
    if success:
        success_render, client_id_html = check_register_page_rendering()
        if success_render:
            if client_id == client_id_html:
                print(f"\n✅ Client ID配置一致: {client_id[:30]}...")
            else:
                print(f"\n❌ Client ID不一致!")
                print(f"   环境变量: {client_id[:30]}...")
                print(f"   HTML渲染: {client_id_html[:30]}...")

if __name__ == "__main__":
    main()



