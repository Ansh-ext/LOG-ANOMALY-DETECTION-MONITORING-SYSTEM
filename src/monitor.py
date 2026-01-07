# src/monitor.py
from parser import parse_log_line
import time
import argparse
import joblib
import pandas as pd
import os

from preprocess import preprocess_log

CRITICAL_LEVELS = {"ERROR", "FATAL"}

def parse_args():
    parser = argparse.ArgumentParser(description="Monitor logs for anomalies")
    parser.add_argument("--logfile", required=True)
    parser.add_argument("--window", type=float, default=0.2)
    parser.add_argument("--alert_multiplier", type=float, default=3.0)
    parser.add_argument("--output", default="monitor_results.csv")
    parser.add_argument(
        "--mode",
        choices=["batch", "stream", "replay"],
        default="stream"
    )
    return parser.parse_args()


def follow(file, mode):
    if mode == "batch":
        file.seek(0)
        for line in file:
            yield line

    elif mode == "stream":
        file.seek(0, 2)
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.5)
                continue
            yield line

    elif mode == "replay":
        file.seek(0)
        prev_time = None

        for line in file:
            parsed = parse_log_line(line.strip())
            if not parsed:
                continue

            curr_time = parsed["event_time"]

            if prev_time:
                delay = (curr_time - prev_time).total_seconds()
                time.sleep(min(delay, 0.1))

            prev_time = curr_time
            yield line


def main():
    args = parse_args()

    vectorizer = joblib.load("models/tfidf_vectorizer_train.pkl")
    scaler = joblib.load("models/scaler_train.pkl")
    model = joblib.load("models/isolation_forest_train.pkl")

    print("✅ Models loaded. Monitoring started...")

    records = []

    with open(args.logfile, "r", encoding="utf-8") as logfile:
        for line in follow(logfile, args.mode):

            parsed = parse_log_line(line.strip())
            if not parsed:
                continue

            ingest_time = pd.Timestamp.now()
            cleaned = preprocess_log(parsed["message"])

            X = vectorizer.transform([cleaned])
            X_scaled = scaler.transform(X.toarray())

            score = model.score_samples(X_scaled)[0]
            is_anomaly = int(model.predict(X_scaled)[0] == -1)

            # ---------- IMMEDIATE ALERT ----------
            if parsed["log_level"] in CRITICAL_LEVELS:
                alert = {
                    "alert_type": "IMMEDIATE",
                    "event_time": parsed["event_time"],
                    "ingest_time": ingest_time,
                    "log_level": parsed["log_level"],
                    "component": parsed["component"],
                    "message": parsed["message"]
                }
                pd.DataFrame([alert]).to_csv(
                    "immediate_alerts.csv",
                    mode="a",
                    header=not os.path.exists("immediate_alerts.csv"),
                    index=False
                )
                print("🚨 IMMEDIATE ALERT:", parsed["message"][:80])

            records.append({
                "event_time": parsed["event_time"],
                "ingest_time": ingest_time,
                "log_level": parsed["log_level"],
                "component": parsed["component"],
                "message": parsed["message"],
                "anomaly_score": score,
                "is_anomaly": is_anomaly,
                "time_window": ingest_time.floor(f"{args.window}min")
            })

            print(f"{ingest_time} | score={score:.4f} | anomaly={is_anomaly}")

            # ---------- BEHAVIORAL ALERT ----------
            if len(records) % 100 == 0:
                df = pd.DataFrame(records)

                summary = df.groupby("time_window").agg(
                    anomaly_rate=("is_anomaly", "mean"),
                    anomaly_count=("is_anomaly", "sum"),
                    total_logs=("is_anomaly", "count")
                )

                if len(summary) >= 5:
                    rolling = summary["anomaly_rate"].iloc[-5:]
                    baseline = rolling.mean()
                    std = max(rolling.std(), 1e-4)
                    threshold = baseline + args.alert_multiplier * std

                    latest = summary.iloc[-1]

                    print("\n📊 Anomaly Summary:")
                    print(summary.tail(3))

                    if latest["anomaly_rate"] > threshold:
                        alert = {
                            "time_window": latest.name,
                            "anomaly_rate": latest["anomaly_rate"],
                            "threshold": threshold
                        }
                        pd.DataFrame([alert]).to_csv(
                            "alerts.csv",
                            mode="a",
                            header=not os.path.exists("alerts.csv"),
                            index=False
                        )
                        print("🚨 BEHAVIORAL ALERT TRIGGERED!")

                df.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
