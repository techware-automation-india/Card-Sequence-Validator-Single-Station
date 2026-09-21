# APIs & Integrations

## Hardware Integrations

### Network Scanner Integration

#### UDP-Based QR Code Scanners
**Protocol**: User Datagram Protocol (UDP)
**Purpose**: Receive QR code data from network-connected scanners in real-time

**Communication Flow**:
```
Scanner Device → UDP Packet → Application UDP Reader → Validation Engine
```

**Configuration Parameters**:
```json
{
  "local_ip": "192.168.1.100",     // Interface to bind to
  "local_port": 5000,              // Port to listen on
  "remote_ip": "192.168.1.50",     // Scanner IP (optional filter)
  "remote_port": 6000              // Scanner port (optional filter)
}
```

**Data Format**:
- **Input**: Raw QR code string via UDP packet
- **Encoding**: UTF-8 text
- **Maximum Size**: 4096 bytes per packet
- **Example**: `"89012345678901234567123"` (ICCID with checksum)

**Implementation Details**:
```python
class UDPReader:
    def __init__(self, local_ip, local_port, remote_ip=None, remote_port=None):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((local_ip, local_port))
        self.socket.settimeout(0.5)  # 500ms timeout
    
    def read_loop(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                if self.should_accept_packet(addr):
                    decoded_data = data.decode('utf-8', errors='ignore').strip()
                    self.callback(decoded_data)
            except socket.timeout:
                continue  # Normal timeout for shutdown checking
```

**Error Handling**:
- Connection timeouts with automatic retry
- Invalid packet filtering
- Network interface binding errors
- Remote device unreachability detection

### Serial Scanner Integration

#### COM Port-Based QR Code Scanners
**Protocol**: RS-232 Serial Communication
**Purpose**: Interface with serial-connected scanning devices for on-demand operations

**Communication Parameters**:
```json
{
  "port": "COM3",           // Serial port identifier
  "baudrate": 115200,       // Communication speed
  "bytesize": 8,           // Data bits
  "parity": "N",           // Parity (None)
  "stopbits": 1,           // Stop bits
  "timeout": 1.0           // Read timeout in seconds
}
```

**Data Processing**:
- **Input**: Serial data stream
- **Cleaning**: Remove non-printable characters (keep 0x20-0x7E)
- **Validation**: Length and format checking
- **Output**: Clean QR code string

**Implementation**:
```python
class ComPortReader:
    def __init__(self, port, baudrate=115200, **kwargs):
        self.serial_instance = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=kwargs.get('timeout', 0.1),
            inter_byte_timeout=0.05
        )
    
    def read_loop(self):
        while self.running:
            if self.serial_instance.in_waiting > 0:
                raw_data = self.serial_instance.read(256)
                decoded_data = raw_data.decode(errors='ignore').strip()
                cleaned_data = re.sub(r'[^\x20-\x7E]', '', decoded_data)
                if cleaned_data:
                    self.callback(cleaned_data)
```

### PLC Integration (Output)

#### UDP-Based Output Signals
**Protocol**: User Datagram Protocol (UDP)
**Purpose**: Send validation results to Programmable Logic Controllers

**Signal Format Configuration**:
```json
{
  "Integers": {
    "single": {
      "OK": "17\r\n",
      "NOT OK": "18\r\n",
      "LAST OK": "19\r\n"
    },
    "half": {
      "OK": "09\r\n",
      "NOT OK": "10\r\n",
      "LAST OK": "11\r\n"
    },
    "quarter": {
      "OK": "05\r\n",
      "NOT OK": "06\r\n",
      "LAST OK": "07\r\n"
    }
  }
}
```

**Output Configuration**:
```json
{
  "local_ip": "192.168.1.100",     // Sending interface
  "local_port": 7000,              // Local port (0 for auto)
  "remote_ip": "192.168.1.200",    // PLC IP address
  "remote_port": 8000              // PLC listening port
}
```

**Signal Transmission Flow**:
```
Validation Result → Format Lookup → UDP Packet → PLC System
```

## Network Communication Protocols

### UDP Communication Protocol

#### Packet Structure
```
UDP Header (8 bytes) + Payload (Variable)
├── Source Port (2 bytes)
├── Destination Port (2 bytes)
├── Length (2 bytes)
├── Checksum (2 bytes)
└── Data (QR Code String)
```

#### Network Interface Management
```python
def get_network_interfaces():
    """Detect available network interfaces"""
    interfaces = []
    for interface in socket.getaddrinfo(socket.gethostname(), None):
        if interface[0] == socket.AF_INET:  # IPv4 only
            ip_address = interface[4][0]
            if not ip_address.startswith('127.'):  # Exclude loopback
                interfaces.append(ip_address)
    return interfaces
```

#### Multi-Interface Support
- **Interface Binding**: Bind to specific network adapter
- **Interface Detection**: Automatic discovery of available interfaces
- **Interface Validation**: Real-time connectivity testing
- **Failover Support**: Automatic interface switching (future enhancement)

### Network Discovery and Validation

#### Ping-Based Device Discovery
```python
def ping_remote_ip_sync(remote_ip, timeout=5):
    """Synchronous ping test for device reachability"""
    if platform.system().lower() == 'windows':
        cmd = f'ping -n 1 -w 2000 {remote_ip}'
    else:
        cmd = f'ping -c 1 -W 2 {remote_ip}'
    
    process = subprocess.Popen(cmd, shell=True, 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(timeout=timeout)
    
    success = process.returncode == 0
    return success, parse_ping_result(stdout, stderr)
```

#### Network Scanning Algorithm
```python
def scan_network_range(base_ip, start_range=1, end_range=254):
    """Scan IP range for responsive devices"""
    base_network = '.'.join(base_ip.split('.')[:-1])
    responsive_devices = []
    
    for i in range(start_range, end_range + 1):
        target_ip = f"{base_network}.{i}"
        success, message = ping_remote_ip_sync(target_ip, timeout=1)
        if success:
            responsive_devices.append({
                'ip': target_ip,
                'status': 'reachable',
                'response_time': extract_response_time(message)
            })
    
    return responsive_devices
```

## Data Communication Methods

### QR Code Data Processing Pipeline

#### Input Data Flow
```
Raw Scanner Data → Cleaning → Checksum Processing → Validation → Logging
```

#### Data Cleaning Algorithm
```python
def clean_qr_data(raw_data):
    """Clean and validate QR code data"""
    # Step 1: Basic cleaning
    cleaned = raw_data.strip()
    
    # Step 2: Remove non-printable characters
    cleaned = re.sub(r'[^\x20-\x7E]', '', cleaned)
    
    # Step 3: Length validation
    if len(cleaned) < 10 or len(cleaned) > 30:
        raise ValueError(f"Invalid QR code length: {len(cleaned)}")
    
    # Step 4: Character set validation
    if not cleaned.isalnum():
        # Allow alphanumeric characters only for ICCIDs
        cleaned = re.sub(r'[^A-Za-z0-9]', '', cleaned)
    
    return cleaned
```

#### Checksum Processing
```python
def process_checksum(qr_code, checksum_digits, scanner_type):
    """Process checksum based on scanner type and configuration"""
    if scanner_type == 'main_scanner':
        # Main scanner strips full checksum_digits (includes secret bit)
        if checksum_digits > 0 and len(qr_code) > checksum_digits:
            return qr_code[:-checksum_digits]
    elif scanner_type == 'ondemand_scanner':
        # On-demand scanner strips checksum_digits - 1 (excludes secret bit)
        strip_count = max(0, checksum_digits - 1)
        if strip_count > 0 and len(qr_code) > strip_count:
            return qr_code[:-strip_count]
    
    return qr_code
```

### File Data Processing

#### CPD File Format Specification
```
Format: Semicolon-delimited text file
Encoding: UTF-8
Header: Required, starts with "NUMCARD"
Columns: NUMCARD (required), ICCID (required), additional columns (optional)

Example:
NUMCARD;ICCID;BATCH;DATE
1;89012345678901234567;B001;20260415
2;89012345678901234568;B001;20260415
```

#### File Parsing Pipeline
```python
def parse_cpd_file(file_path, card_type, rebatch_size=None):
    """Parse CPD file with comprehensive validation"""
    
    # Phase 1: File validation
    validate_file_encoding(file_path)
    validate_file_format(file_path)
    
    # Phase 2: Header processing
    header = extract_header(file_path)
    numcard_idx, iccid_idx = validate_required_columns(header)
    
    # Phase 3: Data extraction
    card_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            if is_data_row(line):
                card = parse_card_row(line, header, numcard_idx, iccid_idx)
                validate_card_data(card, line_num)
                card_data.append(card)
    
    # Phase 4: Card type processing
    return process_by_card_type(card_data, card_type, rebatch_size)
```

### Configuration Data Management

#### Cache System Architecture
```python
class ConfigurationManager:
    """Thread-safe configuration management with atomic operations"""
    
    def __init__(self):
        self.cache_lock = threading.RLock()
        self.cache_file = get_unified_cache_file_path()
        self.auto_save_timer = None
    
    def save_configuration(self, config_data):
        """Atomic configuration save with retry logic"""
        with self.cache_lock:
            for attempt in range(3):
                try:
                    self.atomic_write(config_data)
                    return True
                except Exception as e:
                    if attempt == 2:
                        self.log_error(f"Configuration save failed: {e}")
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
            return False
    
    def atomic_write(self, data):
        """Atomic write operation with temporary file"""
        temp_file = self.cache_file + ".tmp"
        try:
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
            
            os.replace(temp_file, self.cache_file)  # Atomic rename
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
```

## External System Interfaces

### License Validation System

#### License File Format
```
File: license.dat
Format: Encrypted binary data
Contents: Machine ID binding, expiration date, feature flags
Location: Application directory
```

#### License Validation Process
```python
def validate_license():
    """Validate software license against machine hardware"""
    try:
        # Step 1: Generate machine ID
        machine_id = generate_machine_id()
        
        # Step 2: Read license file
        license_data = read_license_file("license.dat")
        
        # Step 3: Decrypt and validate
        decrypted_license = decrypt_license(license_data)
        
        # Step 4: Check machine binding
        if decrypted_license['machine_id'] != machine_id:
            return False, "License not valid for this machine"
        
        # Step 5: Check expiration
        if decrypted_license['expiry_date'] < datetime.now():
            return False, "License has expired"
        
        return True, "License valid"
        
    except Exception as e:
        return False, f"License validation error: {e}"
```

#### Machine ID Generation
```python
def generate_machine_id():
    """Generate unique machine identifier"""
    try:
        # Windows-specific implementation
        import winreg
        
        # Get processor ID
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
        processor_id, _ = winreg.QueryValueEx(key, "ProcessorNameString")
        winreg.CloseKey(key)
        
        # Get system UUID
        cmd = 'wmic csproduct get uuid'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        uuid = result.stdout.split('\n')[1].strip()
        
        # Generate hash
        machine_string = f"{processor_id}:{uuid}"
        return hashlib.sha256(machine_string.encode()).hexdigest()[:16]
        
    except Exception:
        return "DEFAULT_MACHINE_ID"
```

### Windows System Integration

#### Theme Detection
```python
def get_windows_theme():
    """Detect Windows theme preference"""
    if sys.platform != 'win32':
        return "dark"  # Default for non-Windows
    
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                           r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        theme_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        
        return "light" if theme_value == 1 else "dark"
    except Exception:
        return "dark"  # Default fallback
```

#### Single Instance Control
```python
def enforce_single_instance():
    """Prevent multiple application instances"""
    import tempfile
    from PyQt6.QtCore import QLockFile
    
    lock_file_path = os.path.join(tempfile.gettempdir(), 
                                 "CardSequenceValidator.lock")
    lock_file = QLockFile(lock_file_path)
    lock_file.setStaleLockTime(0)  # No stale lock timeout
    
    if not lock_file.tryLock(100):  # Try for 100ms
        return False, "Another instance is already running"
    
    return True, lock_file
```

## API Response Formats

### Validation Result Format
```json
{
  "timestamp": "2026-04-15T14:30:25.123Z",
  "head_id": "A",
  "scanned_code": "89012345678901234567",
  "expected_code": "89012345678901234567",
  "status": "OK",
  "card_index": 150,
  "scan_direction": "top_to_bottom",
  "output_signal": "09\r\n"
}
```

### Network Status Format
```json
{
  "interface": "192.168.1.100",
  "status": "connected",
  "remote_devices": [
    {
      "ip": "192.168.1.50",
      "port": 6000,
      "type": "scanner",
      "reachable": true,
      "response_time": "2ms"
    },
    {
      "ip": "192.168.1.200",
      "port": 8000,
      "type": "plc",
      "reachable": true,
      "response_time": "5ms"
    }
  ]
}
```

### Configuration Export Format
```json
{
  "export_timestamp": "2026-04-15T14:30:25.123Z",
  "application_version": "3.1",
  "heads": {
    "head_a": {
      "card_type": "half",
      "network_config": {
        "main_scanner": {
          "local_ip": "192.168.1.100",
          "local_port": 5000,
          "remote_ip": "192.168.1.50",
          "remote_port": 6000
        },
        "output": {
          "local_ip": "192.168.1.100",
          "local_port": 7000,
          "remote_ip": "192.168.1.200",
          "remote_port": 8000
        }
      },
      "file_config": {
        "selected_file": "production_batch_001.cpd",
        "scan_direction": "top_to_bottom",
        "checksum_digits": 1
      }
    },
    "head_b": {
      // Similar structure for Head B
    }
  }
}
```

## Integration Testing Utilities

### Network Testing Tools
```python
def test_udp_communication(local_ip, local_port, remote_ip, remote_port):
    """Test UDP communication between application and remote device"""
    try:
        # Create test socket
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_socket.bind((local_ip, local_port))
        test_socket.settimeout(5.0)
        
        # Send test message
        test_message = "TEST_MESSAGE"
        test_socket.sendto(test_message.encode(), (remote_ip, remote_port))
        
        # Wait for response
        response, addr = test_socket.recvfrom(1024)
        
        return True, f"Communication successful: {response.decode()}"
        
    except socket.timeout:
        return False, "Communication timeout - no response from remote device"
    except Exception as e:
        return False, f"Communication error: {e}"
    finally:
        test_socket.close()
```

### Serial Testing Tools
```python
def test_serial_communication(port, baudrate=115200):
    """Test serial port communication"""
    try:
        # Open serial port
        ser = serial.Serial(port, baudrate, timeout=2.0)
        
        # Send test command
        test_command = "TEST\r\n"
        ser.write(test_command.encode())
        
        # Read response
        response = ser.readline().decode().strip()
        
        return True, f"Serial communication successful: {response}"
        
    except serial.SerialException as e:
        return False, f"Serial communication error: {e}"
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
```

## Performance Considerations

### Network Performance Optimization
- **Buffer Sizes**: Optimized for typical QR code lengths (4096 bytes)
- **Timeout Values**: Balanced for responsiveness and reliability
- **Connection Pooling**: Reuse connections where possible
- **Error Recovery**: Automatic retry with exponential backoff

### Serial Performance Optimization
- **Baud Rate Selection**: 115200 bps for optimal speed/reliability balance
- **Buffer Management**: Efficient buffer clearing and data processing
- **Timeout Configuration**: Responsive timeouts for real-time operation
- **Thread Safety**: Proper synchronization for concurrent access

### Data Processing Performance
- **Lookup Tables**: O(1) hash table lookups for validation
- **Memory Management**: Efficient data structures and cleanup
- **Caching Strategy**: Intelligent caching with automatic cleanup
- **Batch Processing**: Optimized for high-throughput scenarios

---

*This APIs and integrations documentation provides comprehensive information about all external interfaces, communication protocols, and integration methods used in the Card Sequence Validator system.*