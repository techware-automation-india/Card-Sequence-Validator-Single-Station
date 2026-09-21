# Card Sequence Validator - Complete User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Application Setup](#application-setup)
3. [Network Configuration](#network-configuration)
4. [Job Management](#job-management)
5. [Scanning Operations](#scanning-operations)
6. [Output Signals](#output-signals)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements
- Windows Operating System
- Python 3.8 or higher
- Network scanner (UDP) or Barcode scanner (COM port)
- Output device (COM port) for validation signals

### Installation

1. **Extract the application** to your desired location

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   ```bash
   .venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
.venv\Scripts\activate
python main.py
```

The application will launch with the Main Application window.

---

## Application Setup

### Initial Configuration

When you first launch the application, you'll see three main windows:

1. **Main Application** - Central control panel
2. **Network Configuration** - Configure scanners and output devices
3. **Job Management** - Load and manage card sequence files

### Dual Head System

The application supports two independent scanning heads:
- **Head A (Right)** - Displayed on the right side of panels
- **Head B (Left)** - Displayed on the left side of panels

Each head operates independently with its own:
- Scanner configuration
- Job file
- Validation logs
- Output device

---

## Network Configuration

### Accessing Network Configuration
Click **"⚙ Network Configuration"** from the Main Application window.

### Main Scanner Setup (UDP Network Scanner)

#### For Each Head (A or B):

1. **Local IP Address**
   - Select your computer's network interface IP
   - Click "🔄 Refresh Network" to scan available IPs

2. **Local Port**
   - Enter the UDP port to listen on (e.g., 5000)
   - Must be unique per head

3. **Remote Scanner IP**
   - Enter the IP address of your network scanner

4. **Remote Scanner Port**
   - Enter the UDP port of your scanner

5. **Click "✓ Apply Main Scanner"**
   - Status will show "Connected" in green if successful

### Output Device Setup (COM Port)

#### For Each Head (A or B):

1. **COM Port**
   - Select the COM port connected to your output device
   - Click "🔄 Refresh COM Ports" to scan available ports

2. **Baud Rate**
   - Select appropriate baud rate (default: 9600)

3. **Data Bits**
   - Select data bits (default: 8)

4. **Parity**
   - Select parity (default: None)

5. **Stop Bits**
   - Select stop bits (default: 1)

6. **Output Format**
   - Select "Integers" (default format)

7. **Click "✓ Apply Output"**
   - Status will show "Connected" in green if successful

### On-Demand Scanner Setup (Barcode Scanner via COM Port)

#### For Each Head (A or B):

1. **COM Port**
   - Select the COM port for your barcode scanner

2. **Baud Rate**
   - Select appropriate baud rate (default: 9600)

3. **Data Bits, Parity, Stop Bits**
   - Configure according to your scanner specifications

4. **Click "✓ Apply On-Demand Scanner"**
   - Status will show "Connected" in green if successful

### Testing Connections

- **Ping Scanner**: Click "📡 Ping Scanner" to test UDP connection
- **Test Output**: Click "🔌 Test Output" to send a test signal

---

## Job Management

### Accessing Job Management
Click **"📁 Job Management"** from the Main Application window.

### Loading a Job File

#### For Each Head (A or B):

1. **Click "📁 Load Job File"**

2. **Select your sequence file**
   - Supported formats: `.cpd`, `.txt`, `.csv`

3. **Choose Card Type**
   - **Single Card**: One QR code per card
   - **Half Card**: Two QR codes per card (Left/Right)
   - **Quarter Card**: Four QR codes per card (Top-Left, Top-Right, Bottom-Left, Bottom-Right)

4. **Handle Existing Logs** (if applicable)
   - **Continue from Last Use**: Resume from where you left off
   - **Fresh Start (Download & Clear)**: Export logs and start fresh
   - **Clear and Continue**: Discard logs and start fresh

5. **File Status**
   - Shows "Active: [filename]" when loaded successfully

### Scan Direction

Toggle between:
- **🔄 Top → Bottom**: Scan cards from top to bottom (normal order)
- **🔄 Bottom → Top**: Scan cards from bottom to top (reversed order)

### Preview Sequence

Click **"👁 Preview"** to view:
- Card numbers
- Expected QR codes
- Scan direction indicator

### Checksum Configuration

Configure how many checksum digits to strip from scanned codes:

- **0 (None)**: No additional stripping (default)
- **1 (Last digit)**: Strip 1 additional digit
- **2 (Last 2 digits)**: Strip 2 additional digits
- **3 (Last 3 digits)**: Strip 3 additional digits
- **4 (Last 4 digits)**: Strip 4 additional digits
- **5 (Last 5 digits)**: Strip 5 additional digits

**Note**: The system automatically handles checksum processing. The "0 (None)" option is recommended for most use cases.

### Sequence Control Tools

#### Scan Card Details
1. Click **"Scan Card"**
2. Scan any card with the on-demand scanner
3. View:
   - Card Number
   - QR Code(s)
   - Position in sequence

#### Count Card Range
1. Click **"Count Range"**
2. Scan the first card
3. Scan the last card
4. View:
   - First card number
   - Last card number
   - Total cards in range

---

## Scanning Operations

### Starting Validation

1. **Ensure Configuration is Complete**
   - Main scanner connected
   - Output device connected
   - Job file loaded

2. **Click "▶ Start Validation - Head A/B"**
   - The Scanner & Logging window will open
   - Status shows "Waiting for first scan..."

3. **Scan the First Card**
   - The system will automatically detect:
     - Card position in sequence
     - Which side was scanned (for half/quarter cards)
   - Status updates to show current progress

4. **Continue Scanning**
   - Scan cards in sequence
   - Watch real-time validation results

### Scanner & Logging Window

#### Status Display
- **Current Card**: Shows expected card number
- **Progress**: Shows cards scanned / total cards
- **Status**: Current scanning state

#### Control Buttons
- **⏸ Pause Scanning**: Temporarily pause validation
- **▶ Resume Scanning**: Resume after pause
- **⏹ Stop Scanning**: End validation session

#### Real-Time Log Table

Displays each scan with:
- **Timestamp**: When the scan occurred
- **Scanned Code**: The QR code that was scanned
- **Expected Code**: The QR code that was expected
- **Status**: Validation result (see below)
- **Side**: Which side was scanned (Single/Left/Right/Top-Left/etc.)

---

## Output Signals

### Signal Types

The application sends different output signals based on validation results:

#### Single Card Mode
| Status | Output Signal | Description |
|--------|--------------|-------------|
| OK | `17\r\n` | Card matches expected sequence |
| NOT OK | `18\r\n` | Card does not match expected |
| OK (JUMPED) | `17\r\n` | Card matches after approved skip |
| LAST OK | `19\r\n` | Final card in sequence matches |
| LAST OK (JUMPED) | `19\r\n` | Final card matches after approved skip |

#### Half Card Mode
| Status | Output Signal | Description |
|--------|--------------|-------------|
| OK | `09\r\n` | Card matches expected sequence |
| NOT OK | `10\r\n` | Card does not match expected |
| OK (JUMPED) | `09\r\n` | Card matches after approved skip |
| LAST OK | `11\r\n` | Final card in sequence matches |
| LAST OK (JUMPED) | `11\r\n` | Final card matches after approved skip |

#### Quarter Card Mode
| Status | Output Signal | Description |
|--------|--------------|-------------|
| OK | `05\r\n` | Card matches expected sequence |
| NOT OK | `06\r\n` | Card does not match expected |
| OK (JUMPED) | `05\r\n` | Card matches after approved skip |
| LAST OK | `07\r\n` | Final card in sequence matches |
| LAST OK (JUMPED) | `07\r\n` | Final card matches after approved skip |

### Validation Scenarios

#### Scenario 1: Perfect Sequence Match
**Situation**: Scanned card matches the expected card in sequence

**Result**:
- Status: `OK`
- Output Signal: Sent (17/09/05 depending on card type)
- Log Entry: Green "OK" status
- Action: Automatically advances to next card

**Example**:
```
Expected: Card #5, QR: 123456789
Scanned:  123456789
Result:   OK ✓
```

---

#### Scenario 2: Card Mismatch
**Situation**: Scanned card does not match expected card

**Result**:
- Status: `NOT OK`
- Output Signal: Sent (18/10/06 depending on card type)
- Log Entry: Red "NOT OK" status
- Action: Stays on same expected card (does not advance)

**Example**:
```
Expected: Card #5, QR: 123456789
Scanned:  987654321
Result:   NOT OK ✗
```

---

#### Scenario 3: Card Found Ahead in Sequence
**Situation**: Scanned card exists later in the sequence

**Result**:
- Scanning pauses automatically
- Dialog appears: "Card found ahead in sequence"
- Shows: Number of cards that would be skipped
- Options:
  - **Jump to Card**: Skip ahead to scanned card
  - **Cancel**: Stay on current card

**If "Jump to Card" is selected**:
- Status: `OK (JUMPED)`
- Output Signal: Sent (17/09/05 depending on card type)
- Log Entry: Yellow "OK (JUMPED)" status
- Action: Advances to the scanned card position

**If "Cancel" is selected**:
- No output signal sent
- Scanning resumes at current position

**Example**:
```
Expected: Card #5
Scanned:  Card #8 (3 cards ahead)
Dialog:   "Skip 3 cards and jump to card #8?"
```

---

#### Scenario 4: Wrong Side Scanned (Half/Quarter Cards)
**Situation**: Correct card but wrong QR position scanned

**Result**:
- Status: `NOT OK`
- Output Signal: Sent (10/06 depending on card type)
- Log Entry: Red "NOT OK" status
- Action: Stays on same expected card

**Example (Half Card)**:
```
Expected: Card #5, Left side
Scanned:  Card #5, Right side
Result:   NOT OK ✗ (wrong side)
```

---

#### Scenario 5: Last Card in Sequence
**Situation**: Final card in sequence is scanned correctly

**Result**:
- Status: `LAST OK`
- Output Signal: Sent (19/11/07 depending on card type)
- Log Entry: Green "LAST OK" status
- Action: Sequence complete, scanning continues but logs as "EXTRA SCAN"

**Example**:
```
Expected: Card #100 (last card)
Scanned:  Correct QR code
Result:   LAST OK ✓ (sequence complete)
```

---

#### Scenario 6: Extra Scans After Completion
**Situation**: Scanning continues after sequence is complete

**Result**:
- Status: `EXTRA SCAN`
- Output Signal: None
- Log Entry: Gray "EXTRA SCAN" status
- Action: Logged but no validation performed

---

#### Scenario 7: Card Not in Sequence
**Situation**: Scanned card does not exist anywhere in the loaded file

**Result**:
- Status: `NOT IN SEQUENCE`
- Output Signal: None
- Log Entry: Red "NOT IN SEQUENCE" status
- Action: Stays on current expected card

**Example**:
```
Expected: Card #5
Scanned:  QR code not in file
Result:   NOT IN SEQUENCE ✗
```

---

#### Scenario 8: No File Loaded
**Situation**: Scanning without a loaded job file

**Result**:
- Status: `NO FILE`
- Output Signal: None
- Log Entry: Red "NO FILE" status
- Action: Cannot validate

---

### Log Management

#### Export Logs
Click **"📥 Export Logs"** to save validation logs as CSV:
- Filename format: `logs_head_A_YYYYMMDD_HHMMSS.csv`
- Contains: Timestamp, Scanned Code, Expected Code, Status, Side

#### Download & Clear Logs
Click **"💾 Download & Clear Logs"** to:
1. Export current logs to CSV
2. Clear all log entries
3. Reset statistics

#### Statistics Display
- **Total Scans**: All scans performed
- **Successful**: OK + OK (JUMPED) + LAST OK + LAST OK (JUMPED)
- **Failed**: NOT OK + NOT IN SEQUENCE + NO FILE
- **Skipped**: Number of cards jumped over

---

## Troubleshooting

### Scanner Not Receiving Data

**Check**:
1. Main scanner is connected (green status)
2. Correct IP address and port configured
3. Scanner is powered on and on same network
4. Firewall not blocking UDP port
5. Click "📡 Ping Scanner" to test connection

### Output Device Not Responding

**Check**:
1. Output device is connected (green status)
2. Correct COM port selected
3. Baud rate matches device specifications
4. Cable is properly connected
5. Click "🔌 Test Output" to send test signal

### Barcode Scanner Not Working

**Check**:
1. On-demand scanner is connected (green status)
2. Correct COM port selected
3. Scanner is configured for correct baud rate
4. Scanner is in correct mode (keyboard wedge vs serial)

### Cards Not Validating Correctly

**Check**:
1. Correct card type selected (Single/Half/Quarter)
2. Scan direction matches physical card order
3. Checksum configuration is correct
4. Scanning correct side of card (for Half/Quarter cards)

### Application Crashes or Freezes

**Solutions**:
1. Check `debug_output.txt` for error messages
2. Restart application
3. Verify all configuration files are intact
4. Reinstall dependencies: `pip install -r requirements.txt`

### Session Recovery

The application automatically saves your progress:
- Current card position
- Validation logs
- Configuration settings

If the application closes unexpectedly:
1. Restart the application
2. Load the same job file
3. Choose "Continue from Last Use"
4. Scanning resumes from last position

---

## Advanced Features

### Password Protection

Network configuration is password-protected:
- Default password: `admin123`
- Click "🔑 Change Password" to update
- Password is saved securely

### Theme Switching

Toggle between Dark and Light themes:
- Click theme toggle in Main Application
- Preference is saved automatically

### Multi-Head Operation

Run both Head A and Head B simultaneously:
- Each head operates independently
- Separate scanners and output devices
- Separate job files and logs
- Useful for parallel validation workflows

---

## Best Practices

1. **Always test connections** before starting validation
2. **Preview sequence** to verify correct file and scan direction
3. **Export logs regularly** to prevent data loss
4. **Use appropriate card type** matching your physical cards
5. **Keep backup** of job files
6. **Monitor statistics** to track validation quality
7. **Pause scanning** if you need to adjust cards or equipment

---

## Support

For technical support or questions:
- Check `debug_output.txt` for error logs
- Review documentation files in application folder
- Verify all hardware connections and configurations

---

**Version**: 3.0  
**Last Updated**: 2026-03-01
