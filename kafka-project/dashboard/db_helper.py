import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging
import os
from sqlalchemy import create_engine
from config import DB_CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseHelper:
    def __init__(self):
        self.connection = None
        self.engine = None
        
    def connect(self):
        """Establish database connection"""
        try:
            # Create SQLAlchemy engine for pandas (fixes the warning)
            connection_string = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
            self.engine = create_engine(connection_string)
            
            # Also keep direct connection for other operations
            self.connection = mysql.connector.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port']
            )
            return True
        except Error as e:
            logger.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
        if self.engine:
            self.engine.dispose()
    
    def get_total_events(self):
        """Get total event count"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM events")
        result = cursor.fetchone()
        cursor.close()
        return result['total'] if result else 0
    
    def get_unique_users(self):
        """Get unique user count"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(DISTINCT user_id) as unique_users FROM events")
        result = cursor.fetchone()
        cursor.close()
        return result['unique_users'] if result else 0
    
    def get_events_by_type(self):
        """Get events grouped by type"""
        query = """
            SELECT event_type, COUNT(*) as count 
            FROM events 
            GROUP BY event_type 
            ORDER BY count DESC
        """
        return pd.read_sql(query, self.engine)
    
    def get_events_timeline(self, hours=1):
        """Get events timeline for last N hours - FIXED"""
        query = f"""
            SELECT 
                DATE_FORMAT(event_timestamp, '%%H:%%i') as time,
                COUNT(*) as event_count
            FROM events
            WHERE event_timestamp >= DATE_SUB(NOW(), INTERVAL {hours} HOUR)
            GROUP BY DATE_FORMAT(event_timestamp, '%%H:%%i')
            ORDER BY MIN(event_timestamp)
            LIMIT 60
        """
        return pd.read_sql(query, self.engine)
    
    def get_events_by_device(self):
        """Get events grouped by device"""
        query = """
            SELECT device, COUNT(*) as count 
            FROM events 
            GROUP BY device 
            ORDER BY count DESC
        """
        return pd.read_sql(query, self.engine)
    
    def get_top_countries(self, limit=10):
        """Get top countries by events"""
        query = f"""
            SELECT 
                JSON_UNQUOTE(JSON_EXTRACT(metadata, '$.country')) as country,
                COUNT(*) as count
            FROM events
            WHERE metadata IS NOT NULL
            GROUP BY country
            ORDER BY count DESC
            LIMIT {limit}
        """
        return pd.read_sql(query, self.engine)
    
    def get_recent_events(self, limit=20):
        """Get most recent events"""
        query = f"""
            SELECT 
                DATE_FORMAT(event_timestamp, '%%H:%%i:%%s') as time,
                event_type,
                user_id,
                device,
                JSON_UNQUOTE(JSON_EXTRACT(metadata, '$.country')) as country
            FROM events
            ORDER BY event_timestamp DESC
            LIMIT {limit}
        """
        return pd.read_sql(query, self.engine)
    
    def get_events_per_second(self):
        """Calculate events per second (last minute)"""
        query = """
            SELECT COUNT(*) as eps
            FROM events
            WHERE event_timestamp >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)
        """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        return result['eps'] / 60 if result else 0
    
    def get_dashboard_data(self):
        """Fetch all dashboard data"""
        if not self.connect():
            return None
        
        try:
            data = {
                'total_events': self.get_total_events(),
                'unique_users': self.get_unique_users(),
                'events_by_type': self.get_events_by_type(),
                'events_timeline': self.get_events_timeline(),
                'events_by_device': self.get_events_by_device(),
                'top_countries': self.get_top_countries(),
                'recent_events': self.get_recent_events(),
                'events_per_second': self.get_events_per_second()
            }
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {e}")
            self.disconnect()
            return None
        
        self.disconnect()
        return data

# Create singleton instance
db_helper = DatabaseHelper()