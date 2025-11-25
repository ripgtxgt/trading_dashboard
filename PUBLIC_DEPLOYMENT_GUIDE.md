# Public Network Deployment Guide

## Overview

This guide will help you deploy the Trading Dashboard to the public internet using your domain **cryptoalpha.vip** on Windows Server 2022.

**Server Information:**
- Domain: cryptoalpha.vip
- Public IP: 13.113.194.218
- Server OS: Windows Server 2022
- Dashboard Port: 3000 (localhost)
- Public Ports: 80 (HTTP), 443 (HTTPS)

---

## Prerequisites

Before starting, ensure you have:

1. ✅ Windows Server 2022 with Administrator access
2. ✅ Domain name (cryptoalpha.vip) registered
3. ✅ Access to domain DNS management
4. ✅ Trading Dashboard already running on localhost:3000
5. ✅ All PM2 services running (trading-dashboard, websocket-server, telegram-bot, trading-bot)

---

## Step 1: Configure DNS Records

### 1.1 Log in to Your Domain Registrar

Log in to your domain registrar's control panel (e.g., GoDaddy, Namecheap, Cloudflare, etc.)

### 1.2 Add A Record

Create an A record pointing your domain to your server's public IP:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 13.113.194.218 | 3600 |
| A | www | 13.113.194.218 | 3600 |

**Example for Cloudflare:**
```
Type: A
Name: @
IPv4 address: 13.113.194.218
Proxy status: DNS only (gray cloud)
TTL: Auto
```

**Example for GoDaddy:**
```
Type: A
Host: @
Points to: 13.113.194.218
TTL: 1 Hour
```

### 1.3 Verify DNS Propagation

Wait 5-30 minutes for DNS propagation, then verify:

**Method 1: Using nslookup (Windows CMD)**
```cmd
nslookup cryptoalpha.vip
```

Expected output:
```
Name:    cryptoalpha.vip
Address: 13.113.194.218
```

**Method 2: Online Tool**
Visit: https://dnschecker.org/#A/cryptoalpha.vip

---

## Step 2: Configure Windows Firewall

### 2.1 Open Firewall Ports

Open PowerShell as Administrator and run:

```powershell
# Allow HTTP (port 80)
New-NetFirewallRule -DisplayName "Allow HTTP" -Direction Inbound -LocalPort 80 -Protocol TCP -Action Allow

# Allow HTTPS (port 443)
New-NetFirewallRule -DisplayName "Allow HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
```

### 2.2 Verify Firewall Rules

```powershell
Get-NetFirewallRule -DisplayName "Allow HTTP"
Get-NetFirewallRule -DisplayName "Allow HTTPS"
```

### 2.3 Check Cloud Provider Security Groups

If your server is on AWS/Azure/Google Cloud, also configure security groups:

**AWS EC2 Security Group:**
- Type: HTTP, Protocol: TCP, Port: 80, Source: 0.0.0.0/0
- Type: HTTPS, Protocol: TCP, Port: 443, Source: 0.0.0.0/0

**Azure Network Security Group:**
- Add inbound rule for port 80 (HTTP)
- Add inbound rule for port 443 (HTTPS)

---

## Step 3: Install and Configure Nginx

### 3.1 Download Nginx for Windows

1. Visit: http://nginx.org/en/download.html
2. Download the latest stable version (e.g., nginx-1.24.0.zip)
3. Extract to `C:\nginx`

**Or use PowerShell:**
```powershell
# Download Nginx
$nginxUrl = "http://nginx.org/download/nginx-1.24.0.zip"
$zipFile = "$env:TEMP\nginx.zip"
Invoke-WebRequest -Uri $nginxUrl -OutFile $zipFile

# Extract to C:\nginx
Expand-Archive -Path $zipFile -DestinationPath "C:\" -Force
Rename-Item "C:\nginx-1.24.0" "C:\nginx"
Remove-Item $zipFile
```

### 3.2 Copy Nginx Configuration

Copy the provided `nginx_windows.conf` to `C:\nginx\conf\nginx.conf`:

```powershell
Copy-Item "nginx_windows.conf" "C:\nginx\conf\nginx.conf" -Force
```

### 3.3 Test Nginx Configuration

```cmd
cd C:\nginx
nginx -t
```

Expected output:
```
nginx: the configuration file C:\nginx/conf/nginx.conf syntax is ok
nginx: configuration file C:\nginx/conf/nginx.conf test is successful
```

---

## Step 4: Obtain SSL Certificate

### Option A: Automatic Certificate (Recommended)

Run the SSL setup script:

```powershell
cd C:\path\to\trading_dashboard
.\setup_ssl_windows.ps1
```

Follow the prompts to:
1. Download and install win-acme
2. Obtain Let's Encrypt certificate
3. Configure automatic renewal

### Option B: Manual Certificate

If you have your own SSL certificate:

1. Create SSL directory:
```powershell
New-Item -ItemType Directory -Force -Path "C:\nginx\ssl\cryptoalpha.vip"
```

2. Place your certificate files:
```
C:\nginx\ssl\cryptoalpha.vip\fullchain.pem
C:\nginx\ssl\cryptoalpha.vip\privkey.pem
```

### Option C: Self-Signed Certificate (Testing Only)

**⚠️ WARNING: Only for testing, browsers will show security warnings**

```powershell
# Create SSL directory
New-Item -ItemType Directory -Force -Path "C:\nginx\ssl\cryptoalpha.vip"

# Generate self-signed certificate (requires OpenSSL)
cd "C:\nginx\ssl\cryptoalpha.vip"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
    -keyout privkey.pem `
    -out fullchain.pem `
    -subj "/C=US/ST=State/L=City/O=Organization/CN=cryptoalpha.vip"
```

---

## Step 5: Start Nginx

### 5.1 Start Nginx Service

```cmd
cd C:\nginx
start nginx
```

### 5.2 Verify Nginx is Running

```powershell
# Check Nginx processes
Get-Process nginx

# Check port 80 and 443 are listening
netstat -ano | findstr ":80"
netstat -ano | findstr ":443"
```

### 5.3 Test HTTP Access

Open browser and visit:
- http://cryptoalpha.vip
- https://cryptoalpha.vip

You should see your Trading Dashboard!

---

## Step 6: Configure Nginx as Windows Service (Optional)

To make Nginx start automatically on boot:

### 6.1 Download NSSM (Non-Sucking Service Manager)

```powershell
# Download NSSM
$nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
$zipFile = "$env:TEMP\nssm.zip"
Invoke-WebRequest -Uri $nssmUrl -OutFile $zipFile

# Extract
Expand-Archive -Path $zipFile -DestinationPath "$env:TEMP\nssm" -Force
Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" "C:\nginx\nssm.exe"
```

### 6.2 Install Nginx as Service

```cmd
cd C:\nginx
nssm install nginx "C:\nginx\nginx.exe"
nssm set nginx AppDirectory "C:\nginx"
nssm set nginx DisplayName "Nginx Web Server"
nssm set nginx Description "Nginx reverse proxy for Trading Dashboard"
nssm set nginx Start SERVICE_AUTO_START
```

### 6.3 Start Nginx Service

```cmd
nssm start nginx
```

### 6.4 Verify Service Status

```powershell
Get-Service nginx
```

---

## Step 7: Update Dashboard Configuration

### 7.1 Update Environment Variables

Edit `.env` file and add:

```env
# Public URL
VITE_APP_URL=https://cryptoalpha.vip

# CORS settings (if needed)
CORS_ORIGIN=https://cryptoalpha.vip
```

### 7.2 Restart Dashboard Service

```cmd
pm2 restart trading-dashboard
```

---

## Troubleshooting

### Issue 1: Cannot Access Website

**Check DNS:**
```cmd
nslookup cryptoalpha.vip
```

**Check Firewall:**
```powershell
Get-NetFirewallRule -DisplayName "Allow HTTP"
Get-NetFirewallRule -DisplayName "Allow HTTPS"
```

**Check Nginx:**
```cmd
cd C:\nginx
nginx -t
```

**Check Dashboard:**
```cmd
pm2 status
pm2 logs trading-dashboard
```

### Issue 2: SSL Certificate Errors

**Verify certificate files exist:**
```powershell
Test-Path "C:\nginx\ssl\cryptoalpha.vip\fullchain.pem"
Test-Path "C:\nginx\ssl\cryptoalpha.vip\privkey.pem"
```

**Check certificate expiration:**
```powershell
openssl x509 -in "C:\nginx\ssl\cryptoalpha.vip\fullchain.pem" -noout -dates
```

### Issue 3: 502 Bad Gateway

This means Nginx cannot connect to the Dashboard backend.

**Check Dashboard is running:**
```cmd
pm2 status
curl http://localhost:3000
```

**Check Nginx error logs:**
```cmd
type C:\nginx\logs\error.log
```

### Issue 4: WebSocket Connection Failed

**Verify WebSocket proxy configuration in nginx.conf:**
```nginx
location /socket.io/ {
    proxy_pass http://localhost:3000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

**Restart Nginx:**
```cmd
cd C:\nginx
nginx -s reload
```

---

## Maintenance

### Reload Nginx Configuration

After editing `nginx.conf`:

```cmd
cd C:\nginx
nginx -s reload
```

### Stop Nginx

```cmd
cd C:\nginx
nginx -s stop
```

### View Nginx Logs

**Access log:**
```cmd
type C:\nginx\logs\access.log
```

**Error log:**
```cmd
type C:\nginx\logs\error.log
```

### Renew SSL Certificate

If using Let's Encrypt with win-acme, renewal is automatic.

To manually renew:
```cmd
cd "C:\Program Files\win-acme"
wacs.exe --renew
```

---

## Security Recommendations

### 1. Enable HTTPS Only

After SSL is working, force HTTPS by keeping the HTTP→HTTPS redirect in nginx.conf:

```nginx
server {
    listen 80;
    server_name cryptoalpha.vip www.cryptoalpha.vip;
    return 301 https://$server_name$request_uri;
}
```

### 2. Configure Firewall Rules

Only allow necessary ports:
- Port 80 (HTTP) - for Let's Encrypt validation and HTTPS redirect
- Port 443 (HTTPS) - for secure access
- Port 22 or 3389 (SSH/RDP) - for remote management (restrict to your IP)

### 3. Regular Updates

- Keep Windows Server updated
- Update Nginx regularly
- Renew SSL certificates before expiration
- Update Dashboard dependencies

### 4. Monitor Logs

Regularly check:
- Nginx access/error logs
- PM2 logs (`pm2 logs`)
- Windows Event Viewer

### 5. Backup Configuration

Backup these files regularly:
- `C:\nginx\conf\nginx.conf`
- `.env` file
- SSL certificates
- Database backups

---

## Quick Reference Commands

### Nginx Commands
```cmd
# Start Nginx
cd C:\nginx && nginx

# Stop Nginx
cd C:\nginx && nginx -s stop

# Reload configuration
cd C:\nginx && nginx -s reload

# Test configuration
cd C:\nginx && nginx -t
```

### PM2 Commands
```cmd
# Check status
pm2 status

# Restart Dashboard
pm2 restart trading-dashboard

# View logs
pm2 logs trading-dashboard
```

### Firewall Commands
```powershell
# List firewall rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*HTTP*"}

# Enable rule
Enable-NetFirewallRule -DisplayName "Allow HTTP"

# Disable rule
Disable-NetFirewallRule -DisplayName "Allow HTTP"
```

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Nginx error logs: `C:\nginx\logs\error.log`
3. Review PM2 logs: `pm2 logs`
4. Check Windows Event Viewer for system errors

---

## Summary

After completing all steps, your Trading Dashboard will be:

✅ Accessible at https://cryptoalpha.vip
✅ Secured with SSL/TLS certificate
✅ Protected by firewall rules
✅ Running behind Nginx reverse proxy
✅ Supporting WebSocket connections
✅ Automatically starting on server boot

**Test your deployment:**
1. Visit https://cryptoalpha.vip in your browser
2. Verify SSL certificate is valid (green padlock)
3. Check all Dashboard features work correctly
4. Test WebSocket real-time updates
5. Verify Telegram notifications work

Congratulations! Your Trading Dashboard is now publicly accessible! 🎉
