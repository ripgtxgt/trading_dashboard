# Webhook Auto-Deployment Setup Guide

## Overview

This guide helps you set up automatic deployment using GitHub Webhooks. When you push code to GitHub, the server will automatically pull the latest code and deploy it.

**Advantages over GitHub Actions SSH:**
- ✅ More reliable for Windows servers
- ✅ No SSH configuration needed
- ✅ Real-time deployment logs
- ✅ Works behind firewalls (server pulls from GitHub)
- ✅ Easier to debug

## Quick Setup (3 Steps)

### Step 1: Start Webhook Server on Windows

1. **Open Command Prompt** on your Windows Server

2. **Navigate to project directory:**
   ```cmd
   cd C:\trading_dashboard_fixed
   ```

3. **Start webhook server** (choose one method):

   **Method A: Using PM2 (Recommended - Auto-restart)**
   ```cmd
   pm2 restart ecosystem.config.cjs
   ```
   The webhook server will start automatically with other services.

   **Method B: Manual Start (For testing)**
   ```cmd
   node webhook-deploy-server.js
   ```

4. **Verify server is running:**
   - Open browser: http://localhost:9000
   - You should see "Webhook Deploy Server" page
   - Or check PM2: `pm2 list` (should show webhook-deploy-server online)

### Step 2: Configure Windows Firewall

**Allow incoming connections on port 9000:**

```powershell
# Run PowerShell as Administrator
New-NetFirewallRule -DisplayName "Webhook Deploy Server" -Direction Inbound -LocalPort 9000 -Protocol TCP -Action Allow
```

Or manually:
1. Open Windows Defender Firewall
2. Advanced Settings → Inbound Rules → New Rule
3. Port → TCP → 9000 → Allow the connection
4. Name: "Webhook Deploy Server"

### Step 3: Configure GitHub Webhook

1. **Go to your GitHub repository:**
   https://github.com/ripgtxgt/trading_dashboard/settings/hooks

2. **Click "Add webhook"**

3. **Configure webhook:**
   - **Payload URL:** `http://13.113.194.218:9000/webhook`
   - **Content type:** `application/json`
   - **Secret:** (Optional) Set a secret key for security
   - **Which events:** Select "Just the push event"
   - **Active:** ✅ Check this box

4. **Click "Add webhook"**

5. **Test the webhook:**
   - Make a small change to README.md
   - Push to GitHub
   - Check webhook deliveries in GitHub (should show green checkmark)
   - Check server logs: http://13.113.194.218:9000

## How It Works

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   You Push  │────────▶│    GitHub    │────────▶│  Your Server    │
│   to GitHub │         │   (Webhook)  │         │  (Port 9000)    │
└─────────────┘         └──────────────┘         └─────────────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │  git pull       │
                                                  │  deploy-auto.ps1│
                                                  │  PM2 restart    │
                                                  └─────────────────┘
```

1. You push code to GitHub
2. GitHub sends webhook notification to your server
3. Webhook server receives notification
4. Server runs: `git pull` + `deploy-auto.ps1`
5. Your application is automatically updated!

## Verification

### Check Webhook Server Status

**Via Web Browser:**
```
http://13.113.194.218:9000
```
Should show server status and recent logs.

**Via PM2:**
```cmd
pm2 list
pm2 logs webhook-deploy-server
```

### Check Deployment Logs

**View webhook logs:**
```cmd
cd C:\trading_dashboard_fixed
type webhook-deploy.log
```

**View PM2 logs:**
```cmd
pm2 logs webhook-deploy-server --lines 50
```

### Test Deployment

1. **Make a test change:**
   ```bash
   # On your development machine
   echo "Test deployment" >> README.md
   git add README.md
   git commit -m "test: webhook deployment"
   git push origin main
   ```

2. **Check GitHub webhook delivery:**
   - Go to: https://github.com/ripgtxgt/trading_dashboard/settings/hooks
   - Click on your webhook
   - Check "Recent Deliveries"
   - Should show 200 response

3. **Check server logs:**
   - Visit: http://13.113.194.218:9000
   - Should show deployment in progress/completed

4. **Verify files updated:**
   ```cmd
   cd C:\trading_dashboard_fixed
   dir
   ```
   File modification dates should be recent.

## Security (Optional but Recommended)

### Set Webhook Secret

1. **Generate a secure secret:**
   ```bash
   # On your development machine
   openssl rand -hex 32
   ```

2. **Set secret in Windows Server:**
   ```cmd
   setx WEBHOOK_SECRET "your-generated-secret-here"
   ```

3. **Restart webhook server:**
   ```cmd
   pm2 restart webhook-deploy-server
   ```

4. **Add secret to GitHub webhook:**
   - Go to webhook settings
   - Enter the same secret in "Secret" field
   - Update webhook

Now GitHub will sign all webhook requests, and your server will verify the signature.

## Troubleshooting

### Webhook Server Not Starting

**Check if port 9000 is already in use:**
```cmd
netstat -ano | findstr :9000
```

**Change port if needed:**
Edit `webhook-deploy-server.js` and change `PORT = 9000` to another port.

### GitHub Webhook Shows Red X

**Check firewall:**
- Ensure port 9000 is open in Windows Firewall
- Ensure your router/cloud provider allows incoming traffic on port 9000

**Check server is running:**
```cmd
pm2 list
```
webhook-deploy-server should be "online"

**Check logs:**
```cmd
pm2 logs webhook-deploy-server
```

### Deployment Not Running

**Check webhook-deploy.log:**
```cmd
type C:\trading_dashboard_fixed\webhook-deploy.log
```

**Manually test deployment:**
```cmd
cd C:\trading_dashboard_fixed
git pull origin main
powershell.exe -ExecutionPolicy Bypass -File .\deploy-auto.ps1
```

### Port 9000 Blocked by ISP/Cloud Provider

If your ISP or cloud provider blocks port 9000:

**Option 1: Use a different port**
- Edit `webhook-deploy-server.js`
- Change `PORT = 9000` to `PORT = 8080` or another port
- Update firewall rules
- Update GitHub webhook URL

**Option 2: Use Nginx reverse proxy**
- Configure Nginx to proxy `/webhook` to `localhost:9000`
- Use port 80 or 443 for webhook
- GitHub webhook URL: `http://cryptoalpha.vip/webhook`

## Comparison: Webhook vs GitHub Actions SSH

| Feature | Webhook | GitHub Actions SSH |
|---------|---------|-------------------|
| Windows Compatibility | ✅ Excellent | ⚠️ Limited |
| Setup Complexity | ⭐⭐ Easy | ⭐⭐⭐⭐ Complex |
| Debugging | ✅ Easy (real-time logs) | ❌ Difficult |
| Firewall Friendly | ✅ Yes (server pulls) | ❌ No (requires SSH) |
| Security | ✅ Webhook signature | ✅ SSH keys |
| Deployment Speed | ⚡ Fast (~10s) | ⚡ Fast (~10s) |
| Reliability | ✅ High | ⚠️ Medium (Windows SSH issues) |

## Maintenance

### View Recent Deployments

```cmd
pm2 logs webhook-deploy-server --lines 100
```

### Restart Webhook Server

```cmd
pm2 restart webhook-deploy-server
```

### Stop Webhook Server

```cmd
pm2 stop webhook-deploy-server
```

### Update Webhook Server Code

After updating `webhook-deploy-server.js`:
```cmd
pm2 restart webhook-deploy-server
```

## Next Steps

After successful setup:

1. ✅ **Test deployment** by pushing a small change
2. ✅ **Monitor logs** to ensure everything works
3. ✅ **Set webhook secret** for security
4. ✅ **Configure Nginx** to use domain instead of IP:port

## Support

If you encounter issues:

1. Check webhook server logs: `pm2 logs webhook-deploy-server`
2. Check deployment logs: `type webhook-deploy.log`
3. Check GitHub webhook deliveries
4. Test manual deployment: `manual-deploy.bat`
