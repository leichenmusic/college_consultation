-- Supabase数据库表结构
-- 请在Supabase SQL编辑器中执行此脚本

-- 1. 用户账户表
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL, -- 自定义用户ID
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT, -- 密码哈希（本地注册用户）
    google_id TEXT UNIQUE, -- Google用户ID
    display_name TEXT NOT NULL,
    avatar_url TEXT,
    registration_method TEXT NOT NULL CHECK (registration_method IN ('local', 'google')),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    user_id TEXT, -- 关联到users表
    user_profile JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- 2. 聊天消息表
CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    message_type TEXT NOT NULL CHECK (message_type IN ('user', 'assistant')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE CASCADE
);

-- 3. 用户资料表
CREATE TABLE IF NOT EXISTS user_profiles (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT UNIQUE NOT NULL,
    name TEXT,
    age_range TEXT,
    gender TEXT,
    current_grade TEXT,
    current_major TEXT,
    target_major TEXT, -- JSON array as text
    countries TEXT, -- JSON array as text
    intake_term TEXT,
    budget_cny_range TEXT,
    special_requests TEXT, -- JSON array as text
    contact_method TEXT,
    notes TEXT,
    form_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id) ON DELETE CASCADE
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);

CREATE INDEX IF NOT EXISTS idx_user_sessions_session_id ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_is_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_updated_at ON user_sessions(updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_message_type ON chat_messages(message_type);

CREATE INDEX IF NOT EXISTS idx_user_profiles_session_id ON user_profiles(session_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_form_completed ON user_profiles(form_completed);

-- 创建更新时间自动更新的触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为user_sessions表创建触发器
DROP TRIGGER IF EXISTS update_user_sessions_updated_at ON user_sessions;
CREATE TRIGGER update_user_sessions_updated_at
    BEFORE UPDATE ON user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 为user_profiles表创建触发器
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 启用行级安全策略 (RLS)
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- 创建策略允许匿名用户访问（适用于公开的聊天应用）
-- 注意：在生产环境中，您可能需要更严格的安全策略

-- user_sessions表的策略
DROP POLICY IF EXISTS "Allow anonymous access to user_sessions" ON user_sessions;
CREATE POLICY "Allow anonymous access to user_sessions" ON user_sessions
    FOR ALL USING (true);

-- chat_messages表的策略
DROP POLICY IF EXISTS "Allow anonymous access to chat_messages" ON chat_messages;
CREATE POLICY "Allow anonymous access to chat_messages" ON chat_messages
    FOR ALL USING (true);

-- user_profiles表的策略
DROP POLICY IF EXISTS "Allow anonymous access to user_profiles" ON user_profiles;
CREATE POLICY "Allow anonymous access to user_profiles" ON user_profiles
    FOR ALL USING (true);

-- 创建一些有用的视图

-- 会话统计视图
CREATE OR REPLACE VIEW session_stats AS
SELECT 
    us.session_id,
    us.created_at as session_created,
    us.updated_at as last_activity,
    us.is_active,
    up.name as user_name,
    up.form_completed,
    COUNT(cm.id) as message_count,
    MAX(cm.created_at) as last_message_time
FROM user_sessions us
LEFT JOIN user_profiles up ON us.session_id = up.session_id
LEFT JOIN chat_messages cm ON us.session_id = cm.session_id
GROUP BY us.session_id, us.created_at, us.updated_at, us.is_active, up.name, up.form_completed;

-- 每日活跃会话统计视图
CREATE OR REPLACE VIEW daily_active_sessions AS
SELECT 
    DATE(updated_at) as date,
    COUNT(DISTINCT session_id) as active_sessions,
    COUNT(DISTINCT CASE WHEN is_active THEN session_id END) as currently_active
FROM user_sessions
GROUP BY DATE(updated_at)
ORDER BY date DESC;

-- 插入一些示例数据（可选）
-- INSERT INTO user_sessions (session_id, user_profile) VALUES 
-- ('demo-session-1', '{"demo": true}');

COMMENT ON TABLE user_sessions IS '用户会话表，存储每个用户的会话信息';
COMMENT ON TABLE chat_messages IS '聊天消息表，存储所有的对话记录';
COMMENT ON TABLE user_profiles IS '用户资料表，存储用户的详细信息';

COMMENT ON COLUMN user_sessions.session_id IS '唯一的会话ID，用于标识用户会话';
COMMENT ON COLUMN user_sessions.user_profile IS '用户资料的JSON存储';
COMMENT ON COLUMN user_sessions.is_active IS '会话是否活跃';

COMMENT ON COLUMN chat_messages.message_type IS '消息类型：user（用户）或assistant（AI助手）';
COMMENT ON COLUMN chat_messages.content IS '消息内容';
COMMENT ON COLUMN chat_messages.metadata IS '消息的元数据，如按钮选择等';

COMMENT ON COLUMN user_profiles.target_major IS '目标专业，JSON数组格式';
COMMENT ON COLUMN user_profiles.countries IS '意向国家，JSON数组格式';
COMMENT ON COLUMN user_profiles.special_requests IS '特殊需求，JSON数组格式';
