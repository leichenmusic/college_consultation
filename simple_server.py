#!/usr/bin/env python3
"""
简单的HTTP服务器，用于托管Google OAuth测试页面
解决file://协议的安全限制问题
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

def start_server():
    """启动简单的HTTP服务器"""
    
    # 设置端口
    PORT = 8080
    
    # 获取当前目录
    current_dir = Path(__file__).parent
    
    print("🚀 启动Google OAuth测试服务器...")
    print(f"📁 服务目录: {current_dir}")
    print(f"🌐 服务端口: {PORT}")
    
    # 切换到项目目录
    os.chdir(current_dir)
    
    # 创建HTTP服务器
    Handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"✅ 服务器启动成功!")
            print(f"🔗 测试地址: http://localhost:{PORT}/quick_google_test.html")
            print(f"🎯 请在浏览器中访问上述地址进行Google登录测试")
            print(f"⏹️  按 Ctrl+C 停止服务器")
            print("-" * 60)
            
            # 自动打开浏览器
            try:
                webbrowser.open(f'http://localhost:{PORT}/quick_google_test.html')
                print("🌐 已自动打开浏览器")
            except Exception as e:
                print(f"⚠️  无法自动打开浏览器: {e}")
                print(f"请手动访问: http://localhost:{PORT}/quick_google_test.html")
            
            print("-" * 60)
            
            # 启动服务器
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 端口 {PORT} 已被占用")
            print("请尝试以下解决方案:")
            print(f"1. 关闭占用端口的程序")
            print(f"2. 或者修改 PORT 变量为其他端口号")
        else:
            print(f"❌ 启动服务器失败: {e}")
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")

if __name__ == "__main__":
    start_server()



