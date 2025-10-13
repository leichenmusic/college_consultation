# 🔧 技术规格文档 (Technical Specifications)
## 蕾拉酱的AI留学顾问 - 技术实施方案

**版本**: 2.0  
**日期**: 2024年10月10日  
**技术负责人**: PM Agent  
**状态**: 架构设计阶段  

---

## 📋 目录

1. [系统架构](#系统架构)
2. [核心模块设计](#核心模块设计)
3. [数据库设计](#数据库设计)
4. [API设计](#api设计)
5. [安全架构](#安全架构)
6. [性能优化](#性能优化)
7. [部署架构](#部署架构)
8. [监控告警](#监控告警)

---

## 🏗️ 系统架构

### 整体架构图
```
                            ┌─────────────────┐
                            │   Load Balancer │
                            │   (Cloudflare)  │
                            └─────────┬───────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
          ┌─────────┴───────┐ ┌───────┴───────┐ ┌───────┴───────┐
          │   Web Client    │ │  Mobile App   │ │  Admin Panel  │
          │   (Browser)     │ │ (iOS/Android) │ │   (Dashboard) │
          └─────────────────┘ └───────────────┘ └───────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      │
                            ┌─────────┴───────┐
                            │   API Gateway   │
                            │ (Google Cloud)  │
                            └─────────┬───────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
    ┌─────────┴───────┐    ┌─────────┴───────┐    ┌─────────┴───────┐
    │  Application    │    │   AI Services   │    │  External APIs  │
    │   Services      │    │  (Gemini API)   │    │ (Payment/OAuth) │
    │  (Flask App)    │    │                 │    │                 │
    └─────────┬───────┘    └─────────────────┘    └─────────────────┘
              │
    ┌─────────┴───────┐
    │  Data Layer     │
    │ ┌─────────────┐ │
    │ │  Supabase   │ │
    │ │(PostgreSQL) │ │
    │ └─────────────┘ │
    │ ┌─────────────┐ │
    │ │    Redis    │ │
    │ │   (Cache)   │ │
    │ └─────────────┘ │
    │ ┌─────────────┐ │
    │ │ File Storage│ │
    │ │   (GCS)     │ │
    │ └─────────────┘ │
    └─────────────────┘
```

### 技术栈详解

#### 前端层
- **Web应用**: HTML5 + CSS3 + Vanilla JavaScript
- **移动应用**: React Native (统一代码库)
- **状态管理**: Context API + LocalStorage
- **UI组件**: 自定义组件库 + Material Design
- **构建工具**: Webpack + Babel

#### 后端层  
- **Web框架**: Flask 3.1+ (Python 3.9+)
- **WSGI服务器**: Gunicorn (多进程)
- **异步任务**: Celery + Redis
- **API文档**: Flask-RESTX (Swagger)
- **数据验证**: Marshmallow + JSON Schema

#### AI服务层
- **对话生成**: Google Gemini API
- **推荐算法**: scikit-learn + TensorFlow
- **音频处理**: FFmpeg + librosa  
- **自然语言处理**: spaCy + NLTK

#### 数据层
- **主数据库**: Supabase (PostgreSQL 14+)
- **缓存**: Redis 7.0+ (集群模式)
- **文件存储**: Google Cloud Storage
- **搜索引擎**: Elasticsearch (院校搜索)

---

## 🧩 核心模块设计

### 1. AI推荐引擎模块

#### 架构设计
```python
class RecommendationEngine:
    """AI学校推荐引擎核心类"""
    
    def __init__(self):
        self.user_profiler = UserProfiler()
        self.school_matcher = SchoolMatcher()
        self.ranking_model = RankingModel()
        
    def recommend_schools(self, user_profile: dict) -> List[Recommendation]:
        # 用户画像分析
        user_vector = self.user_profiler.vectorize(user_profile)
        
        # 候选学校筛选
        candidates = self.school_matcher.find_candidates(user_vector)
        
        # 智能排序
        ranked_schools = self.ranking_model.rank(candidates, user_vector)
        
        return self._format_recommendations(ranked_schools)
```

#### 推荐算法流程
```
用户输入 → 特征提取 → 候选筛选 → 相似度计算 → 排序输出
    ↓           ↓           ↓           ↓           ↓
用户画像   →  向量化   →  初筛选   →  匹配度   →  Top-N推荐
    ↓           ↓           ↓           ↓           ↓
偏好学习   →  特征工程  →  规则过滤  →  机器学习  →  个性化解释
```

#### 关键算法
1. **协同过滤**: 基于相似用户的推荐
2. **内容推荐**: 基于学校特征的匹配
3. **深度学习**: 神经网络优化匹配度
4. **强化学习**: 基于用户反馈的持续优化

#### 数据模型
```sql
-- 推荐记录表
CREATE TABLE recommendations (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    school_id TEXT NOT NULL,
    match_score DECIMAL(5,2) NOT NULL, -- 匹配度 0-100
    algorithm_version TEXT NOT NULL,
    features JSONB NOT NULL, -- 匹配特征
    explanation TEXT, -- 推荐理由
    user_feedback INTEGER, -- 用户评分 1-5
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (school_id) REFERENCES schools(school_id)
);

-- 学校特征表
CREATE TABLE school_features (
    school_id TEXT PRIMARY KEY,
    feature_vector VECTOR(512), -- 高维特征向量
    program_tags TEXT[], -- 专业标签
    difficulty_level INTEGER, -- 申请难度 1-10
    tuition_range INT4RANGE, -- 学费区间
    location_vector POINT, -- 地理位置
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (school_id) REFERENCES schools(school_id)
);
```

### 2. 视频咨询模块

#### 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户端应用     │    │   专家端应用     │    │   管理后台       │
│   Web/Mobile    │    │   Web/Mobile    │    │   Admin Panel   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │    咨询服务中心          │
                    │  ┌──────────────────┐  │
                    │  │  预约管理系统    │  │
                    │  └──────────────────┘  │
                    │  ┌──────────────────┐  │
                    │  │  支付处理系统    │  │
                    │  └──────────────────┘  │
                    │  ┌──────────────────┐  │
                    │  │  视频通话系统    │  │
                    │  └──────────────────┘  │
                    └─────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │      第三方服务         │
                    │  ┌──────────────────┐  │
                    │  │  支付宝/微信支付  │  │
                    │  └──────────────────┘  │
                    │  ┌──────────────────┐  │
                    │  │  腾讯云音视频    │  │
                    │  └──────────────────┘  │
                    └─────────────────────────┘
```

#### 核心功能实现
```python
class ConsultationService:
    """视频咨询服务核心类"""
    
    def __init__(self):
        self.scheduler = AppointmentScheduler()
        self.payment = PaymentProcessor()
        self.video_service = VideoCallService()
        
    def book_consultation(self, user_id: str, expert_id: str, 
                         time_slot: datetime, duration: int) -> BookingResult:
        # 1. 检查时间可用性
        if not self.scheduler.is_available(expert_id, time_slot):
            raise TimeSlotUnavailableError()
            
        # 2. 创建预约记录
        booking = self.scheduler.create_booking(
            user_id, expert_id, time_slot, duration
        )
        
        # 3. 处理支付
        payment_result = self.payment.process_payment(
            booking.id, booking.price
        )
        
        if payment_result.success:
            # 4. 确认预约
            booking.status = BookingStatus.CONFIRMED
            booking.save()
            
            # 5. 发送通知
            self._send_booking_notifications(booking)
            
        return BookingResult(booking, payment_result)
```

#### 数据库设计
```sql
-- 专家信息表
CREATE TABLE experts (
    expert_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    specializations TEXT[] NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    rating DECIMAL(3,2) DEFAULT 0,
    total_consultations INTEGER DEFAULT 0,
    availability_schedule JSONB NOT NULL,
    bio TEXT,
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 咨询预约表
CREATE TABLE consultations (
    id BIGSERIAL PRIMARY KEY,
    consultation_id TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    expert_id TEXT NOT NULL,
    scheduled_time TIMESTAMPTZ NOT NULL,
    duration INTEGER NOT NULL, -- 分钟
    price DECIMAL(10,2) NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'confirmed', 'in_progress', 'completed', 'cancelled')),
    payment_status TEXT NOT NULL CHECK (payment_status IN ('pending', 'paid', 'refunded')),
    video_room_id TEXT,
    notes TEXT,
    user_rating INTEGER CHECK (user_rating BETWEEN 1 AND 5),
    expert_feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (expert_id) REFERENCES experts(expert_id)
);
```

### 3. 作品集评估模块

#### 音频分析引擎
```python
class PortfolioAnalyzer:
    """作品集智能分析引擎"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.ml_models = MLModels()
        self.scoring_engine = ScoringEngine()
        
    def analyze_audio(self, audio_file: bytes) -> AnalysisResult:
        # 1. 音频预处理
        processed_audio = self.audio_processor.preprocess(audio_file)
        
        # 2. 特征提取
        features = self.audio_processor.extract_features(processed_audio)
        
        # 3. AI分析
        analysis = self.ml_models.analyze(features)
        
        # 4. 评分计算
        scores = self.scoring_engine.calculate_scores(analysis)
        
        # 5. 生成报告
        report = self._generate_report(scores, analysis)
        
        return AnalysisResult(scores, report, analysis)
```

#### 评估维度设计
```python
class EvaluationDimensions:
    """评估维度定义"""
    
    TECHNICAL_SKILLS = {
        'pitch_accuracy': '音准准确度',
        'rhythm_precision': '节奏精确度', 
        'dynamic_control': '力度控制',
        'articulation': '发音清晰度',
        'tempo_stability': '速度稳定性'
    }
    
    MUSICAL_EXPRESSION = {
        'phrasing': '乐句处理',
        'emotion_conveyance': '情感表达',
        'style_authenticity': '风格准确性',
        'creativity': '创造性',
        'interpretation': '作品理解'
    }
    
    OVERALL_QUALITY = {
        'recording_quality': '录音质量',
        'performance_confidence': '演奏自信度',
        'repertoire_difficulty': '曲目难度',
        'overall_impression': '整体印象'
    }
```

---

## 🗄️ 数据库设计

### 核心数据模型

#### 用户相关表
```sql
-- 用户账户表 (已存在，需扩展)
ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'student' CHECK (user_type IN ('student', 'expert', 'admin'));
ALTER TABLE users ADD COLUMN subscription_plan TEXT DEFAULT 'free';
ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMPTZ;

-- 用户偏好表 (新增)
CREATE TABLE user_preferences (
    user_id TEXT PRIMARY KEY,
    preferred_countries TEXT[] DEFAULT '{}',
    preferred_programs TEXT[] DEFAULT '{}',
    budget_range INT4RANGE,
    notification_settings JSONB DEFAULT '{}',
    privacy_settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### 院校数据表
```sql
-- 学校基础信息表
CREATE TABLE schools (
    school_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_en TEXT,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('conservatory', 'university', 'college')),
    founded_year INTEGER,
    website_url TEXT,
    logo_url TEXT,
    description TEXT,
    ranking_national INTEGER,
    ranking_international INTEGER,
    total_students INTEGER,
    international_students_ratio DECIMAL(5,2),
    acceptance_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 专业项目表
CREATE TABLE programs (
    program_id TEXT PRIMARY KEY,
    school_id TEXT NOT NULL,
    name TEXT NOT NULL,
    name_en TEXT,
    degree_level TEXT NOT NULL CHECK (degree_level IN ('bachelor', 'master', 'phd', 'diploma')),
    duration_years DECIMAL(3,1) NOT NULL,
    tuition_annual DECIMAL(12,2),
    tuition_currency TEXT DEFAULT 'USD',
    language_requirements JSONB,
    academic_requirements TEXT,
    audition_requirements TEXT,
    application_deadline DATE,
    start_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (school_id) REFERENCES schools(school_id)
);

-- 专业标签关联表
CREATE TABLE program_tags (
    program_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (program_id, tag),
    
    FOREIGN KEY (program_id) REFERENCES programs(program_id)
);
```

#### 推荐系统表
```sql
-- 用户行为记录表
CREATE TABLE user_behaviors (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    behavior_type TEXT NOT NULL CHECK (behavior_type IN ('view', 'like', 'share', 'apply', 'bookmark')),
    target_type TEXT NOT NULL CHECK (target_type IN ('school', 'program', 'article')),
    target_id TEXT NOT NULL,
    context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 推荐结果缓存表
CREATE TABLE recommendation_cache (
    user_id TEXT NOT NULL,
    cache_key TEXT NOT NULL,
    recommendations JSONB NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (user_id, cache_key),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### 索引优化策略

#### 查询性能优化
```sql
-- 用户相关索引
CREATE INDEX CONCURRENTLY idx_users_email_active ON users(email) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_users_registration_method ON users(registration_method);
CREATE INDEX CONCURRENTLY idx_users_created_at_desc ON users(created_at DESC);

-- 学校搜索索引
CREATE INDEX CONCURRENTLY idx_schools_country_city ON schools(country, city);
CREATE INDEX CONCURRENTLY idx_schools_type_active ON schools(type) WHERE is_active = true;
CREATE INDEX CONCURRENTLY idx_schools_ranking ON schools(ranking_international) WHERE ranking_international IS NOT NULL;

-- 专业搜索索引
CREATE INDEX CONCURRENTLY idx_programs_school_degree ON programs(school_id, degree_level);
CREATE INDEX CONCURRENTLY idx_programs_tuition_range ON programs(tuition_annual) WHERE tuition_annual IS NOT NULL;

-- 推荐系统索引
CREATE INDEX CONCURRENTLY idx_recommendations_user_created ON recommendations(user_id, created_at DESC);
CREATE INDEX CONCURRENTLY idx_user_behaviors_user_type_created ON user_behaviors(user_id, behavior_type, created_at DESC);

-- 全文搜索索引
CREATE INDEX CONCURRENTLY idx_schools_search ON schools USING gin(to_tsvector('english', name || ' ' || COALESCE(description, '')));
CREATE INDEX CONCURRENTLY idx_programs_search ON programs USING gin(to_tsvector('english', name || ' ' || COALESCE(academic_requirements, '')));
```

---

## 🔗 API设计

### RESTful API架构

#### API版本控制
```
Base URL: https://api.layla-ai.com/v2/
```

#### 认证机制
```python
# JWT Token认证
Authorization: Bearer <jwt_token>

# API Key认证 (第三方集成)
X-API-Key: <api_key>
```

### 核心API端点

#### 1. 用户管理API
```yaml
# 用户注册
POST /auth/register
Content-Type: application/json
{
  "username": "student123",
  "email": "student@example.com", 
  "password": "securePassword123",
  "display_name": "张三"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "user_id": "usr_123456",
    "username": "student123",
    "email": "student@example.com",
    "display_name": "张三",
    "created_at": "2024-10-10T10:00:00Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# 用户登录
POST /auth/login
{
  "username": "student123",
  "password": "securePassword123"
}

# 用户资料更新
PUT /users/{user_id}/profile
Authorization: Bearer <token>
{
  "age_range": "19-22",
  "current_grade": "本科在读",
  "target_major": ["声乐表演", "音乐剧"],
  "countries": ["美国", "英国"],
  "budget_cny_range": "60-100"
}
```

#### 2. 推荐系统API
```yaml
# 获取学校推荐
GET /recommendations/schools?limit=10&offset=0
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "school_id": "sch_juilliard",
        "name": "茱莉亚音乐学院",
        "country": "美国",
        "city": "纽约",
        "match_score": 92.5,
        "match_reasons": [
          "专业匹配度高 (声乐表演)",
          "预算范围适合",
          "地理位置偏好匹配"
        ],
        "programs": [
          {
            "program_id": "prg_juilliard_vocal",
            "name": "声乐表演硕士",
            "tuition_annual": 45000,
            "duration_years": 2
          }
        ]
      }
    ],
    "total": 25,
    "page": 1,
    "per_page": 10
  }
}

# 推荐反馈
POST /recommendations/{recommendation_id}/feedback
{
  "rating": 4,
  "feedback": "推荐很准确，但希望看到更多奖学金信息"
}
```

#### 3. 咨询预约API
```yaml
# 获取专家列表
GET /experts?specialization=vocal&availability=2024-10-15

Response: 200 OK
{
  "success": true,
  "data": {
    "experts": [
      {
        "expert_id": "exp_001",
        "name": "李教授",
        "title": "声乐教育专家",
        "specializations": ["声乐表演", "音乐教育"],
        "hourly_rate": 500.00,
        "rating": 4.8,
        "total_consultations": 156,
        "available_slots": [
          "2024-10-15T14:00:00Z",
          "2024-10-15T16:00:00Z"
        ]
      }
    ]
  }
}

# 预约咨询
POST /consultations/book
{
  "expert_id": "exp_001",
  "scheduled_time": "2024-10-15T14:00:00Z",
  "duration": 60,
  "notes": "希望了解美国声乐专业申请要求"
}

Response: 201 Created
{
  "success": true,
  "data": {
    "consultation_id": "cons_123456",
    "price": 500.00,
    "payment_url": "https://pay.layla-ai.com/cons_123456",
    "status": "pending_payment"
  }
}
```

#### 4. 作品集评估API
```yaml
# 上传作品集
POST /portfolio/upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

FormData:
- audio_file: <audio_file.mp3>
- title: "肖邦夜曲Op.9 No.2"
- composer: "Frederic Chopin"
- instrument: "piano"
- target_schools: ["juilliard", "curtis"]

Response: 202 Accepted
{
  "success": true,
  "data": {
    "upload_id": "upload_123456",
    "status": "processing",
    "estimated_completion": "2024-10-10T10:05:00Z"
  }
}

# 获取评估结果
GET /portfolio/analysis/{upload_id}

Response: 200 OK
{
  "success": true,
  "data": {
    "upload_id": "upload_123456",
    "status": "completed",
    "overall_score": 85.2,
    "dimensions": {
      "technical_skills": {
        "pitch_accuracy": 88.5,
        "rhythm_precision": 92.1,
        "dynamic_control": 81.3
      },
      "musical_expression": {
        "phrasing": 86.7,
        "emotion_conveyance": 84.2
      }
    },
    "feedback": "整体表现优秀，建议加强力度变化的细节处理...",
    "improvement_suggestions": [
      "注意第二乐句的渐强处理",
      "结尾部分可以更加细腻"
    ],
    "school_match_analysis": {
      "juilliard": {
        "admission_probability": 72.3,
        "strengths": ["技术基础扎实", "音乐表现力好"],
        "areas_for_improvement": ["需要提升创新性"]
      }
    }
  }
}
```

### API文档自动生成

#### Swagger/OpenAPI配置
```python
from flask_restx import Api, Resource, fields
from flask import Flask

app = Flask(__name__)
api = Api(app, 
    version='2.0',
    title='蕾拉酱AI留学顾问API',
    description='音乐留学咨询平台API文档',
    doc='/docs/'
)

# 数据模型定义
user_model = api.model('User', {
    'user_id': fields.String(required=True, description='用户ID'),
    'username': fields.String(required=True, description='用户名'),
    'email': fields.String(required=True, description='邮箱'),
    'display_name': fields.String(required=True, description='显示名称')
})

recommendation_model = api.model('Recommendation', {
    'school_id': fields.String(required=True, description='学校ID'),
    'name': fields.String(required=True, description='学校名称'),
    'match_score': fields.Float(required=True, description='匹配分数'),
    'match_reasons': fields.List(fields.String, description='匹配原因')
})
```

---

## 🔒 安全架构

### 安全策略概览

#### 1. 认证与授权
```python
class SecurityManager:
    """安全管理核心类"""
    
    def __init__(self):
        self.jwt_manager = JWTManager()
        self.permission_manager = PermissionManager()
        self.rate_limiter = RateLimiter()
    
    def authenticate_request(self, request) -> AuthResult:
        # 1. Token验证
        token = self.extract_token(request)
        if not token:
            raise UnauthorizedError("Missing authentication token")
            
        # 2. JWT解析验证
        payload = self.jwt_manager.decode_token(token)
        
        # 3. 用户状态检查
        user = self.get_user(payload['user_id'])
        if not user.is_active:
            raise ForbiddenError("User account is inactive")
            
        # 4. 权限验证
        if not self.permission_manager.check_permission(user, request.endpoint):
            raise ForbiddenError("Insufficient permissions")
            
        # 5. 频率限制
        if not self.rate_limiter.allow_request(user.user_id, request.endpoint):
            raise TooManyRequestsError("Rate limit exceeded")
            
        return AuthResult(user, payload)
```

#### 2. 数据加密
```python
class EncryptionService:
    """数据加密服务"""
    
    def __init__(self):
        self.fernet = Fernet(settings.ENCRYPTION_KEY)
        
    def encrypt_sensitive_data(self, data: str) -> str:
        """加密敏感数据"""
        return self.fernet.encrypt(data.encode()).decode()
        
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """解密敏感数据"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
        
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
    def verify_password(self, password: str, hashed: str) -> bool:
        """密码验证"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

#### 3. 输入验证与防护
```python
from marshmallow import Schema, fields, validate, ValidationError

class UserRegistrationSchema(Schema):
    """用户注册数据验证"""
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=20),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error='用户名只能包含字母、数字和下划线')
        ]
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, max=128),
            validate.Regexp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)', error='密码必须包含大小写字母和数字')
        ]
    )
    display_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50)
    )

class SecurityMiddleware:
    """安全中间件"""
    
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ, start_response):
        # SQL注入防护
        self.check_sql_injection(environ)
        
        # XSS防护
        self.sanitize_input(environ)
        
        # CSRF防护
        self.verify_csrf_token(environ)
        
        return self.app(environ, start_response)
```

### 隐私保护措施

#### GDPR合规性
```python
class PrivacyManager:
    """隐私管理"""
    
    def __init__(self):
        self.data_retention_policy = DataRetentionPolicy()
        self.consent_manager = ConsentManager()
        
    def handle_data_deletion_request(self, user_id: str) -> bool:
        """处理数据删除请求"""
        # 1. 验证用户身份
        user = self.get_user(user_id)
        
        # 2. 删除个人数据
        self.delete_user_profile(user_id)
        self.delete_chat_history(user_id)
        self.anonymize_recommendations(user_id)
        
        # 3. 保留必要的业务数据(匿名化)
        self.anonymize_payment_records(user_id)
        
        # 4. 记录删除操作
        self.log_deletion_request(user_id)
        
        return True
        
    def export_user_data(self, user_id: str) -> dict:
        """导出用户数据"""
        return {
            'profile': self.get_user_profile(user_id),
            'chat_history': self.get_chat_history(user_id),
            'recommendations': self.get_recommendations(user_id),
            'consultations': self.get_consultations(user_id)
        }
```

---

## ⚡ 性能优化

### 缓存策略

#### 多级缓存架构
```python
class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.redis_client = redis.Redis(host='redis-cluster')
        self.local_cache = {}
        
    def get_school_recommendations(self, user_id: str) -> List[dict]:
        # L1: 本地内存缓存 (1分钟)
        cache_key = f"recommendations:{user_id}"
        
        if cache_key in self.local_cache:
            data, timestamp = self.local_cache[cache_key]
            if time.time() - timestamp < 60:
                return data
                
        # L2: Redis缓存 (10分钟)
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            data = json.loads(cached_data)
            self.local_cache[cache_key] = (data, time.time())
            return data
            
        # L3: 数据库查询
        data = self.recommendation_engine.get_recommendations(user_id)
        
        # 写入缓存
        self.redis_client.setex(cache_key, 600, json.dumps(data))
        self.local_cache[cache_key] = (data, time.time())
        
        return data
```

#### 数据库查询优化
```sql
-- 分区表设计 (按时间分区)
CREATE TABLE chat_messages_2024_q4 PARTITION OF chat_messages
FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');

-- 读写分离配置
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        return 'replica'
        
    def db_for_write(self, model, **hints):
        return 'primary'
        
-- 查询优化示例
EXPLAIN (ANALYZE, BUFFERS) 
SELECT s.name, p.name as program_name, r.match_score
FROM recommendations r
JOIN schools s ON r.school_id = s.school_id
JOIN programs p ON s.school_id = p.school_id
WHERE r.user_id = 'usr_123456'
  AND r.created_at >= NOW() - INTERVAL '30 days'
ORDER BY r.match_score DESC
LIMIT 10;
```

### 异步处理架构

#### Celery任务队列
```python
from celery import Celery

celery_app = Celery('layla_ai')
celery_app.config_from_object('celery_config')

@celery_app.task(bind=True, max_retries=3)
def process_portfolio_analysis(self, upload_id: str):
    """异步处理作品集分析"""
    try:
        # 1. 获取上传文件
        upload = get_upload_by_id(upload_id)
        
        # 2. 音频预处理
        processed_audio = preprocess_audio(upload.file_path)
        
        # 3. AI分析
        analysis_result = analyze_audio_with_ai(processed_audio)
        
        # 4. 生成报告
        report = generate_analysis_report(analysis_result)
        
        # 5. 保存结果
        save_analysis_result(upload_id, report)
        
        # 6. 发送通知
        send_analysis_complete_notification(upload.user_id, upload_id)
        
    except Exception as exc:
        # 重试机制
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        else:
            # 记录失败
            log_analysis_failure(upload_id, str(exc))
            send_analysis_failed_notification(upload.user_id, upload_id)

@celery_app.task
def update_school_rankings():
    """定期更新学校排名数据"""
    ranking_data = fetch_latest_rankings()
    update_school_database(ranking_data)
    
@celery_app.task  
def send_application_reminders():
    """发送申请截止日期提醒"""
    upcoming_deadlines = get_upcoming_deadlines()
    for deadline in upcoming_deadlines:
        send_reminder_notification(deadline)
```

---

## 🚀 部署架构

### Google Cloud Platform部署

#### 服务架构图
```
                    ┌─────────────────┐
                    │   Cloudflare    │
                    │   (CDN + WAF)   │
                    └─────────┬───────┘
                              │
                    ┌─────────┴───────┐
                    │ Load Balancer   │
                    │  (Cloud LB)     │
                    └─────────┬───────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────┴───────┐ ┌─────┴─────┐ ┌───────┴───────┐
    │  App Engine     │ │  App      │ │  App Engine   │
    │  Instance 1     │ │  Engine   │ │  Instance N   │
    │                 │ │  Instance │ │               │
    └─────────────────┘ │  2        │ └───────────────┘
                        └───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────┴───────┐ ┌─────┴─────┐ ┌───────┴───────┐
    │   Cloud SQL     │ │  Redis    │ │ Cloud Storage │
    │ (PostgreSQL)    │ │ Memstore  │ │   (Files)     │
    └─────────────────┘ └───────────┘ └───────────────┘
```

#### 部署配置文件
```yaml
# app.yaml (Google App Engine)
runtime: python39
service: default
instance_class: F2

automatic_scaling:
  min_instances: 2
  max_instances: 10
  target_cpu_utilization: 0.6
  target_throughput_utilization: 0.8

env_variables:
  FLASK_ENV: production
  SECRET_KEY: ${SECRET_KEY}
  SUPABASE_URL: ${SUPABASE_URL}
  SUPABASE_ANON_KEY: ${SUPABASE_ANON_KEY}
  REDIS_URL: ${REDIS_URL}
  GEMINI_API_KEY: ${GEMINI_API_KEY}

handlers:
- url: /static
  static_dir: static
  secure: always
  
- url: /.*
  script: auto
  secure: always

# cloudbuild.yaml (CI/CD)
steps:
- name: 'gcr.io/cloud-builders/python'
  entrypoint: 'pip'
  args: ['install', '-r', 'requirements.txt']
  
- name: 'gcr.io/cloud-builders/python'
  entrypoint: 'python'
  args: ['-m', 'pytest', 'tests/']
  
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['app', 'deploy', 'app.yaml', '--no-promote']
  
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['app', 'services', 'set-traffic', 'default', '--splits', '${_VERSION}=100']
```

#### 容器化部署 (Docker)
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "app:app"]
```

### 数据库部署

#### Supabase配置
```sql
-- 数据库连接池配置
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- 行级安全策略
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的数据
CREATE POLICY user_isolation ON users
    FOR ALL TO authenticated
    USING (auth.uid()::text = user_id);

CREATE POLICY session_isolation ON user_sessions
    FOR ALL TO authenticated  
    USING (auth.uid()::text = user_id);
```

---

## 📊 监控告警

### 系统监控架构

#### 监控指标体系
```python
class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self.prometheus_client = PrometheusClient()
        self.custom_metrics = {}
        
    def collect_system_metrics(self):
        """收集系统指标"""
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters(),
            'active_connections': len(psutil.net_connections())
        }
        
    def collect_application_metrics(self):
        """收集应用指标"""
        return {
            'active_users': self.get_active_user_count(),
            'requests_per_minute': self.get_request_rate(),
            'response_time_avg': self.get_avg_response_time(),
            'error_rate': self.get_error_rate(),
            'recommendation_accuracy': self.get_recommendation_accuracy()
        }
        
    def collect_business_metrics(self):
        """收集业务指标"""
        return {
            'new_registrations': self.get_new_registrations_count(),
            'consultation_bookings': self.get_consultation_bookings(),
            'revenue_daily': self.get_daily_revenue(),
            'user_satisfaction': self.get_user_satisfaction_score()
        }
```

#### 告警规则配置
```yaml
# alerting_rules.yml
groups:
- name: system_alerts
  rules:
  - alert: HighCPUUsage
    expr: cpu_usage > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      description: "CPU usage is above 80% for more than 5 minutes"
      
  - alert: HighMemoryUsage
    expr: memory_usage > 85
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High memory usage detected"
      
- name: application_alerts  
  rules:
  - alert: HighErrorRate
    expr: error_rate > 5
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      
  - alert: SlowResponseTime
    expr: response_time_avg > 3000
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Slow response time detected"
      
- name: business_alerts
  rules:
  - alert: LowRecommendationAccuracy
    expr: recommendation_accuracy < 80
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "Recommendation accuracy below threshold"
```

#### 日志管理
```python
import logging
from google.cloud import logging as cloud_logging

class LoggingManager:
    """统一日志管理"""
    
    def __init__(self):
        # 初始化Google Cloud Logging
        self.cloud_client = cloud_logging.Client()
        self.cloud_client.setup_logging()
        
        # 配置本地日志
        self.setup_local_logging()
        
    def setup_local_logging(self):
        """配置本地日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
        )
        
    def log_user_action(self, user_id: str, action: str, details: dict):
        """记录用户行为"""
        logging.info(f"User action: {action}", extra={
            'user_id': user_id,
            'action': action,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    def log_recommendation_result(self, user_id: str, recommendations: list):
        """记录推荐结果"""
        logging.info("Recommendation generated", extra={
            'user_id': user_id,
            'recommendation_count': len(recommendations),
            'top_match_score': recommendations[0]['match_score'] if recommendations else 0
        })
        
    def log_error(self, error: Exception, context: dict):
        """记录错误"""
        logging.error(f"Application error: {str(error)}", extra={
            'error_type': type(error).__name__,
            'context': context,
            'stack_trace': traceback.format_exc()
        })
```

---

## 📋 实施时间线

### 开发阶段规划

#### Phase 1: 基础架构 (4周)
- **Week 1-2**: 数据库设计与搭建
  - 新增院校数据表结构
  - 推荐系统相关表
  - 数据迁移脚本
  
- **Week 3-4**: API框架搭建
  - RESTful API设计
  - 认证授权系统
  - 基础安全措施

#### Phase 2: 核心功能 (8周)  
- **Week 5-7**: AI推荐引擎
  - 推荐算法实现
  - 院校数据采集
  - 匹配度计算逻辑
  
- **Week 8-10**: 视频咨询系统
  - 预约管理功能
  - 支付集成
  - 视频通话集成
  
- **Week 11-12**: 作品集评估
  - 音频处理引擎
  - AI分析模型
  - 评估报告生成

#### Phase 3: 用户体验 (6周)
- **Week 13-15**: 移动端开发
  - React Native应用
  - 原生功能集成
  - 性能优化
  
- **Week 16-18**: 前端优化
  - UI/UX改进
  - 响应式设计
  - 交互体验提升

#### Phase 4: 生态建设 (8周)
- **Week 19-22**: 社区功能
  - 论坛系统
  - 用户互动功能
  - 内容管理系统
  
- **Week 23-26**: 数据分析
  - 监控告警系统
  - 数据分析平台
  - 商业智能报表

### 质量保证流程

#### 测试策略
```python
# 单元测试示例
import pytest
from unittest.mock import Mock, patch

class TestRecommendationEngine:
    
    def setup_method(self):
        self.engine = RecommendationEngine()
        self.mock_user_profile = {
            'current_grade': '本科在读',
            'target_major': ['声乐表演'],
            'countries': ['美国'],
            'budget_cny_range': '60-100'
        }
    
    def test_recommend_schools_success(self):
        """测试推荐功能正常流程"""
        recommendations = self.engine.recommend_schools(self.mock_user_profile)
        
        assert len(recommendations) > 0
        assert all(rec.match_score > 0 for rec in recommendations)
        assert recommendations[0].match_score >= recommendations[-1].match_score
    
    @patch('recommendation_engine.SchoolMatcher.find_candidates')
    def test_recommend_schools_no_candidates(self, mock_find_candidates):
        """测试无候选学校情况"""
        mock_find_candidates.return_value = []
        
        recommendations = self.engine.recommend_schools(self.mock_user_profile)
        
        assert len(recommendations) == 0

# 集成测试示例  
class TestConsultationAPI:
    
    def test_book_consultation_flow(self):
        """测试完整预约流程"""
        # 1. 获取专家列表
        experts_response = self.client.get('/api/experts')
        assert experts_response.status_code == 200
        
        # 2. 预约咨询
        booking_data = {
            'expert_id': 'exp_001',
            'scheduled_time': '2024-10-15T14:00:00Z',
            'duration': 60
        }
        booking_response = self.client.post('/api/consultations/book', json=booking_data)
        assert booking_response.status_code == 201
        
        # 3. 验证预约状态
        consultation_id = booking_response.json['data']['consultation_id']
        status_response = self.client.get(f'/api/consultations/{consultation_id}')
        assert status_response.json['data']['status'] == 'pending_payment'
```

---

## 📈 性能基准

### 目标性能指标

| 指标类别 | 指标名称 | 目标值 | 监控方式 |
|---------|---------|--------|----------|
| 响应时间 | API平均响应时间 | < 200ms | APM监控 |
| 响应时间 | 推荐生成时间 | < 2s | 自定义指标 |
| 响应时间 | 页面加载时间 | < 3s | 前端监控 |
| 吞吐量 | 并发用户数 | 1000+ | 负载测试 |
| 吞吐量 | QPS | 500+ | 服务器监控 |
| 可用性 | 系统可用性 | 99.9% | 健康检查 |
| 准确性 | 推荐准确率 | 85%+ | A/B测试 |

### 压力测试计划
```python
# locustfile.py - 性能测试脚本
from locust import HttpUser, task, between

class LayleAIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户登录"""
        response = self.client.post("/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        self.token = response.json()["token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})
    
    @task(3)
    def get_recommendations(self):
        """获取推荐 - 高频操作"""
        self.client.get("/api/recommendations/schools")
    
    @task(2)  
    def chat_with_ai(self):
        """AI对话 - 中频操作"""
        self.client.post("/api/chat", json={
            "message": "我想了解美国音乐学院",
            "history": []
        })
    
    @task(1)
    def book_consultation(self):
        """预约咨询 - 低频操作"""
        self.client.post("/api/consultations/book", json={
            "expert_id": "exp_001",
            "scheduled_time": "2024-10-15T14:00:00Z",
            "duration": 60
        })

# 运行命令:
# locust -f locustfile.py --host=https://api.layla-ai.com
```

---

## 📝 总结

本技术规格文档详细描述了蕾拉酱AI留学顾问产品v2.0的完整技术实施方案，涵盖了：

### 🎯 **核心技术亮点**
1. **AI驱动的推荐引擎**: 多算法融合的智能匹配系统
2. **实时视频咨询**: WebRTC技术的专家服务平台  
3. **智能作品集评估**: 音频AI分析的专业评估工具
4. **微服务架构**: 可扩展的云原生技术栈
5. **全链路监控**: 完善的性能和业务监控体系

### 🚀 **技术优势**
- **高性能**: 多级缓存 + 数据库优化，响应时间 < 200ms
- **高可用**: 99.9%系统可用性，自动扩缩容
- **高安全**: 多层安全防护，GDPR合规
- **易扩展**: 模块化设计，支持快速功能迭代
- **智能化**: AI算法持续优化，推荐准确率85%+

### 📋 **实施要点**
1. **分阶段开发**: 26周完整开发周期，4个主要阶段
2. **质量保证**: 完整的测试策略和CI/CD流程
3. **性能监控**: 全方位的系统和业务指标监控
4. **团队配置**: 8人技术团队，年预算500万
5. **风险控制**: 技术、业务、运营风险的全面评估

该技术方案为产品的成功实施提供了坚实的技术基础，确保能够构建出高质量、高性能、用户体验优秀的音乐留学咨询平台。

---

**文档维护信息**:
- **版本控制**: Git + 技术文档仓库
- **更新频率**: 每月技术评审
- **责任人**: 技术负责人 + 架构师
- **审批流程**: 技术委员会评审确认

*本文档由PM Agent基于产品需求和技术调研自动生成*
