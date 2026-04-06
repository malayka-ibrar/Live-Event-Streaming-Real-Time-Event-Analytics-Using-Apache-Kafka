# 🛡️ Live Event Streaming — Real-Time Event Analytics Using Apache Kafka

## 📌 Overview
A real-time event streaming system built with Apache Kafka and Python.
The system simulates live user events (page views, clicks, purchases, etc.),
processes them in real-time, generates live statistics, and visualizes everything
on an interactive dashboard.

---

## ⚙️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.x | Core language |
| Apache Kafka 4.2.0 | Real-time streaming pipeline |
| kafka-python | Kafka producer/consumer |
| Pandas | Data processing |
| Plotly | Interactive charts |
| Streamlit | Live dashboard |

---

## 📦 Installation

```bash
pip install kafka-python pandas plotly streamlit
```

---

## ▶️ How to Run

### ✅ Step 1 — Start Kafka Server

```bash
cd D:\kafka\kafka_2.13-4.2.0
bin\windows\kafka-server-start.bat config\server.properties
```
⚠️ **Keep this terminal open**

---

### ✅ Step 2 — Create Kafka Topic

```bash
cd D:\kafka\kafka_2.13-4.2.0
bin\windows\kafka-topics.bat --create --topic streaming-events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1
```

---

### ✅ Step 3 — Run Producer (Event Generator)

```bash
cd D:\kafka-project\producers
python producer.py
```
*Simulates real-time user events (page_view, click, purchase, add_to_cart, signup)*

---

### ✅ Step 4 — Run Consumer (Live Statistics)

```bash
cd D:\kafka-project\consumers
python consumer_live.py
```
*Displays live event statistics in terminal*

---

### ✅ Step 5 — Launch Dashboard

```bash
cd D:\kafka-project\dashboard
streamlit run dashboard_simple.py
```
*Opens a live browser dashboard at `http://localhost:8501`* 🌐

---

## 📊 Sample Output

### Terminal Consumer Output:
```
============================================================
📊 REAL-TIME STATISTICS
============================================================
⏱️  Runtime: 45 seconds
📈 Total Events: 1120
👥 Unique Users: 673
⚡ Events/Second: 24.9

📊 Events by Type:
  purchase        228 ████████████████████████████████████████
  add_to_cart     228 ████████████████████████████████████████
  page_view       226 ██████████████████████████████████████
  click           226 ██████████████████████████████████████
  signup          212 ████████████████████████████████████
```

### Data saved to `data/live_stats.json`:

```json
{
  "total_events": 1120,
  "unique_users": 673,
  "events_by_type": {
    "purchase": 228,
    "page_view": 226,
    "click": 226
  },
  "runtime_seconds": 200
}
```

---

## ⚡ Features

| Feature | Description |
|---------|-------------|
| 🔴 Real-time event simulation | Generates 5 types of user events |
| 🛡️ Live statistics processing | Real-time aggregation and display |
| 📡 Kafka streaming pipeline | Distributed message streaming |
| 📊 Live dashboard | Streamlit with auto-refresh (3 sec) |
| 💾 JSON data persistence | Automatic statistics saving |

---

## 📁 Project Files

| File | Purpose |
|------|---------|
| `producer.py` | Generates and sends events to Kafka |
| `consumer_live.py` | Consumes events, displays stats, saves JSON |
| `dashboard_simple.py` | Streamlit dashboard for visualization |
| `live_stats.json` | Stored statistics data |

---


---

## 📝 License

MIT License

---

**Built with ❤️ using Apache Kafka and Python**
