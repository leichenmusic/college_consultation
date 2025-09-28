# 蕾拉酱的AI留学顾问 🎓✨

一个基于Flask的智能留学咨询聊天应用，采用黑紫主题设计，支持语音输入和打字机效果。

## 📸 预览

- **左侧面板**: 蕾拉酱头像、介绍信息和功能特色
- **右侧聊天**: 智能对话界面，支持语音输入
- **主题色彩**: 黑色和紫色渐变设计
- **交互效果**: 打字机效果、动画和视觉反馈

## ✨ 功能特色

- 🤖 **智能AI对话**: 蕾拉酱的AI小助理提供个性化留学咨询
- 🎤 **语音输入**: 支持中文语音识别，点击麦克风即可说话
- ⌨️ **打字机效果**: AI回复逐字显示，增强互动体验
- 🎨 **现代UI设计**: 黑紫渐变主题，左右分栏布局
- 📱 **响应式设计**: 支持桌面和移动端访问
- 🔄 **会话管理**: 自动保存对话历史和用户信息

## 🛠️ 技术栈

- **后端**: Flask (Python)
- **前端**: HTML5, CSS3, JavaScript
- **语音识别**: Web Speech API
- **部署**: Google App Engine
- **API集成**: Vercel Gemini Proxy

## 📁 项目结构

```
college_consultation/
├── README.md                 # 项目说明文档
├── app.py                    # Flask主应用
├── main.py                   # GAE入口文件
├── requirements.txt          # Python依赖
├── app.yaml                  # Google App Engine配置
├── .gcloudignore            # 部署排除文件
├── static/                   # 静态资源
│   ├── css/
│   │   └── style.css        # 样式文件
│   ├── js/
│   │   └── chat.js          # 前端交互逻辑
│   └── images/
│       └── layla_avatar.png # 蕾拉酱头像
└── templates/                # HTML模板
    ├── index.html           # 首页（重定向到聊天）
    └── chat.html            # 聊天界面
```

## 🚀 本地开发

### 环境要求
- Python 3.9+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd college_consultation
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **添加蕾拉酱头像**
   - 将头像图片重命名为 `layla_avatar.png`
   - 放置在 `static/images/` 目录下

5. **运行应用**
```bash
python app.py
```

6. **访问应用**
   - 打开浏览器访问: http://localhost:5001

## ☁️ Google Cloud Platform 部署

### 前置条件

1. **Google Cloud账户**: 在 [cloud.google.com](https://cloud.google.com) 创建账户
2. **创建GCP项目**: 在Google Cloud Console中创建新项目
3. **启用计费**: 确保项目已启用计费（可使用免费额度）

### gcloud CLI 配置详细步骤

#### 1. 安装 gcloud CLI

**macOS:**

**方法1: 使用 Homebrew (推荐)**
```bash
# 使用 Homebrew 安装
brew install --cask google-cloud-sdk
```

**方法2: 手动安装**
```bash
# 下载并安装 gcloud CLI
curl https://sdk.cloud.google.com | bash

# 添加 gcloud 到 PATH (适用于 zsh shell)
echo 'export PATH="$HOME/Documents/google-cloud-sdk/bin:$PATH"' >> ~/.zshrc

# 重新加载 shell 配置
exec zsh -l

# 如果使用 bash shell，请使用以下命令替代
# echo 'export PATH="$HOME/Documents/google-cloud-sdk/bin:$PATH"' >> ~/.bashrc
# exec bash -l
```

**验证安装路径:**
```bash
# 检查 gcloud 是否在 PATH 中
which gcloud

# 如果显示类似 /Users/yourname/Documents/google-cloud-sdk/bin/gcloud 则安装成功
```

**Linux:**
```bash
# 添加 Cloud SDK 分发 URI 作为包源
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# 导入 Google Cloud 公钥
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# 更新并安装 Cloud SDK
sudo apt-get update && sudo apt-get install google-cloud-cli
```

**Windows:**
1. 下载 [Google Cloud CLI 安装程序](https://cloud.google.com/sdk/docs/install#windows)
2. 运行安装程序并按照提示操作
3. 重启命令提示符

#### 2. 验证安装
```bash
gcloud --version
```

#### 3. 初始化和身份验证

**登录Google账户:**
```bash
gcloud auth login
```
这将打开浏览器，请使用您的Google账户登录。

**设置默认项目:**
```bash
# 查看可用项目
gcloud projects list

# 设置默认项目（替换 YOUR_PROJECT_ID 为您的实际项目ID）
gcloud config set project YOUR_PROJECT_ID

# 验证当前配置
gcloud config list
```

**设置默认区域（可选但推荐）:**
```bash
# 查看可用区域
gcloud compute zones list

# 设置默认区域（推荐选择离您最近的区域）
gcloud config set compute/zone asia-east1-a
gcloud config set compute/region asia-east1
```

#### 4. 启用必要的API服务

```bash
# 启用 App Engine API
gcloud services enable appengine.googleapis.com

# 启用 Cloud Build API（如果需要）
gcloud services enable cloudbuild.googleapis.com

# 查看已启用的服务
gcloud services list --enabled
```

#### 5. 初始化 App Engine

```bash
# 创建 App Engine 应用（只需执行一次）
gcloud app create

# 选择区域时，推荐选择：
# - asia-northeast1 (东京)
# - asia-east1 (台湾)
# - us-central1 (美国中部)
```

### 部署步骤

#### 1. 准备部署

确保您在项目根目录：
```bash
cd ~/Documents/Education\ Business/gitrepo/college_consultation
```

检查必要文件：
```bash
ls -la
# 应该看到：app.yaml, main.py, app.py, requirements.txt, deploy.sh 等文件
```

#### 2. 生产环境部署 (推荐)

**使用自动化部署脚本:**
```bash
# 使用当前时间戳作为版本号
./deploy.sh

# 或指定自定义版本号
./deploy.sh v1.0.0
```

**手动生产部署:**
```bash
# 部署到生产环境，使用版本控制
gcloud app deploy --version=v1-0-0 --promote --stop-previous-version

# 验证部署
gcloud app browse
```

#### 3. 开发/测试部署

**快速开发部署:**
```bash
gcloud app deploy --version=dev --no-promote
```

**测试特定版本:**
```bash
gcloud app deploy --version=test-$(date +%Y%m%d) --no-promote
```

#### 4. 验证部署

**查看应用状态:**
```bash
gcloud app describe
```

**在浏览器中打开应用:**
```bash
gcloud app browse
```

**查看实时日志:**
```bash
gcloud app logs tail -s default
```

**查看所有版本:**
```bash
gcloud app versions list
```

### 高级配置

#### 生产环境最佳实践

**1. 环境变量配置**

在部署前，编辑 `app.yaml` 文件中的生产环境变量：
```yaml
env_variables:
  GAE_ENV: standard
  SECRET_KEY: "your-secure-production-secret-key-here"  # 请更改为强密码
  GEMINI_PROXY_URL: "https://vercel-gemini-proxy-kappa.vercel.app/api/gemini-proxy"
```

**2. 生产环境特性**
- ✅ **自动缩放**: 无流量时缩放到0，高流量时最多20个实例
- ✅ **静态文件缓存**: CSS/JS缓存1小时，图片缓存7天
- ✅ **健康检查**: 自动监控应用健康状态
- ✅ **HTTPS强制**: 所有请求自动使用HTTPS
- ✅ **生产日志**: 优化的日志级别和格式

**3. 版本管理**
```bash
# 查看所有版本
gcloud app versions list

# 切换流量到特定版本
gcloud app services set-traffic default --splits=v1-0-0=100

# 分流测试 (金丝雀部署)
gcloud app services set-traffic default --splits=v1-0-0=90,v1-1-0=10

# 删除旧版本
gcloud app versions delete old-version-id
```

**4. 监控和日志**
```bash
# 实时日志
gcloud app logs tail -s default

# 错误日志
gcloud app logs read --severity=ERROR --limit=50

# 性能监控
# 访问: https://console.cloud.google.com/appengine/monitoring
```

#### 环境变量设置

编辑 `app.yaml` 文件：
```yaml
env_variables:
  GEMINI_PROXY_URL: "https://vercel-gemini-proxy-kappa.vercel.app/api/gemini-proxy"
  SECRET_KEY: "your-secret-key-here"
```

#### 自定义域名

1. 在 Google Cloud Console 中：
   - 导航到 App Engine → 设置 → 自定义域名
   - 点击"添加自定义域名"
   - 按照验证流程操作

2. 使用命令行：
```bash
gcloud app domain-mappings create example.com
```

#### 版本管理

```bash
# 列出所有版本
gcloud app versions list

# 切换流量到特定版本
gcloud app services set-traffic default --splits=v2=1

# 删除旧版本
gcloud app versions delete v1
```

## 🔧 故障排除

### 常见问题

**1. 部署失败 - 服务账户权限错误**

如果遇到类似以下错误：
```
service account [PROJECT-ID]@appspot.gserviceaccount.com does not have access to the bucket
```

**解决方案：**

**步骤1: 获取项目信息**
```bash
# 获取当前项目ID
gcloud config get-value project

# 查看项目详情
gcloud projects describe $(gcloud config get-value project)
```

**步骤2: 启用必要的API**
```bash
# 启用所有必要的API
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

**步骤3: 修复服务账户权限**
```bash
# 获取项目ID
export PROJECT_ID=$(gcloud config get-value project)

# 为App Engine默认服务账户添加必要权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

# 为Cloud Build服务账户添加权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com" \
    --role="roles/storage.admin"
```

**步骤4: 重新尝试部署**
```bash
# 等待几分钟让权限生效，然后重新部署
gcloud app deploy --verbosity=info
```

**替代解决方案（如果上述方法不行）：**
```bash
# 使用用户凭据进行部署
gcloud auth application-default login
gcloud app deploy

# 或者指定服务账户密钥文件
# gcloud auth activate-service-account --key-file=path/to/service-account-key.json
# gcloud app deploy
```

**2. 其他部署失败情况**
```bash
# 查看详细错误信息
gcloud app deploy --verbosity=debug

# 检查配置
gcloud config list
gcloud app describe
```

**2. 静态文件未加载（包括头像图片）**

如果头像或其他静态文件未显示：

**检查文件名大小写：**
```bash
# 检查实际文件名
ls -la static/images/

# 确保HTML模板中的文件名与实际文件名完全匹配
# 文件名: layla_avatar.png (小写)
# HTML中: layla_avatar.png (必须完全一致)
```

**检查文件是否被部署：**
```bash
# 查看部署的文件
gcloud app deploy --dry-run

# 检查 .gcloudignore 文件，确保图片文件没有被排除
cat .gcloudignore | grep -i "\.png\|images"
```

**验证静态文件配置：**
- 确保 `static/` 目录结构正确
- 检查 `app.yaml` 中的静态文件处理配置：
```yaml
handlers:
- url: /static
  static_dir: static
  secure: always
```

**强制重新部署静态文件：**
```bash
# 清理并重新部署
gcloud app deploy --stop-previous-version
```

**3. API调用失败**
- 检查 Vercel 代理 API 是否正常工作
- 验证网络连接和CORS设置

**4. 语音识别不工作**
- 确保使用 HTTPS 访问（GAE自动提供）
- 检查浏览器麦克风权限

### 日志查看

```bash
# 实时日志
gcloud app logs tail -s default

# 历史日志
gcloud app logs read --limit=100

# 错误日志
gcloud app logs read --severity=ERROR
```

### 性能监控

在 Google Cloud Console 中：
1. 导航到 App Engine → 监控
2. 查看请求延迟、错误率等指标
3. 设置告警规则

## 🔒 安全建议

1. **API密钥管理**: 使用环境变量存储敏感信息
2. **HTTPS强制**: 已在 `app.yaml` 中配置
3. **访问控制**: 考虑添加身份验证机制
4. **日志监控**: 定期检查应用日志

## 💰 成本优化

1. **免费额度**: Google App Engine 提供慷慨的免费额度
2. **自动缩放**: 配置合理的实例数量限制
3. **资源监控**: 定期检查资源使用情况

## 📞 支持

如果遇到问题，请：
1. 查看 Google Cloud 官方文档
2. 检查项目的 GitHub Issues
3. 联系开发团队

## 📄 许可证

[添加您的许可证信息]

---

**开发团队**: 蕾拉酱AI团队  
**最后更新**: 2024年  
**版本**: 1.0.0

🌟 享受与蕾拉酱的AI小助理的智能对话体验！
