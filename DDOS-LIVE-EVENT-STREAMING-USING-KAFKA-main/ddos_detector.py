# ddos_detector.py - KAFKA CONSUMER (DDoS Detector)
# This reads traffic from Kafka and detects DDoS attacks in real-time

from kafka import KafkaConsumer
import json
from collections import defaultdict
from datetime import datetime
import time

print("="*60)
print("🛡️ KAFKA CONSUMER - DDoS Detection Engine")
print("="*60)

# Connect to Kafka
try:
    consumer = KafkaConsumer(
        'traffic',
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        consumer_timeout_ms=1000
    )
    print("✅ Connected to Kafka at localhost:9092")
    print("📡 Listening to topic: 'traffic'")
except Exception as e:
    print(f"❌ Failed to connect to Kafka: {e}")
    print("Make sure Zookeeper and Kafka Server are running!")
    exit(1)

print("-"*60)

# Detection settings
THRESHOLD = 100  # Attack if >100 requests per minute
ip_count = defaultdict(int)
start_time = datetime.now()
packet_count = 0
attack_count = 0
unique_ips = set()

# Clear old alerts
with open("alerts.json", "w") as f:
    f.write("")

print(f"⚙️ Detection Settings:")
print(f"   - Threshold: {THRESHOLD} requests per minute")
print(f"   - Monitoring: REAL-TIME")
print(f"   - Output: alerts.json")
print("-"*60)
print("🎯 Waiting for traffic from Kafka...\n")

try:
    while True:
        # Poll for messages with timeout
        for message in consumer:
            traffic = message.value
            source_ip = traffic.get('source_ip', 'unknown')
            
            # Count requests from this IP
            ip_count[source_ip] += 1
            packet_count += 1
            unique_ips.add(source_ip)
            
            # Print each received message (optional - can comment out)
            print(f"[{packet_count}] 📥 {source_ip} → {traffic.get('destination_ip', 'unknown')} | Count: {ip_count[source_ip]}")
            
            # Check if 60 seconds have passed
            elapsed = (datetime.now() - start_time).seconds
            
            if elapsed >= 60:
                print("\n" + "="*60)
                print("🔍 SCANNING FOR DDoS ATTACKS")
                print("="*60)
                
                attack_found = False
                
                for ip, count in ip_count.items():
                    if count > THRESHOLD:
                        attack_found = True
                        attack_count += 1
                        alert = {
                            "timestamp": str(datetime.now()),
                            "ip": ip,
                            "count": count,
                            "status": "ATTACK",
                            "severity": "HIGH",
                            "message": f"⚠️ DDoS Attack detected from {ip} - {count} requests in 60 seconds!"
                        }
                        print(f"🚨 [{attack_count}] ATTACK DETECTED! {ip} → {count} requests")
                        
                        # Save to alerts.json
                        with open("alerts.json", "a") as f:
                            f.write(json.dumps(alert) + "\n")
                    else:
                        if count > 10:  # Only show if some activity
                            print(f"✅ Normal: {ip} → {count} requests")
                
                # Show summary
                print("-"*60)
                print(f"📊 SCAN SUMMARY:")
                print(f"   - Total packets received: {packet_count}")
                print(f"   - Unique IPs detected: {len(unique_ips)}")
                print(f"   - Attacks found this minute: {attack_count if attack_found else 0}")
                print(f"   - Total attacks overall: {attack_count}")
                
                if attack_found:
                    top_attacker = max(ip_count.items(), key=lambda x: x[1])
                    print(f"   - Top attacker: {top_attacker[0]} ({top_attacker[1]} requests)")
                print("="*60 + "\n")
                
                # Reset for next minute
                ip_count.clear()
                unique_ips.clear()
                start_time = datetime.now()
                packet_count = 0
        
        # Small sleep to prevent CPU spinning
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n" + "="*60)
    print("🛑 Consumer stopped by user")
    print(f"📊 Final stats - Total attacks detected: {attack_count}")
    print("="*60)
    
finally:
    consumer.close()
    print("[*] Consumer closed")