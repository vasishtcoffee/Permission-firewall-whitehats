import csv
import psutil
from datetime import datetime
import random
import time
import os
from main import predict_anomaly


# Define the CSV file and header
csv_file = 'permission_events.csv'
headers = ['timestamp', 'app_name', 'permission_type', 'anomaly_flag', 'hour']


# Create the CSV file with headers ONLY if it doesn't exist
if not os.path.isfile(csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)


# List of simulated sensitive apps and permissions
apps = ['Zoom', 'Chrome', 'Teams', 'Skype', 'Discord']
permissions = ['camera', 'microphone', 'location']


print("🔥 Privacy Firewall Started - Monitoring permissions...")


# Monitor and log events
while True:
    for proc in psutil.process_iter(['name']):
        try:
            app_name = proc.info['name']
            if any(app.lower() in app_name.lower() for app in apps):
                permission = random.choice(permissions)
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                hour = datetime.now().hour
                
                # GET PREDICTION FIRST before logging
                anomaly_flag = predict_anomaly(app_name, permission, hour)
                
                # Record event in CSV with the actual anomaly prediction
                with open(csv_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([timestamp, app_name, permission, anomaly_flag, hour])
                
                # Display result with color coding
                if anomaly_flag == 1:
                    print(f"🔴 [ANOMALY] {app_name} requested {permission} at {timestamp}")
                else:
                    print(f"✅ [NORMAL] {app_name} requested {permission} at {timestamp}")
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    time.sleep(5)  # Wait before next check
