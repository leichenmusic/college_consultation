-- 创建用户认证系统数据库表
-- 请在Supabase SQL编辑器中执行此脚本

-- 1. 创建用户账户表
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

-- 2. 检查user_sessions表是否已存在user_id列，如果不存在则添加
DO $$
BEGIN
    -- 检查user_id列是否存在
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'user_sessions' 
        AND column_name = 'user_id'
    ) THEN
        -- 添加user_id列
        ALTER TABLE user_sessions ADD COLUMN user_id TEXT;
        
        -- 添加外键约束
        ALTER TABLE user_sessions 
        ADD CONSTRAINT fk_user_sessions_user_id 
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL;
        
        RAISE NOTICE 'Added user_id column and foreign key constraint to user_sessions table';
    ELSE
        RAISE NOTICE 'user_id column already exists in user_sessions table';
    END IF;
END $$;

-- 3. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_users_registration_method ON users(registration_method);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at DESC);

-- 为user_sessions表的user_id列创建索引
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);

-- 4. 启用行级安全 (RLS) - 可选，用于生产环境
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 5. 创建RLS策略 - 可选，用于生产环境
-- 用户只能查看和修改自己的数据
-- CREATE POLICY "Users can view own data" ON users
--     FOR SELECT USING (auth.uid()::text = user_id);

-- CREATE POLICY "Users can update own data" ON users
--     FOR UPDATE USING (auth.uid()::text = user_id);

-- 6. 验证表结构
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name IN ('users', 'user_sessions')
ORDER BY table_name, ordinal_position;

-- 7. 显示创建结果
SELECT 'Users table created successfully' as status;
SELECT 'User_sessions table updated successfully' as status;
