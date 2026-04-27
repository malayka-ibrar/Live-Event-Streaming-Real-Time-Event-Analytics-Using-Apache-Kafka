

# 🛡️ DDoS Shield - Real-Time DDoS Attack Detection System

## 📌 Overview

**DDoS Shield** is a real-time Distributed Denial of Service (DDoS) attack detection system built with **Apache Kafka** and **Python**. It captures live network traffic, analyzes request patterns using a producer-consumer architecture, and displays attack alerts on a professional live dashboard.

### 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 📡 **Real-time Traffic Capture** | Sniffs network packets using Scapy |
| 🔄 **Kafka Streaming** | Producer-Consumer architecture for real-time data flow |
| 🚨 **DDoS Detection** | Identifies attacks based on configurable request frequency threshold |
| 📊 **Live Dashboard** | Streamlit-based web interface with real-time attack statistics |
| 💾 **JSON Storage** | Saves alerts and logs for future analysis |
| ⚙️ **Configurable Thresholds** | Adjustable sensitivity for different environments |

---

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Core programming language |
| Apache Kafka | 3.9.0 | Message streaming platform |
| Scapy | Latest | Network packet capture |
| kafka-python | Latest | Kafka client for Python |
| Streamlit | Latest | Web dashboard framework |
| Pandas | Latest | Data processing |
| Matplotlib | Latest | Data visualization |

---

## 📁 Project Structure

```
DDoS-Shield/
│
├── capture.py              # Kafka PRODUCER - Captures and sends network traffic
├── ddos_detector.py        # Kafka CONSUMER - Detects DDoS attacks
├── dashboard.py            # Streamlit dashboard - Visualizes alerts
├── alerts.json             # Generated - Stores attack alerts
├── logs.json               # Generated - Stores raw traffic logs
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

---

## 🚀 Installation Guide

### Prerequisites

- Windows 10/11 (Linux/Mac compatible with path changes)
- Python 3.8 or higher
- Administrator privileges (for packet capture)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install kafka-python pandas matplotlib streamlit scapy
```

### Step 2: Download and Install Apache Kafka

1. Go to: https://kafka.apache.org/downloads
2. Download **Kafka 3.9.0** (Scala 2.13 version)
   - File: `kafka_2.13-3.9.0.tgz`
3. Extract using 7-Zip or WinRAR
4. Move extracted folder to: `C:\kafka\kafka_2.13-3.9.0`

### Step 3: Verify Kafka Installation

```bash
dir C:\kafka\kafka_2.13-3.9.0\bin\windows\*.bat
```

Expected output includes:
- `zookeeper-server-start.bat`
- `kafka-server-start.bat`
- `kafka-topics.bat`

---

## ▶️ How to Run the System

### Step 1: Start Zookeeper

**Terminal 1 (Command Prompt)**:
```bash
cd C:\kafka\kafka_2.13-3.9.0
bin\windows\zookeeper-server-start.bat config\zookeeper.properties
```
> ⚠️ **Keep this terminal open**

### Step 2: Start Kafka Server

**Terminal 2 (Command Prompt)**:
```bash
cd C:\kafka\kafka_2.13-3.9.0
bin\windows\kafka-server-start.bat config\server.properties
```
> ⚠️ **Keep this terminal open**

### Step 3: Create Kafka Topic (One Time Only)

**Terminal 3 (Command Prompt)**:
```bash
cd C:\kafka\kafka_2.13-3.9.0
bin\windows\kafka-topics.bat --create --topic traffic --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Step 4: Run Kafka Consumer (DDoS Detector)

**Terminal 4 (Command Prompt)**:
```bash
cd path\to\your\project
python ddos_detector.py
```
> ⚠️ **Keep this terminal open**

### Step 5: Run Kafka Producer (Traffic Capture)

**Terminal 5 (Command Prompt)**:
```bash
cd path\to\your\project
python capture.py
```
> This captures traffic for 60 seconds

### Step 6: Launch Dashboard

**Terminal 6 (Command Prompt)**:
```bash
cd path\to\your\project
streamlit run dashboard.py
```

### Step 7: Open Dashboard

Open your browser and go to: `http://localhost:8501`

---

## 📊 System Architecture

```
[Network Traffic]
       ↓
  capture.py (PRODUCER)
       ↓
  Sends to Kafka Topic "traffic"
       ↓
  ddos_detector.py (CONSUMER)
       ↓
  Analyzes requests per IP (every 60 seconds)
       ↓
  If count > THRESHOLD → Saves to alerts.json
       ↓
  dashboard.py reads alerts.json
       ↓
  Browser displays live attacks
```

### Detection Logic

```python
THRESHOLD = 100  # Requests per minute

if ip_request_count > THRESHOLD:
    status = "ATTACK"  # DDoS detected
else:
    status = "Normal"  # Regular traffic
```

---

## 📈 Dashboard Features

| Feature | Description |
|---------|-------------|
| 🚨 Attack Banner | Shows when DDoS is detected |
| 📊 Attack Events | Total number of attacking IPs |
| 📈 Total Alerts | Number of alert records |
| 👥 Unique IPs | Distinct IPs that contacted you |
| 🎯 Top Offender | IP with highest request count |
| 📉 Bar Charts | Visual representation of requests per IP |
| 📋 Alert Log | Table showing all detected attacks |

---

## ⚙️ Configuration

### Adjusting Detection Threshold

Edit `ddos_detector.py`:

```python
THRESHOLD = 100  # Change this value
```

| Threshold | Best for |
|-----------|----------|
| 50 | Sensitive detection (more false positives) |
| 100 | Normal browsing (default) |
| 200 | Heavy streaming/gaming |
| 500 | Server environments |

### Ignoring Your Own IP

Add your IP to the ignore list in `ddos_detector.py`:

```python
ignore_ips = [
    "192.168.0.102",  # Your computer
    "192.168.1.1",    # Your router
    "127.0.0.1",      # Localhost
]
```

---

## 📝 Sample Output

### Consumer Terminal - When Attack Detected:

```
============================================================
🔍 RUNNING DETECTION SCAN
============================================================
🚨 [1] ATTACK DETECTED! 20.57.103.21 → 299 requests
🚨 [2] ATTACK DETECTED! 192.168.1.7 → 1349 requests
✅ Normal: 142.251.152.119 → 45 requests
------------------------------------------------------------
📊 SCAN SUMMARY:
   - Total packets received: 800
   - Unique IPs detected: 15
   - Attacks found: 2
   - Top attacker: 192.168.1.7 (1349 requests)
============================================================
```

### Dashboard Display:

```
⚠️ DDOS ATTACK DETECTED
2 attack event(s) recorded · Last checked: 21:08:06

Attack Events: 2     Total Alerts: 2     Unique IPs: 2
Top Offender: 192.168.1.7

Alert Log:
192.168.1.7    1349    ⚡ ATTACK
20.57.103.21   299     ⚡ ATTACK
```

---


## 🛑 Stopping the System

Press `Ctrl + C` in each terminal in this order:

1. Terminal 6 (Dashboard)
2. Terminal 5 (Producer)
3. Terminal 4 (Consumer)
4. Terminal 2 (Kafka Server)
5. Terminal 1 (Zookeeper)

---



## 🎯 Future Improvements

- [ ] Add email/SMS alerts for real attacks
- [ ] Implement machine learning for anomaly detection
- [ ] Add geolocation tracking for attackers


---


---
