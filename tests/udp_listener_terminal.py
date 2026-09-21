#!/usr/bin/env python3
"""
Simple Terminal UDP Listener
Listens on a port and displays all incoming UDP packets
Run with: python tests/udp_listener_terminal.py
"""

import socket
import time
from datetime import datetime


def get_local_ip():
    """Get the local machine IP address"""
    try:
        # Connect to a public DNS server to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def print_header():
    """Print application header"""
    print("\n" + "="*70)
    print("UDP LISTENER - Terminal Version".center(70))
    print("="*70 + "\n")


def print_section(title):
    """Print a section header"""
    print(f"\n{title}")
    print("-" * 70)


def get_user_input():
    """Get configuration from user"""
    print_section("CONFIGURATION")
    
    # Get local IP
    while True:
        local_ip = input("Enter Local IP to listen on (default 0.0.0.0 for all interfaces): ").strip() or "0.0.0.0"
        if local_ip == "0.0.0.0" or is_valid_ip(local_ip):
            break
        print("❌ Invalid IP address")
    
    # Get local port
    while True:
        try:
            local_port = int(input("Enter Local Port to listen on (default 5000): ").strip() or "5000")
            if 1 <= local_port <= 65535:
                break
            print("❌ Port must be between 1 and 65535")
        except ValueError:
            print("❌ Please enter a valid port number")
    
    # Get remote IP (optional)
    remote_ip = input("Enter Remote IP to filter from (leave empty for no filter): ").strip() or None
    if remote_ip and not is_valid_ip(remote_ip):
        print("⚠️  Invalid remote IP, will accept from any IP")
        remote_ip = None
    
    # Get remote port (optional)
    remote_port = None
    if remote_ip:
        while True:
            try:
                port_input = input("Enter Remote Port to filter from (leave empty for no filter): ").strip()
                if not port_input:
                    break
                remote_port = int(port_input)
                if 1 <= remote_port <= 65535:
                    break
                print("❌ Port must be between 1 and 65535")
            except ValueError:
                print("❌ Please enter a valid port number")
    
    return local_ip, local_port, remote_ip, remote_port


def is_valid_ip(ip):
    """Check if IP address is valid"""
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except ValueError:
        return False


def display_connection_info(local_ip, local_port):
    """Display connection information"""
    print_section("CONNECTION INFORMATION")
    
    print("\n📍 YOUR CONFIGURATION (Share with Provider):")
    print(f"   Local IP:   {local_ip}")
    print(f"   Local Port: {local_port}")
    
    print("\n" + "="*70)
    print("Provider should send UDP packets to your IP and port above")
    print("="*70 + "\n")


def main():
    """Main entry point"""
    print_header()
    
    # Get user input
    local_ip, local_port, remote_ip, remote_port = get_user_input()
    
    # Display connection info
    display_connection_info(local_ip, local_port)
    
    # Create UDP socket
    print("Starting listener...\n")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((local_ip, local_port))
        sock.settimeout(1.0)
        
        print_section("LISTENING FOR PACKETS")
        print(f"✓ Listening on {local_ip}:{local_port}")
        
        if remote_ip:
            print(f"✓ Filtering packets from {remote_ip}", end="")
            if remote_port:
                print(f":{remote_port}")
            else:
                print(" (any port)")
        else:
            print("✓ Accepting packets from any IP/Port")
        
        print("Press Ctrl+C to stop listening\n")
        
        packet_count = 0
        
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                
                # Filter by remote IP/port if specified
                if remote_ip and addr[0] != remote_ip:
                    continue
                if remote_port and addr[1] != remote_port:
                    continue
                
                packet_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Decode data
                try:
                    decoded_data = data.decode('utf-8', errors='ignore').strip()
                except:
                    decoded_data = str(data)
                
                # Display packet
                print(f"[{timestamp}] Packet #{packet_count}")
                print(f"  From: {addr[0]}:{addr[1]}")
                print(f"  Data: {decoded_data}")
                print()
                
            except socket.timeout:
                continue
            except Exception as e:
                print(f"❌ Error receiving data: {e}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if "Address already in use" in str(e):
            print(f"   Port {local_port} is already in use. Try a different port.")
        elif "Cannot assign requested address" in str(e):
            print(f"   Cannot bind to IP {local_ip}. Check if the IP is valid for this machine.")
    
    finally:
        try:
            sock.close()
        except:
            pass
        
        print("\n" + "="*70)
        print(f"Listener stopped. Total packets received: {packet_count}")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
