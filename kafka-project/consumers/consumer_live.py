import socket
import os

# Force IPv4
os.environ['KAFKA_CLIENT_DNS_LOOKUP'] = 'use_all_dns_ips'
socket.setdefaulttimeout(10)

from kafka import KafkaConsumer
import json
import logging
from datetime import datetime
from collections import defaultdict
import threading
import time
import os

# Create logs directory if it doesn't exist
os.makedirs('D:/kafka-project/logs', exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:/kafka-project/logs/live_consumer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveConsumer:
    def __init__(self, group_id="live_consumer_group"):
        self.consumer = KafkaConsumer(
            'streaming-events',
            bootstrap_servers=['127.0.0.1:9092'],  # Change from localhost
            auto_offset_reset='latest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: x.decode('utf-8') if x else None,
            api_version_auto_timeout_ms=30000,
            request_timeout_ms=30000
        )
        self.stats = {
            'total_events': 0,
            'events_by_type': defaultdict(int),
            'events_by_device': defaultdict(int),
            'events_by_country': defaultdict(int),
            'unique_users': set(),
            'events_per_minute': [],
            'start_time': datetime.now()
        }
        self.last_minute = datetime.now().minute
        self.minute_count = 0
        
    def process_event(self, event):
        """Process single event and update statistics"""
        self.stats['total_events'] += 1
        self.stats['events_by_type'][event['event_type']] += 1
        self.stats['events_by_device'][event['device']] += 1
        self.stats['events_by_country'][event['metadata']['country']] += 1
        self.stats['unique_users'].add(event['user_id'])
        
        # Calculate events per minute
        current_minute = datetime.now().minute
        if current_minute != self.last_minute:
            if self.minute_count > 0:
                self.stats['events_per_minute'].append(self.minute_count)
                logger.info(f"Events in last minute: {self.minute_count}")
            self.minute_count = 0
            self.last_minute = current_minute
        else:
            self.minute_count += 1
    
    def display_stats(self):
        """Display real-time statistics"""
        while True:
            time.sleep(10)  # Update every 10 seconds
            print("\n" + "="*60)
            print("📊 REAL-TIME STATISTICS")
            print("="*60)
            print(f"⏱️  Runtime: {(datetime.now() - self.stats['start_time']).seconds} seconds")
            print(f"📈 Total Events: {self.stats['total_events']}")
            print(f"👥 Unique Users: {len(self.stats['unique_users'])}")
            print(f"⚡ Events/Second: {self.stats['total_events'] / max((datetime.now() - self.stats['start_time']).seconds, 1):.1f}")
            
            print("\n📊 Events by Type:")
            for event_type, count in sorted(self.stats['events_by_type'].items(), key=lambda x: x[1], reverse=True):
                bar = "█" * int(count / max(self.stats['total_events'], 1) * 50)
                print(f"  {event_type:15} {count:6} {bar}")
            
            print("\n📱 Events by Device:")
            for device, count in self.stats['events_by_device'].items():
                bar = "█" * int(count / max(self.stats['total_events'], 1) * 50)
                print(f"  {device:10} {count:6} {bar}")
            
            print("\n🌍 Top Countries:")
            for country, count in sorted(self.stats['events_by_country'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {country:10} {count:6}")
            
            print("="*60)
    
    def consume(self):
        """Start consuming events"""
        logger.info("🚀 Starting live consumer...")
        
        # Start stats display in separate thread
        stats_thread = threading.Thread(target=self.display_stats, daemon=True)
        stats_thread.start()
        
        try:
            for message in self.consumer:
                event = message.value
                logger.debug(f"Received event: {event['event_id']}")
                self.process_event(event)
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
        finally:
            self.consumer.close()
            self.save_final_stats()
    
    def save_final_stats(self):
        """Save final statistics to file"""
        os.makedirs('D:/kafka-project/data', exist_ok=True)
        stats_file = 'D:/kafka-project/data/live_stats.json'
        with open(stats_file, 'w') as f:
            json.dump({
                'total_events': self.stats['total_events'],
                'events_by_type': dict(self.stats['events_by_type']),
                'events_by_device': dict(self.stats['events_by_device']),
                'events_by_country': dict(self.stats['events_by_country']),
                'unique_users': len(self.stats['unique_users']),
                'events_per_minute': self.stats['events_per_minute'],
                'runtime_seconds': (datetime.now() - self.stats['start_time']).seconds
            }, f, indent=2)
        logger.info(f"💾 Final statistics saved to {stats_file}")

if __name__ == "__main__":
    consumer = LiveConsumer()
    consumer.consume()