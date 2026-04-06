import sys
import io
import os
import json
import logging
from datetime import datetime
from kafka import KafkaConsumer

# Fix Unicode issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add path for storage module
sys.path.append('D:/kafka-project/storage')
from mysql_handler import MySQLHandler

# Setup logging
os.makedirs('D:/kafka-project/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:/kafka-project/logs/consumer_mysql.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MySQLStorageConsumer:
    def __init__(self, group_id="mysql_consumer_group"):
        # Kafka consumer configuration
        self.consumer = KafkaConsumer(
            'streaming-events',
            bootstrap_servers=['127.0.0.1:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            api_version_auto_timeout_ms=30000,
            request_timeout_ms=30000
        )
        
        # MySQL handler - CHANGE PASSWORD HERE
        self.db = MySQLHandler(password='root123')
        self.buffer = []
        self.BUFFER_SIZE = 50  # Insert every 50 events
        self.total_inserted = 0
        
    def start(self):
        """Start consuming and storing events"""
        logger.info("Starting MySQL Storage Consumer...")
        
        # Connect to MySQL
        if not self.db.connect():
            logger.error("Cannot start consumer without database connection")
            return
        
        logger.info("Waiting for events from Kafka...")
        
        try:
            for message in self.consumer:
                event = message.value
                self.buffer.append(event)
                
                if len(self.buffer) >= self.BUFFER_SIZE:
                    inserted = self.db.insert_batch(self.buffer)
                    self.total_inserted += inserted
                    logger.info(f"Stored {self.total_inserted} events total")
                    self.buffer = []
                    
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            if self.buffer:
                inserted = self.db.insert_batch(self.buffer)
                self.total_inserted += inserted
        finally:
            self.db.disconnect()
            self.consumer.close()
            logger.info(f"Final total: {self.total_inserted} events stored in MySQL")

if __name__ == "__main__":
    consumer = MySQLStorageConsumer()
    consumer.start()