#!/usr/bin/env python3
"""
测试表单提交到Supabase数据库的功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db_manager
import uuid

def test_form_submission():
    """测试表单提交功能"""
    print("🧪 开始测试表单提交到Supabase...")
    
    # 创建测试会话
    test_session_id = str(uuid.uuid4())
    print(f"📝 创建测试会话: {test_session_id}")
    
    # 创建会话
    session_id = db_manager.create_session(test_session_id)
    print(f"✅ 会话创建成功: {session_id}")
    
    # 模拟表单数据
    test_profile = {
        "name": "测试用户",
        "age_range": "19–22",
        "gender": "女",
        "current_grade": "本科在读",
        "current_major": "声乐",
        "target_major": ["声乐表演", "音乐剧"],
        "countries": ["美国", "英国"],
        "intake_term": "2025 Fall",
        "budget_cny_range": "60–100",
        "special_requests": ["学校推荐", "奖学金策略"],
        "contact_method": "微信",
        "notes": "希望了解更多关于声乐表演专业的信息",
        "form_completed": True
    }
    
    print("📋 测试用户资料:")
    for key, value in test_profile.items():
        print(f"   {key}: {value}")
    
    # 保存用户资料
    print("\n💾 保存用户资料到Supabase...")
    success = db_manager.save_user_profile(session_id, test_profile)
    
    if success:
        print("✅ 用户资料保存成功!")
        
        # 验证数据是否正确保存
        print("\n🔍 验证保存的数据...")
        retrieved_profile = db_manager.get_user_profile(session_id)
        
        if retrieved_profile:
            print("✅ 数据检索成功!")
            print("📋 检索到的用户资料:")
            for key, value in retrieved_profile.items():
                if key not in ['id', 'created_at', 'updated_at']:
                    print(f"   {key}: {value}")
            
            # 验证关键字段
            if retrieved_profile.get('name') == test_profile['name']:
                print("✅ 姓名字段验证通过")
            else:
                print("❌ 姓名字段验证失败")
                
            if retrieved_profile.get('target_major') == test_profile['target_major']:
                print("✅ 目标专业字段验证通过")
            else:
                print("❌ 目标专业字段验证失败")
                
            if retrieved_profile.get('countries') == test_profile['countries']:
                print("✅ 意向国家字段验证通过")
            else:
                print("❌ 意向国家字段验证失败")
                
        else:
            print("❌ 数据检索失败")
            
    else:
        print("❌ 用户资料保存失败")
    
    # 测试聊天消息保存
    print("\n💬 测试聊天消息保存...")
    
    # 保存用户消息
    user_msg_success = db_manager.save_message(session_id, 'user', '你好，我想了解声乐表演专业')
    if user_msg_success:
        print("✅ 用户消息保存成功")
    else:
        print("❌ 用户消息保存失败")
    
    # 保存AI响应
    ai_msg_success = db_manager.save_message(session_id, 'assistant', '你好！我是蕾拉酱，很高兴为您介绍声乐表演专业。')
    if ai_msg_success:
        print("✅ AI消息保存成功")
    else:
        print("❌ AI消息保存失败")
    
    # 获取聊天历史
    chat_history = db_manager.get_chat_history(session_id)
    if chat_history:
        print(f"✅ 聊天历史检索成功，共 {len(chat_history)} 条消息")
        for msg in chat_history:
            print(f"   {msg['message_type']}: {msg['content'][:50]}...")
    else:
        print("❌ 聊天历史检索失败")
    
    # 获取会话统计
    print("\n📊 获取会话统计...")
    stats = db_manager.get_session_stats(session_id)
    if stats:
        print("✅ 会话统计获取成功:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print("❌ 会话统计获取失败")
    
    print(f"\n🎉 测试完成! 测试会话ID: {session_id}")
    print("💡 您可以在管理后台查看这些测试数据: http://localhost:5001/admin")

def check_supabase_config():
    """检查Supabase配置"""
    print("🔧 检查Supabase配置...")
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or supabase_url == 'your-supabase-url':
        print("❌ SUPABASE_URL 未配置")
        return False
    
    if not supabase_key or supabase_key == 'your-supabase-anon-key':
        print("❌ SUPABASE_ANON_KEY 未配置")
        return False
    
    print(f"✅ SUPABASE_URL: {supabase_url}")
    print(f"✅ SUPABASE_ANON_KEY: {supabase_key[:20]}...")
    
    return True

if __name__ == "__main__":
    print("🎵 蕾拉酱音乐留学咨询系统 - Supabase数据库测试")
    print("=" * 60)
    
    # 检查配置
    if check_supabase_config():
        test_form_submission()
    else:
        print("\n❌ Supabase配置不完整，请先设置环境变量:")
        print("1. 复制 env.example 为 .env")
        print("2. 填入您的Supabase URL和API密钥")
        print("3. 重新运行此测试")
        print("\n📖 详细设置指南请参考: DATABASE_SETUP.md")



