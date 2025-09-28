# 🚀 Deployment Guide - 蕾拉酱的AI留学顾问

## 📋 Pre-Deployment Checklist

### 1. **Environment Variables Setup**

Before deploying, you MUST update the environment variables in `app.yaml`:

```yaml
env_variables:
  GAE_ENV: standard
  SECRET_KEY: "your-actual-secret-key-here"  # Generate a strong secret key
  GEMINI_PROXY_URL: "https://vercel-gemini-proxy.vercel.app/api/gemini-2.5-flash"
  SUPABASE_URL: "https://your-project-ref.supabase.co"
  SUPABASE_ANON_KEY: "your-supabase-anon-key"
  GOOGLE_CLIENT_ID: "your-google-client-id.apps.googleusercontent.com"
  GOOGLE_CLIENT_SECRET: "your-google-client-secret"
```

### 2. **Required Services Setup**

#### **Supabase Database**
1. Create a Supabase project at https://supabase.com
2. Run the SQL schema from `supabase_schema.sql`
3. Get your project URL and anon key from Settings > API

#### **Google OAuth**
1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Add your domain to authorized origins
4. Add redirect URIs for your deployed app

### 3. **Google Cloud Setup**

#### **Install Google Cloud CLI**
```bash
# macOS
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Or using Homebrew
brew install google-cloud-sdk
```

#### **Authenticate and Setup**
```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable App Engine API
gcloud services enable appengine.googleapis.com
```

## 🚀 Deployment Options

### **Option 1: Automated Deployment (Recommended)**

Use the provided deployment script:

```bash
# Make script executable
chmod +x deploy.sh

# Deploy with automatic version
./deploy.sh

# Or deploy with custom version
./deploy.sh v1.0.0
```

### **Option 2: Manual Deployment**

```bash
# Navigate to project directory
cd "/Users/rfu/Documents/Education Business/gitrepo/college_consultation"

# Deploy to App Engine
gcloud app deploy

# View your deployed app
gcloud app browse
```

## 📊 Post-Deployment

### **Monitor Your App**
```bash
# View logs
gcloud app logs tail -s default

# View app in browser
gcloud app browse

# Check app status
gcloud app versions list
```

### **Environment URLs**
- **Production**: `https://YOUR_PROJECT_ID.appspot.com`
- **Admin Panel**: `https://YOUR_PROJECT_ID.appspot.com/admin`
- **API Health Check**: `https://YOUR_PROJECT_ID.appspot.com/api/check_database`

## 🔧 Configuration Notes

### **Domain Setup (Optional)**
To use a custom domain:
```bash
# Map custom domain
gcloud app domain-mappings create YOUR_DOMAIN.com
```

### **SSL/HTTPS**
- App Engine automatically provides SSL certificates
- All traffic is automatically redirected to HTTPS (configured in app.yaml)

### **Scaling Configuration**
Current settings in `app.yaml`:
- **Min instances**: 0 (scales to zero when no traffic)
- **Max instances**: 20
- **Memory**: 1GB per instance
- **CPU**: 1 vCPU per instance

### **Static File Caching**
- CSS/JS files: 1 hour cache
- Images: 7 days cache
- Other static files: 1 hour cache

## 🛠️ Troubleshooting

### **Common Issues**

1. **Environment Variables Not Set**
   - Error: Database connection fails
   - Solution: Update `app.yaml` with correct Supabase credentials

2. **Google OAuth Not Working**
   - Error: OAuth redirect mismatch
   - Solution: Add your deployed domain to Google OAuth settings

3. **Static Files Not Loading**
   - Error: CSS/JS not found
   - Solution: Check static file handlers in `app.yaml`

4. **Database Schema Not Created**
   - Error: Table doesn't exist
   - Solution: Run `supabase_schema.sql` in your Supabase project

### **Useful Commands**
```bash
# View app logs in real-time
gcloud app logs tail -s default

# Deploy specific version without promoting
gcloud app deploy --no-promote --version=staging

# Switch traffic between versions
gcloud app services set-traffic default --splits=v1=50,v2=50

# Delete old versions
gcloud app versions delete VERSION_ID
```

## 📈 Performance Optimization

### **Current Optimizations**
- ✅ Static file caching with appropriate expiration
- ✅ Gzip compression enabled
- ✅ Auto-scaling based on CPU and throughput
- ✅ Health checks configured
- ✅ HTTPS-only traffic

### **Recommended Monitoring**
- Monitor response times in Google Cloud Console
- Set up alerting for high error rates
- Monitor database performance in Supabase dashboard
- Track user engagement and chat completion rates

## 🔐 Security Checklist

- ✅ HTTPS-only traffic enforced
- ✅ Strong secret keys in production
- ✅ Database credentials secured
- ✅ OAuth properly configured
- ✅ Static files served with proper headers
- ✅ Health checks configured

---

**Ready to deploy? Run `./deploy.sh` and your AI留学顾问 will be live!** 🎉

