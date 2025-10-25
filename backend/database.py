# database.py
import csv
import psutil
from datetime import datetime
import random
import time
import os
from main import hybrid_threat_detection

# CSV setup with NEW headers for hybrid system
csv_file = 'permission_events.csv'
headers = ['timestamp', 'app_name', 'permission_type', 'threat_level', 'reason', 'layers_triggered', 'hour']

# Create CSV with headers if it doesn't exist
if not os.path.isfile(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

# Apps and permissions to monitor
apps = ['Zoom', 'Chrome', 'Teams', 'Discord', 'Calculator', 'Notepad', 'cmd']
permissions = ['camera', 'microphone', 'location', 'storage']

print("🔒 Privacy Firewall Started")

while True:
    for proc in psutil.process_iter(['name']):
        try:
            app_name = proc.info['name']
            if any(app.lower() in app_name.lower() for app in apps):
                permission = random.choice(permissions)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                hour = datetime.now().hour
                
                # Use hybrid detection (returns: threat_level, reason, layers_triggered)
                threat_level, reason, layers = hybrid_threat_detection(app_name, permission, hour)
                
                # Log to CSV
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        timestamp,
                        app_name,
                        permission,
                        threat_level,
                        reason,
                        ','.join(layers),  # Convert list to string
                        hour
                    ])
                
                # Console output with color coding
                if threat_level == "CRITICAL":
                    print(f"🔴 [CRITICAL] {app_name} → {permission}")
                    print(f"   {reason}")
                    print(f"   Detected by: {', '.join(layers)}")
                elif threat_level == "HIGH":
                    print(f"🟠 [HIGH] {app_name} → {permission}")
                    print(f"   {reason}")
                    print(f"   Detected by: {', '.join(layers)}")
                elif threat_level == "MEDIUM":
                    print(f"🟡 [MEDIUM] {app_name} → {permission}")
                    print(f"   {reason}")
                    print(f"   Detected by: {', '.join(layers)}")
                else:
                    print(f"✅ [NORMAL] {app_name} → {permission}")
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    time.sleep(5)
