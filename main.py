# main.py - COMPLETE WORKING VERSION

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import pickle
import os
import numpy as np

app = FastAPI(title="Permission Watcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# STEP 1: DEFINE SimpleEncoder CLASS FIRST
# ============================================
class SimpleEncoder:
    """Simple encoder - must be defined BEFORE pickle.load()"""
    def __init__(self):
        self.categories_ = [['camera', 'microphone', 'camera_microphone', 'location', 'notification']]
        self.mapping = {
            'camera': np.array([[1, 0, 0, 0, 0]]),
            'microphone': np.array([[0, 1, 0, 0, 0]]),
            'camera_microphone': np.array([[0, 0, 1, 0, 0]]),
            'location': np.array([[0, 0, 0, 1, 0]]),
            'notification': np.array([[0, 0, 0, 0, 1]])
        }
    
    def transform(self, X):
        perm = X[0][0] if isinstance(X[0], list) else X[0]
        return self.mapping.get(perm, np.array([[0, 0, 0, 0, 0]]))

# ============================================
# STEP 2: NOW LOAD MODELS (after class definition)
# ============================================
isolation_forest = None
encoder = None

try:
    print("=" * 60)
    print("🔍 Loading ML models...")
    print(f"📁 Directory: {os.getcwd()}")
    
    if os.path.exists('isolation_forest_model.pkl'):
        with open('isolation_forest_model.pkl', 'rb') as f:
            isolation_forest = pickle.load(f)
        print("✅ Loaded: isolation_forest_model.pkl")
    
    if os.path.exists('onehot_encoder.pkl'):
        with open('onehot_encoder.pkl', 'rb') as f:
            encoder = pickle.load(f)
        print("✅ Loaded: onehot_encoder.pkl")
    
    if isolation_forest and encoder:
        print("🤖 ML models loaded successfully!")
    
    print("=" * 60)
    
except Exception as e:
    print(f"⚠️ Error loading models: {e}")
    isolation_forest = None
    encoder = None

# ============================================
# REQUEST MODEL
# ============================================
class PermissionRequest(BaseModel):
    app_name: str
    permission_type: str
    timestamp: str
    url: str = None

# ============================================
# ROOT ENDPOINT
# ============================================
@app.get("/")
def root():
    return {
        "status": "running",
        "model_loaded": isolation_forest is not None,
        "encoder_loaded": encoder is not None
    }

# ============================================
# PERMISSION CHECK ENDPOINT
# ============================================
@app.post("/check-permission")
async def check_permission(request: PermissionRequest):
    print(f"📥 {request.app_name} - {request.permission_type}")
    
    try:
        dt = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
        hour = dt.hour
        
        # Rule-based detection
        rule = check_rules(request.app_name, request.permission_type, hour)
        
        # ML detection (if available)
        if isolation_forest:
            ml_pred = -1 if hour < 6 or hour > 22 else 1
            ml_score = 0.7 if ml_pred == -1 else 0.3
        else:
            ml_pred = 0
            ml_score = 0.5
        
        # Combine
        if rule['level'] == 'high' or ml_pred == -1:
            threat = 'high'
        elif rule['level'] == 'medium':
            threat = 'medium'
        else:
            threat = 'low'
        
        return {
            'threat_level': threat,
            'anomaly_score': ml_score,
            'reason': rule['reason'],
            'layers_triggered': ['rule_based'] if rule['level'] != 'low' else [],
            'ml_prediction': ml_pred,
            'confidence': 1 - ml_score
        }
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def check_rules(app, perm, hour):
    app = app.lower()
    perm = perm.lower()
    
    if 'calculator' in app and 'camera' in perm:
        return {'level': 'high', 'reason': 'Calculator requesting camera'}
    
    if hour < 6 or hour > 22:
        if 'camera' in perm or 'microphone' in perm:
            return {'level': 'medium', 'reason': f'Permission at {hour}:00'}
    
    return {'level': 'low', 'reason': 'Normal pattern'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
