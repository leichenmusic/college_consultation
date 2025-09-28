-- 简化版用户认证表创建脚本
-- 在Supabase SQL编辑器中执行

-- 创建users表
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

-- 添加user_id列到user_sessions表
ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS user_id TEXT;

-- 添加外键约束
ALTER TABLE user_sessions 
ADD CONSTRAINT IF NOT EXISTS fk_user_sessions_user_id 
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL;

-- 创建必要的索引
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
