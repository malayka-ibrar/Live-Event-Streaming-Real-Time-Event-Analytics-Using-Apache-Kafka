import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
import random
 
# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="DDoS Shield — Detection Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)
 
# ─── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@700;900&family=Inter:wght@300;400;500&display=swap');
 
:root {
    --bg-dark:     #060910;
    --bg-card:     #0d1117;
    --bg-panel:    #111827;
    --accent-red:  #ff2d55;
    --accent-cyan: #00e5ff;
    --accent-gold: #ffd60a;
    --text-main:   #e8eaf0;
    --text-muted:  #6b7280;
    --border:      rgba(0,229,255,0.15);
    --danger-glow: 0 0 20px rgba(255,45,85,0.5);
    --cyan-glow:   0 0 15px rgba(0,229,255,0.4);
}
 
/* ── Global reset ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-dark) !important;
    color: var(--text-main) !important;
    font-family: 'Inter', sans-serif;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: var(--bg-card) !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1400px; }
h1,h2,h3 { font-family: 'Orbitron', monospace !important; }
 
/* ── Scrolling ticker ── */
.ticker-wrap {
    background: linear-gradient(90deg, var(--accent-red), #a00028);
    padding: 6px 0;
    overflow: hidden;
    border-bottom: 1px solid var(--accent-red);
    margin-bottom: 2rem;
    border-radius: 0 0 8px 8px;
}
.ticker-content {
    display: inline-block;
    white-space: nowrap;
    animation: ticker 28s linear infinite;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    color: #fff;
}
@keyframes ticker { 0%{transform:translateX(100vw)} 100%{transform:translateX(-100%)} }
 
/* ── Header ── */
.hero {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    margin-bottom: 2rem;
}
.hero-icon {
    font-size: 3rem;
    filter: drop-shadow(0 0 12px var(--accent-cyan));
    animation: pulse 2.5s ease-in-out infinite;
}
@keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.06)} }
.hero-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 2rem !important;
    font-weight: 900 !important;
    background: linear-gradient(90deg, var(--accent-cyan), #fff, var(--accent-red));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 !important;
    line-height: 1.2 !important;
}
.hero-sub {
    font-size: 0.78rem;
    color: var(--text-muted);
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 4px;
}
 
/* ── Stat cards ── */
.stat-grid { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.stat-card {
    flex: 1; min-width: 160px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: transform .2s;
}
.stat-card:hover { transform: translateY(-3px); }
.stat-card::before {
    content:'';
    position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
}
.stat-card.danger::before { background: linear-gradient(90deg, transparent, var(--accent-red), transparent); }
.stat-card.warn::before  { background: linear-gradient(90deg, transparent, var(--accent-gold), transparent); }
.stat-label {
    font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text-muted); font-family: 'Share Tech Mono', monospace;
    margin-bottom: 0.5rem;
}
.stat-value {
    font-family: 'Orbitron', monospace;
    font-size: 2rem; font-weight: 700;
    color: var(--text-main);
}
.stat-card.danger .stat-value { color: var(--accent-red); text-shadow: var(--danger-glow); }
.stat-card.ok    .stat-value  { color: var(--accent-cyan); text-shadow: var(--cyan-glow); }
.stat-card.warn  .stat-value  { color: var(--accent-gold); }
 
/* ── Alert badge ── */
.alert-banner {
    background: linear-gradient(135deg, rgba(255,45,85,.18), rgba(160,0,40,.08));
    border: 1px solid var(--accent-red);
    border-left: 4px solid var(--accent-red);
    border-radius: 8px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
    animation: flash 1.2s ease-in-out infinite alternate;
    box-shadow: var(--danger-glow);
}
@keyframes flash { from{opacity:1} to{opacity:.7} }
.alert-text { font-family:'Orbitron',monospace; font-size:1rem; color:var(--accent-red); font-weight:700; }
.alert-sub  { font-size:0.75rem; color:#f87171; margin-top:2px; font-family:'Share Tech Mono',monospace; }
 
.safe-banner {
    background: rgba(0,229,255,.06);
    border: 1px solid rgba(0,229,255,.3);
    border-left: 4px solid var(--accent-cyan);
    border-radius: 8px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.5rem;
    display: flex; align-items: center; gap: 1rem;
}
.safe-text { font-family:'Orbitron',monospace; font-size:1rem; color:var(--accent-cyan); font-weight:700; }
 
/* ── Section titles ── */
.section-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.8rem 0 0.8rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.section-title::after {
    content:''; flex:1; height:1px;
    background: linear-gradient(90deg, var(--border), transparent);
}
 
/* ── Table ── */
.styled-table {
    width: 100%;
    border-collapse: collapse;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.82rem;
    margin-bottom: 1rem;
}
.styled-table th {
    background: rgba(0,229,255,.06);
    color: var(--accent-cyan);
    font-size: 0.68rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.7rem 1rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
}
.styled-table td {
    padding: 0.65rem 1rem;
    border-bottom: 1px solid rgba(255,255,255,.04);
    color: var(--text-main);
}
.styled-table tr:hover td { background: rgba(255,255,255,.03); }
.badge-attack {
    background: rgba(255,45,85,.18); color: var(--accent-red);
    border: 1px solid rgba(255,45,85,.4);
    border-radius: 99px; padding: 2px 10px;
    font-size: 0.7rem; font-weight: 700;
}
.badge-normal {
    background: rgba(0,229,255,.1); color: var(--accent-cyan);
    border: 1px solid rgba(0,229,255,.3);
    border-radius: 99px; padding: 2px 10px;
    font-size: 0.7rem;
}
 
/* ── Chart wrapper ── */
[data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] {
    background: var(--bg-card) !important;
    border-radius: 12px;
    padding: 1rem;
    border: 1px solid var(--border);
}
 
/* ── Streamlit element overrides ── */
.stDataFrame { border-radius: 12px; overflow: hidden; }
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
div[data-testid="stMetricValue"] { color: var(--accent-cyan) !important; font-family:'Orbitron',monospace !important; }
 
/* ── Footer ── */
.footer {
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    margin-top: 3rem;
    border-top: 1px solid var(--border);
    padding-top: 1.2rem;
}
</style>
""", unsafe_allow_html=True)
 
 
# ─── Load Data ───────────────────────────────────────────────────
def load_alerts():
    data = []
    try:
        with open("alerts.json", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except:
                        data.append(eval(line))
    except FileNotFoundError:
        pass
    return data
 
 
# ─── Ticker ──────────────────────────────────────────────────────
st.markdown("""
<div class="ticker-wrap">
  <span class="ticker-content">
    ⚠ DDOS SHIELD ACTIVE &nbsp;|&nbsp;
    MONITORING NETWORK TRAFFIC IN REAL-TIME &nbsp;|&nbsp;
    KAFKA STREAM CONNECTED &nbsp;|&nbsp;
    ANOMALY DETECTION ENABLED &nbsp;|&nbsp;
    ALL SYSTEMS OPERATIONAL &nbsp;|&nbsp;
    THRESHOLD: 100 REQ/MIN &nbsp;|&nbsp;
    ⚠ DDOS SHIELD ACTIVE &nbsp;|&nbsp;
    MONITORING NETWORK TRAFFIC IN REAL-TIME &nbsp;|&nbsp;
  </span>
</div>
""", unsafe_allow_html=True)
 
 
# ─── Header ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-icon">🛡️</div>
  <div>
    <div class="hero-title">DDoS Shield</div>
    <div class="hero-sub">Real-Time Detection Dashboard &nbsp;·&nbsp; Powered by Apache Kafka</div>
  </div>
</div>
""", unsafe_allow_html=True)
 
 
# ─── Load & Process ──────────────────────────────────────────────
data = load_alerts()
now_str = datetime.now().strftime("%H:%M:%S")
 
if data:
    df = pd.DataFrame(data)
 
    # Ensure columns exist
    if "ip" not in df.columns:    df["ip"] = "Unknown"
    if "count" not in df.columns: df["count"] = 1
    if "status" not in df.columns:
        df["status"] = df["count"].apply(lambda x: "ATTACK" if x > 100 else "Normal")
 
    total_alerts   = len(df)
    attack_rows    = df[df["status"].str.upper() == "ATTACK"] if "status" in df.columns else pd.DataFrame()
    attack_count   = len(attack_rows)
    unique_ips     = df["ip"].nunique()
    top_ip         = df["ip"].value_counts().idxmax()
    is_under_attack = attack_count > 0
 
    # ── Status Banner ──
    if is_under_attack:
        st.markdown(f"""
        <div class="alert-banner">
          <span style="font-size:2rem">🚨</span>
          <div>
            <div class="alert-text">⚠ DDOS ATTACK DETECTED</div>
            <div class="alert-sub">{attack_count} attack event(s) recorded &nbsp;·&nbsp; Last checked: {now_str}</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="safe-banner">
          <span style="font-size:2rem">✅</span>
          <div>
            <div class="safe-text">NETWORK SECURE</div>
            <div style="font-size:0.75rem;color:#6b7280;font-family:Share Tech Mono,monospace">
              All traffic within normal thresholds &nbsp;·&nbsp; {now_str}
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
 
    # ── Stat Cards ──
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-card {'danger' if is_under_attack else 'ok'}">
        <div class="stat-label">Attack Events</div>
        <div class="stat-value">{attack_count}</div>
      </div>
      <div class="stat-card ok">
        <div class="stat-label">Total Alerts</div>
        <div class="stat-value">{total_alerts}</div>
      </div>
      <div class="stat-card warn">
        <div class="stat-label">Unique IPs</div>
        <div class="stat-value">{unique_ips}</div>
      </div>
      <div class="stat-card ok">
        <div class="stat-label">Top Offender</div>
        <div class="stat-value" style="font-size:1.1rem;padding-top:4px">{top_ip}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
 
    # ── Charts ──
    col1, col2 = st.columns([3, 2])
 
    with col1:
        st.markdown('<div class="section-title">📊 Requests per IP Address</div>', unsafe_allow_html=True)
        ip_counts = df["ip"].value_counts().reset_index()
        ip_counts.columns = ["IP Address", "Request Count"]
        st.bar_chart(ip_counts.set_index("IP Address"), color="#00e5ff")
 
    with col2:
        st.markdown('<div class="section-title">📡 Traffic Status Breakdown</div>', unsafe_allow_html=True)
        if "status" in df.columns:
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            st.bar_chart(status_counts.set_index("Status"), color="#ff2d55")
 
    # ── Alert Log Table ──
    st.markdown('<div class="section-title">🗂️ Alert Log — All Events</div>', unsafe_allow_html=True)
 
    rows_html = ""
    for _, row in df.iterrows():
        ip     = row.get("ip", "—")
        count  = row.get("count", "—")
        status = str(row.get("status", "Normal"))
        ts     = row.get("timestamp", row.get("time", "—"))
        badge  = f'<span class="badge-attack">⚡ ATTACK</span>' if "ATTACK" in status.upper() \
                 else f'<span class="badge-normal">✓ Normal</span>'
        rows_html += f"""
        <tr>
          <td>{ip}</td>
          <td>{count}</td>
          <td>{badge}</td>
          <td>{ts}</td>
        </tr>"""
 
    st.markdown(f"""
    <table class="styled-table">
      <thead>
        <tr>
          <th>IP Address</th>
          <th>Request Count</th>
          <th>Status</th>
          <th>Timestamp</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)
 
else:
    # ── Empty State ──
    st.markdown("""
    <div class="safe-banner">
      <span style="font-size:2rem">📡</span>
      <div>
        <div class="safe-text">LISTENING FOR TRAFFIC...</div>
        <div style="font-size:0.75rem;color:#6b7280;font-family:Share Tech Mono,monospace">
          No alerts yet. Kafka consumer is running. Waiting for data stream.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
 
    st.markdown(f"""
    <div class="stat-grid">
      <div class="stat-card ok"><div class="stat-label">Attack Events</div><div class="stat-value">0</div></div>
      <div class="stat-card ok"><div class="stat-label">Total Alerts</div><div class="stat-value">0</div></div>
      <div class="stat-card warn"><div class="stat-label">Unique IPs</div><div class="stat-value">0</div></div>
      <div class="stat-card ok"><div class="stat-label">Status</div><div class="stat-value" style="font-size:1rem;padding-top:6px">SECURE</div></div>
    </div>
    """, unsafe_allow_html=True)
 
 
# ─── Auto-refresh hint ───────────────────────────────────────────
st.markdown('<div class="section-title">🔄 Auto Refresh</div>', unsafe_allow_html=True)
if st.button("🔄 Refresh Dashboard"):
    st.rerun()
 
st.caption("Tip: Run with `streamlit run dashboard.py` — press Refresh to reload latest alerts.")
 
 
# ─── Footer ──────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  🛡️ DDOS SHIELD &nbsp;·&nbsp; REAL-TIME NETWORK PROTECTION &nbsp;·&nbsp;
  KAFKA-POWERED &nbsp;·&nbsp; LAST UPDATED {now_str}
</div>
""", unsafe_allow_html=True)
 