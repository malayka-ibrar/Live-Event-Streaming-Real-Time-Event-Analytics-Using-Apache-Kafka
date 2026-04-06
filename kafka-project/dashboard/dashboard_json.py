import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
import time

st.set_page_config(
    page_title="Event Streaming Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .main-header h1 {
        color: white;
        margin: 0;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown("""
<div class="main-header">
    <h1>📊 Real-Time Event Streaming Dashboard</h1>
    <p>Live data from Kafka Event Streaming Pipeline</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Dashboard Controls")
auto_refresh = st.sidebar.checkbox("Auto Refresh (3 seconds)", value=True)
refresh_button = st.sidebar.button("🔄 Refresh Now")

# File path
STATS_FILE = 'D:/kafka-project/data/live_stats.json'

# Check file status
if os.path.exists(STATS_FILE):
    file_size = os.path.getsize(STATS_FILE)
    st.sidebar.success(f"✅ Stats file found ({file_size} bytes)")
else:
    st.sidebar.error("❌ Stats file NOT found")

st.sidebar.markdown("---")
st.sidebar.subheader("📡 Pipeline Status")

def load_json_stats():
    """Load statistics from JSON file"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        return None

# Main placeholder
placeholder = st.empty()
counter = 0

# Auto-refresh loop
while True:
    with placeholder.container():
        stats = load_json_stats()
        counter += 1
        
        if stats and stats.get('total_events', 0) > 0:
            st.success(f"✅ Data loaded! Total events: {stats.get('total_events', 0)}")
            
            # Metrics Row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📊 Total Events",
                    f"{stats.get('total_events', 0):,}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "👥 Unique Users",
                    f"{stats.get('unique_users', 0):,}",
                    delta=None
                )
            
            with col3:
                runtime = stats.get('runtime_seconds', 0)
                minutes = runtime // 60
                seconds = runtime % 60
                st.metric(
                    "⏱️ Runtime",
                    f"{minutes}m {seconds}s",
                    delta=None
                )
            
            with col4:
                eps = stats.get('total_events', 0) / max(runtime, 1)
                st.metric(
                    "⚡ Events/Second",
                    f"{eps:.1f}",
                    delta=None
                )
            
            st.markdown("---")
            
            # Events by Type Chart - WITH UNIQUE KEY
            st.subheader("📊 Events by Type")
            if stats.get('events_by_type'):
                df = pd.DataFrame([
                    {'Event Type': k, 'Count': v} 
                    for k, v in stats['events_by_type'].items()
                ])
                fig = px.bar(
                    df, 
                    x='Event Type', 
                    y='Count', 
                    color='Event Type',
                    text='Count'
                )
                fig.update_traces(textposition='outside')
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, key=f"event_type_chart_{counter}")
            else:
                st.info("No event type data yet")
            
            # Two columns for device and country
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📱 Events by Device")
                if stats.get('events_by_device'):
                    df = pd.DataFrame([
                        {'Device': k, 'Count': v} 
                        for k, v in stats['events_by_device'].items()
                    ])
                    fig = px.pie(
                        df, 
                        values='Count', 
                        names='Device',
                        hole=0.3
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True, key=f"device_chart_{counter}")
                else:
                    st.info("No device data yet")
            
            with col2:
                st.subheader("🌍 Top Countries")
                if stats.get('events_by_country'):
                    df = pd.DataFrame([
                        {'Country': k, 'Count': v} 
                        for k, v in stats['events_by_country'].items()
                    ]).sort_values('Count', ascending=False).head(10)
                    fig = px.bar(
                        df, 
                        x='Country', 
                        y='Count',
                        color='Count',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True, key=f"country_chart_{counter}")
                else:
                    st.info("No country data yet")
            
            # Events per minute chart
            st.subheader("📈 Events Per Minute")
            if stats.get('events_per_minute') and len(stats['events_per_minute']) > 0:
                df = pd.DataFrame({
                    'Minute': range(1, len(stats['events_per_minute']) + 1),
                    'Count': stats['events_per_minute']
                })
                fig = px.line(
                    df, 
                    x='Minute', 
                    y='Count',
                    markers=True,
                    line_shape='spline'
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, key=f"timeline_chart_{counter}")
            else:
                st.info("Waiting for minute-by-minute data...")
            
            # Footer
            st.markdown("---")
            st.caption(f"🔄 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        else:
            # No data yet
            st.warning("⏳ Waiting for data from Kafka...")
            st.info("""
            ### Please ensure:
            1. ✅ Kafka is running (Terminal 1)
            2. ✅ Producer is running (Terminal 2)
            3. ✅ Live Consumer is running (Terminal 3)
            
            **Data location:** `D:/kafka-project/data/live_stats.json`
            
            The dashboard will automatically update when data arrives.
            """)
    
    # Refresh logic
    if auto_refresh and not refresh_button:
        time.sleep(3)
    elif refresh_button:
        st.cache_data.clear()
        st.rerun()
    else:
        break