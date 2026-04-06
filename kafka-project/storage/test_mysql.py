import sys
import os

# Add paths
sys.path.append('D:/kafka-project/storage')
from mysql_handler import MySQLHandler

def test_mysql_connection():
    print("="*50)
    print("Testing MySQL Connection")
    print("="*50)
    
    # CHANGE THIS to your MySQL password
    db = MySQLHandler(password='root123')
    
    if db.connect():
        print("\n Connection successful!")
        
        # Test insert with sample event
        test_event = {
            'event_id': 'test-001',
            'event_type': 'test',
            'user_id': 999,
            'device': 'desktop',
            'timestamp': '2024-01-01 12:00:00',
            'session_id': 'test-session-001',
            'metadata': {
                'test': True,
                'message': 'Hello MySQL!',
                'country': 'Testland',
                'city': 'Test City'
            }
        }
        
        print("\n Inserting test event...")
        if db.insert_event(test_event):
            print(" Test event inserted successfully!")
        
        print(f"\n Total events in database: {db.get_total_events()}")
        
        print("\n Events by type:")
        for row in db.get_events_by_type():
            print(f"   {row['event_type']}: {row['count']}")
        
        print("\n Recent events:")
        for row in db.get_recent_events(5):
            print(f"   {row['event_type']} - User: {row['user_id']}")
        
        db.disconnect()
        print("\n Test completed successfully!")
    else:
        print("\n Failed to connect to MySQL")
        print("\n Please check:")
        print("1. MySQL service is running")
        print("2. Password is correct")
        print("3. Database 'event_streaming' exists")

if __name__ == "__main__":
    test_mysql_connection()