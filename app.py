import os
import requests # 导入 requests 库
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import re
import logging
import datetime
from dotenv import load_dotenv
from database import db_manager
from admin import create_admin_routes
from auth import auth_manager, User
from pm_agent import get_pm_agent, analyze_session_for_insights
from ai_conversation_optimizer import analyze_user_intent, generate_optimized_prompt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import uuid

# 加载环境变量
load_dotenv()

# --- 配置 ---
# 设置 Flask 应用
app = Flask(__name__)

# 配置Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面'
login_manager.login_message_category = 'info'

# 生产环境配置
if os.getenv('GAE_ENV', '').startswith('standard'):
    # 生产环境 - Google App Engine
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    # 使用更安全的 session 密钥
    app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
    # 配置日志级别
    logging.getLogger().setLevel(logging.INFO)
else:
    # 开发环境
    app.config['DEBUG'] = True
    app.secret_key = os.urandom(24)
    logging.getLogger().setLevel(logging.DEBUG) 

# !! 定义你的 Vercel 代理 API 地址
GEMINI_PROXY_URL = os.getenv('GEMINI_PROXY_URL', "https://vercel-gemini-proxy.vercel.app/api/gemini-2.5-flash")

# Flask-Login用户加载器
@login_manager.user_loader
def load_user(user_id):
    """Flask-Login要求的用户加载函数"""
    return auth_manager.get_user_by_id(user_id)

# 会话ID管理辅助函数
def get_or_create_session_id():
    """获取或创建会话ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        # 在数据库中创建新会话
        db_manager.create_session(session['session_id'])
        
        # 如果用户已登录，关联会话到用户
        if current_user.is_authenticated:
            auth_manager.link_session_to_user(session['session_id'], current_user.user_id)
    
    return session['session_id']

# --- 辅助函数 ---
def generate_first_conversation_prompt(user_profile, user_intent_analysis):
    """生成第一次对话的提示词"""
    # 检查是否有历史对话记录（已登录用户可能有历史记录）
    has_history = False
    if current_user.is_authenticated:
        try:
            session_id = get_or_create_session_id()
            recent_messages = db_manager.get_recent_messages(session_id, 5)
            has_history = len(recent_messages) > 0
        except:
            has_history = False
    
    # 根据用户是否已登录和是否有历史记录调整开场白
    if current_user.is_authenticated and user_profile.get('name'):
        if has_history:
            # 有历史记录的已登录用户
            greeting = f"嗨～{user_profile['name']}！我是蕾拉酱的AI小助手 🎶 欢迎回来！"
            next_question = "你想了解什么音乐留学问题呢？"
            choices = "院校推荐|申请指导|作品集建议|费用咨询|填写表单"
        else:
            # 没有历史记录的已登录用户
            greeting = f"嗨～{user_profile['name']}！我是蕾拉酱的AI小助手 🎶 欢迎来到音乐留学咨询！"
            next_question = "你目前在读什么学段？"
            choices = "初中|高中|本科在读|本科已毕业|研究生|在职提升|填写表单"
    else:
        # 未登录用户的开场白
        greeting = "嗨～我是蕾拉酱的AI小助手 🎶 欢迎来到音乐留学咨询！"
        next_question = "请问怎么称呼你？"
        choices = "直接输入姓名|填写表单"
    
    return f"""
你是「蕾拉酱的AI小助手」，专业音乐留学顾问。

请发送开场白：
{greeting}

{next_question}

[CHOICES]
{choices}
[/CHOICES]

要求：简洁友好，不超过3行。
"""

def extract_user_info(user_message, current_profile):
    """从用户消息中提取并更新用户信息"""
    message_lower = user_message.lower().strip()
    
    # 如果还没有姓名且用户未登录，尝试从消息中提取
    if ('name' not in current_profile or not current_profile['name']) and not current_user.is_authenticated:
        # 简单的姓名提取逻辑
        if len(message_lower) <= 10 and not any(word in message_lower for word in 
            ['你好', '嗯', '是的', '对', '不是', '没有', '有', '我想', '我要', '请问', '谢谢', '跳过', '填写表单']):
            current_profile['name'] = user_message.strip()
    
    # 提取年龄段信息
    age_mappings = {
        '≤15': '≤15', '15以下': '≤15', '15岁以下': '≤15',
        '16-18': '16–18', '16到18': '16–18', '高中': '16–18',
        '19-22': '19–22', '19到22': '19–22', '大学': '19–22', '本科': '19–22',
        '23-26': '23–26', '23到26': '23–26', '研究生': '23–26',
        '27-30': '27–30', '27到30': '27–30',
        '30+': '30+', '30以上': '30+', '30岁以上': '30+'
    }
    
    for key, value in age_mappings.items():
        if key in message_lower:
            current_profile['age_range'] = value
            break
    
    # 提取性别信息
    if any(word in message_lower for word in ['女', '女生', '女孩']):
        current_profile['gender'] = '女'
    elif any(word in message_lower for word in ['男', '男生', '男孩']):
        current_profile['gender'] = '男'
    
    # 提取学段信息
    grade_mappings = {
        '初中': '初中', '中学': '初中',
        '高中': '高中', '高中生': '高中',
        '本科在读': '本科在读', '大学在读': '本科在读', '本科生': '本科在读',
        '本科已毕业': '本科已毕业', '本科毕业': '本科已毕业',
        '研究生': '研究生', '硕士': '研究生', '博士': '研究生',
        '在职': '在职提升', '工作': '在职提升'
    }
    
    for key, value in grade_mappings.items():
        if key in message_lower:
            current_profile['current_grade'] = value
            break
    
    # 提取专业信息
    major_mappings = {
        '声乐': '声乐', '唱歌': '声乐', '歌唱': '声乐',
        '钢琴': '器乐', '小提琴': '器乐', '大提琴': '器乐', '长笛': '器乐', '萨克斯': '器乐',
        '作曲': '作曲/指挥/音乐教育', '指挥': '作曲/指挥/音乐教育', '音乐教育': '作曲/指挥/音乐教育',
        '音乐技术': '音乐技术/音乐产业', '音乐制作': '音乐技术/音乐产业', '音乐产业': '音乐技术/音乐产业'
    }
    
    for key, value in major_mappings.items():
        if key in message_lower:
            current_profile['current_major'] = value
            break
    
    # 提取国家信息
    countries = []
    country_mappings = {
        '美国': '美国', 'usa': '美国', 'america': '美国',
        '英国': '英国', 'uk': '英国', 'britain': '英国',
        '意大利': '意大利', 'italy': '意大利',
        '德国': '德国', 'germany': '德国',
        '法国': '法国', 'france': '法国',
        '加拿大': '加拿大', 'canada': '加拿大',
        '澳大利亚': '澳大利亚', 'australia': '澳大利亚', '澳洲': '澳大利亚'
    }
    
    for key, value in country_mappings.items():
        if key in message_lower:
            countries.append(value)
    
    if countries:
        current_profile['countries'] = list(set(countries))  # 去重
    
    # 将对话内容添加到profile中
    if 'conversation_data' not in current_profile:
        current_profile['conversation_data'] = []
    current_profile['conversation_data'].append(user_message)
    
    return current_profile

# --- 路由和逻辑 ---

@app.route("/")
def index():
    """首页重定向到聊天页面"""
    return redirect(url_for('chat'))


@app.route("/chat")
def chat():
    """渲染聊天页面"""
    session_id = get_or_create_session_id()
    
    # 从数据库获取或初始化用户档案
    user_profile = db_manager.get_user_profile(session_id)
    if not user_profile:
        user_profile = {}
        session['user_profile'] = user_profile
    else:
        session['user_profile'] = user_profile
        
    return render_template("chat.html")

@app.route("/test_buttons")
def test_buttons():
    """测试按钮功能的页面"""
    return render_template("test_buttons.html")

@app.route("/force_choice_test", methods=["POST"])
def force_choice_test():
    """强制返回选择题格式进行测试"""
    return jsonify({
        "response": "你现在在读什么学历呢？\n[CHOICES]\n高中在读|本科在读|硕士在读|已经毕业\n[/CHOICES]"
    })

@app.route("/generate_summary", methods=["POST"])
def generate_summary():
    """生成用户信息的JSON总结和下一步建议"""
    user_profile = session.get('user_profile', {})
    
    # 构建标准化的JSON输出
    summary_json = {
        "name": user_profile.get('name', ''),
        "age_range": user_profile.get('age_range', ''),
        "gender": user_profile.get('gender', ''),
        "current_grade": user_profile.get('current_grade', ''),
        "current_major": user_profile.get('current_major', ''),
        "target_major": user_profile.get('target_major', ''),
        "countries": user_profile.get('countries', []),
        "intake_term": user_profile.get('intake_term', ''),
        "budget_cny_range": user_profile.get('budget_cny_range', ''),
        "special_requests": user_profile.get('special_requests', []),
        "contact_method": user_profile.get('contact_method', ''),
        "notes": user_profile.get('notes', '')
    }
    
    # 生成简短总结
    summary_parts = []
    if summary_json['name']:
        summary_parts.append(f"{summary_json['name']}")
    if summary_json['target_major']:
        summary_parts.append(f"想学{summary_json['target_major']}")
    if summary_json['countries']:
        summary_parts.append(f"目标国家：{', '.join(summary_json['countries'])}")
    if summary_json['intake_term']:
        summary_parts.append(f"计划{summary_json['intake_term']}入学")
    if summary_json['budget_cny_range']:
        summary_parts.append(f"预算{summary_json['budget_cny_range']}万")
    
    summary_text = "，".join(summary_parts) if summary_parts else "信息收集中"
    
    return jsonify({
        "json_data": summary_json,
        "summary": summary_text,
        "next_steps": [
            "领取初步院校清单",
            "预约顾问15分钟初谈", 
            "获取曲目与录制指南",
            "生成申请时间线",
            "加入咨询群"
        ]
    })

@app.route("/test_choice_buttons")
def test_choice_buttons():
    """测试选择题按钮功能的专用页面"""
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>测试选择题按钮</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <div class="main-container">
            <div class="right-panel">
                <div class="chat-container">
                    <div class="chat-messages" id="chat-messages"></div>
                    <button onclick="testChoiceButtons()">测试选择题按钮</button>
                </div>
            </div>
        </div>
        
        <script>
            const chatMessages = document.getElementById('chat-messages');
            
            // 复制必要的函数
            function addMessage(sender, text, useTypewriter = false) {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message', sender + '-message');
                chatMessages.appendChild(messageElement);
                
                if (useTypewriter && sender === 'gemini') {
                    typewriterEffect(messageElement, text, 20, () => {
                        if (sender === 'gemini') {
                            addChoiceButtons(messageElement, text);
                        }
                    });
                } else {
                    displayFormattedText(messageElement, text);
                    if (sender === 'gemini') {
                        addChoiceButtons(messageElement, text);
                    }
                }
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function displayFormattedText(element, text) {
                let cleanText = text.replace(/\\[CHOICES\\][\\s\\S]*?\\[\\/CHOICES\\]/g, '');
                let formattedText = cleanText
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>')
                    .replace(/\\*(.*?)\\*/g, '<i>$1</i>')
                    .replace(/\\n/g, '<br>');
                element.innerHTML = formattedText;
            }
            
            function addChoiceButtons(messageElement, text) {
                console.log('检查选择题:', text);
                const choicesMatch = text.match(/\\[CHOICES\\]([\\s\\S]*?)\\[\\/CHOICES\\]/);
                if (choicesMatch) {
                    console.log('找到选择题:', choicesMatch[1]);
                    const choicesText = choicesMatch[1].trim();
                    const choices = choicesText.split('|').map(choice => choice.trim());
                    
                    const buttonsContainer = document.createElement('div');
                    buttonsContainer.classList.add('choice-buttons');
                    
                    choices.forEach(choice => {
                        const button = document.createElement('button');
                        button.classList.add('choice-btn');
                        button.textContent = choice;
                        button.onclick = () => handleChoiceClick(choice, buttonsContainer);
                        buttonsContainer.appendChild(button);
                    });
                    
                    messageElement.appendChild(buttonsContainer);
                } else {
                    console.log('没有找到选择题格式');
                }
            }
            
            function handleChoiceClick(choice, buttonsContainer) {
                const buttons = buttonsContainer.querySelectorAll('.choice-btn');
                buttons.forEach(btn => {
                    btn.disabled = true;
                    if (btn.textContent === choice) {
                        btn.classList.add('selected');
                    }
                });
                alert('你选择了: ' + choice);
            }
            
            function typewriterEffect(element, text, speed = 20, callback = null) {
                let formattedText = text
                    .replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>')
                    .replace(/\\*(.*?)\\*/g, '<i>$1</i>')
                    .replace(/\\n/g, '<br>');
                
                let displayText = formattedText.replace(/\\[CHOICES\\][\\s\\S]*?\\[\\/CHOICES\\]/g, '');
                
                element.innerHTML = '';
                let index = 0;
                let currentText = '';
                
                const typeInterval = setInterval(() => {
                    if (index < displayText.length) {
                        if (displayText[index] === '<') {
                            let tagEnd = displayText.indexOf('>', index);
                            if (tagEnd !== -1) {
                                currentText += displayText.substring(index, tagEnd + 1);
                                index = tagEnd + 1;
                            } else {
                                currentText += displayText[index];
                                index++;
                            }
                        } else {
                            currentText += displayText[index];
                            index++;
                        }
                        
                        element.innerHTML = currentText + '<span class="typing-cursor">|</span>';
                    } else {
                        element.innerHTML = currentText;
                        clearInterval(typeInterval);
                        
                        if (callback && typeof callback === 'function') {
                            callback();
                        }
                    }
                }, speed);
            }
            
            function testChoiceButtons() {
                // 测试不带打字机效果的
                addMessage('gemini', '你现在在读什么学历呢？\\n[CHOICES]\\n高中在读|本科在读|硕士在读|已经毕业\\n[/CHOICES]', false);
                
                // 测试带打字机效果的
                setTimeout(() => {
                    addMessage('gemini', '你想申请什么学历呢？\\n[CHOICES]\\n本科|硕士|博士\\n[/CHOICES]', true);
                }, 2000);
            }
        </script>
    </body>
    </html>
    """

@app.route("/get_user_profile", methods=["GET"])
def get_user_profile():
    """获取当前用户档案信息"""
    session_id = get_or_create_session_id()
    
    # 优先从数据库获取，然后从session获取
    user_profile = db_manager.get_user_profile(session_id) or session.get('user_profile', {})
    
    return jsonify({"user_profile": user_profile})

@app.route("/submit_form", methods=["POST"])
def submit_form():
    """处理聊天界面中的表单提交"""
    try:
        session_id = get_or_create_session_id()
        
        # 检查请求数据
        if not request.json:
            return jsonify({
                "success": False,
                "message": "请求数据为空"
            }), 400
            
        data = request.json
        print(f"收到表单数据: {data}")  # 调试日志
        
        # 验证必填字段
        if not data.get("name"):
            return jsonify({
                "success": False,
                "message": "姓名是必填项"
            }), 400
        
        if not data.get("current_grade"):
            return jsonify({
                "success": False,
                "message": "当前学段是必填项"
            }), 400
        
        # 处理多选字段
        special_requests = data.get("special_requests", [])
        countries = data.get("countries", [])
        target_major = data.get("target_major", [])
        
        user_profile = {
            "name": data.get("name"),
            "age_range": data.get("age_range"),
            "gender": data.get("gender"),
            "current_grade": data.get("current_grade"),
            "current_major": data.get("current_major"),
            "target_major": target_major[0] if len(target_major) == 1 else target_major,
            "countries": countries,
            "intake_term": data.get("intake_term"),
            "budget_cny_range": data.get("budget_cny_range"),
            "special_requests": special_requests,
            "contact_method": data.get("contact_method"),
            "notes": data.get("notes"),
            "form_completed": True
        }
        
        print(f"处理后的用户档案: {user_profile}")  # 调试日志
        
        # 保存到session和数据库
        session['user_profile'] = user_profile
        
        # 尝试保存到数据库
        db_save_success = False
        db_error_msg = None
        try:
            db_save_success = db_manager.save_user_profile(session_id, user_profile)
            if db_save_success:
                print("用户档案保存到数据库成功")
            else:
                print("数据库保存失败：连接问题")
                db_error_msg = "数据库连接不可用"
        except Exception as db_error:
            print(f"数据库保存失败: {db_error}")
            db_error_msg = str(db_error)
            # 数据库保存失败不影响表单提交成功
        
        # 生成AI总结
        summary_parts = []
        if user_profile.get('name'):
            summary_parts.append(f"你好 {user_profile['name']}")
        
        summary_parts.append("我已经收到你的信息了！让我总结一下：")
        
        details = []
        if user_profile.get('current_grade'):
            details.append(f"当前学段：{user_profile['current_grade']}")
        if user_profile.get('current_major'):
            details.append(f"专业方向：{user_profile['current_major']}")
        if user_profile.get('target_major'):
            majors = user_profile['target_major'] if isinstance(user_profile['target_major'], list) else [user_profile['target_major']]
            details.append(f"目标专业：{', '.join(majors)}")
        if user_profile.get('countries'):
            details.append(f"意向国家：{', '.join(user_profile['countries'])}")
        if user_profile.get('intake_term'):
            details.append(f"入学时间：{user_profile['intake_term']}")
        if user_profile.get('budget_cny_range'):
            details.append(f"预算：{user_profile['budget_cny_range']}万")
        
        if details:
            summary_parts.append("\n".join(details))
        
        summary_parts.append("\n信息是否正确？如果需要修改，我可以重新为你打开表单。")
        summary_parts.append("\n[CHOICES]\n信息正确，继续咨询|需要修改信息\n[/CHOICES]")
        
        summary_text = "\n\n".join(summary_parts)
        
        return jsonify({
            "success": True,
            "summary": summary_text,
            "database_saved": db_save_success,
            "database_error": db_error_msg
        })
        
    except Exception as e:
        print(f"表单提交处理出错: {e}")
        return jsonify({
            "success": False,
            "message": f"服务器处理错误: {str(e)}"
        }), 500

@app.route("/ask", methods=["POST"])
def ask():
    """处理前端发来的聊天消息，并调用你的 Vercel API 代理"""
    session_id = get_or_create_session_id()
    data = request.json
    user_message = data.get("message")
    chat_history = data.get("history", [])
    
    # 保存用户消息到数据库
    db_manager.save_message(session_id, 'user', user_message)
    
    user_profile = session.get('user_profile', {}) or db_manager.get_user_profile(session_id) or {}
    
    # 如果用户已登录，自动填充用户信息到profile
    if current_user.is_authenticated and not user_profile.get('name'):
        user_profile['name'] = current_user.display_name or current_user.username
        user_profile['email'] = current_user.email
        # 关联当前会话到用户
        auth_manager.link_session_to_user(session_id, current_user.user_id)
        # 保存更新的profile
        session['user_profile'] = user_profile
        db_manager.save_user_profile(session_id, user_profile)
        print(f"已登录用户 {user_profile['name']} 的信息已自动填充")
    
    # 🚀 智能分析用户意图
    user_intent_analysis = analyze_user_intent(user_message, chat_history, user_profile)
    print(f"用户意图分析: {user_intent_analysis}")
    
    # 如果不是第一次对话，更新用户信息
    if chat_history and user_message:
        user_profile = extract_user_info(user_message, user_profile)
        session['user_profile'] = user_profile
        # 更新数据库中的用户信息
        db_manager.save_user_profile(session_id, user_profile)
    
    # 🎯 使用优化的提示词生成系统
    if not chat_history:
        # 第一次对话的开场白
        prompt = generate_first_conversation_prompt(user_profile, user_intent_analysis)
    else:
        # 后续对话使用智能提示词
        prompt = generate_optimized_prompt(user_message, user_profile, chat_history, user_intent_analysis)

    # 构建发送到代理服务器的 payload
    if not chat_history:
        # 检查是否有历史对话记录（已登录用户可能有历史记录）
        has_history = False
        if current_user.is_authenticated:
            try:
                recent_messages = db_manager.get_recent_messages(session_id, 5)
                has_history = len(recent_messages) > 0
            except:
                has_history = False
        
        # 根据用户是否已登录和是否有历史记录调整开场白
        if current_user.is_authenticated and user_profile.get('name'):
            if has_history:
                # 有历史记录的已登录用户
                greeting = f"嗨～{user_profile['name']}！我是蕾拉酱的AI小助手 🎶 欢迎回来！我已经加载了我们之前的对话记录。"
                next_question = "基于我们之前的交流，你还有什么想了解的音乐留学问题吗？或者我们可以继续完善你的申请信息。"
                choices = "继续咨询|填写表单|查看院校推荐"
            else:
                # 没有历史记录的已登录用户
                greeting = f"嗨～{user_profile['name']}！我是蕾拉酱的AI小助手 🎶 欢迎来到音乐留学咨询！让我为你提供专业的音乐留学指导。"
                next_question = "让我了解一下你的音乐背景，你目前在读什么学段呢？"
                choices = "初中|高中|本科在读|本科已毕业|研究生|在职提升|填写表单"
        else:
            # 未登录用户的开场白
            greeting = "嗨～我是蕾拉酱的AI小助手 🎶 欢迎来到音乐留学咨询！你可以跟我继续聊天。让我收集你的信息，也可以随时说'填写表单'，或点击下面的按钮。"
            next_question = "请问你怎么称呼？"
            choices = "填写表单"
        
        prompt = f"""
        你是「蕾拉酱的AI小助手」，音乐留学顾问机器人。请用简短、礼貌、低打扰的方式，与学生完成信息采集或引导其使用表单。每一步提供按钮选项，并始终包含「其他/自填」「跳过」「返回上一步」。任意时刻允许切换为表单模式。

        收集字段包含：name、age_range、gender、current_grade、current_major、target_major、countries（多选）、intake_term、budget_cny_range、special_requests（多选）、contact_method、notes。

        若用户已提供信息则跳过重复提问。任何问题都要支持"跳过"。结束时输出统一 JSON（缺失用 null/[]），并给 1–2 句总结与 3–5 个下一步按钮（如"领取院校清单/预约顾问/曲目指南/申请时间线/加入群"）。

        默认中文，若用户要求英文则切英文。严禁过度营销或作出虚假承诺。

        回答问题一定要简短，不要超过10行。

        ## 当前已收集的学生信息
        {user_profile if user_profile else "暂无信息"}

        请发送开场白：
        {greeting}

        {next_question}

        [CHOICES]
        {choices}
        [/CHOICES]
        """
    else:
        # 如果是后续对话，需要分析用户回答并继续提问
        prompt = f"""
        你是「蕾拉酱的AI小助手」，音乐留学顾问机器人。继续与学生进行信息采集，每一步提供按钮选项，并始终包含「其他/自填」「跳过」「返回上一步」。

        ## 当前已收集的学生信息
        {user_profile}

        ## 用户刚才的回答
        {user_message}

        ## 需要收集的字段（按优先级）
        1. name（称呼）- 如果还没有且用户未登录
        2. age_range（年龄段）- 按钮选项：≤15|16–18|19–22|23–26|27–30|30+|其他/自填|跳过
        3. gender（性别）- 按钮选项：女|男|非二元/不便透露|其他/自填|跳过
        4. current_grade（当前学段）- 按钮选项：初中|高中|本科在读|本科已毕业|研究生|在职提升|其他/自填|跳过
        5. current_major（当前专业）- 按钮选项：声乐|器乐|作曲/指挥/音乐教育|音乐技术/音乐产业|其他/自填|跳过
        6. target_major（目标专业）- 多选按钮：声乐表演|音乐剧|器乐表演|作曲/编曲|指挥|音乐教育|音乐科技/制作|音乐商业/管理|其他/自填|跳过
        7. countries（意向国家）- 多选按钮：美国|英国|意大利|德国|法国|加拿大|澳大利亚|西班牙|荷兰|奥地利|其他/自填|跳过
        8. intake_term（入学时间）- 按钮选项：2025 Fall|2026 Fall|2027 Fall|2026 Spring|待定/跳过|其他/自填
        9. budget_cny_range（预算区间万元）- 按钮选项：≤30|30–60|60–100|100–150|≥150|待定/跳过
        10. special_requests（特殊诉求）- 多选按钮：学校推荐|国家推荐|教授推荐/试音|奖学金策略|语言/考试辅导|作品集/曲目/录制|面试/试音模拟|时间线提醒/清单|宿舍/生活指导|其他/自填|暂无
        11. contact_method（联系方式）- 按钮选项：邮箱|微信|手机|都可以|稍后提供

        ## 任务指令
        1. 简短回应用户刚才说的话（不超过一行）
        2. 根据已收集信息，问下一个缺失的字段
        3. 使用对应的按钮选项格式 [CHOICES]选项1|选项2|...[/CHOICES]
        4. 如果信息收集差不多了，询问是否结束并生成总结
        5. 每次回复控制在2行以内，语气轻松友好

        ## 特殊情况处理
        - 如果用户说"直接填写表单"，回复表单链接提示
        - 如果用户说"跳过"，直接进入下一个问题
        - 如果用户说"返回上一步"，重新问上一个问题
        - 如果收集了6个以上字段，可以询问是否结束

        请简短回复并提供相应的选择按钮。
        """

    # 构建发送到代理服务器的 payload
    # 修改payload格式以匹配API的期望格式
    if not chat_history:
        # 第一次对话，只发送系统指令
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ]
        }
    else:
        # 后续对话，包含历史记录
        contents = []
        # 📊 只保留最近10轮对话，避免token过多，提升响应速度
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        for msg in recent_history:
            contents.append(msg)
        # 添加当前用户消息
        contents.append({
            "role": "user", 
            "parts": [{"text": user_message}]
        })
        payload = {"contents": contents}
    
    try:
        # 使用 requests 库向你的 Vercel API 发送 POST 请求
        response = requests.post(
            GEMINI_PROXY_URL, 
            json=payload, 
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        # 打印调试信息
        print(f"Intent: {user_intent_analysis['primary_intent']}, Profile completeness: {user_intent_analysis['profile_completeness']:.2f}")
        print(f"Response status: {response.status_code}")
        
        response.raise_for_status() 
        api_response_data = response.json()
        
        # 尝试不同的响应字段名
        ai_text = (api_response_data.get("text") or 
                  api_response_data.get("response") or
                  api_response_data.get("content") or
                  api_response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text") or
                  "抱歉，代理返回了无效的数据格式。")
        
        # 保存AI响应到数据库
        db_manager.save_message(session_id, 'assistant', ai_text)
        
        return jsonify({"response": ai_text})

    except requests.exceptions.RequestException as e:
        print(f"调用代理 API 时出错: {e}")
        
        # 如果第一种格式失败，尝试备用格式
        try:
            backup_payload = {
                "message": prompt if not chat_history else user_message,
                "history": chat_history
            }
            print(f"尝试备用格式: {backup_payload}")
            
            backup_response = requests.post(
                GEMINI_PROXY_URL, 
                json=backup_payload, 
                headers={'Content-Type': 'application/json'},
                timeout=120
            )
            backup_response.raise_for_status()
            backup_data = backup_response.json()
            ai_text = (backup_data.get("text") or 
                      backup_data.get("response") or
                      "使用备用格式成功，但返回格式未知。")
            
            # 保存AI响应到数据库
            db_manager.save_message(session_id, 'assistant', ai_text)
            
            return jsonify({"response": ai_text})
            
        except Exception as backup_e:
            print(f"备用格式也失败: {backup_e}")
            return jsonify({"error": f"与蕾拉酱的AI小助理通信时发生网络错误: {e}"}), 500
            
    except Exception as e:
        print(f"处理代理响应时出错: {e}")
        return jsonify({"error": f"处理蕾拉酱的AI小助理响应时发生错误: {e}"}), 500


# === 认证相关路由 ===

@app.route("/register", methods=["GET", "POST"])
def register():
    """用户注册页面"""
    if request.method == "GET":
        google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        return render_template("register.html", google_client_id=google_client_id)
    
    # 处理注册表单
    data = request.json if request.is_json else request.form
    
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    display_name = data.get("display_name", "").strip()
    
    if not display_name:
        display_name = username
    
    success, message, user = auth_manager.create_local_user(username, email, password, display_name)
    
    if request.is_json:
        if success:
            login_user(user)
            # 关联当前会话到用户
            session_id = get_or_create_session_id()
            auth_manager.link_session_to_user(session_id, user.user_id)
            return jsonify({"success": True, "message": message, "redirect": url_for('chat')})
        else:
            return jsonify({"success": False, "message": message})
    else:
        if success:
            login_user(user)
            session_id = get_or_create_session_id()
            auth_manager.link_session_to_user(session_id, user.user_id)
            return redirect(url_for('chat'))
        else:
            return render_template("register.html", error=message)

@app.route("/login", methods=["GET", "POST"])
def login():
    """用户登录页面"""
    if request.method == "GET":
        google_client_id = os.getenv('GOOGLE_CLIENT_ID', '')
        return render_template("login.html", google_client_id=google_client_id)
    
    # 处理登录表单
    data = request.json if request.is_json else request.form
    
    username_or_email = data.get("username_or_email", "").strip()
    password = data.get("password", "").strip()
    
    success, message, user = auth_manager.authenticate_local_user(username_or_email, password)
    
    if request.is_json:
        if success:
            login_user(user)
            # 关联当前会话到用户
            session_id = get_or_create_session_id()
            auth_manager.link_session_to_user(session_id, user.user_id)
            return jsonify({"success": True, "message": message, "redirect": url_for('chat')})
        else:
            return jsonify({"success": False, "message": message})
    else:
        if success:
            login_user(user)
            session_id = get_or_create_session_id()
            auth_manager.link_session_to_user(session_id, user.user_id)
            return redirect(url_for('chat'))
        else:
            return render_template("login.html", error=message)

@app.route("/logout")
@login_required
def logout():
    """用户登出"""
    logout_user()
    return redirect(url_for('index'))

@app.route("/auth/google", methods=["POST"])
def google_auth():
    """Google OAuth登录"""
    data = request.json
    token = data.get("token")
    
    if not token:
        return jsonify({"success": False, "message": "缺少Google token"})
    
    # 验证Google token
    success, message, google_user_info = auth_manager.verify_google_token(token)
    
    if not success:
        return jsonify({"success": False, "message": message})
    
    # 认证或创建Google用户
    success, message, user = auth_manager.authenticate_google_user(google_user_info)
    
    if success:
        login_user(user)
        # 关联当前会话到用户
        session_id = get_or_create_session_id()
        auth_manager.link_session_to_user(session_id, user.user_id)
        return jsonify({"success": True, "message": message, "redirect": url_for('chat')})
    else:
        return jsonify({"success": False, "message": message})

@app.route("/api/check_username")
def check_username():
    """检查用户名是否可用"""
    username = request.args.get("username", "").strip()
    
    if len(username) < 3:
        return jsonify({"available": False, "message": "用户名至少需要3个字符"})
    
    available = auth_manager.is_username_available(username)
    
    if available:
        return jsonify({"available": True, "message": "用户名可用"})
    else:
        # 提供用户名建议
        suggestions = auth_manager.generate_username_suggestions(username)
        available_suggestions = []
        
        for suggestion in suggestions:
            if auth_manager.is_username_available(suggestion):
                available_suggestions.append(suggestion)
                if len(available_suggestions) >= 3:
                    break
        
        return jsonify({
            "available": False, 
            "message": "用户名已被使用",
            "suggestions": available_suggestions
        })

@app.route("/api/user_info")
@login_required
def get_user_info():
    """获取当前登录用户信息"""
    return jsonify({
        "success": True,
        "user": current_user.to_dict()
    })

@app.route("/test_google_login")
def test_google_login():
    """Google登录测试页面"""
    return render_template("test_google_login.html")

@app.route("/api/check_database")
def check_database():
    """检查数据库连接状态和用户数据"""
    session_id = get_or_create_session_id()
    
    # 检查数据库连接
    db_connected = db_manager._check_connection()
    
    # 尝试获取用户资料
    user_profile = None
    if db_connected:
        try:
            user_profile = db_manager.get_user_profile(session_id)
        except Exception as e:
            return jsonify({
                "database_connected": db_connected,
                "database_error": str(e),
                "session_id": session_id,
                "user_profile_from_db": None,
                "user_profile_from_session": session.get('user_profile')
            })
    
    return jsonify({
        "database_connected": db_connected,
        "session_id": session_id,
        "user_profile_from_db": user_profile,
        "user_profile_from_session": session.get('user_profile'),
        "supabase_url": os.getenv('SUPABASE_URL', 'Not configured'),
        "supabase_key_configured": bool(os.getenv('SUPABASE_ANON_KEY')) and os.getenv('SUPABASE_ANON_KEY') != 'your-supabase-anon-key'
    })

@app.route("/api/chat_history")
@login_required
def get_chat_history():
    """获取已登录用户的聊天历史"""
    try:
        session_id = get_or_create_session_id()
        
        # 获取最近50条消息
        messages = db_manager.get_recent_messages(session_id, 50)
        
        # 转换为前端需要的格式
        chat_history = []
        conversation_history = []
        
        for msg in messages:
            # 添加到聊天显示历史
            chat_history.append({
                'sender': msg['sender_type'],
                'message': msg['content'],
                'timestamp': msg['created_at']
            })
            
            # 添加到对话历史（用于AI上下文）
            if msg['sender_type'] == 'user':
                conversation_history.append({
                    'role': 'user',
                    'parts': [{'text': msg['content']}]
                })
            elif msg['sender_type'] == 'assistant':
                conversation_history.append({
                    'role': 'model', 
                    'parts': [{'text': msg['content']}]
                })
        
        return jsonify({
            "success": True,
            "chat_history": chat_history,
            "conversation_history": conversation_history,
            "message_count": len(messages)
        })
        
    except Exception as e:
        print(f"获取聊天历史失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# === PM Agent Routes ===

@app.route("/pm/dashboard")
@login_required
def pm_dashboard():
    """PM Dashboard - requires admin access"""
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    return render_template('pm_dashboard.html')

@app.route("/api/pm/analysis")
@login_required
def pm_analysis():
    """Get strategic analysis from PM agent"""
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        analysis = pm_agent.generate_strategic_analysis()
        return jsonify({
            "success": True,
            "analysis": analysis
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/pm/roadmap")
@login_required
def pm_roadmap():
    """Get product roadmap"""
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        roadmap = pm_agent.get_product_roadmap()
        # Convert dataclasses to dicts for JSON serialization
        json_roadmap = {}
        for status, features in roadmap.items():
            json_roadmap[status] = [
                {
                    "id": f.id,
                    "name": f.name,
                    "description": f.description,
                    "priority": f.priority.value,
                    "status": f.status.value,
                    "estimated_effort": f.estimated_effort,
                    "business_value": f.business_value,
                    "target_users": f.target_users,
                    "success_metrics": f.success_metrics,
                    "dependencies": f.dependencies,
                    "created_date": f.created_date,
                    "target_launch": f.target_launch,
                    "owner": f.owner
                } for f in features
            ]
        
        return jsonify({
            "success": True,
            "roadmap": json_roadmap
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/pm/features", methods=["POST"])
@login_required
def add_feature():
    """Add a new feature to the roadmap"""
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        feature_data = request.json
        feature = pm_agent.add_feature(feature_data)
        
        return jsonify({
            "success": True,
            "feature": {
                "id": feature.id,
                "name": feature.name,
                "description": feature.description,
                "priority": feature.priority.value,
                "status": feature.status.value,
                "estimated_effort": feature.estimated_effort,
                "business_value": feature.business_value,
                "target_users": feature.target_users,
                "success_metrics": feature.success_metrics,
                "dependencies": feature.dependencies,
                "created_date": feature.created_date,
                "target_launch": feature.target_launch,
                "owner": feature.owner
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/pm/features/<feature_id>/status", methods=["PUT"])
@login_required
def update_feature_status(feature_id):
    """Update feature status"""
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        from pm_agent import FeatureStatus
        new_status = FeatureStatus(request.json.get('status'))
        success = pm_agent.update_feature_status(feature_id, new_status)
        
        return jsonify({
            "success": success,
            "message": f"Feature {feature_id} status updated to {new_status.value}" if success else "Feature not found"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/pm/insights")
@login_required
def pm_insights():
    """Get user behavior insights"""
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        # Analyze current session for insights
        session_data = {
            "user_profile": session.get('user_profile', {}),
            "chat_history": []  # Could be enhanced to include recent chat data
        }
        
        insights = analyze_session_for_insights(session_data, db_manager)
        
        return jsonify({
            "success": True,
            "insights": insights
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/api/pm/export/<format>")
@login_required
def export_roadmap(format):
    """Export roadmap in specified format"""
    if not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        if format not in ["json", "markdown"]:
            return jsonify({"error": "Unsupported format"}), 400
        
        content = pm_agent.export_roadmap(format)
        
        if format == "json":
            return jsonify({
                "success": True,
                "content": content,
                "filename": f"roadmap_{datetime.datetime.now().strftime('%Y%m%d')}.json"
            })
        else:
            return jsonify({
                "success": True,
                "content": content,
                "filename": f"roadmap_{datetime.datetime.now().strftime('%Y%m%d')}.md"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# 添加管理后台路由
create_admin_routes(app)

# 初始化PM Agent
pm_agent = get_pm_agent(db_manager)

if __name__ == "__main__":
    # For local development
    app.run(debug=True, port=5001)
