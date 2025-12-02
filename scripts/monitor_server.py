#!/usr/bin/env python3
"""
Server Monitoring Script
Monitors CPU, memory, disk usage and PM2 process status
Sends Telegram alerts when thresholds are exceeded
"""

import os
import subprocess
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = 300  # 5 minutes

# Thresholds
CPU_THRESHOLD = 80  # %
MEMORY_THRESHOLD = 85  # %
DISK_THRESHOLD = 90  # %

class ServerMonitor:
    def __init__(self):
        self.last_alert_time = {}
        self.alert_cooldown = 1800  # 30 minutes cooldown between same alerts
        
    def send_telegram_alert(self, message):
        """Send alert via Telegram"""
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            print(f"Telegram not configured, alert: {message}")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"🚨 *Server Alert*\n\n{message}",
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send Telegram alert: {e}")
            return False
    
    def should_send_alert(self, alert_key):
        """Check if enough time has passed since last alert"""
        now = time.time()
        last_time = self.last_alert_time.get(alert_key, 0)
        if now - last_time > self.alert_cooldown:
            self.last_alert_time[alert_key] = now
            return True
        return False
    
    def get_cpu_usage(self):
        """Get CPU usage percentage"""
        try:
            output = subprocess.check_output(
                "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1",
                shell=True
            ).decode().strip()
            return float(output)
        except:
            return 0.0
    
    def get_memory_usage(self):
        """Get memory usage percentage"""
        try:
            output = subprocess.check_output(
                "free | grep Mem | awk '{printf \"%.1f\", $3/$2 * 100.0}'",
                shell=True
            ).decode().strip()
            return float(output)
        except:
            return 0.0
    
    def get_disk_usage(self):
        """Get disk usage percentage"""
        try:
            output = subprocess.check_output(
                "df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1",
                shell=True
            ).decode().strip()
            return float(output)
        except:
            return 0.0
    
    def get_pm2_status(self):
        """Get PM2 process status"""
        try:
            output = subprocess.check_output(
                "pm2 jlist",
                shell=True
            ).decode()
            processes = json.loads(output)
            
            status = {
                'total': len(processes),
                'online': 0,
                'errored': 0,
                'stopped': 0,
                'errored_processes': []
            }
            
            for proc in processes:
                pm2_env = proc.get('pm2_env', {})
                proc_status = pm2_env.get('status', 'unknown')
                
                if proc_status == 'online':
                    status['online'] += 1
                elif proc_status in ['errored', 'error']:
                    status['errored'] += 1
                    status['errored_processes'].append(proc.get('name', 'unknown'))
                elif proc_status == 'stopped':
                    status['stopped'] += 1
            
            return status
        except Exception as e:
            print(f"Failed to get PM2 status: {e}")
            return None
    
    def check_system_resources(self):
        """Check system resources and send alerts if needed"""
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        
        alerts = []
        
        if cpu > CPU_THRESHOLD and self.should_send_alert('cpu'):
            alerts.append(f"⚠️ High CPU usage: {cpu:.1f}%")
        
        if memory > MEMORY_THRESHOLD and self.should_send_alert('memory'):
            alerts.append(f"⚠️ High memory usage: {memory:.1f}%")
        
        if disk > DISK_THRESHOLD and self.should_send_alert('disk'):
            alerts.append(f"⚠️ High disk usage: {disk:.1f}%")
        
        if alerts:
            message = "\n".join(alerts)
            message += f"\n\n*Server:* cryptoalpha.vip\n*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.send_telegram_alert(message)
        
        return {
            'cpu': cpu,
            'memory': memory,
            'disk': disk,
            'alerts': len(alerts) > 0
        }
    
    def check_pm2_processes(self):
        """Check PM2 processes and send alerts if needed"""
        status = self.get_pm2_status()
        
        if not status:
            return None
        
        if status['errored'] > 0 and self.should_send_alert('pm2_errored'):
            message = f"⚠️ PM2 Process Errors\n\n"
            message += f"Errored processes: {status['errored']}\n"
            message += f"Process names: {', '.join(status['errored_processes'])}\n\n"
            message += f"*Server:* cryptoalpha.vip\n"
            message += f"*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            message += f"Check logs: `pm2 logs`"
            self.send_telegram_alert(message)
        
        return status
    
    def run_once(self):
        """Run monitoring checks once"""
        print(f"\n{'='*60}")
        print(f"Server Monitoring - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Check system resources
        resources = self.check_system_resources()
        print(f"\nSystem Resources:")
        print(f"  CPU: {resources['cpu']:.1f}%")
        print(f"  Memory: {resources['memory']:.1f}%")
        print(f"  Disk: {resources['disk']:.1f}%")
        
        # Check PM2 processes
        pm2_status = self.check_pm2_processes()
        if pm2_status:
            print(f"\nPM2 Processes:")
            print(f"  Total: {pm2_status['total']}")
            print(f"  Online: {pm2_status['online']}")
            print(f"  Errored: {pm2_status['errored']}")
            print(f"  Stopped: {pm2_status['stopped']}")
            
            if pm2_status['errored_processes']:
                print(f"  Errored processes: {', '.join(pm2_status['errored_processes'])}")
        
        print(f"\n{'='*60}\n")
    
    def run_loop(self):
        """Run monitoring loop"""
        print(f"Server Monitoring Started")
        print(f"Check interval: {CHECK_INTERVAL} seconds")
        print(f"Thresholds: CPU={CPU_THRESHOLD}%, Memory={MEMORY_THRESHOLD}%, Disk={DISK_THRESHOLD}%")
        
        while True:
            try:
                self.run_once()
                time.sleep(CHECK_INTERVAL)
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    monitor = ServerMonitor()
    
    # Check if running in one-shot mode
    if len(os.sys.argv) > 1 and os.sys.argv[1] == '--once':
        monitor.run_once()
    else:
        monitor.run_loop()
