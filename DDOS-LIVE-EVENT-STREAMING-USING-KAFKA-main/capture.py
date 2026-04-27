# capture.py - KAFKA PRODUCER (Updated)
# This replaces your old capture.py with Kafka producer functionality

from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP

print("="*60)
print("🎬 KAFKA PRODUCER - DDoS Traffic Monitor")
print("="*60)

# Connect to Kafka
try:
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("✅ Connected to Kafka at localhost:9092")
    print("📡 Sending to topic: 'traffic'")
except Exception as e:
    print(f"❌ Failed to connect to Kafka: {e}")
    print("Make sure Zookeeper and Kafka Server are running!")
    exit(1)

print("-"*60)

# Function to label events based on port
def label_event(port):
    labels = {
        22: "ssh_attempt",
        80: "web_request",
        443: "https_request",
        21: "ftp_attempt",
        3389: "rdp_attempt",
        23: "telnet_attempt",
    }
    return labels.get(port, "connection")

# Function to process captured packets
def process_packet(pkt):
    if IP not in pkt:
        return
    
    src_ip = pkt[IP].src
    dst_ip = pkt[IP].dst
    
    if TCP in pkt:
        protocol = "TCP"
        port = pkt[TCP].dport
    elif UDP in pkt:
        protocol = "UDP"
        port = pkt[UDP].dport
    else:
        protocol = "OTHER"
        port = None
    
    event = label_event(port) if port else "connection"
    
    # Create traffic packet
    traffic_packet = {
        "timestamp": str(datetime.now()),
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "protocol": protocol,
        "port": port,
        "event": event
    }
    
    # Send to Kafka
    try:
        producer.send('traffic', value=traffic_packet)
        print(f"[📤] {src_ip} → {dst_ip} | Port: {port} | {event}")
    except Exception as e:
        print(f"[❌] Failed to send: {e}")

print("[*] Starting real-time traffic capture...")
print("[*] Sending all captured traffic to Kafka topic 'traffic'")
print("[*] Press Ctrl+C to stop\n")

try:
    # Sniff packets for 60 seconds (you can change timeout)
    sniff(prn=process_packet, store=0, timeout=60)
    print("\n[*] Capture complete! Flushing messages...")
    producer.flush()
    print("[✓] All messages sent to Kafka")
    
except KeyboardInterrupt:
    print("\n[*] Stopped by user. Flushing messages...")
    producer.flush()
    print("[✓] All messages sent to Kafka")
    
finally:
    producer.close()
    print("[*] Producer closed")