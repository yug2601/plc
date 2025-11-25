# Complete Railway Deployment Guide for PLC Gateway

## 🚀 Step-by-Step Deployment to Railway

### Prerequisites
- ✅ GitHub account
- ✅ Railway account (free)
- ✅ Node.js installed (for Railway CLI)

---

## Step 1: Install Railway CLI

Open PowerShell and run:
```powershell
npm install -g @railway/cli
```

Verify installation:
```powershell
railway --version
```

---

## Step 2: Prepare Your Code for GitHub

### 2.1 Initialize Git Repository
```powershell
cd C:\PLC_Project\backend
git init
```

### 2.2 Create .gitignore
Create a `.gitignore` file to exclude sensitive data:
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
.env
*.log
.DS_Store
```

### 2.3 Add Files to Git
```powershell
git add .
git commit -m "Initial commit: PLC Gateway for Railway deployment"
```

### 2.4 Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name it: `plc-gateway-backend`
4. Make it **Public** (required for Railway free tier)
5. Don't initialize with README (you already have files)
6. Click "Create repository"

### 2.5 Push to GitHub
```powershell
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/plc-gateway-backend.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy on Railway

### 3.1 Sign Up for Railway
1. Go to [Railway.app](https://railway.app)
2. Click "Login"
3. Sign in with your GitHub account
4. Authorize Railway to access your repositories

### 3.2 Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `plc-gateway-backend` repository
4. Railway will automatically detect it's a Python project

### 3.3 Configure Deployment
Railway will automatically:
- ✅ Detect `requirements.txt`
- ✅ Install Python dependencies
- ✅ Use the `Procfile` to start your app
- ✅ Deploy your code

---

## Step 4: Configure Environment Variables

### 4.1 Set PLC Connection Variables
In Railway dashboard:
1. Go to your project
2. Click "Variables" tab
3. Add these variables:

**Variable 1:**
- Name: `PLC_IP`
- Value: `192.168.0.10` (your current PLC IP - we'll update this later)

**Variable 2:**
- Name: `PLC_PORT`
- Value: `502`

**Variable 3:**
- Name: `UPLOAD_RATE`
- Value: `2`

**Variable 4:**
- Name: `PORT`
- Value: `8080`

### 4.2 Deploy with Variables
Click "Deploy" - Railway will redeploy with your environment variables.

---

## Step 5: Configure Firebase (Important!)

### 5.1 Upload Service Account Key
Your `serviceAccountKey.json` is already in your repository, so this should work automatically.

### 5.2 Alternative: Use Environment Variables (More Secure)
For better security, you can use Firebase environment variables instead:

1. Open your `serviceAccountKey.json`
2. Copy the entire JSON content
3. In Railway, add a new variable:
   - Name: `FIREBASE_SERVICE_ACCOUNT`
   - Value: [paste the entire JSON content]

Then update your code to use this (optional):
```python
# In plc_gateway.py, replace the Firebase initialization with:
if not firebase_admin._apps:
    try:
        if os.getenv('FIREBASE_SERVICE_ACCOUNT'):
            import json
            service_account_info = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))
            cred = credentials.Certificate(service_account_info)
            firebase_admin.initialize_app(cred)
        elif os.path.exists("serviceAccountKey.json"):
            cred = credentials.Certificate("serviceAccountKey.json")
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        raise
```

---

## Step 6: Monitor Deployment

### 6.1 Check Deployment Status
1. In Railway dashboard, go to "Deployments" tab
2. You should see "Building" → "Deploying" → "Success"
3. If it fails, check the logs for errors

### 6.2 View Logs
Click on your deployment to see real-time logs:
```
=== PLC GATEWAY STARTED ===
Target PLC: 192.168.0.10:502
Upload Rate: 2 seconds
Firebase Collection: factory_data/oven_1
===============================
Health check server running on port 8080
```

### 6.3 Test Health Check
Railway will provide a URL like: `https://your-app-name.up.railway.app`
Visit this URL - you should see:
```json
{"status": "running", "service": "PLC Gateway"}
```

---

## Step 7: Network Configuration (Critical!)

⚠️ **Your cloud service needs to reach your PLC over the internet**

### 7.1 Find Your Public IP
Visit [whatismyip.com](https://whatismyip.com) to find your public IP address.

### 7.2 Configure Router Port Forwarding
In your router settings:
1. **External Port**: `502` (or choose another like `8502`)
2. **Internal IP**: `192.168.0.10` (your PLC)
3. **Internal Port**: `502`
4. **Protocol**: `TCP`

### 7.3 Update Railway Environment Variable
1. In Railway dashboard, go to "Variables"
2. Update `PLC_IP` to your **public IP address**
3. If you used a different external port, update `PLC_PORT` too
4. Save - Railway will automatically redeploy

---

## Step 8: Test Complete System

### 8.1 Check Railway Logs
Monitor the logs for successful PLC connections:
```
✅ PLC connection test SUCCESSFUL to YOUR_PUBLIC_IP:502
Uploaded 20 registers successfully
```

### 8.2 Check Firebase
1. Go to Firebase Console
2. Navigate to Firestore Database
3. Check `factory_data/oven_1` document for recent data

### 8.3 Test Your Vercel Frontend
Your Vercel app should now display live PLC data!

---

## Step 9: Maintenance & Updates

### 9.1 Update Code
When you need to update your code:
```powershell
cd C:\PLC_Project\backend
# Make your changes
git add .
git commit -m "Update: description of changes"
git push
```
Railway will automatically redeploy!

### 9.2 Monitor Usage
Railway free tier includes:
- ✅ 500 execution hours/month
- ✅ 1GB RAM
- ✅ Shared CPU
- ✅ $5 credit monthly

This is more than enough for your PLC gateway!

### 9.3 Scale Up (Optional)
If needed, you can upgrade to Railway Pro for:
- ✅ Always-on (no sleep)
- ✅ More resources
- ✅ Custom domains

---

## 🎉 Success!

After completing these steps:
- ✅ **Frontend**: Deployed on Vercel
- ✅ **Backend**: Deployed on Railway  
- ✅ **Database**: Firebase (cloud)
- ✅ **PLC Connection**: Via internet

**Your entire system runs in the cloud - no PC required!**

---

## Troubleshooting

### Common Issues:

1. **"Cannot reach PLC"**
   - Check port forwarding configuration
   - Verify public IP is correct
   - Test connection: `telnet YOUR_PUBLIC_IP 502`

2. **"Firebase permission denied"**
   - Verify serviceAccountKey.json is correct
   - Check Firebase project settings

3. **"Build failed"**
   - Check requirements.txt syntax
   - Verify all files are committed to GitHub

4. **"App keeps crashing"**
   - Check Railway logs for specific errors
   - Verify environment variables are set correctly

### Need Help?
- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)