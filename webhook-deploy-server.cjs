/**
 * GitHub Webhook Auto-Deployment Server
 * 
 * This server listens for GitHub push events and automatically
 * pulls latest code and runs deployment script.
 * 
 * Setup:
 * 1. Run this on Windows Server: node webhook-deploy-server.js
 * 2. Configure GitHub webhook to point to: http://your-server:9000/webhook
 * 3. Set webhook secret in GitHub (optional but recommended)
 */

const http = require('http');
const crypto = require('crypto');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const PORT = 9000;
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'your-webhook-secret-here';
const PROJECT_PATH = process.env.PROJECT_PATH || '/home/ubuntu/trading_dashboard';
const LOG_FILE = path.join(PROJECT_PATH, 'webhook-deploy.log');
const DEPLOY_HISTORY_FILE = path.join(PROJECT_PATH, 'deploy-history.json');

// Logging function
function log(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  console.log(logMessage.trim());
  fs.appendFileSync(LOG_FILE, logMessage);
}

// Save deployment history
function saveDeploymentHistory(commitInfo, status, duration) {
  try {
    let history = [];
    if (fs.existsSync(DEPLOY_HISTORY_FILE)) {
      history = JSON.parse(fs.readFileSync(DEPLOY_HISTORY_FILE, 'utf8'));
    }
    
    history.unshift({
      timestamp: new Date().toISOString(),
      commit: commitInfo.sha || commitInfo.after,
      message: commitInfo.message,
      author: commitInfo.author,
      status: status,
      duration: duration
    });
    
    // Keep only last 50 deployments
    if (history.length > 50) {
      history = history.slice(0, 50);
    }
    
    fs.writeFileSync(DEPLOY_HISTORY_FILE, JSON.stringify(history, null, 2));
    log(`Deployment history saved: ${status}`);
  } catch (error) {
    log(`Failed to save deployment history: ${error.message}`);
  }
}

// Get deployment history
function getDeploymentHistory() {
  try {
    if (fs.existsSync(DEPLOY_HISTORY_FILE)) {
      return JSON.parse(fs.readFileSync(DEPLOY_HISTORY_FILE, 'utf8'));
    }
  } catch (error) {
    log(`Failed to read deployment history: ${error.message}`);
  }
  return [];
}

// Verify GitHub webhook signature
function verifySignature(payload, signature) {
  if (!signature) {
    return false;
  }
  
  const hmac = crypto.createHmac('sha256', WEBHOOK_SECRET);
  const digest = 'sha256=' + hmac.update(payload).digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(digest)
  );
}

// Check and start Nginx if not running
function checkAndStartNginx() {
  return new Promise((resolve) => {
    log('Checking Nginx status...');
    
    // Check if Nginx is running
    exec('systemctl is-active nginx', (error, stdout) => {
      const nginxRunning = stdout.trim() === 'active';
      
      if (nginxRunning) {
        log('Nginx is already running');
        resolve(true);
      } else {
        log('Nginx is not running, attempting to start...');
        
        // Try to start Nginx
        const nginxPath = '/etc/nginx';
        exec(`sudo systemctl start nginx`, (startError) => {
          if (startError) {
            log(`Failed to start Nginx: ${startError.message}`);
            resolve(false);
          } else {
            log('Nginx started successfully');
            resolve(true);
          }
        });
      }
    });
  });
}

// Execute deployment
function deploy() {
  return new Promise((resolve, reject) => {
    log('Starting deployment...');
    
    const deployScript = path.join(PROJECT_PATH, 'deploy-auto.sh');
    const command = `cd ${PROJECT_PATH} && git pull origin main && bash "${deployScript}"`;
    
    exec(command, { cwd: PROJECT_PATH, maxBuffer: 1024 * 1024 * 10 }, async (error, stdout, stderr) => {
      if (error) {
        log(`Deployment error: ${error.message}`);
        reject(error);
        return;
      }
      
      if (stderr) {
        log(`Deployment stderr: ${stderr}`);
      }
      
      log(`Deployment stdout: ${stdout}`);
      
      // Check and start Nginx after deployment
      await checkAndStartNginx();
      
      log('Deployment completed successfully!');
      resolve(stdout);
    });
  });
}

// HTTP server
const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/webhook') {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', async () => {
      try {
        // Verify signature
        const signature = req.headers['x-hub-signature-256'];
        if (WEBHOOK_SECRET !== 'your-webhook-secret-here' && !verifySignature(body, signature)) {
          log('Invalid webhook signature');
          res.writeHead(401);
          res.end('Invalid signature');
          return;
        }
        
        // Parse payload
        const payload = JSON.parse(body);
        const event = req.headers['x-github-event'];
        
        log(`Received GitHub event: ${event}`);
        log(`Repository: ${payload.repository?.full_name}`);
        log(`Branch: ${payload.ref}`);
        log(`Commit: ${payload.after}`);
        log(`Pusher: ${payload.pusher?.name}`);
        
        // Only deploy on push to main branch
        if (event === 'push' && payload.ref === 'refs/heads/main') {
          log('Push to main branch detected, starting deployment...');
          
          const startTime = Date.now();
          const commitInfo = {
            sha: payload.after,
            message: payload.head_commit?.message || 'No message',
            author: payload.pusher?.name || 'Unknown'
          };
          
          try {
            await deploy();
            const duration = Math.round((Date.now() - startTime) / 1000);
            saveDeploymentHistory(commitInfo, 'success', duration);
            
            res.writeHead(200);
            res.end('Deployment triggered successfully');
          } catch (error) {
            const duration = Math.round((Date.now() - startTime) / 1000);
            saveDeploymentHistory(commitInfo, 'failed', duration);
            
            log(`Deployment failed: ${error.message}`);
            res.writeHead(500);
            res.end('Deployment failed');
          }
        } else {
          log('Not a push to main branch, skipping deployment');
          res.writeHead(200);
          res.end('Event received but no deployment triggered');
        }
      } catch (error) {
        log(`Error processing webhook: ${error.message}`);
        res.writeHead(400);
        res.end('Bad request');
      }
    });
  } else if (req.method === 'GET' && req.url === '/history') {
    // Deployment history endpoint
    res.writeHead(200, { 'Content-Type': 'application/json' });
    const history = getDeploymentHistory();
    res.end(JSON.stringify(history, null, 2));
  } else if (req.method === 'GET' && req.url === '/') {
    // Health check endpoint
    res.writeHead(200, { 'Content-Type': 'text/html' });
    res.end(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Webhook Deploy Server</title>
        <style>
          body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
          h1 { color: #333; }
          .status { padding: 10px; background: #e8f5e9; border-left: 4px solid #4caf50; margin: 20px 0; }
          .info { background: #e3f2fd; border-left-color: #2196f3; }
          code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; }
        </style>
      </head>
      <body>
        <h1>🚀 Webhook Deploy Server</h1>
        <div class="status">
          <strong>Status:</strong> Server is running
        </div>
        <div class="info">
          <strong>Webhook URL:</strong> <code>http://your-server:${PORT}/webhook</code>
        </div>
        <h2>Setup Instructions:</h2>
        <ol>
          <li>Go to GitHub repository settings</li>
          <li>Navigate to Webhooks → Add webhook</li>
          <li>Set Payload URL to: <code>http://your-server-ip:${PORT}/webhook</code></li>
          <li>Set Content type to: <code>application/json</code></li>
          <li>Set Secret to your webhook secret (optional)</li>
          <li>Select "Just the push event"</li>
          <li>Click "Add webhook"</li>
        </ol>
        <h2>Recent Logs:</h2>
        <pre>${getRecentLogs()}</pre>
      </body>
      </html>
    `);
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

// Get recent logs
function getRecentLogs() {
  try {
    if (fs.existsSync(LOG_FILE)) {
      const logs = fs.readFileSync(LOG_FILE, 'utf8');
      const lines = logs.split('\n').slice(-20); // Last 20 lines
      return lines.join('\n');
    }
    return 'No logs yet';
  } catch (error) {
    return `Error reading logs: ${error.message}`;
  }
}

// Start server
server.listen(PORT, () => {
  log(`Webhook deployment server started on port ${PORT}`);
  log(`Webhook URL: http://localhost:${PORT}/webhook`);
  log(`Project path: ${PROJECT_PATH}`);
  log(`Waiting for GitHub push events...`);
  
  // Check Nginx status on startup
  checkAndStartNginx().then((running) => {
    if (running) {
      log('Initial Nginx check: Running');
    } else {
      log('Initial Nginx check: Failed to start');
    }
  });
});

// Handle errors
server.on('error', (error) => {
  log(`Server error: ${error.message}`);
  process.exit(1);
});

// Graceful shutdown
process.on('SIGINT', () => {
  log('Shutting down webhook server...');
  server.close(() => {
    log('Server stopped');
    process.exit(0);
  });
});
