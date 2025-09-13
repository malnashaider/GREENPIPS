# scripts/model.py
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def build_model():
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42))
    ])
    return pipe

def save_model(model, path: str):
    joblib.dump(model, path)

def load_model(path: str):
    return joblib.load(path)
