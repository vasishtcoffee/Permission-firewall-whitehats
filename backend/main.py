import joblib
import numpy as np
from datetime import datetime

# Load the trained model and encoder at startup (only once)
model = joblib.load('isolation_forest_model.pkl')
encoder = joblib.load('onehot_encoder.pkl')

def predict_anomaly(app_name, permission_type, hour):
    """
    Predicts if a permission event is anomalous
    Returns: 1 for anomaly, 0 for normal
    """
    try:
        # Create input data in the same format as training
        # Format: [[app_name, permission_type, hour]]
        input_data = np.array([[app_name, permission_type, hour]], dtype=object)
        
        # Transform categorical features using the loaded encoder
        # The encoder expects the first two columns (app_name, permission_type)
        categorical_features = input_data[:, :2]
        encoded_features = encoder.transform(categorical_features)
        
        # Combine encoded categorical features with numeric hour feature
        hour_feature = np.array([[hour]])
        final_features = np.hstack([encoded_features, hour_feature])
        
        # Predict: -1 means anomaly, 1 means normal in Isolation Forest
        prediction = model.predict(final_features)
        
        # Convert Isolation Forest output: -1 (anomaly) → 1, 1 (normal) → 0
        anomaly_flag = 1 if prediction[0] == -1 else 0
        
        return anomaly_flag
        
    except Exception as e:
        print(f"⚠️ Prediction error: {e}")
        return 0  # Default to normal if error occurs