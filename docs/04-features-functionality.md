# Features & Functionality

## Complete Feature List

### Core Validation Features
1. **Dual-Head Validation System**
2. **Multi-Card Type Support**
3. **Real-Time Sequence Validation**
4. **Bidirectional Scanning**
5. **Checksum Processing**
6. **Automatic Scan Completion**

### Network and Hardware Integration
7. **UDP Network Communication**
8. **Serial COM Port Support**
9. **Output Signal Generation**
10. **Multi-Interface Network Support**
11. **Real-Time Connectivity Testing**

### Data Management
12. **CPD File Processing**
13. **Comprehensive Logging System**
14. **CSV Export Functionality**
15. **Session Recovery**
16. **Configuration Persistence**

### User Interface Features
17. **Split-Screen Dual Interface**
18. **Real-Time Status Display**
19. **Theme Support (Dark/Light)**
20. **Interactive Mismatch Resolution**
21. **Card Detail Scanning**
22. **Range Counting Tools**

### Advanced Features
23. **Password-Protected Configuration**
24. **License Validation System**
25. **Single Instance Control**
26. **Automatic Cache Management**
27. **Network Device Discovery**

---

## Detailed Feature Descriptions

### 1. Dual-Head Validation System

**Description**: Independent operation of two validation heads (Head A - Right, Head B - Left) for simultaneous card sequence validation.

**Working**: 
- Each head maintains separate configuration, file loading, and validation state
- Independent network and serial connections
- Separate logging and export capabilities
- Color-coded UI identification (Green for Head A, Blue for Head B)

**Input**: 
- Separate CPD files for each head
- Independent scanner connections
- Individual configuration settings

**Output**: 
- Simultaneous validation results
- Independent log files
- Separate status reporting
- Dual PLC output signals

**Use Cases**:
- High-throughput production lines
- Parallel quality control processes
- Independent product validation streams

---

### 2. Multi-Card Type Support

**Description**: Support for three different card configurations with varying QR code layouts.

**Working**:
- **Single Cards**: One QR code per card (ICCID)
- **Half Cards**: Two QR codes per card (Left ICCID, Right ICCID)
- **Quarter Cards**: Four QR codes per card (Bottom-Left, Top-Left, Top-Right, Bottom-Right ICCIDs)

**Input**: 
- Card type selection during file loading
- CPD files with appropriate ICCID columns
- Scanner data matching card configuration

**Output**: 
- Validation results based on card type
- Appropriate output signals for each type
- Card-specific logging information

**Configuration**:
```
Single Card Output Signals:
- OK: 17, NOT OK: 18, LAST OK: 19

Half Card Output Signals:
- OK: 09, NOT OK: 10, LAST OK: 11

Quarter Card Output Signals:
- OK: 05, NOT OK: 06, LAST OK: 07
```

---

### 3. Real-Time Sequence Validation

**Description**: Immediate validation of scanned QR codes against expected card sequences with comprehensive status reporting.

**Working**:
1. Scanner sends QR code data via UDP or serial
2. System strips configured checksum digits
3. Validates against expected sequence position
4. Determines validation status
5. Sends output signal to PLC
6. Updates UI and logs result

**Input**: 
- QR code data from scanners
- Expected card sequence from CPD file
- Current scan position and direction

**Output**: 
- Validation status codes:
  - `OK`: Correct card in sequence
  - `NOT OK`: Wrong card or sequence error
  - `OK (JUMPED)`: Approved skip-ahead in sequence
  - `SKIPPED`: Cards jumped over in sequence
  - `EXTRA SCAN`: Scanning beyond sequence end
  - `NOT IN SEQUENCE`: Card not found in loaded file
  - `NO FILE`: No sequence file loaded

**Performance**: 
- Sub-second validation response time
- Concurrent processing for dual heads
- Real-time UI updates

---

### 4. Bidirectional Scanning

**Description**: Support for both top-to-bottom and bottom-to-top scanning directions with automatic sequence adjustment.

**Working**:
- **Top-to-Bottom**: Standard sequential scanning from first to last card
- **Bottom-to-Top**: Reverse scanning from last to first card
- Automatic sequence reversal for bottom-to-top mode
- Direction-aware completion detection

**Input**: 
- Scan direction selection in File Management
- First scanned card determines starting position
- Subsequent scans follow selected direction

**Output**: 
- Direction-appropriate validation results
- Correct sequence progression
- Proper completion detection

**Configuration**:
- Toggle button in File Management window
- Visual indicators for current direction
- Preview window shows direction-adjusted sequence

---

### 5. Checksum Processing

**Description**: Configurable stripping of checksum digits from scanned QR codes to match file ICCIDs.

**Working**:
1. Scanner reads QR code with appended checksum digits
2. System strips configured number of digits (0-5) from the end
3. Validates trimmed ICCID against file data
4. Logs trimmed value only

**Input**: 
- Checksum digit configuration (0-5 digits)
- Scanned QR codes with checksums
- File ICCIDs without checksums

**Output**: 
- Validation using trimmed ICCIDs
- Logs show trimmed values
- Original checksums are discarded

**Configuration Example**:
```
Checksum Digits: 2
Scanned: 89012345678901234567123
File ICCID: 89012345678901234567
Trimmed: 89012345678901234567
Result: Match ✓
```

---

### 6. Automatic Scan Completion

**Description**: Intelligent detection of validation completion with statistical summary display.

**Working**:
1. Monitors scan progress against total card count
2. Detects when last card in sequence is successfully scanned
3. Automatically stops scanning process
4. Displays completion dialog with statistics

**Input**: 
- Successful scan of final card in sequence
- Complete validation session data

**Output**: 
- Completion dialog showing:
  - Total scans performed
  - Successful validations
  - Failed validations
  - Skipped cards
- Automatic scanning termination

**Statistics Calculation**:
```
Total Scans: All scan entries
Successful: OK + OK (JUMPED) status
Failed: NOT OK + NO FILE + EXTRA SCAN + NOT IN SEQUENCE
Skipped: SKIPPED status cards
```

---

### 7. UDP Network Communication

**Description**: Network-based communication with scanners and PLCs using UDP protocol.

**Working**:
- Binds to specified local IP and port for incoming data
- Filters packets by remote IP/port if configured
- Processes received QR code data in real-time
- Sends validation results to configured output destinations

**Input**: 
- Network configuration (Local IP, Local Port, Remote IP, Remote Port)
- UDP packets containing QR code data
- Network interface selection

**Output**: 
- Processed QR code validation
- UDP packets to PLC systems
- Connection status updates
- Network diagnostic information

**Configuration Parameters**:
```
Main Scanner Input:
- Local IP: 192.168.1.100 (listening interface)
- Local Port: 5000 (listening port)
- Remote IP: 192.168.1.50 (scanner IP)
- Remote Port: 6000 (scanner port)

Output Configuration:
- Local IP: 192.168.1.100 (sending interface)
- Local Port: 7000 (sending port)
- Remote IP: 192.168.1.200 (PLC IP)
- Remote Port: 8000 (PLC port)
```

---

### 8. Serial COM Port Support

**Description**: Serial communication interface for on-demand scanners and legacy hardware integration.

**Working**:
- Configurable serial parameters (baud rate, data bits, parity, stop bits)
- Real-time data reception and processing
- Automatic COM port detection and validation
- Thread-safe serial communication

**Input**: 
- COM port selection and configuration
- Serial data from connected scanners
- Baud rate and communication parameters

**Output**: 
- Processed scan data for validation
- Connection status indicators
- Serial communication diagnostics

**Supported Parameters**:
```
Baud Rates: 9600, 19200, 38400, 57600, 115200
Data Bits: 8
Parity: None (N)
Stop Bits: 1
Timeout: 1 second
```

---

### 9. Output Signal Generation

**Description**: Configurable output signals sent to PLCs and control systems based on validation results.

**Working**:
1. Validation result determines signal type
2. Looks up appropriate signal from configuration
3. Sends formatted signal via UDP or serial
4. Logs transmission for audit trail

**Input**: 
- Validation status (OK, NOT OK, etc.)
- Card type configuration
- Output format selection

**Output**: 
- Formatted signals to PLC systems
- Transmission confirmation
- Error handling for failed transmissions

**Signal Formats** (from `output_formats.json`):
```json
{
  "Integers": {
    "single": {"OK": "17\r\n", "NOT OK": "18\r\n"},
    "half": {"OK": "09\r\n", "NOT OK": "10\r\n"},
    "quarter": {"OK": "05\r\n", "NOT OK": "06\r\n"}
  }
}
```

---

### 10. Multi-Interface Network Support

**Description**: Support for multiple network interfaces with automatic detection and configuration.

**Working**:
- Detects all available network interfaces
- Populates dropdown menus with valid IP addresses
- Supports binding to specific interfaces
- Handles multi-NIC environments correctly

**Input**: 
- System network interface enumeration
- User interface selection
- Network adapter configuration

**Output**: 
- Available IP address lists
- Interface-specific binding
- Network connectivity validation

**Features**:
- Automatic interface discovery
- IPv4 address validation
- Interface status monitoring
- Multi-adapter support

---

### 11. Real-Time Connectivity Testing

**Description**: Live network connectivity testing with ping validation and status reporting.

**Working**:
- Background ping operations to remote devices
- Real-time status updates in UI
- Connectivity state caching
- Automatic retry mechanisms

**Input**: 
- Remote IP addresses for testing
- Ping timeout configuration
- Test interval settings

**Output**: 
- Connectivity status indicators
- Ping response times
- Network diagnostic messages
- Connection state persistence

**Status Indicators**:
- 🟢 Green: Device reachable
- 🟡 Orange: Device unreachable
- 🔴 Red: Connection error
- ⚪ Gray: Unknown status

---

### 12. CPD File Processing

**Description**: Comprehensive processing of Card Production Data files with validation and error handling.

**Working**:
1. File format validation and header parsing
2. Data integrity checking and error reporting
3. Card type-specific data organization
4. Lookup table generation for fast validation

**Input**: 
- CPD files in semicolon-delimited format
- Card type selection
- Rebatch size configuration (optional)

**Output**: 
- Parsed card sequence data
- Validation lookup tables
- File processing status
- Error messages for invalid files

**File Format Requirements**:
```
Header: NUMCARD;ICCID;[other columns]
Data: 1;89012345678901234567;...
      2;89012345678901234568;...
```

**Validation Checks**:
- Header presence and format
- NUMCARD and ICCID column existence
- Data row completeness
- Numeric NUMCARD validation
- Non-empty ICCID validation

---

### 13. Comprehensive Logging System

**Description**: Detailed logging of all validation events with timestamps, status codes, and audit trail capabilities.

**Working**:
- Real-time log entry creation for each scan
- Structured data format for analysis
- Memory-based storage during session
- Automatic log rotation and management

**Input**: 
- Validation events and results
- Scanner data and timestamps
- System status changes

**Output**: 
- Structured log entries
- Real-time UI display
- Export-ready data format
- Statistical summaries

**Log Entry Structure**:
```json
{
  "timestamp": "2026-04-15 14:30:25",
  "scanned_code": "89012345678901234567",
  "expected_code": "89012345678901234567",
  "status": "OK",
  "card_index": 150,
  "scan_direction": "top_to_bottom"
}
```

---

### 14. CSV Export Functionality

**Description**: Export validation logs to CSV format for analysis, reporting, and compliance documentation.

**Working**:
1. Converts in-memory log data to CSV format
2. Adds headers and metadata
3. Saves to user-specified location
4. Provides export confirmation and statistics

**Input**: 
- Validation log data
- Export location selection
- File naming preferences

**Output**: 
- CSV files with validation history
- Export success confirmation
- File location information
- Export statistics

**CSV Format**:
```csv
Timestamp,Scanned Code,Expected Code,Status,Card Index,Direction
2026-04-15 14:30:25,89012345678901234567,89012345678901234567,OK,150,top_to_bottom
```

---

### 15. Session Recovery

**Description**: Ability to recover and resume validation sessions after application restart or crash.

**Working**:
- Preserves log data across application restarts
- Offers resume or fresh start options
- Restores scan position from log analysis
- Maintains configuration and file associations

**Input**: 
- Previous session log data
- File path associations
- User recovery preferences

**Output**: 
- Restored validation state
- Continued scan position
- Preserved configuration
- Recovery status confirmation

**Recovery Options**:
- **Continue from Last Use**: Resume from last successful scan
- **Fresh Start**: Clear logs and restart validation
- **Export and Clear**: Save logs before starting fresh

---

### 16. Configuration Persistence

**Description**: Automatic saving and restoration of system configuration across application sessions.

**Working**:
- Unified cache system for both validation heads
- Atomic write operations for data integrity
- Thread-safe configuration access
- Automatic migration from old formats

**Input**: 
- Configuration changes from UI
- System state updates
- User preference modifications

**Output**: 
- Persistent configuration storage
- Automatic restoration on startup
- Configuration validation and migration
- Error recovery for corrupted settings

**Cache Location**: `%LOCALAPPDATA%\YourCompany\CardSequenceValidator\app_cache_unified.json`

---

### 17. Split-Screen Dual Interface

**Description**: Dedicated user interface panels for independent operation of both validation heads.

**Working**:
- Left panel for Head B (Blue theme)
- Right panel for Head A (Green theme)
- Independent controls and status displays
- Synchronized theme and clock widgets

**Input**: 
- User interactions with head-specific controls
- Configuration changes per head
- File operations for each head

**Output**: 
- Head-specific status displays
- Independent operation controls
- Color-coded identification
- Unified navigation interface

**Interface Layout**:
```
┌─────────────────────────────────────────────────────────┐
│                    Header & Navigation                   │
├──────────────────────┬──────────────────────────────────┤
│     Head B (Left)    │        Head A (Right)           │
│    Blue Theme        │       Green Theme               │
│                      │                                 │
│  - File Management   │    - File Management            │
│  - Network Config    │    - Network Config             │
│  - Scanner Logging   │    - Scanner Logging            │
│  - Status Display    │    - Status Display             │
└──────────────────────┴──────────────────────────────────┘
```

---

### 18. Real-Time Status Display

**Description**: Live status indicators showing system health, connectivity, and operational state for both validation heads.

**Working**:
- Continuous monitoring of system components
- Real-time UI updates via Qt signals
- Color-coded status indicators
- Detailed status messages

**Input**: 
- System component states
- Network connectivity status
- Hardware connection status
- Validation process status

**Output**: 
- Visual status indicators
- Status text descriptions
- Color-coded health indicators
- Real-time updates

**Status Categories**:
- **Scanner Status**: Idle/Scanning
- **File Status**: Loaded/Not Loaded/File Name
- **Input Port**: Connected/Not Connected/IP:Port
- **Output Port**: Connected/Not Connected/IP:Port
- **Scan Card Port**: Connected/Not Connected/COM Port

---

### 19. Theme Support (Dark/Light)

**Description**: User-selectable visual themes for different working environments and user preferences.

**Working**:
- System theme detection on Windows
- Manual theme switching capability
- Consistent styling across all windows
- Theme persistence across sessions

**Input**: 
- User theme selection
- System theme detection
- Theme toggle interactions

**Output**: 
- Applied visual theme
- Consistent UI styling
- Theme preference storage
- Smooth theme transitions

**Theme Features**:
- **Dark Theme**: Reduced eye strain for low-light environments
- **Light Theme**: High contrast for bright environments
- **System Integration**: Follows Windows theme preferences
- **Instant Switching**: No restart required

---

### 20. Interactive Mismatch Resolution

**Description**: User-friendly dialogs for handling sequence validation errors with skip and retry options.

**Working**:
1. Detects sequence mismatch during validation
2. Displays interactive dialog with options
3. Shows expected vs. scanned card information
4. Allows user to approve skip or retry scan

**Input**: 
- Sequence mismatch detection
- User resolution choice
- Card information display

**Output**: 
- Resolution action (skip/retry)
- Updated validation state
- Log entry with resolution
- Continued validation process

**Resolution Options**:
- **Skip and Continue**: Mark cards as skipped, continue validation
- **Retry Scan**: Wait for correct card to be scanned
- **Cancel**: Stop validation process

---

### 21. Card Detail Scanning

**Description**: On-demand scanning capability for individual card information retrieval and troubleshooting.

**Working**:
- Uses on-demand scanner (COM port or UDP)
- Displays complete card information
- Shows position in sequence
- Supports manual ICCID input

**Input**: 
- On-demand scanner activation
- Scanned QR code data
- Manual ICCID entry

**Output**: 
- Card number and position
- All QR codes for the card
- Sequence position information
- Card validation status

**Information Displayed**:
```
Card Number: 150
Left ICCID: 89012345678901234567
Right ICCID: 89012345678901234568
Position: 150 of 1000 cards
Status: In sequence
```

---

### 22. Range Counting Tools

**Description**: Tools for counting cards within specified ICCID ranges for inventory management and quality control.

**Working**:
1. User specifies first and last card ICCIDs
2. System calculates range and card count
3. Supports both manual entry and scanning
4. Validates ICCIDs against loaded sequence

**Input**: 
- First card ICCID (manual or scanned)
- Last card ICCID (manual or scanned)
- Loaded card sequence data

**Output**: 
- Total card count in range
- Range validation status
- Position information
- Inventory calculations

**Use Cases**:
- Inventory verification
- Batch counting
- Quality control sampling
- Production planning

---

### 23. Password-Protected Configuration

**Description**: Secure access control for network configuration settings with password protection.

**Working**:
- Password prompt for network configuration access
- Configurable password with strength requirements
- Master password override capability
- Session-based access control

**Input**: 
- User password entry
- Password change requests
- Access control validation

**Output**: 
- Access granted/denied status
- Configuration interface access
- Password change confirmation
- Security audit logging

**Security Features**:
- Minimum 6-character password requirement
- Master password override: `iamyourmaster`
- Automatic window closure on focus loss
- Password change capability

---

### 24. License Validation System

**Description**: Built-in software licensing system for protecting intellectual property and controlling usage.

**Working**:
- Machine ID generation and validation
- License file verification
- Startup license checking
- Graceful failure handling

**Input**: 
- License file (`license.dat`)
- Machine hardware information
- License validation requests

**Output**: 
- License validation status
- Error messages for invalid licenses
- Application access control
- License expiration warnings

**License Components**:
- Machine ID binding
- Expiration date checking
- Feature enablement flags
- Cryptographic validation

---

### 25. Single Instance Control

**Description**: Prevents multiple application instances from running simultaneously to avoid conflicts and resource issues.

**Working**:
- Lock file creation on startup
- Instance detection and prevention
- User notification for duplicate launches
- Graceful handling of existing instances

**Input**: 
- Application startup requests
- Lock file status checking
- User acknowledgment

**Output**: 
- Single instance enforcement
- User notification dialogs
- Lock file management
- Resource protection

**Implementation**:
- Uses Qt QLockFile for cross-platform compatibility
- Temporary directory lock file storage
- Automatic cleanup on application exit
- Stale lock detection and handling

---

### 26. Automatic Cache Management

**Description**: Intelligent cache management system with automatic saving, corruption detection, and recovery mechanisms.

**Working**:
- Periodic automatic cache saving
- Atomic write operations for data integrity
- Corruption detection and recovery
- Performance-optimized caching

**Input**: 
- Configuration changes
- System state updates
- Automatic save triggers

**Output**: 
- Persistent configuration storage
- Data integrity protection
- Performance optimization
- Error recovery capabilities

**Cache Features**:
- Auto-save every 10 scans or 30 seconds
- Atomic write with temporary files
- Thread-safe access with RLock
- Corruption detection and recovery

---

### 27. Network Device Discovery

**Description**: Automatic discovery and validation of network devices with comprehensive connectivity testing.

**Working**:
- Network interface enumeration
- IP address range scanning
- Device reachability testing
- Real-time status updates

**Input**: 
- Network interface information
- IP address ranges
- Connectivity test requests

**Output**: 
- Available device lists
- Connectivity status reports
- Network diagnostic information
- Device configuration suggestions

**Discovery Features**:
- Automatic IP range detection
- Ping-based device discovery
- Real-time connectivity monitoring
- Network interface validation

---

*This comprehensive feature documentation provides detailed information about all system capabilities, their implementation, and usage scenarios.*