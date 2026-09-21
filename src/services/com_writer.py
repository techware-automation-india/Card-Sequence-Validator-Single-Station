# services/com_writer.py
import serial

class ComPortWriter:
    def __init__(self):
        self.serial_instance = None
        self.is_connected = False

    # --- MODIFIED: connect method now accepts all serial settings ---
    def connect(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1):
        # Validate port parameter
        if not port or port.strip() == "":
            self.serial_instance = None
            self.is_connected = False
            return False, "No port specified"
        
        try:
            self.serial_instance = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout
            )
            self.is_connected = True
            return True, f"Output port {port} connected successfully."
        except serial.SerialException as e:
            self.serial_instance = None
            self.is_connected = False
            return False, f"Failed to connect to output port {port}: {e}"
        except Exception as e:
            self.serial_instance = None
            self.is_connected = False
            return False, f"Unexpected error connecting to {port}: {e}"

    def disconnect(self):
        if self.serial_instance and self.serial_instance.is_open:
            self.serial_instance.close()
        self.is_connected = False

    def send(self, message):
        if not self.is_connected or not self.serial_instance:
            return False, "Output port is not connected."
        
        try:
            self.serial_instance.write(message.encode('utf-8'))
            return True, f"Sent: {message.strip()}"
        except serial.SerialException as e:
            return False, f"Error sending data: {e}"