from kafka import KafkaConsumer
import json
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import os

# Create logs directory if it doesn't exist
os.makedirs('D:/kafka-project/logs', exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:/kafka-project/logs/storage_consumer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StorageConsumer:
    def __init__(self, group_id="storage_consumer_group"):
        self.consumer = KafkaConsumer(
            'streaming-events',
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.db_connection = None
        self.buffer = []
        self.BUFFER_SIZE = 100
        self.total_stored = 0
        
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_connection = psycopg2.connect(
                host="localhost",
                database="event_streaming",
                user="postgres",
                password="postgres",  # Change this to your password
                port=5432
            )
            logger.info("✅ Connected to database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            logger.info("Make sure PostgreSQL is installed and running")
            return False
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        with self.db_connection.cursor() as cursor:
            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id VARCHAR(255) PRIMARY KEY,
                    event_type VARCHAR(50),
                    user_id INTEGER,
                    device VARCHAR(20),
                    timestamp TIMESTAMP,
                    session_id VARCHAR(255),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON events(event_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON events(user_id)")
            
            # Aggregated stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS aggregated_stats (
                    stat_date DATE PRIMARY KEY,
                    total_events INTEGER,
                    unique_users INTEGER,
                    events_by_type JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.db_connection.commit()
            logger.info("✅ Tables created successfully")
    
    def insert_events(self, events):
        """Insert batch of events into database"""
        if not events:
            return
            
        insert_query = """
            INSERT INTO events (event_id, event_type, user_id, device, timestamp, session_id, metadata)
            VALUES %s
            ON CONFLICT (event_id) DO NOTHING
        """
        
        values = [(
            event['event_id'],
            event['event_type'],
            event['user_id'],
            event['device'],
            event['timestamp'],
            event['session_id'],
            json.dumps(event['metadata'])
        ) for event in events]
        
        try:
            with self.db_connection.cursor() as cursor:
                execute_values(cursor, insert_query, values)
                self.db_connection.commit()
                self.total_stored += len(events)
                logger.info(f"💾 Inserted {len(events)} events to database (Total: {self.total_stored})")
        except Exception as e:
            logger.error(f"❌ Failed to insert events: {e}")
            self.db_connection.rollback()
    
    def consume_and_store(self):
        """Consume events and store in database"""
        if not self.connect_database():
            return
        
        self.create_tables()
        logger.info("🚀 Starting storage consumer...")
        
        try:
            for message in self.consumer:
                event = message.value
                self.buffer.append(event)
                
                # Store when buffer reaches size
                if len(self.buffer) >= self.BUFFER_SIZE:
                    self.insert_events(self.buffer)
                    self.buffer = []
                    
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            # Insert remaining events
            if self.buffer:
                self.insert_events(self.buffer)
            logger.info(f"📊 Total events stored: {self.total_stored}")
        finally:
            if self.db_connection:
                self.db_connection.close()
            self.consumer.close()

if __name__ == "__main__":
    consumer = StorageConsumer()
    consumer.consume_and_store()