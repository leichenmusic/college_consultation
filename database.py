"""
Supabase数据库配置和操作模块
用于存储用户会话、聊天记录和用户信息
"""

import os
import json
from datetime import datetime
from supabase import create_client, Client
from typing import Dict, List, Optional, Any
import uuid

# Supabase配置
SUPABASE_URL = os.getenv('SUPABASE_URL', 'your-supabase-url')
SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY', 'your-supabase-anon-key')

# 创建Supabase客户端（延迟初始化）
supabase: Client = None

def init_supabase():
    """初始化Supabase客户端"""
    global supabase
    if supabase is None:
        try:
            if SUPABASE_URL.startswith('https://') and SUPABASE_KEY != 'your-supabase-anon-key':
                supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
            else:
                print("警告: Supabase配置未设置，数据库功能将不可用")
        except Exception as e:
            print(f"Supabase初始化失败: {e}")
    return supabase

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        self.supabase = init_supabase()
    
    def _check_connection(self) -> bool:
        """检查数据库连接是否可用"""
        if not self.supabase:
            print("Supabase未初始化，跳过数据库操作")
            return False
        return True
    
    # === 用户会话管理 ===
    
    def create_session(self, session_id: str = None) -> str:
        """创建新的用户会话"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        if not self._check_connection():
            return session_id
            
        try:
            result = self.supabase.table('user_sessions').insert({
                'session_id': session_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'is_active': True,
                'user_profile': {}
            }).execute()
            
            return session_id
        except Exception as e:
            print(f"创建会话失败: {e}")
            return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        if not self._check_connection():
            return None
            
        try:
            result = self.supabase.table('user_sessions').select('*').eq('session_id', session_id).execute()
            
            if result.data:
                return result.data[0]
            return None
        except Exception as e:
            print(f"获取会话失败: {e}")
            return None
    
    def update_session_profile(self, session_id: str, user_profile: Dict) -> bool:
        """更新会话的用户信息"""
        try:
            result = self.supabase.table('user_sessions').update({
                'user_profile': user_profile,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('session_id', session_id).execute()
            
            return True
        except Exception as e:
            print(f"更新用户信息失败: {e}")
            return False
    
    def close_session(self, session_id: str) -> bool:
        """关闭会话"""
        try:
            result = self.supabase.table('user_sessions').update({
                'is_active': False,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('session_id', session_id).execute()
            
            return True
        except Exception as e:
            print(f"关闭会话失败: {e}")
            return False
    
    # === 聊天消息管理 ===
    
    def save_message(self, session_id: str, message_type: str, content: str, 
                    metadata: Dict = None) -> bool:
        """保存聊天消息"""
        if not self._check_connection():
            return False
            
        try:
            result = self.supabase.table('chat_messages').insert({
                'session_id': session_id,
                'message_type': message_type,  # 'user' 或 'assistant'
                'content': content,
                'metadata': metadata or {},
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            # 更新会话的最后活动时间
            self.supabase.table('user_sessions').update({
                'updated_at': datetime.utcnow().isoformat()
            }).eq('session_id', session_id).execute()
            
            return True
        except Exception as e:
            print(f"保存消息失败: {e}")
            return False
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """获取聊天历史"""
        try:
            result = self.supabase.table('chat_messages').select('*').eq(
                'session_id', session_id
            ).order('created_at', desc=False).limit(limit).execute()
            
            return result.data or []
        except Exception as e:
            print(f"获取聊天历史失败: {e}")
            return []
    
    def get_recent_messages(self, session_id: str, count: int = 10) -> List[Dict]:
        """获取最近的消息"""
        try:
            result = self.supabase.table('chat_messages').select('*').eq(
                'session_id', session_id
            ).order('created_at', desc=True).limit(count).execute()
            
            # 反转顺序，使最早的消息在前
            return list(reversed(result.data or []))
        except Exception as e:
            print(f"获取最近消息失败: {e}")
            return []
    
    # === 用户信息管理 ===
    
    def save_user_profile(self, session_id: str, profile_data: Dict) -> bool:
        """保存用户资料"""
        if not self._check_connection():
            return False
            
        try:
            # 更新会话中的用户信息
            self.update_session_profile(session_id, profile_data)
            
            # 同时保存到用户资料表
            result = self.supabase.table('user_profiles').upsert({
                'session_id': session_id,
                'name': profile_data.get('name'),
                'age_range': profile_data.get('age_range'),
                'gender': profile_data.get('gender'),
                'current_grade': profile_data.get('current_grade'),
                'current_major': profile_data.get('current_major'),
                'target_major': json.dumps(profile_data.get('target_major', [])),
                'countries': json.dumps(profile_data.get('countries', [])),
                'intake_term': profile_data.get('intake_term'),
                'budget_cny_range': profile_data.get('budget_cny_range'),
                'special_requests': json.dumps(profile_data.get('special_requests', [])),
                'contact_method': profile_data.get('contact_method'),
                'notes': profile_data.get('notes'),
                'form_completed': profile_data.get('form_completed', False),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }).execute()
            
            return True
        except Exception as e:
            print(f"保存用户资料失败: {e}")
            return False
    
    def get_user_profile(self, session_id: str) -> Optional[Dict]:
        """获取用户资料"""
        try:
            result = self.supabase.table('user_profiles').select('*').eq('session_id', session_id).execute()
            
            if result.data:
                profile = result.data[0]
                # 解析JSON字段
                profile['target_major'] = json.loads(profile.get('target_major', '[]'))
                profile['countries'] = json.loads(profile.get('countries', '[]'))
                profile['special_requests'] = json.loads(profile.get('special_requests', '[]'))
                return profile
            return None
        except Exception as e:
            print(f"获取用户资料失败: {e}")
            return None
    
    # === 统计和分析 ===
    
    def get_session_stats(self, session_id: str) -> Dict:
        """获取会话统计信息"""
        try:
            # 获取消息数量
            message_count = self.supabase.table('chat_messages').select(
                'id', count='exact'
            ).eq('session_id', session_id).execute()
            
            # 获取会话信息
            session_info = self.get_session(session_id)
            
            return {
                'session_id': session_id,
                'message_count': len(message_count.data) if message_count.data else 0,
                'created_at': session_info.get('created_at') if session_info else None,
                'updated_at': session_info.get('updated_at') if session_info else None,
                'is_active': session_info.get('is_active') if session_info else False
            }
        except Exception as e:
            print(f"获取会话统计失败: {e}")
            return {}
    
    def get_all_active_sessions(self) -> List[Dict]:
        """获取所有活跃会话"""
        try:
            result = self.supabase.table('user_sessions').select('*').eq(
                'is_active', True
            ).order('updated_at', desc=True).execute()
            
            return result.data or []
        except Exception as e:
            print(f"获取活跃会话失败: {e}")
            return []
    
    # === 数据库初始化 ===
    
    def init_database(self):
        """初始化数据库表结构（仅用于参考，实际表需要在Supabase控制台创建）"""
        print("请在Supabase控制台创建以下表结构：")
        
        print("""
        1. user_sessions 表:
        - id: bigint (primary key, auto increment)
        - session_id: text (unique, not null)
        - user_profile: jsonb
        - is_active: boolean (default true)
        - created_at: timestamptz (default now())
        - updated_at: timestamptz (default now())
        
        2. chat_messages 表:
        - id: bigint (primary key, auto increment)
        - session_id: text (not null, foreign key to user_sessions.session_id)
        - message_type: text (not null) -- 'user' or 'assistant'
        - content: text (not null)
        - metadata: jsonb
        - created_at: timestamptz (default now())
        
        3. user_profiles 表:
        - id: bigint (primary key, auto increment)
        - session_id: text (unique, not null, foreign key to user_sessions.session_id)
        - name: text
        - age_range: text
        - gender: text
        - current_grade: text
        - current_major: text
        - target_major: text (JSON array)
        - countries: text (JSON array)
        - intake_term: text
        - budget_cny_range: text
        - special_requests: text (JSON array)
        - contact_method: text
        - notes: text
        - form_completed: boolean (default false)
        - created_at: timestamptz (default now())
        - updated_at: timestamptz (default now())
        """)

# 创建全局数据库管理实例
db_manager = DatabaseManager()
