# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime

app = FastAPI()

# Enable CORS (allows frontend to call this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (frontend can connect)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Privacy Firewall API Running", "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

@app.get("/events")
def get_events(limit: int = 50):
    """Get recent permission events"""
    try:
        df = pd.read_csv('permission_events.csv')
        recent = df.tail(limit)
        return {
            "success": True,
            "count": len(recent),
            "events": recent.to_dict('records')
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "events": []
        }

@app.get("/stats")
def get_stats():
    """Get threat statistics"""
    try:
        df = pd.read_csv('permission_events.csv')
        return {
            "success": True,
            "total": len(df),
            "critical": int(len(df[df['threat_level'] == 'CRITICAL'])),
            "high": int(len(df[df['threat_level'] == 'HIGH'])),
            "medium": int(len(df[df['threat_level'] == 'MEDIUM'])),
            "low": int(len(df[df['threat_level'] == 'LOW']))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

@app.get("/threats")
def get_threats():
    """Get only threat events (CRITICAL and HIGH)"""
    try:
        df = pd.read_csv('permission_events.csv')
        threats = df[df['threat_level'].isin(['CRITICAL', 'HIGH'])]
        return {
            "success": True,
            "count": len(threats),
            "threats": threats.to_dict('records')
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "threats": []
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Privacy Firewall API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
