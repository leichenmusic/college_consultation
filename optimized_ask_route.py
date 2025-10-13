# 这是优化后的ask路由代码，需要替换到app.py中

@app.route("/ask", methods=["POST"])
def ask():
    """处理前端发来的聊天消息，并调用你的 Vercel API 代理 - 优化版"""
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
        print(f"请求代理服务器失败: {e}")
        return jsonify({"error": "网络请求失败，请稍后重试"}), 500
    except Exception as e:
        print(f"处理响应时出错: {e}")
        return jsonify({"error": f"处理响应失败: {str(e)}"}), 500
