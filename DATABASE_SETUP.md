# 🗄️ Supabase数据库设置指南

本指南将帮助您为蕾拉酱音乐留学咨询系统设置Supabase数据库。

## 📋 前置条件

1. 一个Supabase账号 (https://supabase.com)
2. Python 3.7+
3. 已安装项目依赖

## 🚀 快速开始

### 1. 创建Supabase项目

1. 访问 [Supabase Dashboard](https://app.supabase.com)
2. 点击 "New Project"
3. 选择组织并填写项目信息：
   - **Name**: `music-consultation` (或您喜欢的名称)
   - **Database Password**: 设置一个强密码
   - **Region**: 选择离您最近的区域
4. 点击 "Create new project"
5. 等待项目创建完成（通常需要1-2分钟）

### 2. 获取项目配置信息

项目创建完成后，在项目设置页面获取以下信息：

1. 进入 **Settings** → **API**
2. 复制以下信息：
   - **Project URL**: `https://your-project-ref.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (保密！)

### 3. 配置环境变量

1. 复制 `env.example` 文件为 `.env`:
   ```bash
   cp env.example .env
   ```

2. 编辑 `.env` 文件，填入您的Supabase配置：
   ```env
   # Supabase配置
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_ANON_KEY=your-supabase-anon-key
   SUPABASE_SERVICE_KEY=your-supabase-service-key
   
   # Flask配置
   FLASK_SECRET_KEY=your-super-secret-key-here
   
   # Gemini API配置
   GEMINI_PROXY_URL=https://vercel-gemini-proxy.vercel.app/api/gemini-2.5-flash
   ```

### 4. 创建数据库表

1. 在Supabase Dashboard中，进入 **SQL Editor**
2. 复制 `supabase_schema.sql` 文件的全部内容
3. 粘贴到SQL编辑器中
4. 点击 **Run** 执行SQL脚本

这将创建以下表：
- `user_sessions` - 用户会话表
- `chat_messages` - 聊天消息表  
- `user_profiles` - 用户资料表

### 5. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 6. 启动应用

```bash
python app.py
```

应用将在 `http://localhost:5001` 启动。

## 📊 数据库结构

### user_sessions 表
存储用户会话信息
- `id`: 主键
- `session_id`: 唯一会话标识符
- `user_profile`: 用户资料JSON
- `is_active`: 会话是否活跃
- `created_at`: 创建时间
- `updated_at`: 更新时间

### chat_messages 表
存储所有聊天消息
- `id`: 主键
- `session_id`: 关联的会话ID
- `message_type`: 消息类型 ('user' 或 'assistant')
- `content`: 消息内容
- `metadata`: 消息元数据JSON
- `created_at`: 创建时间

### user_profiles 表
存储详细的用户资料
- `id`: 主键
- `session_id`: 关联的会话ID
- `name`: 用户姓名
- `age_range`: 年龄段
- `gender`: 性别
- `current_grade`: 当前学段
- `current_major`: 当前专业
- `target_major`: 目标专业 (JSON数组)
- `countries`: 意向国家 (JSON数组)
- `intake_term`: 入学时间
- `budget_cny_range`: 预算范围
- `special_requests`: 特殊需求 (JSON数组)
- `contact_method`: 联系方式
- `notes`: 备注
- `form_completed`: 表单是否完成
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 🔧 管理后台

访问 `http://localhost:5001/admin` 查看管理后台，功能包括：

- 📊 **仪表板**: 查看总体统计信息
- 📋 **会话管理**: 查看所有用户会话
- 💬 **聊天记录**: 查看具体会话的聊天历史
- 👤 **用户资料**: 查看用户填写的详细信息

### 管理后台路由
- `/admin` - 管理后台首页
- `/admin/sessions` - 会话列表
- `/admin/session/<session_id>` - 会话详情
- `/admin/api/sessions` - API: 获取会话列表
- `/admin/api/session/<session_id>/messages` - API: 获取聊天记录

## 🔒 安全配置

### 行级安全策略 (RLS)
数据库已启用RLS，当前配置为允许匿名访问。在生产环境中，建议：

1. 创建更严格的安全策略
2. 实现用户认证系统
3. 限制管理后台访问权限

### 环境变量安全
- 确保 `.env` 文件不被提交到版本控制
- 在生产环境中使用环境变量而非文件
- 定期轮换API密钥

## 🚀 部署到生产环境

### Vercel部署
1. 在Vercel中设置环境变量
2. 确保Supabase项目在生产模式
3. 更新安全策略

### 其他平台
确保在部署平台中正确设置所有环境变量。

## 🛠️ 故障排除

### 常见问题

**1. 连接错误**
- 检查SUPABASE_URL和SUPABASE_ANON_KEY是否正确
- 确认Supabase项目状态正常

**2. 权限错误**
- 检查RLS策略是否正确配置
- 确认使用正确的API密钥

**3. 表不存在**
- 确认已执行`supabase_schema.sql`脚本
- 检查表名是否正确

### 调试模式
在开发环境中，可以通过以下方式查看详细错误信息：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 监控和维护

### 数据库监控
在Supabase Dashboard中可以查看：
- 数据库使用情况
- API请求统计
- 错误日志

### 定期维护
- 定期备份数据库
- 清理过期会话
- 监控存储使用量

## 🆘 获取帮助

如果遇到问题：
1. 查看Supabase官方文档: https://supabase.com/docs
2. 检查项目的GitHub Issues
3. 联系开发团队

---

🎵 **蕾拉酱音乐留学咨询系统** - 让音乐梦想触手可及！
