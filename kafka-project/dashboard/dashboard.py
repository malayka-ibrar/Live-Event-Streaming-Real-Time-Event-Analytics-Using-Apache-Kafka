import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append('D:/kafka-project/dashboard')
from db_helper import db_helper
from config import DASHBOARD_CONFIG, COLORS

# Page configuration
st.set_page_config(
    page_title=DASHBOARD_CONFIG['page_title'],
    page_icon="📊",
    layout=DASHBOARD_CONFIG['layout'],
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
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
    .main-header p {
        color: #e0e0e0;
        margin: 5px 0 0 0;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown(f"""
<div class="main-header">
    <h1>📊 {DASHBOARD_CONFIG['title']}</h1>
    <p>Real-time event streaming analytics powered by Apache Kafka</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Dashboard Controls")

# Auto-refresh option
auto_refresh = st.sidebar.checkbox("Auto Refresh (5 seconds)", value=True)

# Manual refresh button
refresh_button = st.sidebar.button("🔄 Refresh Now")

# Time range filter
time_range = st.sidebar.selectbox(
    "Time Range",
    options=["Last Hour", "Last 6 Hours", "Last 24 Hours", "All Time"],
    index=0
)

# Event type filter
st.sidebar.subheader("Filter by Event Type")
event_types_filter = st.sidebar.multiselect(
    "Select Event Types",
    options=['page_view', 'click', 'purchase', 'add_to_cart', 'signup'],
    default=[]
)

# Device filter
st.sidebar.subheader("Filter by Device")
device_filter = st.sidebar.multiselect(
    "Select Devices",
    options=['mobile', 'desktop', 'tablet'],
    default=[]
)

# Dashboard info
st.sidebar.markdown("---")
st.sidebar.info(f"""
**Pipeline Status:**
- ✅ Kafka Broker: Running
- ✅ Producer: Active
- ✅ Consumer: Active
- ✅ MySQL: Connected

**Last Updated:** {datetime.now().strftime('%H:%M:%S')}
""")

# Main content area
placeholder = st.empty()

def create_metrics_row(data):
    """Create metrics row with 4 columns"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Events",
            value=f"{data['total_events']:,}",
            delta=None,
            help="Total events captured since start"
        )
    
    with col2:
        st.metric(
            label="👥 Unique Users",
            value=f"{data['unique_users']:,}",
            delta=None,
            help="Unique users who generated events"
        )
    
    with col3:
        st.metric(
            label="⚡ Events/Second",
            value=f"{data['events_per_second']:.1f}",
            delta=None,
            help="Average events per second (last minute)"
        )
    
    with col4:
        active_types = len(data['events_by_type']) if not data['events_by_type'].empty else 0
        st.metric(
            label="🎯 Active Event Types",
            value=active_types,
            delta=None,
            help="Number of event types detected"
        )

def create_event_type_chart(data):
    """Create bar chart for events by type"""
    if not data['events_by_type'].empty:
        fig = px.bar(
            data['events_by_type'],
            x='event_type',
            y='count',
            title="📊 Events by Type",
            color='event_type',
            color_discrete_map=COLORS,
            text='count'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    return None

def create_timeline_chart(data):
    """Create line chart for event timeline"""
    if not data['events_timeline'].empty:
        fig = px.line(
            data['events_timeline'],
            x='time',
            y='event_count',
            title="📈 Event Timeline (Last Hour)",
            markers=True,
            line_shape='spline'
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Event Count",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    return None

def create_device_chart(data):
    """Create pie chart for device distribution"""
    if not data['events_by_device'].empty:
        fig = px.pie(
            data['events_by_device'],
            values='count',
            names='device',
            title="📱 Events by Device",
            color='device',
            color_discrete_map=COLORS,
            hole=0.3
        )
        fig.update_layout(height=400)
        return fig
    return None

def create_country_chart(data):
    """Create bar chart for top countries"""
    if not data['top_countries'].empty:
        fig = px.bar(
            data['top_countries'].head(10),
            x='country',
            y='count',
            title="🌍 Top Countries",
            color='count',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            xaxis_title="Country",
            yaxis_title="Event Count",
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig
    return None

def create_recent_events_table(data):
    """Create table for recent events"""
    if not data['recent_events'].empty:
        # Style the dataframe
        df = data['recent_events'].copy()
        
        # Add event type colors
        def color_event_type(val):
            colors = {'page_view': '#FF6B6B', 'click': '#4ECDC4', 
                     'purchase': '#45B7D1', 'add_to_cart': '#96CEB4',
                     'signup': '#FFEAA7'}
            return f'background-color: {colors.get(val, "#666")}; color: white; padding: 5px; border-radius: 5px;'
        
        styled_df = df.style.applymap(color_event_type, subset=['event_type'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "time": "Time",
                "event_type": "Event Type",
                "user_id": "User ID",
                "device": "Device",
                "country": "Country"
            }
        )

def main():
    """Main dashboard function"""
    while True:
        with placeholder.container():
            # Fetch data
            data = db_helper.get_dashboard_data()
            
            if data is None:
                st.error("❌ Failed to connect to database. Make sure MySQL is running!")
                st.info("Waiting for data... Dashboard will refresh automatically when data is available.")
                time.sleep(5)
                continue
            
            # Metrics row
            create_metrics_row(data)
            st.markdown("---")
            
            # First row: Event Type and Timeline
            col1, col2 = st.columns(2)
            
            with col1:
                event_chart = create_event_type_chart(data)
                if event_chart:
                    st.plotly_chart(event_chart, use_container_width=True)
                else:
                    st.info("No event type data available yet. Waiting for events...")
            
            with col2:
                timeline_chart = create_timeline_chart(data)
                if timeline_chart:
                    st.plotly_chart(timeline_chart, use_container_width=True)
                else:
                    st.info("No timeline data available yet. Waiting for events...")
            
            # Second row: Device and Country charts
            col3, col4 = st.columns(2)
            
            with col3:
                device_chart = create_device_chart(data)
                if device_chart:
                    st.plotly_chart(device_chart, use_container_width=True)
                else:
                    st.info("No device data available yet.")
            
            with col4:
                country_chart = create_country_chart(data)
                if country_chart:
                    st.plotly_chart(country_chart, use_container_width=True)
                else:
                    st.info("No country data available yet.")
            
            # Third row: Recent Events
            st.subheader("📋 Recent Events")
            create_recent_events_table(data)
            
            # Footer
            st.markdown("---")
            st.caption(f"🔄 Dashboard auto-refreshes every {DASHBOARD_CONFIG['auto_refresh_seconds']} seconds | Data from Kafka Event Streaming Pipeline")
        
        # Refresh logic
        if auto_refresh and not refresh_button:
            time.sleep(DASHBOARD_CONFIG['auto_refresh_seconds'])
        elif refresh_button:
            st.cache_data.clear()
            st.rerun()
        else:
            break

if __name__ == "__main__":
    main()