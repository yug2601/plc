# 🚀 RENDER DEPLOYMENT GUIDE - Deploy in 10 Minutes!

## ⚡ Quick Deploy Steps

### Step 1: Go to Render (2 minutes)
1. Open browser: [render.com](https://render.com)
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (use same account as your repo)

### Step 2: Create Web Service (3 minutes)
1. Click **"New +"** → **"Web Service"**
2. Click **"Connect GitHub"** → Authorize Render
3. Find and select **"plc"** repository
4. Click **"Connect"**

### Step 3: Configure Service (3 minutes)
Fill in these exact settings:

**Basic Settings:**
- **Name**: `plc-gateway`
- **Region**: `Oregon (US West)` (or closest to you)
- **Branch**: `main`
- **Root Directory**: (leave blank)

**Build & Deploy:**
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python plc_gateway.py`

**Plan:**
- **Instance Type**: `Free` (select this!)

### Step 4: Environment Variables (1 minute)
Scroll down to **"Environment Variables"** and add these 4 variables:

| Key | Value |
|-----|-------|
| `PLC_IP` | `152.59.34.144` |
| `PLC_PORT` | `502` |
| `UPLOAD_RATE` | `2` |
| `PORT` | `10000` |

### Step 5: Deploy! (1 minute)
1. Click **"Create Web Service"**
2. Wait for deployment (2-3 minutes)
3. You'll see logs like:
   ```
   === PLC GATEWAY STARTED ===
   Target PLC: 152.59.34.144:502
   Health check server running on port 10000
   ```

### Step 6: Get Your URL
Your app will be live at: `https://plc-gateway.onrender.com`

## 🔥 That's It! Your Backend is Live!

### Next: Router Configuration
**IMPORTANT**: Your PLC must be accessible from internet.

1. **Access Router**: Go to `192.168.1.1` or `192.168.0.1`
2. **Port Forwarding**: Forward port `502` to `192.168.0.10:502`
3. **Test**: Your Render logs should show successful PLC connections

### Troubleshooting
- **Build Failed**: Check requirements.txt
- **Connection Error**: Configure port forwarding
- **Logs**: Click "Logs" tab in Render dashboard

## 🎉 Success Indicators
✅ Render deployment shows "Live"
✅ Logs show "PLC GATEWAY STARTED"
✅ Your Vercel app displays live PLC data

**Total Time: Under 10 minutes!**