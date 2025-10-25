import joblib
import numpy as np
import pandas as pd
from rules import rule_based_check

# Load your ML model (only once at startup)
model = joblib.load('isolation_forest_model.pkl')
encoder = joblib.load('onehot_encoder.pkl')

def predict_anomaly(app_name, permission, hour):
    """
    ML-based anomaly detection using Isolation Forest
    Returns: 1 for anomaly, 0 for normal
    """
    try:
        # Normalize inputs
        app_clean = app_name.lower().replace('.exe', '').strip()
        perm_clean = permission.lower().strip()
        
        # Create DataFrame for encoding (avoids sklearn warnings)
        X_new = pd.DataFrame([[app_clean, perm_clean]], 
                            columns=['app_name', 'permission_type'])
        
        # Encode categorical features
        X_encoded = encoder.transform(X_new)
        
        # Add hour feature
        X_final = np.hstack([X_encoded, [[hour]]])
        
        # Predict: -1 = anomaly, 1 = normal in Isolation Forest
        prediction = model.predict(X_final)[0]
        
        # Convert to our format: 1 = anomaly, 0 = normal
        return 1 if prediction == -1 else 0
        
    except Exception as e:
        print(f"⚠️ ML prediction error: {e}")
        return 0  # Default to normal if error

def hybrid_threat_detection(app_name, permission, hour):
    """
    Combines rule-based + ML detection
    Returns: (threat_level, reason, layers_triggered)
    """
    layers_triggered = []
    
    # Layer 1: Rule-based (check rules.py)
    rule_threat, rule_level, rule_reason = rule_based_check(app_name, permission, hour)
    if rule_threat:
        layers_triggered.append("Rule-Based")
        return rule_level, rule_reason, layers_triggered
    
    # Layer 2: ML-based
    ml_anomaly = predict_anomaly(app_name, permission, hour)
    if ml_anomaly == 1:
        layers_triggered.append("ML-Behavioral")
        return "MEDIUM", "Machine learning detected unusual behavior pattern", layers_triggered
    
    # Normal - no threats detected
    return "LOW", "Normal activity", []

# Test when run directly
if __name__ == "__main__":
    print("\n🧪 Testing Hybrid Threat Detection\n")
    print("=" * 60)
    
    test_cases = [
        ("calculator.exe", "camera", 14),      # Should trigger rule
        ("chrome.exe", "microphone", 3),       # Should trigger ML (late night)
        ("discord.exe", "microphone", 20),     # Should be normal
        ("notepad.exe", "microphone", 16),     # Should trigger rule
    ]
    
    for app, perm, hour in test_cases:
        level, reason, layers = hybrid_threat_detection(app, perm, hour)
        
        # Color code output
        if level == "CRITICAL":
            emoji = "🔴"
        elif level == "HIGH":
            emoji = "🟠"
        elif level == "MEDIUM":
            emoji = "🟡"
        else:
            emoji = "✅"
        
        print(f"{emoji} {app} + {perm} @ {hour}h")
        print(f"   Level: {level}")
        print(f"   Reason: {reason}")
        print(f"   Layers: {', '.join(layers) if layers else 'None'}")
        print()
