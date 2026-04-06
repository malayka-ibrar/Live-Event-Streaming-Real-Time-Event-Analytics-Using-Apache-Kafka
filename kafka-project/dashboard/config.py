# Dashboard Configuration
import os

# Database configuration (for MySQL)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'malayka',  # Change to your MySQL password
    'database': 'event_streaming',
    'port': 3306
}

# Dashboard settings
DASHBOARD_CONFIG = {
    'title': 'Event Streaming Dashboard',
    'page_title': 'Real-Time Event Streaming Dashboard',
    'layout': 'wide',
    'auto_refresh_seconds': 5,
    'theme': 'dark'
}

# File paths
PATHS = {
    'logs_dir': 'D:/kafka-project/logs',
    'data_dir': 'D:/kafka-project/data',
    'storage_dir': 'D:/kafka-project/storage'
}

# Create directories if not exist
for path in PATHS.values():
    os.makedirs(path, exist_ok=True)

# Chart colors
COLORS = {
    'page_view': '#FF6B6B',
    'click': '#4ECDC4',
    'purchase': '#45B7D1',
    'add_to_cart': '#96CEB4',
    'signup': '#FFEAA7',
    'mobile': '#FF6B6B',
    'desktop': '#4ECDC4',
    'tablet': '#45B7D1'
}