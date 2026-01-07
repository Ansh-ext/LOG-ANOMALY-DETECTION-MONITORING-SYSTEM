# 🚨 Log Anomaly Detection & Monitoring System

An end-to-end log anomaly detection and alerting system that monitors system logs in real time, detects anomalous behavior using unsupervised machine learning, triggers alerts on abnormal patterns, and visualizes everything in an interactive dashboard.

This project demonstrates how modern production monitoring systems (like Datadog, Splunk, CloudWatch) combine rule-based alerts with ML-based behavioral anomaly detection.

## 📌 Problem Statement
            
System logs are:
- High-volume and noisy
- Mostly **unlabeled**
- Difficult to monitor with static rules
- Prone to **unknown failure patterns**
## 💡 Solution Overview (v1)

This project implements a **hybrid log monitoring architecture**:

### 1️⃣ Rule-Based Alerts (Immediate)
- Trigger instantly on known critical events
- Example: `ERROR`, `FATAL` logs
- Deterministic and reliable

### 2️⃣ ML-Based Behavioral Alerts
- Uses **Isolation Forest** (unsupervised)
- Detects **statistically rare log patterns**
- Alerts on **spikes in anomaly rate over time windows**
- Requires **no labeled data**

Both alert types are unified and visualized in a dashboard.

## 🏗️ System Architecture
<img width="299" height="673" alt="image" src="https://github.com/user-attachments/assets/67777dd0-acba-429a-9c30-8ee0ef2a6cae" />



<img width="1713" height="148" alt="image" src="https://github.com/user-attachments/assets/c9909fb0-b543-40ae-9543-f3aea0939287" />
<img width="1798" height="853" alt="image" src="https://github.com/user-attachments/assets/6e79a40e-67f8-4e20-9749-ba027f032875" />
<img width="1748" height="520" alt="image" src="https://github.com/user-attachments/assets/b7c70343-f5aa-4ebd-92f9-298377ad5ee5" />




❗ Important Notes

The ML model detects statistical rarity, not semantic meaning

A single error log may not trigger an alert

Alerts focus on behavioral changes over time
