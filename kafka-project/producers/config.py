# Kafka Configuration
KAFKA_CONFIG = {
    'bootstrap_servers': '127.0.0.1:9092',  # Change from localhost to 127.0.0.1
    'topic': 'streaming-events'
}

# Data Generation Settings
EVENT_TYPES = ['page_view', 'click', 'purchase', 'add_to_cart', 'signup']
DEVICE_TYPES = ['mobile', 'desktop', 'tablet']
USER_IDS = list(range(1, 1001))

# Streaming Settings
BATCH_SIZE = 100
SLEEP_INTERVAL = 0.1  # seconds between events
MAX_EVENTS = None  # None for infinite, or set number