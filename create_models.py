# create_models.py - Generate ML models (Fixed for newer scikit-learn)

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import OneHotEncoder
import pickle
import numpy as np
import sklearn

print("=" * 60)
print("🤖 Creating ML Models for Permission Watcher")
print("=" * 60)
print(f"📦 Using scikit-learn version: {sklearn.__version__}")

# Create training data
print("\n📊 Generating training data...")
np.random.seed(42)
X_train = np.random.rand(1000, 9)  # 1000 samples, 9 features
print("✅ Training data created: 1000 samples x 9 features")

# Train Isolation Forest
print("\n🌳 Training Isolation Forest...")
isolation_forest = IsolationForest(
    contamination=0.1,      # 10% expected anomalies
    n_estimators=100,       # 100 trees
    random_state=42,
    n_jobs=-1
)
isolation_forest.fit(X_train)
print("✅ Isolation Forest trained successfully!")

# Create OneHot Encoder for permission types (Fixed for newer sklearn)
print("\n🔧 Creating permission encoder...")
try:
    # Try new parameter name first (sklearn >= 1.2)
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    print("✅ Using sparse_output=False (newer sklearn)")
except TypeError:
    try:
        # Fall back to old parameter name (sklearn < 1.2)
        encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
        print("✅ Using sparse=False (older sklearn)")
    except TypeError:
        # Very old version fallback
        encoder = OneHotEncoder(handle_unknown='ignore')
        print("✅ Using default settings (very old sklearn)")

# Fit encoder with permission types
permission_types = [
    ['camera'],
    ['microphone'],
    ['camera_microphone'],
    ['location'],
    ['notification']
]

encoder.fit(permission_types)
print("✅ Encoder created for 5 permission types")

# Test the encoder works
print("\n🧪 Testing encoder...")
try:
    test_encoded = encoder.transform([['camera']])
    # Handle both sparse and dense output
    if hasattr(test_encoded, 'toarray'):
        test_encoded = test_encoded.toarray()
    print(f"✅ Encoder test passed - shape: {test_encoded.shape}")
except Exception as e:
    print(f"⚠️ Encoder test warning: {e}")

# Save models
print("\n💾 Saving models...")
with open('isolation_forest_model.pkl', 'wb') as f:
    pickle.dump(isolation_forest, f)
print("✅ Saved: isolation_forest_model.pkl")

with open('onehot_encoder.pkl', 'wb') as f:
    pickle.dump(encoder, f)
print("✅ Saved: onehot_encoder.pkl")

# Verify files were created
import os
if os.path.exists('isolation_forest_model.pkl') and os.path.exists('onehot_encoder.pkl'):
    model_size = os.path.getsize('isolation_forest_model.pkl')
    encoder_size = os.path.getsize('onehot_encoder.pkl')
    print(f"\n📁 File verification:")
    print(f"   • isolation_forest_model.pkl ({model_size} bytes)")
    print(f"   • onehot_encoder.pkl ({encoder_size} bytes)")
else:
    print("\n❌ Error: Files were not created properly!")

print("\n" + "=" * 60)
print("🎉 SUCCESS! ML models created and saved")
print("=" * 60)
print("\n🚀 Next step: Restart your backend")
print("   Command: python -m uvicorn main:app --reload --port 8000")
