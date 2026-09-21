# src/services/udp_reader.py
import socket
import threading
import re

class UDPReader:
    """
    UDP Reader for receiving QR code data from network scanners.
    Listens on a specified local IP and port for incoming UDP packets.
    """
    def __init__(self, local_ip, local_port, remote_ip=None, remote_port=None, 
                 callback=None, error_callback=None):
        """
        Initialize UDP Reader
        
        Args:
            local_ip: Local IP address to bind to (e.g., "192.168.1.100" or "0.0.0.0" for all interfaces)
            local_port: Local port to listen on (e.g., 5000)
            remote_ip: Remote IP to accept packets from (None = accept from any IP)
            remote_port: Remote port to accept packets from (None = accept from any port)
            callback: Function to call when data is received
            error_callback: Function to call for status/error messages
        """
        self.local_ip = local_ip
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self.callback = callback
        self.error_callback = error_callback
        
        self.running = False
        self.thread = None
        self.socket_instance = None
        self.paused = threading.Event()
        self.paused.set()  # Start unpaused

    def start_reading(self):
        """Start the UDP reader thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self.read_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop_reading(self):
        """Stop the UDP reader thread and close socket"""
        self.running = False
        self.resume()  # Ensure thread isn't blocked
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        
        if self.socket_instance:
            try:
                self.socket_instance.close()
            except:
                pass
            self.socket_instance = None

    def pause(self):
        """Pause reading (blocks the read loop)"""
        self.paused.clear()

    def resume(self):
        """Resume reading after pause"""
        self.paused.set()

    def read_loop(self):
        """Main reading loop - runs in background thread"""
        try:
            # Create UDP socket
            self.socket_instance = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_instance.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # CRITICAL FIX: Bind to specific interface IP (not 0.0.0.0) for multi-NIC systems
            # This ensures we listen on the correct Ethernet adapter
            bind_ip = self.local_ip if self.local_ip else "0.0.0.0"
            
            # Bind to local address
            self.socket_instance.bind((bind_ip, self.local_port))
            self.socket_instance.settimeout(0.5)  # 500ms timeout for checking running flag
            
            if self.error_callback:
                bind_msg = f"Listening on {bind_ip}:{self.local_port}"
                if self.remote_ip:
                    bind_msg += f" (from {self.remote_ip}:{self.remote_port or 'any'})"
                self.error_callback(bind_msg, "green")

            while self.running:
                self.paused.wait()  # Block if paused
                
                if not self.running:
                    break

                try:
                    # Receive data (max 4096 bytes)
                    data, addr = self.socket_instance.recvfrom(4096)
                    
                    # Filter by remote IP/port if specified
                    if self.remote_ip and addr[0] != self.remote_ip:
                        continue
                    if self.remote_port and addr[1] != self.remote_port:
                        continue
                    
                    # Decode and clean data
                    decoded_data = data.decode('utf-8', errors='ignore').strip()
                    decoded_data = re.sub(r'[^\x20-\x7E]', '', decoded_data)
                    
                    if decoded_data and self.callback:
                        self.callback(decoded_data)
                        
                except socket.timeout:
                    # Timeout is normal - allows checking running flag
                    continue
                except Exception as e:
                    if self.running:  # Only log if we're supposed to be running
                        if self.error_callback:
                            self.error_callback(f"Read error: {e}", "orange")
                    
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Error binding to {bind_ip}:{self.local_port}: {e}", "red")
        finally:
            self.running = False
            if self.socket_instance:
                try:
                    self.socket_instance.close()
                except:
                    pass
            if self.error_callback:
                self.error_callback("Not Connected", "red")
