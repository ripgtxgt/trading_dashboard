# GitHub Actions Auto-Deployment Troubleshooting Guide

## Problem: Deployment Succeeds but Files Not Updated on Server

### Symptoms
- GitHub Actions shows "Success" status
- Deployment step completes in ~2 seconds
- Files on server have old modification dates
- No actual deployment occurs

### Root Causes

#### 1. SSH Connection Issues

**Check SSH Secrets in GitHub:**
1. Go to: https://github.com/ripgtxgt/trading_dashboard/settings/secrets/actions
2. Verify these secrets exist:
   - `SERVER_HOST`: 13.113.194.218
   - `SERVER_USER`: Your Windows username
   - `SERVER_SSH_KEY`: Your private SSH key
   - `SERVER_PORT`: 22 (default)

**Test SSH Connection Manually:**
```bash
ssh -i your_private_key.pem username@13.113.194.218
```

#### 2. Server Path Issues

**Verify the deployment path exists:**
- Current path in workflow: `C:\trading_dashboard_fixed`
- If this path doesn't exist, create it or update `.github/workflows/deploy.yml`

**Check Git repository:**
```cmd
cd C:\trading_dashboard_fixed
git status
git remote -v
```

#### 3. PowerShell Execution Policy

**On Windows Server, run:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Quick Fix: Manual Deployment

Since GitHub Actions is not working, use manual deployment:

### Method 1: Run Manual Deploy Script (Recommended)

1. **On Windows Server**, navigate to project folder:
   ```cmd
   cd C:\trading_dashboard_fixed
   ```

2. **Double-click** `manual-deploy.bat` or run:
   ```cmd
   manual-deploy.bat
   ```

This will:
- Pull latest code from GitHub
- Run deploy-auto.ps1
- Install dependencies
- Build project
- Restart PM2 services
- Configure Nginx

### Method 2: Step-by-Step Manual Deployment

```cmd
cd C:\trading_dashboard_fixed

REM 1. Pull latest code
git pull origin main

REM 2. Install Node.js dependencies
pnpm install

REM 3. Install Python dependencies
pip install -r scripts\requirements.txt

REM 4. Build frontend
pnpm run build

REM 5. Copy build files
xcopy /E /Y dist\public\* server\_core\public\

REM 6. Restart PM2 services
pm2 stop all
pm2 delete all
pm2 start ecosystem.config.cjs
pm2 save

REM 7. Check status
pm2 list
```

## Fix GitHub Actions Deployment

### Option 1: Re-configure SSH Keys

1. **Generate new SSH key pair** (on your local machine):
   ```bash
   ssh-keygen -t rsa -b 4096 -f trading_dashboard_deploy_key
   ```

2. **Add public key to Windows Server:**
   - Copy content of `trading_dashboard_deploy_key.pub`
   - Add to `C:\Users\YourUsername\.ssh\authorized_keys`

3. **Update GitHub Secret:**
   - Go to: https://github.com/ripgtxgt/trading_dashboard/settings/secrets/actions
   - Update `SERVER_SSH_KEY` with content of `trading_dashboard_deploy_key` (private key)

### Option 2: Use GitHub Personal Access Token

Modify `.github/workflows/deploy.yml` to use HTTPS instead of SSH:

```yaml
- name: Deploy via PowerShell Remoting
  run: |
    # Use PowerShell remoting or WinRM instead of SSH
    # This requires setting up WinRM on Windows Server
```

### Option 3: Use Self-hosted Runner

1. **On Windows Server**, install GitHub Actions runner
2. Configure as self-hosted runner
3. Update workflow to use `runs-on: self-hosted`

## Verify Deployment Success

After deployment, check:

1. **File modification dates:**
   ```cmd
   dir C:\trading_dashboard_fixed
   ```
   Should show current date/time

2. **PM2 services:**
   ```cmd
   pm2 list
   ```
   All services should be "online"

3. **Access dashboard:**
   - http://localhost:3000
   - http://13.113.194.218:3000
   - http://cryptoalpha.vip (if Nginx configured)

## Current Workaround

Until GitHub Actions is fixed, use **manual-deploy.bat** after each code push:

1. Push code to GitHub (from development machine)
2. On Windows Server, run `manual-deploy.bat`
3. Verify deployment success

## Support

If issues persist:
1. Check GitHub Actions logs: https://github.com/ripgtxgt/trading_dashboard/actions
2. Check PM2 logs: `pm2 logs`
3. Check Nginx error log: `C:\nginx\logs\error.log`
