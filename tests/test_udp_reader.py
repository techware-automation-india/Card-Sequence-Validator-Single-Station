#!/usr/bin/env python3
"""
Test file for UDPReader - Listens for UDP packets and displays them in terminal
Usage: python test_udp_reader.py [local_ip] [local_port] [remote_ip] [remote_port]
Example: python test_udp_reader.py 192.168.1.100 5000
"""

import sys
import time
import os

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.udp_reader import UDPReader


class UDPTestListener:
    """Simple test listener for UDP packets"""
    
    def __init__(self, local_ip, local_port, remote_ip=None, remote_port=None):
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.packet_count = 0
        
        # Create UDPReader with callbacks
        self.reader = UDPReader(
            local_ip=local_ip,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
            callback=self.on_data_received,
            error_callback=self.on_status_update
        )
    
    def on_data_received(self, data):
        """Callback when data is received"""
        self.packet_count += 1
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Packet #{self.packet_count}: {data}")
    
    def on_status_update(self, message, status_type):
        """Callback for status updates"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        status_icon = {
            "green": "✓",
            "red": "✗",
            "orange": "⚠",
            "black": "•"
        }.get(status_type, "•")
        
        print(f"[{timestamp}] {status_icon} {message}")
    
    def start(self):
        """Start listening for UDP packets"""
        print("\n" + "="*60)
        print("UDP Reader Test - Listening for packets")
        print("="*60)
        print(f"Local IP: {self.local_ip}")
        print(f"Local Port: {self.local_port}")
        if self.remote_ip:
            print(f"Remote IP Filter: {self.remote_ip}")
        if self.remote_port:
            print(f"Remote Port Filter: {self.remote_port}")
        print("="*60)
        print("Waiting for UDP packets... (Press Ctrl+C to stop)\n")
        
        self.reader.start_reading()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\nStopping listener...")
            self.stop()
    
    def stop(self):
        """Stop listening"""
        self.reader.stop_reading()
        print(f"\nListener stopped. Total packets received: {self.packet_count}")
        print("="*60 + "\n")


def main():
    """Main entry point"""
    # Parse command line arguments
    local_ip = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
    local_port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    remote_ip = sys.argv[3] if len(sys.argv) > 3 else None
    remote_port = int(sys.argv[4]) if len(sys.argv) > 4 else None
    
    # Create and start listener
    listener = UDPTestListener(local_ip, local_port, remote_ip, remote_port)
    listener.start()


if __name__ == "__main__":
    main()
