# quick_fix_models.py

from sklearn.ensemble import IsolationForest
import pickle
import numpy as np

print("🤖 Creating ML models...")

# Train model
np.random.seed(42)
X = np.random.rand(1000, 5)
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X)
print("✅ Model trained")

# Create encoder (must match main.py)
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

encoder = SimpleEncoder()
print("✅ Encoder created")

# Save
with open('isolation_forest_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('onehot_encoder.pkl', 'wb') as f:
    pickle.dump(encoder, f)

print("💾 Models saved!")
