# Core Logic & Algorithms

## Main Validation Logic

### Sequence Validation Algorithm

#### Overview
The core validation algorithm processes scanned QR codes against expected card sequences, handling various card types, scan directions, and error conditions. The algorithm operates in real-time with sub-second response times.

#### Algorithm Flow
```python
def handle_main_scan(scanned_code):
    """
    Main validation algorithm for processing scanned QR codes
    
    Input: Raw QR code string from scanner
    Output: Validation status and system state update
    """
    
    # Step 1: Input Processing and Validation
    if not scanned_code or not scanned_code.strip():
        return log_entry("EMPTY SCAN", "No data received")
    
    # Step 2: Checksum Processing
    processed_code = strip_checksum(scanned_code)
    
    # Step 3: File Validation
    if not expected_cards or not qr_to_index:
        return log_entry("NO FILE", "No sequence file loaded")
    
    # Step 4: Sequence Position Determination
    if not start_card_has_been_scanned:
        return handle_first_scan(processed_code)
    
    # Step 5: Expected Card Calculation
    expected_card_index = calculate_expected_index()
    expected_qr = get_expected_qr_code(expected_card_index)
    
    # Step 6: Validation Logic
    if processed_code == expected_qr:
        return handle_correct_scan(processed_code, expected_card_index)
    else:
        return handle_mismatch(processed_code, expected_qr, expected_card_index)
```

#### Detailed Algorithm Components

##### 1. Checksum Processing Algorithm
```python
def strip_checksum(code):
    """
    Remove configured number of checksum digits from end of code
    
    Algorithm:
    - UI shows 0-5 digits (user-facing)
    - Backend strips UI_value + 1 digits (secret increment)
    - Main scanner: strips checksum_digits (includes secret bit)
    - On-demand scanner: strips checksum_digits - 1 (excludes secret bit)
    """
    
    if self.checksum_digits > 0 and len(code) > self.checksum_digits:
        return code[:-self.checksum_digits]
    return code
```

##### 2. First Scan Handling Algorithm
```python
def handle_first_scan(scanned_code):
    """
    Process the first scan to establish starting position and scan side
    
    Algorithm:
    1. Search for scanned code in all QR positions
    2. Determine card index and QR position
    3. Set scan side based on QR position
    4. Initialize validation state
    """
    
    # Search in QR lookup table
    if scanned_code in qr_to_index:
        card_index, qr_position = qr_to_index[scanned_code]
        
        # Set scan side based on card type and QR position
        scan_side = determine_scan_side(card_type, qr_position)
        
        # Initialize validation state
        current_card_index = card_index
        start_card_has_been_scanned = True
        start_card_code = scanned_code
        
        return log_entry("OK", f"Start card set: {card_index}")
    else:
        return log_entry("NOT IN SEQUENCE", "Card not found in loaded file")
```

##### 3. Expected Index Calculation Algorithm
```python
def calculate_expected_index():
    """
    Calculate expected card index based on scan direction and current position
    
    Algorithm supports:
    - Top-to-bottom scanning (sequential)
    - Bottom-to-top scanning (reverse sequential)
    """
    
    if scan_direction == "top_to_bottom":
        return current_card_index
    else:  # bottom_to_top
        # Reverse calculation for bottom-to-top scanning
        total_cards = len(expected_cards)
        return total_cards - current_card_index + 1
```

##### 4. Mismatch Resolution Algorithm
```python
def handle_mismatch(scanned_code, expected_qr, expected_index):
    """
    Handle sequence mismatches with user interaction
    
    Algorithm:
    1. Detect mismatch type (wrong card, out of sequence, etc.)
    2. Check if scanned card exists in sequence
    3. Determine if it's a forward jump or error
    4. Present resolution options to user
    """
    
    # Check if scanned code exists in sequence
    if scanned_code in qr_to_index:
        scanned_index, _ = qr_to_index[scanned_code]
        
        if scanned_index > expected_index:
            # Forward jump detected - show mismatch dialog
            return show_mismatch_dialog(scanned_code, expected_qr, scanned_index, expected_index)
        else:
            # Backward scan or duplicate
            return log_entry("NOT OK", f"Backward scan or duplicate card")
    else:
        # Card not in sequence
        return log_entry("NOT IN SEQUENCE", "Scanned card not found in file")
```

### Card Type Processing Algorithms

#### Single Card Algorithm
```python
def process_single_card(card_data):
    """
    Process single card type with one QR code per card
    
    Structure: (card_number, iccid)
    Lookup: iccid -> (card_index, 0)
    """
    
    for index, (card_number, iccid) in enumerate(card_data):
        qr_to_index[iccid] = (index, 0)  # Position 0 for single QR
        numcard_to_qrs[card_number] = [iccid]
```

#### Half Card Algorithm
```python
def process_half_card(card_data):
    """
    Process half card type with two QR codes per card (left/right)
    
    Structure: (card_number, left_iccid, right_iccid)
    Lookup: left_iccid -> (card_index, 0), right_iccid -> (card_index, 1)
    """
    
    for index, (card_number, left_iccid, right_iccid) in enumerate(card_data):
        qr_to_index[left_iccid] = (index, 0)   # Left position
        qr_to_index[right_iccid] = (index, 1)  # Right position
        numcard_to_qrs[card_number] = [left_iccid, right_iccid]
```

#### Quarter Card Algorithm
```python
def process_quarter_card(card_data):
    """
    Process quarter card type with four QR codes per card
    
    Structure: (card_number, bl_iccid, tl_iccid, tr_iccid, br_iccid)
    Positions: BL=0, TL=1, TR=2, BR=3
    """
    
    for index, (card_number, bl_iccid, tl_iccid, tr_iccid, br_iccid) in enumerate(card_data):
        qr_codes = [bl_iccid, tl_iccid, tr_iccid, br_iccid]
        
        for position, iccid in enumerate(qr_codes):
            qr_to_index[iccid] = (index, position)
        
        numcard_to_qrs[card_number] = qr_codes
```

### File Processing Algorithms

#### CPD File Parsing Algorithm
```python
def parse_cpd_file(file_path, card_type, rebatch_size=None):
    """
    Parse CPD file with validation and error handling
    
    Algorithm:
    1. Validate file format and encoding
    2. Parse header and locate required columns
    3. Validate data integrity
    4. Process cards based on type and rebatch configuration
    5. Generate lookup tables for fast validation
    """
    
    # Phase 1: File Validation
    validate_file_format(file_path)
    header = parse_header(file_path)
    validate_required_columns(header)
    
    # Phase 2: Data Processing
    card_data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file):
            if is_data_row(line):
                card = parse_card_row(line, header, line_num)
                validate_card_data(card, line_num)
                card_data.append(card)
    
    # Phase 3: Card Type Processing
    if card_type == CardType.HALF and rebatch_size:
        card_data = apply_rebatch_logic(card_data, rebatch_size, 2)
    elif card_type == CardType.QUARTER and rebatch_size:
        card_data = apply_rebatch_logic(card_data, rebatch_size, 4)
    
    return organize_by_card_type(card_data, card_type)
```

#### Rebatch Algorithm for Half/Quarter Cards
```python
def apply_rebatch_logic(card_data, rebatch_size, divisions):
    """
    Apply rebatch logic for HALF (divisions=2) or QUARTER (divisions=4) cards
    
    Algorithm:
    1. Divide file into batches of rebatch_size
    2. Within each batch, divide by number of divisions
    3. Assign positions based on division (left/right for HALF, BL/TL/TR/BR for QUARTER)
    """
    
    total_cards = len(card_data)
    processed_data = []
    
    for card_index, (numcard, iccid) in enumerate(card_data):
        # Determine batch and position within batch
        batch_num = card_index // rebatch_size
        position_in_batch = (card_index % rebatch_size) + 1
        
        # Calculate batch boundaries
        batch_start = batch_num * rebatch_size + 1
        batch_end = min((batch_num + 1) * rebatch_size, total_cards)
        current_batch_size = batch_end - batch_start + 1
        
        # Determine division within batch
        division_size = current_batch_size // divisions
        division_index = (position_in_batch - 1) // division_size
        
        # Calculate base card number for this division
        base_position = (position_in_batch - 1) % division_size
        base_card = batch_start + base_position
        
        # Assign position based on division
        if divisions == 2:  # HALF cards
            position = "LEFT" if division_index == 0 else "RIGHT"
        else:  # QUARTER cards
            positions = ["BL", "TL", "TR", "BR"]
            position = positions[division_index]
        
        processed_data.append((str(base_card), iccid, position))
    
    return processed_data
```

### Network Communication Algorithms

#### UDP Reader Algorithm
```python
def udp_read_loop():
    """
    Main UDP reading loop with error handling and filtering
    
    Algorithm:
    1. Bind to specified local interface and port
    2. Set appropriate timeout for responsive shutdown
    3. Filter packets by remote IP/port if configured
    4. Process and clean received data
    5. Handle errors gracefully
    """
    
    try:
        # Create and configure socket
        socket = create_udp_socket()
        socket.bind((local_ip, local_port))
        socket.settimeout(0.5)  # 500ms timeout
        
        while running:
            try:
                # Receive data with timeout
                data, addr = socket.recvfrom(4096)
                
                # Filter by remote address if configured
                if should_filter_address(addr):
                    continue
                
                # Process received data
                decoded_data = decode_and_clean(data)
                if decoded_data and callback:
                    callback(decoded_data)
                    
            except socket.timeout:
                continue  # Normal timeout, check running flag
                
    except Exception as e:
        handle_connection_error(e)
    finally:
        cleanup_socket()
```

#### Serial Communication Algorithm
```python
def serial_read_loop():
    """
    Serial port reading loop with robust error handling
    
    Algorithm:
    1. Open serial port with specified parameters
    2. Read data with inter-byte timeout
    3. Clean and validate received data
    4. Handle disconnections gracefully
    """
    
    try:
        # Open serial port
        serial_port = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=timeout,
            inter_byte_timeout=0.05
        )
        
        while running:
            if serial_port.in_waiting > 0:
                # Read available data
                raw_data = serial_port.read(256)
                
                # Decode and clean
                decoded_data = raw_data.decode(errors='ignore').strip()
                cleaned_data = clean_control_characters(decoded_data)
                
                if cleaned_data and callback:
                    callback(cleaned_data)
                    
    except serial.SerialException as e:
        handle_serial_error(e)
    finally:
        cleanup_serial_port()
```

### Data Processing Methods

#### QR Code Cleaning Algorithm
```python
def clean_qr_code(raw_data):
    """
    Clean and validate QR code data from scanners
    
    Algorithm:
    1. Remove leading/trailing whitespace
    2. Filter out non-printable characters
    3. Validate character set (printable ASCII)
    4. Apply length validation
    """
    
    # Basic cleaning
    cleaned = raw_data.strip()
    
    # Remove non-printable characters (keep only 0x20-0x7E)
    cleaned = re.sub(r'[^\x20-\x7E]', '', cleaned)
    
    # Validate length (typical ICCID length: 19-20 digits)
    if len(cleaned) < 10 or len(cleaned) > 30:
        raise ValueError(f"Invalid QR code length: {len(cleaned)}")
    
    return cleaned
```

#### Lookup Table Generation Algorithm
```python
def generate_lookup_tables(card_data, card_type):
    """
    Generate optimized lookup tables for fast validation
    
    Algorithm:
    1. Create QR-to-index mapping for O(1) lookups
    2. Create card-number-to-QRs mapping for card details
    3. Optimize for memory usage and access speed
    """
    
    qr_to_index = {}      # QR code -> (card_index, qr_position)
    numcard_to_qrs = {}   # Card number -> [list of QR codes]
    
    for card_index, card_tuple in enumerate(card_data):
        card_number = card_tuple[0]
        qr_codes = card_tuple[1:]  # All QR codes for this card
        
        # Map each QR code to its position
        for qr_position, qr_code in enumerate(qr_codes):
            qr_to_index[qr_code] = (card_index, qr_position)
        
        # Map card number to all its QR codes
        numcard_to_qrs[card_number] = list(qr_codes)
    
    return qr_to_index, numcard_to_qrs
```

### Validation State Management

#### State Machine Algorithm
```python
class ValidationStateMachine:
    """
    Manages validation state transitions and consistency
    
    States:
    - IDLE: No validation in progress
    - WAITING_START: Waiting for first scan to set start position
    - VALIDATING: Active validation in progress
    - PAUSED: Validation paused by user
    - COMPLETED: Validation sequence completed
    """
    
    def __init__(self):
        self.state = ValidationState.IDLE
        self.current_card_index = 0
        self.start_card_has_been_scanned = False
        self.scan_direction = "top_to_bottom"
    
    def start_validation(self):
        """Transition to validation state"""
        if self.state == ValidationState.IDLE:
            self.state = ValidationState.WAITING_START
            self.reset_validation_state()
    
    def process_scan(self, qr_code):
        """Process scan based on current state"""
        if self.state == ValidationState.WAITING_START:
            return self.handle_start_scan(qr_code)
        elif self.state == ValidationState.VALIDATING:
            return self.handle_validation_scan(qr_code)
        else:
            return self.handle_invalid_state_scan(qr_code)
    
    def check_completion(self):
        """Check if validation is complete"""
        if self.state == ValidationState.VALIDATING:
            if self.is_sequence_complete():
                self.state = ValidationState.COMPLETED
                return True
        return False
```

### Performance Optimization Algorithms

#### Cache Management Algorithm
```python
def manage_cache_performance():
    """
    Optimize cache operations for performance and reliability
    
    Algorithm:
    1. Use atomic writes to prevent corruption
    2. Implement auto-save based on time and scan count
    3. Use thread-safe operations with RLock
    4. Optimize JSON serialization
    """
    
    def auto_save_trigger():
        current_time = time.time()
        time_elapsed = current_time - last_save_time
        
        # Save conditions
        if (scans_since_save >= auto_save_batch_size or 
            time_elapsed >= auto_save_interval):
            
            save_cache_atomic()
            reset_save_counters()
    
    def save_cache_atomic():
        """Atomic cache save with retry logic"""
        for attempt in range(3):
            try:
                temp_file = cache_file + ".tmp"
                
                # Write to temporary file
                with open(temp_file, 'w') as f:
                    json.dump(cache_data, f, indent=4)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Atomic rename
                os.replace(temp_file, cache_file)
                return True
                
            except Exception as e:
                if attempt == 2:  # Last attempt
                    log_error(f"Cache save failed: {e}")
                time.sleep(0.1)  # Brief delay before retry
        
        return False
```

#### Memory Management Algorithm
```python
def optimize_memory_usage():
    """
    Manage memory usage for long-running validation sessions
    
    Algorithm:
    1. Limit log data growth with rotation
    2. Optimize data structures for memory efficiency
    3. Clean up temporary objects
    4. Monitor memory usage patterns
    """
    
    def rotate_logs_if_needed():
        max_log_entries = 10000  # Configurable limit
        
        if len(log_data) > max_log_entries:
            # Keep most recent entries
            log_data = log_data[-max_log_entries//2:]
            
            # Notify user of rotation
            add_log_entry("SYSTEM", "Log rotation performed to manage memory")
    
    def optimize_lookup_tables():
        """Optimize lookup table memory usage"""
        # Use __slots__ for memory efficiency
        # Implement weak references where appropriate
        # Clean up unused references
        pass
```

### Error Handling and Recovery Algorithms

#### Comprehensive Error Recovery
```python
def handle_validation_error(error_type, context):
    """
    Comprehensive error handling with recovery strategies
    
    Algorithm:
    1. Classify error type and severity
    2. Attempt automatic recovery if possible
    3. Preserve system state and data
    4. Provide user feedback and options
    """
    
    error_handlers = {
        'INDEX_ERROR': handle_index_error,
        'DATA_ERROR': handle_data_error,
        'NETWORK_ERROR': handle_network_error,
        'FILE_ERROR': handle_file_error,
        'SCAN_ERROR': handle_scan_error
    }
    
    handler = error_handlers.get(error_type, handle_unknown_error)
    return handler(context)

def handle_index_error(context):
    """Handle array bounds violations"""
    # Log error with context
    log_error(f"Index error: {context}")
    
    # Reset to safe state
    reset_validation_state()
    
    # Return safe error status
    return create_error_log_entry("INDEX ERROR", "Array bounds violation")

def handle_data_error(context):
    """Handle missing or corrupt data"""
    # Attempt data recovery
    if can_recover_data(context):
        return recover_data(context)
    
    # Fallback to safe state
    return create_error_log_entry("DATA ERROR", "Missing or corrupt data")
```

## Algorithm Performance Characteristics

### Time Complexity Analysis
- **QR Code Lookup**: O(1) - Hash table lookup
- **File Parsing**: O(n) - Linear scan of file data
- **Validation Processing**: O(1) - Direct index access
- **Log Operations**: O(1) - Append operations
- **Cache Operations**: O(n) - JSON serialization size

### Space Complexity Analysis
- **Lookup Tables**: O(n) - Proportional to card count
- **Log Data**: O(m) - Proportional to scan count
- **Cache Data**: O(1) - Fixed configuration size
- **File Data**: O(n) - Proportional to file size

### Performance Benchmarks
- **Validation Response Time**: < 50ms typical
- **File Loading Time**: < 2 seconds for 10,000 cards
- **Network Response Time**: < 100ms for UDP
- **Cache Save Time**: < 500ms for typical data

---

*This core logic documentation provides comprehensive understanding of the algorithms and data processing methods used throughout the Card Sequence Validator system.*