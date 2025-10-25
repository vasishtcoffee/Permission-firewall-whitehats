# recreate_models.py - Create fresh models

from sklearn.ensemble import IsolationForest
import pickle
import numpy as np

print("🤖 Creating fresh ML models...")

# SimpleEncoder definition (same as in main.py)
class SimpleEncoder:
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

# Train Isolation Forest
print("  Training Isolation Forest...")
np.random.seed(42)
X = np.random.rand(1000, 5)
model = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
model.fit(X)
print("  ✅ Trained")

# Create encoder
print("  Creating SimpleEncoder...")
encoder = SimpleEncoder()
print("  ✅ Created")

# Save with protocol 3 (compatible)
print("  Saving models...")
with open('isolation_forest_model.pkl', 'wb') as f:
    pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)
print("  ✅ Saved: isolation_forest_model.pkl")

with open('onehot_encoder.pkl', 'wb') as f:
    pickle.dump(encoder, f, protocol=pickle.HIGHEST_PROTOCOL)
print("  ✅ Saved: onehot_encoder.pkl")

print("\n✅ SUCCESS! Fresh models created.")
print("🚀 Now run: python -m uvicorn main:app --reload --port 8000")
