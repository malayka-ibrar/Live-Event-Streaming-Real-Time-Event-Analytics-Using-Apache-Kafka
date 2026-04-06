import socket
import os

# Force IPv4 (add this before Kafka imports)
os.environ['KAFKA_CLIENT_DNS_LOOKUP'] = 'use_all_dns_ips'
socket.setdefaulttimeout(10)

from kafka import KafkaProducer
import json
import time
import logging
import os
from datetime import datetime
from data_generator import EventGenerator
from config import KAFKA_CONFIG, SLEEP_INTERVAL, MAX_EVENTS

# Create logs directory if it doesn't exist
os.makedirs('D:/kafka-project/logs', exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:/kafka-project/logs/producer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EventProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: str(k).encode('utf-8'),
            acks='all',
            retries=3,
            max_in_flight_requests_per_connection=5,
            compression_type='gzip',
            api_version_auto_timeout_ms=30000,  # Add this
            request_timeout_ms=30000,  # Add this
            connections_max_idle_ms=540000,  # Add this
            # Force IPv4
            client_id='kafka-python-producer-1',
            # Add this to force IPv4 resolution
            metadata_max_age_ms=30000
        )
        self.topic = KAFKA_CONFIG['topic']
        self.event_generator = EventGenerator()
        self.event_count = 0
        
    def send_event(self, event):
        """Send single event to Kafka"""
        try:
            future = self.producer.send(
                self.topic,
                key=event['user_id'],
                value=event
            )
            # Wait for acknowledgement
            record_metadata = future.get(timeout=10)
            self.event_count += 1
            
            if self.event_count % 100 == 0:
                logger.info(f"Sent {self.event_count} events so far")
                
            return True
        except Exception as e:
            logger.error(f"Failed to send event: {e}")
            return False
    
    def stream_events(self, duration_seconds=None):
        """Stream events continuously"""
        start_time = datetime.now()
        
        logger.info(f"Starting event streaming...")
        logger.info(f"Topic: {self.topic}")
        logger.info(f"Bootstrap servers: {KAFKA_CONFIG['bootstrap_servers']}")
        
        try:
            while True:
                # Check stopping conditions
                if MAX_EVENTS and self.event_count >= MAX_EVENTS:
                    logger.info(f"Reached target of {MAX_EVENTS} events")
                    break
                    
                if duration_seconds:
                    elapsed = (datetime.now() - start_time).seconds
                    if elapsed >= duration_seconds:
                        logger.info(f"Reached duration of {duration_seconds} seconds")
                        break
                
                # Generate and send event
                event = self.event_generator.generate_event()
                self.send_event(event)
                
                # Small delay to control rate
                time.sleep(SLEEP_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Streaming stopped by user")
        finally:
            self.producer.flush()
            self.producer.close()
            logger.info(f"Total events sent: {self.event_count}")
    
    def send_batch(self, batch_size=100):
        """Send a batch of events"""
        logger.info(f"Sending batch of {batch_size} events...")
        events = self.event_generator.generate_batch(batch_size)
        for event in events:
            self.send_event(event)
        self.producer.flush()
        logger.info(f"Sent batch of {batch_size} events")

if __name__ == "__main__":
    producer = EventProducer()
    
    # Choose one option:
    
    # Option 1: Stream for 60 seconds
    producer.stream_events(duration_seconds=60)
    
    # Option 2: Send specific number of events
    # producer.stream_events(total_events=1000)
    
    # Option 3: Send batch
    # producer.send_batch(batch_size=500)