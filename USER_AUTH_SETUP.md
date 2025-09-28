# 👤 用户认证系统设置指南

本指南将帮助您为蕾拉酱音乐留学咨询系统设置完整的用户认证功能，包括本地注册/登录和Google OAuth登录。

## 🚀 功能概览

### ✅ **已实现功能**
- 🔐 **本地注册/登录**: 用户名密码方式
- 🌐 **Google OAuth登录**: 一键Google登录
- 👤 **用户管理**: 完整的用户信息管理
- 🔗 **会话关联**: 用户账号与聊天会话关联
- 🛡️ **安全认证**: 密码哈希、token验证
- 📱 **响应式UI**: 美观的登录注册界面

## 📋 前置条件

1. **Supabase数据库**: 已配置并运行
2. **Google Cloud Console**: 用于OAuth配置
3. **Python依赖**: 认证相关包已安装

## 🛠️ 设置步骤

### 1. **安装依赖包**

```bash
pip install -r requirements.txt
```

新增的认证依赖包：
- `Flask-Login>=0.6.0` - Flask用户会话管理
- `bcrypt>=4.0.0` - 密码哈希加密
- `google-auth>=2.0.0` - Google认证库
- `google-auth-oauthlib>=1.0.0` - Google OAuth流程
- `google-auth-httplib2>=0.2.0` - Google HTTP客户端

### 2. **更新数据库架构**

在Supabase SQL编辑器中执行更新后的 `supabase_schema.sql`：

```sql
-- 新增用户账户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT,
    google_id TEXT UNIQUE,
    display_name TEXT NOT NULL,
    avatar_url TEXT,
    registration_method TEXT NOT NULL CHECK (registration_method IN ('local', 'google')),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 更新用户会话表，添加用户关联
ALTER TABLE user_sessions ADD COLUMN user_id TEXT;
ALTER TABLE user_sessions ADD FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL;
```

### 3. **配置Google OAuth**

#### 3.1 创建Google Cloud项目
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用 "Google+ API" 和 "Google Identity Services"

#### 3.2 创建OAuth 2.0凭据
1. 进入 **APIs & Services** → **Credentials**
2. 点击 **Create Credentials** → **OAuth 2.0 Client IDs**
3. 选择 **Web application**
4. 配置授权域名：
   - **Authorized JavaScript origins**: `http://localhost:5001`
   - **Authorized redirect URIs**: `http://localhost:5001/auth/google`

#### 3.3 获取客户端信息
复制以下信息：
- **Client ID**: `your-client-id.apps.googleusercontent.com`
- **Client Secret**: `your-client-secret`

### 4. **配置环境变量**

编辑 `.env` 文件，添加Google OAuth配置：

```env
# Google OAuth配置
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 5. **启动应用**

```bash
python app.py
```

## 🎯 用户认证流程

### **注册流程**

1. **访问注册页面**: `http://localhost:5001/register`
2. **选择注册方式**:
   - **本地注册**: 填写用户名、邮箱、密码
   - **Google注册**: 点击"使用Google注册"

#### **本地注册步骤**:
```
用户填写表单 → 实时检查用户名可用性 → 提交注册 → 密码哈希存储 → 自动登录 → 跳转聊天页面
```

#### **Google注册步骤**:
```
点击Google按钮 → Google授权弹窗 → 获取用户信息 → 创建账户 → 自动登录 → 跳转聊天页面
```

### **登录流程**

1. **访问登录页面**: `http://localhost:5001/login`
2. **选择登录方式**:
   - **本地登录**: 用户名/邮箱 + 密码
   - **Google登录**: 一键Google登录

#### **本地登录步骤**:
```
输入凭据 → 验证用户存在 → 验证密码 → 创建会话 → 关联用户到会话 → 跳转聊天页面
```

#### **Google登录步骤**:
```
点击Google按钮 → Google授权 → 验证token → 查找/创建用户 → 创建会话 → 跳转聊天页面
```

## 🔧 技术实现

### **数据库设计**

#### **users表结构**
```sql
users (
    user_id TEXT UNIQUE,           -- 自定义用户ID
    username TEXT UNIQUE,          -- 用户名（本地注册）
    email TEXT UNIQUE,            -- 邮箱地址
    password_hash TEXT,           -- 密码哈希（本地用户）
    google_id TEXT UNIQUE,        -- Google用户ID
    display_name TEXT,            -- 显示名称
    avatar_url TEXT,              -- 头像URL
    registration_method TEXT,      -- 注册方式：'local'/'google'
    is_active BOOLEAN,            -- 账户状态
    email_verified BOOLEAN        -- 邮箱验证状态
)
```

#### **会话关联**
```sql
user_sessions (
    session_id TEXT UNIQUE,       -- 会话ID
    user_id TEXT,                 -- 关联用户ID
    user_profile JSONB,           -- 用户资料
    is_active BOOLEAN             -- 会话状态
)
```

### **安全特性**

#### **密码安全**
- 使用 `bcrypt` 进行密码哈希
- 盐值自动生成，防止彩虹表攻击
- 密码最少6个字符要求

#### **Google OAuth安全**
- Token服务器端验证
- 防止CSRF攻击
- 安全的用户信息获取

#### **会话管理**
- Flask-Login会话管理
- 自动会话关联
- 安全的用户状态维护

## 🎨 用户界面

### **注册页面特性**
- ✅ 实时用户名可用性检查
- ✅ 用户名建议功能
- ✅ 表单验证和错误提示
- ✅ Google一键注册
- ✅ 响应式设计

### **登录页面特性**
- ✅ 支持用户名或邮箱登录
- ✅ 密码显示/隐藏切换
- ✅ Google一键登录
- ✅ 友好的错误提示

### **弹窗注册提醒**
- ✅ 聊天5次后自动提醒
- ✅ 从右上角滑入动画
- ✅ 提供注册和登录选项
- ✅ 点击外部自动关闭

## 📊 用户数据管理

### **用户信息获取**
```javascript
// 获取当前登录用户信息
fetch('/api/user_info')
    .then(response => response.json())
    .then(data => {
        console.log('用户信息:', data.user);
    });
```

### **会话关联**
- 用户登录后自动关联当前会话
- 历史聊天记录保持关联
- 跨设备会话同步

### **管理后台集成**
- 用户列表查看
- 用户会话统计
- 用户活动监控

## 🔍 API接口

### **认证相关接口**
- `POST /register` - 用户注册
- `POST /login` - 用户登录
- `GET /logout` - 用户登出
- `POST /auth/google` - Google OAuth登录
- `GET /api/check_username` - 检查用户名可用性
- `GET /api/user_info` - 获取用户信息

### **页面路由**
- `/register` - 注册页面
- `/login` - 登录页面
- `/chat` - 聊天页面（需要登录）
- `/admin` - 管理后台（需要登录）

## 🧪 测试验证

### **功能测试清单**
- [ ] 本地用户注册
- [ ] 用户名可用性检查
- [ ] 密码强度验证
- [ ] 本地用户登录
- [ ] Google用户注册
- [ ] Google用户登录
- [ ] 会话关联
- [ ] 用户登出
- [ ] 权限保护

### **测试用例**
```bash
# 测试用户注册
curl -X POST http://localhost:5001/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"123456","display_name":"测试用户"}'

# 测试用户登录
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"testuser","password":"123456"}'
```

## 🚀 部署注意事项

### **生产环境配置**
1. **HTTPS必须**: Google OAuth要求HTTPS
2. **域名配置**: 更新Google OAuth授权域名
3. **环境变量**: 安全存储敏感配置
4. **数据库安全**: 启用RLS和访问控制

### **Google OAuth生产配置**
```env
# 生产环境Google OAuth
GOOGLE_CLIENT_ID=your-prod-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-prod-client-secret
```

更新Google Cloud Console中的授权域名：
- **Authorized JavaScript origins**: `https://yourdomain.com`
- **Authorized redirect URIs**: `https://yourdomain.com/auth/google`

## 🎉 使用示例

### **完整用户注册流程**
1. 用户访问聊天页面，聊天5次后弹出注册提醒
2. 点击"好的，注册账号"跳转到注册页面
3. 选择本地注册或Google注册
4. 完成注册后自动登录并返回聊天页面
5. 用户的聊天记录与账号关联
6. 下次访问可直接登录继续对话

### **管理员视角**
- 在管理后台查看所有注册用户
- 监控用户活动和会话统计
- 管理用户账户状态

---

🎵 **蕾拉酱音乐留学咨询系统** - 现在支持完整的用户账户体系！
