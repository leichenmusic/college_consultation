"""
数据库管理后台
提供查看用户会话、聊天记录等功能
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import db_manager
import json
from datetime import datetime, timedelta

def create_admin_routes(app):
    """为Flask应用添加管理后台路由"""
    
    @app.route("/admin")
    def admin_dashboard():
        """管理后台首页"""
        try:
            # 获取统计数据
            active_sessions = db_manager.get_all_active_sessions()
            total_sessions = len(active_sessions)
            
            # 获取最近的会话
            recent_sessions = active_sessions[:10]
            
            stats = {
                'total_sessions': total_sessions,
                'active_sessions': len([s for s in active_sessions if s.get('is_active')]),
                'recent_sessions': recent_sessions
            }
            
            return render_template_string(ADMIN_DASHBOARD_TEMPLATE, stats=stats)
        except Exception as e:
            return f"数据库连接错误: {e}", 500
    
    @app.route("/admin/sessions")
    def admin_sessions():
        """查看所有会话"""
        try:
            sessions = db_manager.get_all_active_sessions()
            
            # 为每个会话添加统计信息
            for session in sessions:
                session_stats = db_manager.get_session_stats(session['session_id'])
                session.update(session_stats)
            
            return render_template_string(ADMIN_SESSIONS_TEMPLATE, sessions=sessions)
        except Exception as e:
            return f"获取会话数据失败: {e}", 500
    
    @app.route("/admin/session/<session_id>")
    def admin_session_detail(session_id):
        """查看特定会话的详细信息"""
        try:
            # 获取会话信息
            session_info = db_manager.get_session(session_id)
            if not session_info:
                return "会话不存在", 404
            
            # 获取用户资料
            user_profile = db_manager.get_user_profile(session_id)
            
            # 获取聊天历史
            chat_history = db_manager.get_chat_history(session_id)
            
            # 获取统计信息
            stats = db_manager.get_session_stats(session_id)
            
            return render_template_string(
                ADMIN_SESSION_DETAIL_TEMPLATE,
                session_info=session_info,
                user_profile=user_profile,
                chat_history=chat_history,
                stats=stats
            )
        except Exception as e:
            return f"获取会话详情失败: {e}", 500
    
    @app.route("/admin/api/sessions")
    def admin_api_sessions():
        """API: 获取会话列表"""
        try:
            sessions = db_manager.get_all_active_sessions()
            return jsonify({"success": True, "data": sessions})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
    
    @app.route("/admin/api/session/<session_id>/messages")
    def admin_api_session_messages(session_id):
        """API: 获取会话的聊天记录"""
        try:
            messages = db_manager.get_chat_history(session_id)
            return jsonify({"success": True, "data": messages})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

# HTML模板
ADMIN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>蕾拉酱 · 管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #2d1b69 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 40px; }
        .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
        .header p { opacity: 0.8; }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 40px; 
        }
        .stat-card { 
            background: rgba(255, 255, 255, 0.1); 
            padding: 20px; 
            border-radius: 12px; 
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .stat-number { font-size: 2rem; font-weight: bold; color: #9b59b6; }
        .stat-label { margin-top: 5px; opacity: 0.8; }
        .nav-links { 
            display: flex; 
            gap: 15px; 
            justify-content: center; 
            margin-bottom: 30px; 
        }
        .nav-link { 
            background: rgba(155, 89, 182, 0.2); 
            color: #ffffff; 
            padding: 10px 20px; 
            border-radius: 8px; 
            text-decoration: none; 
            transition: all 0.3s ease;
        }
        .nav-link:hover { 
            background: rgba(155, 89, 182, 0.4); 
            transform: translateY(-2px); 
        }
        .recent-sessions { 
            background: rgba(255, 255, 255, 0.05); 
            padding: 20px; 
            border-radius: 12px; 
        }
        .session-item { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            padding: 10px 0; 
            border-bottom: 1px solid rgba(255, 255, 255, 0.1); 
        }
        .session-item:last-child { border-bottom: none; }
        .session-id { font-family: monospace; opacity: 0.7; }
        .session-time { opacity: 0.6; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎵 蕾拉酱 · 管理后台</h1>
            <p>音乐留学咨询系统数据管理</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_sessions }}</div>
                <div class="stat-label">总会话数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.active_sessions }}</div>
                <div class="stat-label">活跃会话</div>
            </div>
        </div>
        
        <div class="nav-links">
            <a href="/admin/sessions" class="nav-link">📋 查看所有会话</a>
            <a href="/chat" class="nav-link">💬 返回聊天</a>
        </div>
        
        <div class="recent-sessions">
            <h3 style="margin-bottom: 20px;">📈 最近会话</h3>
            {% for session in stats.recent_sessions %}
            <div class="session-item">
                <div>
                    <div class="session-id">{{ session.session_id[:8] }}...</div>
                    <div>{{ session.user_profile.get('name', '未知用户') if session.user_profile else '未知用户' }}</div>
                </div>
                <div class="session-time">{{ session.updated_at[:19] if session.updated_at else '未知时间' }}</div>
                <a href="/admin/session/{{ session.session_id }}" class="nav-link" style="margin: 0;">查看详情</a>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

ADMIN_SESSIONS_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>会话管理 - 蕾拉酱管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #2d1b69 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; margin-bottom: 30px; }
        .back-link { 
            display: inline-block; 
            margin-bottom: 20px; 
            color: #9b59b6; 
            text-decoration: none; 
        }
        .sessions-table { 
            background: rgba(255, 255, 255, 0.05); 
            border-radius: 12px; 
            overflow: hidden; 
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        th { background: rgba(155, 89, 182, 0.2); font-weight: 600; }
        .session-id { font-family: monospace; font-size: 0.9rem; }
        .status-active { color: #4CAF50; }
        .status-inactive { color: #f44336; }
        .view-link { 
            color: #9b59b6; 
            text-decoration: none; 
            padding: 4px 8px; 
            border-radius: 4px; 
            background: rgba(155, 89, 182, 0.1); 
        }
        .view-link:hover { background: rgba(155, 89, 182, 0.2); }
    </style>
</head>
<body>
    <div class="container">
        <a href="/admin" class="back-link">← 返回管理后台</a>
        
        <div class="header">
            <h1>📋 会话管理</h1>
            <p>共 {{ sessions|length }} 个会话</p>
        </div>
        
        <div class="sessions-table">
            <table>
                <thead>
                    <tr>
                        <th>会话ID</th>
                        <th>用户名</th>
                        <th>消息数</th>
                        <th>状态</th>
                        <th>创建时间</th>
                        <th>最后活动</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {% for session in sessions %}
                    <tr>
                        <td class="session-id">{{ session.session_id[:12] }}...</td>
                        <td>{{ session.user_profile.get('name', '未知') if session.user_profile else '未知' }}</td>
                        <td>{{ session.get('message_count', 0) }}</td>
                        <td class="{% if session.is_active %}status-active{% else %}status-inactive{% endif %}">
                            {{ '活跃' if session.is_active else '非活跃' }}
                        </td>
                        <td>{{ session.created_at[:19] if session.created_at else '未知' }}</td>
                        <td>{{ session.updated_at[:19] if session.updated_at else '未知' }}</td>
                        <td>
                            <a href="/admin/session/{{ session.session_id }}" class="view-link">查看详情</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

ADMIN_SESSION_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>会话详情 - 蕾拉酱管理后台</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #2d1b69 0%, #1a1a2e 50%, #16213e 100%);
            color: #ffffff;
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .back-link { 
            display: inline-block; 
            margin-bottom: 20px; 
            color: #9b59b6; 
            text-decoration: none; 
        }
        .session-header { 
            background: rgba(255, 255, 255, 0.05); 
            padding: 20px; 
            border-radius: 12px; 
            margin-bottom: 20px; 
        }
        .session-id { font-family: monospace; opacity: 0.7; margin-bottom: 10px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        .card { 
            background: rgba(255, 255, 255, 0.05); 
            padding: 20px; 
            border-radius: 12px; 
        }
        .card h3 { margin-bottom: 15px; color: #9b59b6; }
        .profile-item { margin-bottom: 10px; }
        .profile-label { opacity: 0.7; margin-right: 10px; }
        .chat-history { 
            background: rgba(255, 255, 255, 0.05); 
            padding: 20px; 
            border-radius: 12px; 
            max-height: 600px; 
            overflow-y: auto; 
        }
        .message { 
            margin-bottom: 15px; 
            padding: 10px; 
            border-radius: 8px; 
        }
        .message.user { 
            background: rgba(155, 89, 182, 0.2); 
            margin-left: 20px; 
        }
        .message.assistant { 
            background: rgba(255, 255, 255, 0.1); 
            margin-right: 20px; 
        }
        .message-header { 
            font-size: 0.9rem; 
            opacity: 0.7; 
            margin-bottom: 5px; 
        }
        .message-content { line-height: 1.5; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/admin/sessions" class="back-link">← 返回会话列表</a>
        
        <div class="session-header">
            <div class="session-id">会话ID: {{ session_info.session_id }}</div>
            <h1>会话详情</h1>
            <p>创建时间: {{ session_info.created_at[:19] if session_info.created_at else '未知' }} | 
               最后活动: {{ session_info.updated_at[:19] if session_info.updated_at else '未知' }} | 
               状态: {{ '活跃' if session_info.is_active else '非活跃' }}</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>👤 用户资料</h3>
                {% if user_profile %}
                    <div class="profile-item">
                        <span class="profile-label">姓名:</span>{{ user_profile.name or '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">年龄段:</span>{{ user_profile.age_range or '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">性别:</span>{{ user_profile.gender or '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">当前学段:</span>{{ user_profile.current_grade or '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">当前专业:</span>{{ user_profile.current_major or '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">目标专业:</span>{{ user_profile.target_major|join(', ') if user_profile.target_major else '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">意向国家:</span>{{ user_profile.countries|join(', ') if user_profile.countries else '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">入学时间:</span>{{ user_profile.intake_term or '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">预算:</span>{{ user_profile.budget_cny_range or '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">联系方式:</span>{{ user_profile.contact_method or '未填写' }}
                    </div>
                    <div class="profile-item">
                        <span class="profile-label">表单完成:</span>{{ '是' if user_profile.form_completed else '否' }}
                    </div>
                {% else %}
                    <p>暂无用户资料</p>
                {% endif %}
            </div>
            
            <div class="card">
                <h3>📊 统计信息</h3>
                <div class="profile-item">
                    <span class="profile-label">消息总数:</span>{{ stats.message_count or 0 }}
                </div>
                <div class="profile-item">
                    <span class="profile-label">会话时长:</span>
                    {% if session_info.created_at and session_info.updated_at %}
                        {{ ((session_info.updated_at|replace('T', ' ')|replace('Z', '')|strptime('%Y-%m-%d %H:%M:%S.%f')) - (session_info.created_at|replace('T', ' ')|replace('Z', '')|strptime('%Y-%m-%d %H:%M:%S.%f'))).total_seconds() // 60 }} 分钟
                    {% else %}
                        未知
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="chat-history">
            <h3 style="margin-bottom: 20px;">💬 聊天记录 ({{ chat_history|length }} 条消息)</h3>
            {% for message in chat_history %}
            <div class="message {{ message.message_type }}">
                <div class="message-header">
                    {{ '👤 用户' if message.message_type == 'user' else '🤖 蕾拉酱' }} - 
                    {{ message.created_at[:19] if message.created_at else '未知时间' }}
                </div>
                <div class="message-content">{{ message.content }}</div>
            </div>
            {% endfor %}
            
            {% if not chat_history %}
            <p style="text-align: center; opacity: 0.6;">暂无聊天记录</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

def render_template_string(template, **context):
    """简单的模板渲染函数"""
    from jinja2 import Template
    return Template(template).render(**context)



