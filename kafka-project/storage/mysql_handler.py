import mysql.connector
from mysql.connector import Error
import json
import logging
import pandas as pd
from datetime import datetime
import os

# Setup logging
os.makedirs('D:/kafka-project/storage/logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:/kafka-project/storage/logs/mysql_handler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MySQLHandler:
    def __init__(self, host='localhost', user='root', password='root123', database='event_streaming'):
        """
        Initialize MySQL connection
        CHANGE PASSWORD to what you set during MySQL installation
        """
        self.host = host
        self.user = user
        self.password = password  # CHANGE THIS to your MySQL password
        self.database = database
        self.connection = None
        self.cursor = None
        
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False,
                use_pure=True
            )
            self.cursor = self.connection.cursor(dictionary=True)
            logger.info("Connected to MySQL database")
            return True
        except Error as e:
            logger.error(f"MySQL connection failed: {e}")
            logger.info("Troubleshooting:")
            logger.info("1. Is MySQL installed?")
            logger.info("2. Is MySQL service running?")
            logger.info("3. Is password correct?")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("MySQL connection closed")
    
    def insert_event(self, event):
        """Insert single event into database"""
        query = """
            INSERT INTO events 
            (event_id, event_type, user_id, device, event_timestamp, session_id, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            event_type = VALUES(event_type),
            metadata = VALUES(metadata)
        """
        
        # Handle timestamp conversion
        if isinstance(event['timestamp'], str):
            timestamp = event['timestamp'].replace('Z', '+00:00')
        else:
            timestamp = event['timestamp']
        
        values = (
            event['event_id'],
            event['event_type'],
            event['user_id'],
            event['device'],
            timestamp,
            event['session_id'],
            json.dumps(event['metadata'])
        )
        
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            logger.error(f"Failed to insert event: {e}")
            self.connection.rollback()
            return False
    
    def insert_batch(self, events):
        """Insert multiple events in batch"""
        if not events:
            return 0
            
        query = """
            INSERT INTO events 
            (event_id, event_type, user_id, device, event_timestamp, session_id, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            event_type = VALUES(event_type)
        """
        
        values = []
        for event in events:
            # Handle timestamp conversion
            if isinstance(event['timestamp'], str):
                timestamp = event['timestamp'].replace('Z', '+00:00')
            else:
                timestamp = event['timestamp']
                
            values.append((
                event['event_id'],
                event['event_type'],
                event['user_id'],
                event['device'],
                timestamp,
                event['session_id'],
                json.dumps(event['metadata'])
            ))
        
        try:
            self.cursor.executemany(query, values)
            self.connection.commit()
            logger.info(f"Inserted {len(events)} events to MySQL")
            return len(events)
        except Error as e:
            logger.error(f"Batch insert failed: {e}")
            self.connection.rollback()
            return 0
    
    def get_total_events(self):
        """Get total event count"""
        self.cursor.execute("SELECT COUNT(*) as total FROM events")
        result = self.cursor.fetchone()
        return result['total'] if result else 0
    
    def get_events_by_type(self):
        """Get event counts grouped by type"""
        self.cursor.execute("""
            SELECT event_type, COUNT(*) as count 
            FROM events 
            GROUP BY event_type 
            ORDER BY count DESC
        """)
        return self.cursor.fetchall()
    
    def get_recent_events(self, limit=20):
        """Get most recent events"""
        self.cursor.execute("""
            SELECT event_id, event_type, user_id, device, event_timestamp
            FROM events 
            ORDER BY event_timestamp DESC 
            LIMIT %s
        """, (limit,))
        return self.cursor.fetchall()
    
    def get_stats_by_hour(self, hours=24):
        """Get statistics for last N hours"""
        self.cursor.execute("""
            SELECT 
                DATE_FORMAT(event_timestamp, '%%Y-%%m-%%d %%H:00:00') as hour,
                event_type,
                COUNT(*) as event_count,
                COUNT(DISTINCT user_id) as unique_users
            FROM events
            WHERE event_timestamp >= DATE_SUB(NOW(), INTERVAL %s HOUR)
            GROUP BY DATE_FORMAT(event_timestamp, '%%Y-%%m-%%d %%H:00:00'), event_type
            ORDER BY hour DESC
        """, (hours,))
        return self.cursor.fetchall()
    
    def update_aggregated_stats(self):
        """Update daily aggregated statistics"""
        query = """
            INSERT INTO aggregated_stats (stat_date, total_events, unique_users, events_by_type, top_countries)
            SELECT 
                CURDATE() as stat_date,
                COUNT(*) as total_events,
                COUNT(DISTINCT user_id) as unique_users,
                JSON_OBJECTAGG(event_type, COUNT(*)) as events_by_type,
                JSON_OBJECTAGG(JSON_UNQUOTE(JSON_EXTRACT(metadata, '$.country')), COUNT(*)) as top_countries
            FROM events
            WHERE DATE(event_timestamp) = CURDATE()
            ON DUPLICATE KEY UPDATE
                total_events = VALUES(total_events),
                unique_users = VALUES(unique_users),
                events_by_type = VALUES(events_by_type),
                top_countries = VALUES(top_countries)
        """
        
        try:
            self.cursor.execute(query)
            self.connection.commit()
            logger.info("Aggregated stats updated")
            return True
        except Error as e:
            logger.error(f"Failed to update stats: {e}")
            return False
    
    def get_dashboard_data(self):
        """Get all data needed for dashboard"""
        return {
            'total_events': self.get_total_events(),
            'events_by_type': self.get_events_by_type(),
            'recent_events': self.get_recent_events(20),
            'hourly_stats': self.get_stats_by_hour(24)
        }

# Test the handler
if __name__ == "__main__":
    # Test connection
    db = MySQLHandler(password='root123')  # CHANGE THIS to your MySQL password
    
    if db.connect():
        print("="*50)
        print("MySQL Connection Successful!")
        print("="*50)
        
        # Test queries
        print(f"Total events: {db.get_total_events()}")
        print(f"Events by type: {db.get_events_by_type()}")
        
        db.disconnect()
    else:
        print("Failed to connect to MySQL")