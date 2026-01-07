import streamlit as st
import pandas as pd
import os

immediate_alerts = pd.DataFrame()
behavioral_alerts = pd.DataFrame()

if os.path.exists("immediate_alerts.csv"):
    immediate_alerts = pd.read_csv(
        "immediate_alerts.csv",
        parse_dates=["event_time", "ingest_time"]
    )
    immediate_alerts["alert_type"] = "IMMEDIATE"

if os.path.exists("alerts.csv"):
    behavioral_alerts = pd.read_csv(
        "alerts.csv",
        parse_dates=["time_window"]
    )
    behavioral_alerts["alert_type"] = "BEHAVIORAL"

if not behavioral_alerts.empty:
    behavioral_alerts["event_time"] = behavioral_alerts["time_window"]
    behavioral_alerts["log_level"] = "ML"
    behavioral_alerts["component"] = "AnomalyDetector"
    behavioral_alerts["message"] = (
        "Anomaly rate spike detected"
    )

alert_columns = [
    "alert_type",
    "event_time",
    "log_level",
    "component",
    "message",
    "anomaly_rate",
    "threshold"
]

all_alerts = pd.concat(
    [immediate_alerts, behavioral_alerts],
    ignore_index=True,
    sort=False
)

all_alerts = all_alerts.sort_values(
    "event_time",
    ascending=False
)

st.set_page_config(layout="wide")

st.title("🚨 Log Anomaly Monitoring Dashboard")

if not all_alerts.empty:
    latest = all_alerts.iloc[0]

    if latest["alert_type"] == "IMMEDIATE":
        st.error(
            f"🚨 IMMEDIATE ALERT\n\n"
            f"Level: {latest['log_level']}\n"
            f"Component: {latest['component']}\n"
            f"Message: {latest['message']}"
        )
    else:
        st.warning(
            f"⚠️ BEHAVIORAL ALERT\n\n"
            f"Anomaly Rate Spike Detected\n"
            f"Rate: {latest['anomaly_rate']:.2%}"
        )
else:
    st.success("✅ System operating normally")

df = pd.read_csv("monitor_results.csv", parse_dates=["event_time","ingest_time", "time_window"])


st.write("Total logs processed:", len(df))

# -------- Anomaly Rate Over Time --------
agg = (
    df.groupby("time_window")["is_anomaly"]
    .mean()
    .reset_index()
    .sort_values("time_window")
)

st.subheader("Anomaly Rate Over Time")
st.line_chart(agg, x="time_window", y="is_anomaly",x_label="time",y_label="anomaly_rate")

st.subheader("Anomaly Scores Timeline")
st.scatter_chart(
    df,
    x="ingest_time",
    y="anomaly_score",
    color="is_anomaly"
)

st.subheader("Recent Anomalies")
st.dataframe(df[df["is_anomaly"] == 1].tail(20))

st.subheader("All anomalies")
st.dataframe(df[df["is_anomaly"] == 1])

