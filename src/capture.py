import csv
from scapy.all import sniff, IP, TCP, UDP

def packet_callback(packet):
    fields = {
        "src_ip": packet[IP].src if IP in packet else "",
        "dst_ip": packet[IP].dst if IP in packet else "",
        "protocol": packet.proto if IP in packet else "",
        "src_port": packet[TCP].sport if TCP in packet else packet[UDP].sport if UDP in packet else "",
        "dst_port": packet[TCP].dport if TCP in packet else packet[UDP].dport if UDP in packet else "",
        "length": len(packet)
    }
    with open("data/live_traffic.csv", "a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields.keys())
        writer.writerow(fields)

def main():
    print("Starting packet capture...")
    sniff(prn=packet_callback, store=0)

if __name__ == "__main__":
    main()
