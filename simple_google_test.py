#!/usr/bin/env python3
"""
简化的Google登录测试应用
"""

import os
from flask import Flask, render_template_string
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'test-secret-key')

# 简化的HTML模板
GOOGLE_TEST_TEMPLATE = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google登录测试</title>
    <script src="https://accounts.google.com/gsi/client" async defer></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .google-btn {
            background: #4285f4;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 0;
        }
        .google-btn:hover {
            background: #357ae8;
        }
        .info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .success {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }
        pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Google登录测试</h1>
        
        <div class="info">
            <h3>配置信息:</h3>
            <p><strong>Google Client ID:</strong> {{ client_id[:30] }}...</p>
            <p><strong>状态:</strong> {% if client_id %}✅ 已配置{% else %}❌ 未配置{% endif %}</p>
        </div>
        
        <div id="g_id_onload"
             data-client_id="{{ client_id }}"
             data-context="signin"
             data-ux_mode="popup"
             data-callback="handleGoogleSignin"
             data-auto_prompt="false">
        </div>
        
        <button class="google-btn" onclick="triggerGoogleLogin()">
            🔐 使用Google登录
        </button>
        
        <div id="result"></div>
        
        <div class="info">
            <h3>测试步骤:</h3>
            <ol>
                <li>点击上面的"使用Google登录"按钮</li>
                <li>选择您的Google账号</li>
                <li>查看下方的结果信息</li>
            </ol>
        </div>
        
        <div class="info">
            <h3>如果没有反应，请检查:</h3>
            <ul>
                <li>浏览器控制台是否有错误 (按F12查看)</li>
                <li>Google Client ID是否正确配置</li>
                <li>网络连接是否正常</li>
                <li>是否允许弹窗</li>
            </ul>
        </div>
    </div>
    
    <script>
        console.log('Google登录测试页面已加载');
        console.log('Client ID: {{ client_id }}');
        
        // Google登录回调
        function handleGoogleSignin(response) {
            console.log('Google登录成功:', response);
            
            try {
                // 解析JWT token
                const payload = JSON.parse(atob(response.credential.split('.')[1]));
                
                document.getElementById('result').innerHTML = `
                    <div class="success">
                        <h3>✅ Google登录成功！</h3>
                        <p><strong>用户名:</strong> ${payload.name}</p>
                        <p><strong>邮箱:</strong> ${payload.email}</p>
                        <p><strong>头像:</strong> <img src="${payload.picture}" width="50" height="50" style="border-radius: 25px;"></p>
                        <details>
                            <summary>详细信息</summary>
                            <pre>${JSON.stringify(payload, null, 2)}</pre>
                        </details>
                    </div>
                `;
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <div class="error">
                        <h3>❌ 解析token失败</h3>
                        <p>错误: ${error.message}</p>
                    </div>
                `;
            }
        }
        
        // 触发Google登录
        function triggerGoogleLogin() {
            console.log('触发Google登录...');
            
            // 检查Google Identity Services是否已加载
            if (typeof google === 'undefined') {
                document.getElementById('result').innerHTML = `
                    <div class="error">
                        <h3>❌ Google Identity Services未加载</h3>
                        <p>请检查网络连接或稍后重试</p>
                    </div>
                `;
                return;
            }
            
            // Google Identity Services会自动处理登录
            console.log('Google Identity Services已就绪');
        }
        
        // 页面加载完成检查
        window.addEventListener('load', function() {
            setTimeout(function() {
                if (typeof google !== 'undefined') {
                    console.log('✅ Google Identity Services已加载');
                } else {
                    console.log('❌ Google Identity Services未加载');
                    document.getElementById('result').innerHTML = `
                        <div class="error">
                            <h3>⚠️ Google服务加载中...</h3>
                            <p>如果长时间未加载，请检查网络连接</p>
                        </div>
                    `;
                }
            }, 2000);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def test_google():
    """Google登录测试页面"""
    client_id = os.getenv('GOOGLE_CLIENT_ID', '')
    return render_template_string(GOOGLE_TEST_TEMPLATE, client_id=client_id)

if __name__ == '__main__':
    print("🚀 启动Google登录测试服务器...")
    print("📱 访问: http://localhost:5002")
    print("🔍 Google Client ID:", os.getenv('GOOGLE_CLIENT_ID', '未配置')[:30] + '...')
    
    try:
        app.run(debug=True, port=5002, host='127.0.0.1')
    except Exception as e:
        print(f"❌ 启动失败: {e}")



