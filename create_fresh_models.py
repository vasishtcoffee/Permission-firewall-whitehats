# create_fresh_models.py - Create models with proper class

from sklearn.ensemble import IsolationForest
import pickle
import numpy as np
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Import SimpleEncoder from main
print("🔍 Importing SimpleEncoder from main.py...")
from main import SimpleEncoder

print("🤖 Creating ML models...")

# Train Isolation Forest
np.random.seed(42)
X = np.random.rand(1000, 5)
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(X)
print("✅ Isolation Forest trained")

# Create encoder
encoder = SimpleEncoder()
print("✅ SimpleEncoder created")

# Save models
with open('isolation_forest_model.pkl', 'wb') as f:
    pickle.dump(model, f)
print("💾 Saved: isolation_forest_model.pkl")

with open('onehot_encoder.pkl', 'wb') as f:
    pickle.dump(encoder, f)
print("💾 Saved: onehot_encoder.pkl")

print("\n✅ SUCCESS! Models created.")
print("🚀 Now restart: python -m uvicorn main:app --reload --port 8000")
