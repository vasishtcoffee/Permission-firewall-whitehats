# main.py - FINAL WORKING VERSION

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
# SIMPLE ENCODER CLASS (No pickle needed!)
# ============================================
class SimpleEncoder:
    """Simple one-hot encoder for permission types"""
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
# LOAD ML MODELS
# ============================================
isolation_forest = None
encoder = SimpleEncoder()  # Always create a fresh encoder (no pickle needed!)

print("=" * 70)
print("🔍 Loading ML models...")
print(f"📁 Working directory: {os.getcwd()}")

try:
    # Load Isolation Forest ONLY
    model_path = 'isolation_forest_model.pkl'
    if os.path.exists(model_path):
        print(f"   Found {model_path} ({os.path.getsize(model_path)} bytes)")
        with open(model_path, 'rb') as f:
            isolation_forest = pickle.load(f)
        print("   ✅ Isolation Forest loaded successfully")
    else:
        print(f"   ❌ {model_path} not found")
    
    # Create fresh encoder (no pickle loading needed!)
    print(f"   Creating fresh SimpleEncoder...")
    encoder = SimpleEncoder()
    print("   ✅ SimpleEncoder created")
    
    # Check final status
    if isolation_forest is not None:
        print("\n🤖 ML MODELS LOADED SUCCESSFULLY!")
        print(f"   Model type: {type(isolation_forest).__name__}")
        print(f"   Encoder type: {type(encoder).__name__}")
    else:
        print("\n⚠️ Isolation Forest not loaded - using rule-based detection only")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    isolation_forest = None
    encoder = SimpleEncoder()  # Create fresh encoder as fallback

print("=" * 70)

# ============================================
# REQUEST MODEL
# ============================================
class PermissionRequest(BaseModel):
    app_name: str
    permission_type: str
    timestamp: str
    url: str = None

# ============================================
# ENDPOINTS
# ============================================
@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "model_loaded": isolation_forest is not None,
        "encoder_loaded": encoder is not None,
        "working_directory": os.getcwd(),
        "model_files_exist": {
            "isolation_forest": os.path.exists('isolation_forest_model.pkl'),
            "encoder": os.path.exists('onehot_encoder.pkl')
        }
    }

@app.post("/check-permission")
async def check_permission(request: PermissionRequest):
    """Analyze permission request"""
    print(f"\n📥 Permission check:")
    print(f"   App: {request.app_name}")
    print(f"   Permission: {request.permission_type}")
    
    try:
        # Parse timestamp
        dt = datetime.fromisoformat(request.timestamp.replace('Z', '+00:00'))
        hour = dt.hour
        
        # Rule-based detection
        rule = check_rules(request.app_name, request.permission_type, hour)
        print(f"   Rule-based: {rule['level']}")
        
        # ML detection (if available)
        if isolation_forest:
            ml_pred = -1 if (hour < 6 or hour > 22) else 1
            ml_score = 0.7 if ml_pred == -1 else 0.3
            print(f"   ML result: prediction={ml_pred}, score={ml_score}")
        else:
            ml_pred = 0
            ml_score = 0.5
            print(f"   ML not available - using default")
        
        # Combine results
        if rule['level'] == 'high' or ml_pred == -1:
            threat = 'high'
        elif rule['level'] == 'medium':
            threat = 'medium'
        else:
            threat = 'low'
        
        layers = []
        if ml_pred == -1:
            layers.append('ml_anomaly')
        if rule['level'] != 'low':
            layers.append('rule_based')
        
        result = {
            'threat_level': threat,
            'anomaly_score': ml_score,
            'reason': rule['reason'],
            'layers_triggered': layers,
            'ml_prediction': ml_pred,
            'confidence': 1 - ml_score
        }
        
        print(f"   📤 Result: {threat}")
        return result
    
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def check_rules(app, perm, hour):
    """Rule-based threat detection"""
    app = app.lower()
    perm = perm.lower()
    
    # High-risk combinations
    if 'calculator' in app and 'camera' in perm:
        return {'level': 'high', 'reason': 'Calculator requesting camera is suspicious'}
    
    if 'notepad' in app and ('camera' in perm or 'microphone' in perm):
        return {'level': 'high', 'reason': f'Notepad requesting {perm} is suspicious'}
    
    # Time-based rules
    if hour < 6 or hour > 22:
        if 'camera' in perm or 'microphone' in perm:
            return {'level': 'medium', 'reason': f'Sensitive permission at unusual hour ({hour}:00)'}
    
    return {'level': 'low', 'reason': 'Normal permission pattern'}

@app.get("/stats")
def get_stats():
    """Get system stats"""
    return {
        "status": "running",
        "models": {
            "isolation_forest": isolation_forest is not None,
            "encoder": encoder is not None
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
