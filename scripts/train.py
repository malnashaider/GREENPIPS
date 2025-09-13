# scripts/train.py
import argparse
import os
import yaml
from scripts.data_fetch import fetch_ohlcv
from scripts.features import build_features_and_labels
from scripts.model import build_model, save_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def main(config_path):
    cfg = yaml.safe_load(open(config_path))
    sym = cfg.get("symbol", "AAPL")
    interval = cfg.get("interval", "15m")
    days = cfg.get("history_days", 365)
    model_path = cfg.get("model_path", "models/rf_model.pkl")
    os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)

    print("Fetching data...", sym, interval)
    df = fetch_ohlcv(sym, interval=interval, days=days)
    X, y, df_all = build_features_and_labels(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = build_model()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("Classification report:")
    print(classification_report(y_test, preds))

    save_model(model, model_path)
    print("Saved model to", model_path)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config_example.yml")
    args = ap.parse_args()
    main(args.config)
