# src/train.py
import joblib
import argparse

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

from preprocess import preprocess_log
from parser import parse_log_line


def parse_args():
    parser = argparse.ArgumentParser(
        description="Train log anomaly detection model"
    )
    parser.add_argument(
        "--logs",
        required=True,
        help="Path to historical log file"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Load logs
    with open(args.logs, "r", encoding="utf-8") as f:
        raw_logs = f.readlines()

    print(f"Loaded {len(raw_logs)} log lines")

    # Preprocess
    cleaned_logs = []

    for line in raw_logs:
        line = line.strip()
        if not line:
            continue

        parsed = parse_log_line(line)
        if not parsed:
            continue

        cleaned = preprocess_log(parsed["message"])
        if cleaned.strip():
            cleaned_logs.append(cleaned)

    print(f"Preprocessed {len(cleaned_logs)} logs")

    # TF-IDF
    vectorizer = TfidfVectorizer(
        max_features=50,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        lowercase=False
    )
    cleaned_logs = [log for log in cleaned_logs if log.strip()]

    X = vectorizer.fit_transform(cleaned_logs)

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X.toarray())

    # Train model
    model = IsolationForest(
        n_estimators=100,
        contamination=0.03,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_scaled)

    # Save artifacts
    joblib.dump(vectorizer, "models/tfidf_vectorizer_train.pkl")
    joblib.dump(scaler, "models/scaler_train.pkl")
    joblib.dump(model, "models/isolation_forest_train.pkl")

    print("Training complete. Models saved in /models")

if __name__ == "__main__":
    main()
