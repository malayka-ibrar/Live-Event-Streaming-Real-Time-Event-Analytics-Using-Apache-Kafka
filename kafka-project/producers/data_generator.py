import json
import random
import uuid
from datetime import datetime
from config import EVENT_TYPES, DEVICE_TYPES, USER_IDS

class EventGenerator:
    @staticmethod
    def generate_event():
        """Generate a random event"""
        return {
            'event_id': str(uuid.uuid4()),
            'event_type': random.choice(EVENT_TYPES),
            'user_id': random.choice(USER_IDS),
            'device': random.choice(DEVICE_TYPES),
            'timestamp': datetime.now().isoformat(),
            'session_id': str(uuid.uuid4()),
            'metadata': {
                'ip_address': f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                'user_agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                'referrer': random.choice(['google.com', 'facebook.com', 'direct', 'twitter.com']),
                'country': random.choice(['USA', 'UK', 'Canada', 'Germany', 'France']),
                'city': random.choice(['New York', 'London', 'Toronto', 'Berlin', 'Paris'])
            }
        }
    
    @staticmethod
    def generate_batch(size=10):
        """Generate batch of events"""
        return [EventGenerator.generate_event() for _ in range(size)]

if __name__ == "__main__":
    # Test the generator
    print(json.dumps(EventGenerator.generate_event(), indent=2))