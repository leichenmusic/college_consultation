"""
用户认证管理模块
支持本地注册/登录和Google OAuth登录
"""

import os
import bcrypt
import uuid
import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from flask_login import UserMixin
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from database import db_manager

class User(UserMixin):
    """用户类，继承Flask-Login的UserMixin"""
    
    def __init__(self, user_data: Dict):
        self.id = user_data.get('user_id')
        self.user_id = user_data.get('user_id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.display_name = user_data.get('display_name')
        self.avatar_url = user_data.get('avatar_url')
        self.registration_method = user_data.get('registration_method')
        self._is_active = user_data.get('is_active', True)  # 使用私有属性存储
        self.email_verified = user_data.get('email_verified', False)
        self.created_at = user_data.get('created_at')
        self.is_admin = user_data.get('is_admin', False)  # Add admin flag
    
    @property
    def is_active(self):
        """重写UserMixin的is_active属性"""
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        """设置is_active属性"""
        self._is_active = value
    
    def get_id(self):
        """Flask-Login要求的方法"""
        return self.user_id
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'registration_method': self.registration_method,
            'is_active': self.is_active,  # 这里会调用我们的property
            'email_verified': self.email_verified,
            'created_at': self.created_at
        }

class AuthManager:
    """认证管理类"""
    
    def __init__(self):
        self.db = db_manager
    
    def generate_user_id(self) -> str:
        """生成唯一的用户ID"""
        return f"user_{uuid.uuid4().hex[:12]}"
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def generate_username_suggestions(self, base_name: str) -> list:
        """生成用户名建议"""
        suggestions = []
        base_clean = ''.join(c for c in base_name if c.isalnum()).lower()
        
        if len(base_clean) < 3:
            base_clean = 'user'
        
        # 基础建议
        suggestions.append(base_clean)
        
        # 添加数字后缀
        for i in range(1, 6):
            suggestions.append(f"{base_clean}{i}")
            suggestions.append(f"{base_clean}_{i}")
        
        # 添加随机后缀
        import random
        for _ in range(3):
            suffix = random.randint(100, 999)
            suggestions.append(f"{base_clean}_{suffix}")
        
        return suggestions
    
    def is_username_available(self, username: str) -> bool:
        """检查用户名是否可用"""
        if not self.db._check_connection():
            return False
        
        try:
            result = self.db.supabase.table('users').select('username').eq('username', username).execute()
            return len(result.data) == 0
        except Exception as e:
            print(f"检查用户名可用性失败: {e}")
            return False
    
    def is_email_available(self, email: str) -> bool:
        """检查邮箱是否可用"""
        if not self.db._check_connection():
            return False
        
        try:
            result = self.db.supabase.table('users').select('email').eq('email', email).execute()
            return len(result.data) == 0
        except Exception as e:
            print(f"检查邮箱可用性失败: {e}")
            return False
    
    def create_local_user(self, username: str, email: str, password: str, display_name: str) -> Tuple[bool, str, Optional[User]]:
        """创建本地注册用户"""
        if not self.db._check_connection():
            return False, "数据库连接失败", None
        
        # 验证输入
        if not username or len(username) < 3:
            return False, "用户名至少需要3个字符", None
        
        if not email or '@' not in email:
            return False, "请输入有效的邮箱地址", None
        
        if not password or len(password) < 6:
            return False, "密码至少需要6个字符", None
        
        # 检查用户名和邮箱是否已存在
        if not self.is_username_available(username):
            return False, "用户名已被使用", None
        
        if not self.is_email_available(email):
            return False, "邮箱已被注册", None
        
        try:
            user_id = self.generate_user_id()
            password_hash = self.hash_password(password)
            
            user_data = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'display_name': display_name,
                'registration_method': 'local',
                'is_active': True,
                'email_verified': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.db.supabase.table('users').insert(user_data).execute()
            
            if result.data:
                user = User(user_data)
                return True, "注册成功", user
            else:
                return False, "注册失败，请重试", None
                
        except Exception as e:
            print(f"创建用户失败: {e}")
            return False, f"注册失败: {str(e)}", None
    
    def authenticate_local_user(self, username_or_email: str, password: str) -> Tuple[bool, str, Optional[User]]:
        """本地用户登录验证"""
        if not self.db._check_connection():
            return False, "数据库连接失败", None
        
        try:
            # 支持用户名或邮箱登录
            query = self.db.supabase.table('users').select('*')
            if '@' in username_or_email:
                query = query.eq('email', username_or_email)
            else:
                query = query.eq('username', username_or_email)
            
            result = query.execute()
            
            if not result.data:
                return False, "用户不存在", None
            
            user_data = result.data[0]
            
            # 检查是否是本地注册用户
            if user_data.get('registration_method') != 'local':
                return False, "请使用Google登录", None
            
            # 验证密码
            if not self.verify_password(password, user_data.get('password_hash', '')):
                return False, "密码错误", None
            
            # 检查用户状态
            if not user_data.get('is_active', False):
                return False, "账户已被禁用", None
            
            user = User(user_data)
            return True, "登录成功", user
            
        except Exception as e:
            print(f"用户登录失败: {e}")
            return False, f"登录失败: {str(e)}", None
    
    def create_google_user(self, google_user_info: Dict) -> Tuple[bool, str, Optional[User]]:
        """创建Google登录用户"""
        if not self.db._check_connection():
            return False, "数据库连接失败", None
        
        try:
            user_id = self.generate_user_id()
            email = google_user_info.get('email')
            
            # 检查邮箱是否已被本地用户注册
            if not self.is_email_available(email):
                return False, "该邮箱已被注册，请使用密码登录", None
            
            user_data = {
                'user_id': user_id,
                'email': email,
                'google_id': google_user_info.get('sub'),
                'display_name': google_user_info.get('name', email.split('@')[0]),
                'avatar_url': google_user_info.get('picture'),
                'registration_method': 'google',
                'is_active': True,
                'email_verified': google_user_info.get('email_verified', False),
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            result = self.db.supabase.table('users').insert(user_data).execute()
            
            if result.data:
                user = User(user_data)
                return True, "Google登录成功", user
            else:
                return False, "Google登录失败，请重试", None
                
        except Exception as e:
            print(f"创建Google用户失败: {e}")
            return False, f"Google登录失败: {str(e)}", None
    
    def authenticate_google_user(self, google_user_info: Dict) -> Tuple[bool, str, Optional[User]]:
        """Google用户登录验证"""
        if not self.db._check_connection():
            return False, "数据库连接失败", None
        
        try:
            google_id = google_user_info.get('sub')
            email = google_user_info.get('email')
            
            # 先尝试通过Google ID查找
            result = self.db.supabase.table('users').select('*').eq('google_id', google_id).execute()
            
            if result.data:
                user_data = result.data[0]
                user = User(user_data)
                return True, "Google登录成功", user
            
            # 如果没找到，尝试通过邮箱查找（可能是首次Google登录）
            result = self.db.supabase.table('users').select('*').eq('email', email).execute()
            
            if result.data:
                user_data = result.data[0]
                if user_data.get('registration_method') == 'local':
                    return False, "该邮箱已注册，请使用密码登录", None
                else:
                    # 更新Google ID
                    self.db.supabase.table('users').update({
                        'google_id': google_id,
                        'updated_at': datetime.utcnow().isoformat()
                    }).eq('email', email).execute()
                    
                    user = User(user_data)
                    return True, "Google登录成功", user
            
            # 新用户，创建账户
            return self.create_google_user(google_user_info)
            
        except Exception as e:
            print(f"Google用户验证失败: {e}")
            return False, f"Google登录失败: {str(e)}", None
    
    def verify_google_token(self, token: str) -> Tuple[bool, str, Optional[Dict]]:
        """验证Google ID Token"""
        try:
            google_client_id = os.getenv('GOOGLE_CLIENT_ID')
            if not google_client_id:
                return False, "Google登录未配置", None
            
            # 验证token
            idinfo = id_token.verify_oauth2_token(
                token, google_requests.Request(), google_client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                return False, "无效的Google token", None
            
            return True, "Token验证成功", idinfo
            
        except ValueError as e:
            return False, f"Google token验证失败: {str(e)}", None
        except Exception as e:
            return False, f"Google登录错误: {str(e)}", None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据用户ID获取用户信息"""
        if not self.db._check_connection():
            return None
        
        try:
            result = self.db.supabase.table('users').select('*').eq('user_id', user_id).execute()
            
            if result.data:
                return User(result.data[0])
            return None
            
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def link_session_to_user(self, session_id: str, user_id: str) -> bool:
        """将会话关联到用户"""
        if not self.db._check_connection():
            return False
        
        try:
            result = self.db.supabase.table('user_sessions').update({
                'user_id': user_id,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('session_id', session_id).execute()
            
            return True
        except Exception as e:
            print(f"关联会话到用户失败: {e}")
            return False

# 创建全局认证管理实例
auth_manager = AuthManager()



