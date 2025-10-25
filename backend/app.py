from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime
import os
import joblib
import numpy as np

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'permission_events.csv')

# === ML Model additions ===
MODEL_PATH = os.path.join(BASE_DIR, 'isolation_forest_dns_public.pkl')
DNS_FEATURES = ['Entropy', 'DomainLength', 'StrangeCharacters', 'SpecialCharRatio']
model = joblib.load(MODEL_PATH)

def detect_dns_anomaly(event: dict):
    """
    event: dict with keys: 'Entropy', 'DomainLength', 'StrangeCharacters', 'SpecialCharRatio'
    """
    arr = np.array([[event[f] for f in DNS_FEATURES]])
    pred = model.predict(arr)[0]
    score = float(model.decision_function(arr)[0])
    is_anomaly = (pred == -1)
    return {'is_anomaly': is_anomaly, 'anomaly_score': score}

# ==========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Privacy Firewall API Running", "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

@app.get("/events")
def get_events(limit: int = 50):
    try:
        df = pd.read_csv(CSV_FILE)
        recent = df.tail(limit)
        return {
            "success": True,
            "count": len(recent),
            "events": recent.to_dict('records')
        }
    except Exception as e:
        return {"success": False, "error": str(e), "events": []}

@app.get("/events/dashboard")
def get_dashboard_events(limit: int = 50):
    try:
        df = pd.read_csv(CSV_FILE)
        important = df[df['threat_level'].isin(['CRITICAL', 'HIGH', 'MEDIUM'])]
        noise_apps = ['svchost.exe', 'System', 'Registry', 'dwm.exe', 'RuntimeBroker.exe']
        clean = important[~important['app_name'].isin(noise_apps)]
        recent = clean.tail(limit)
        return {
            "success": True,
            "count": len(recent),
            "total_in_db": len(df),
            "events": recent.to_dict('records')
        }
    except Exception as e:
        return {"success": False, "error": str(e), "events": []}

@app.get("/stats")
def get_stats():
    try:
        df = pd.read_csv(CSV_FILE)
        return {
            "success": True,
            "total": len(df),
            "critical": int(len(df[df['threat_level'] == 'CRITICAL'])),
            "high": int(len(df[df['threat_level'] == 'HIGH'])),
            "medium": int(len(df[df['threat_level'] == 'MEDIUM'])),
            "low": int(len(df[df['threat_level'] == 'LOW']))
        }
    except Exception as e:
        return {"success": False, "error": str(e), "total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}

@app.get("/threats")
def get_threats():
    try:
        df = pd.read_csv(CSV_FILE)
        threats = df[df['threat_level'].isin(['CRITICAL', 'HIGH'])]
        return {
            "success": True,
            "count": len(threats),
            "threats": threats.to_dict('records')
        }
    except Exception as e:
        return {"success": False, "error": str(e), "threats": []}

@app.get("/apps/simple")
def get_simple_apps():
    """Simple grouped view - one app per row"""
    try:
        df = pd.read_csv(CSV_FILE)
        threats = df[df['threat_level'].isin(['CRITICAL', 'HIGH', 'MEDIUM'])]

        if len(threats) == 0:
            return {"success": True, "apps": []}

        apps = []
        threat_levels = {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1}
        for app_name in threats['app_name'].unique():
            app_events = threats[threats['app_name'] == app_name]
            permissions = sorted(app_events['permission_type'].unique().tolist())
            max_threat = max(app_events['threat_level'], key=lambda x: threat_levels.get(x, 0))

            apps.append({
                'name': app_name,
                'permissions': permissions,
                'threat_level': max_threat
            })

        apps.sort(key=lambda x: threat_levels.get(x['threat_level'], 0), reverse=True)
        return {"success": True, "apps": apps}
    except Exception as e:
        return {"success": False, "error": str(e), "apps": []}

# === ML API endpoint for DNS scoring ===
@app.post("/api/check_dns")
async def api_check_dns(event: dict):
    """
    Accept JSON: {"Entropy": float, "DomainLength": int, "StrangeCharacters": int, "SpecialCharRatio": float}
    """
    result = detect_dns_anomaly(event)
    return result

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Privacy Firewall API on http://localhost:8000")
    print(f"📁 Looking for CSV at: {CSV_FILE}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
