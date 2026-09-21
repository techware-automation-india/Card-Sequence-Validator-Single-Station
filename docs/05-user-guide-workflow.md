# User Guide & Workflow

## Step-by-Step User Journey from Start to Finish

### Initial System Setup (First Time Use)

#### Step 1: Application Launch and License Validation
1. **Launch Application**
   - Double-click `CardSequenceValidator.exe`
   - Wait for license validation (automatic)
   - Application opens with dual-head dashboard

2. **Initial Interface Overview**
   - Main dashboard displays system status for both heads
   - Head A (Right) shown in green theme
   - Head B (Left) shown in blue theme
   - All status indicators show "Not Set" or "No File"

#### Step 2: Network Configuration Setup
1. **Access Network Configuration**
   - Click "Configuration" button on main dashboard
   - Enter default password: `admin123`
   - Network & COM Port Configuration window opens

2. **Configure Head A (Right Side)**
   ```
   Main Scanner Input (UDP):
   - Local IP: Select from dropdown (e.g., 192.168.1.100)
   - Local Port: 5000
   - Remote IP: Enter scanner IP (e.g., 192.168.1.50)
   - Remote Port: 6000
   - Click "Apply Main Scanner"
   
   Output Configuration (UDP):
   - Local IP: Same as main scanner
   - Local Port: 7000
   - Remote IP: Enter PLC IP (e.g., 192.168.1.200)
   - Remote Port: 8000
   - Click "Apply Output"
   
   On-Demand Scanner (Serial):
   - COM Port: Select available port (e.g., COM3)
   - Baud Rate: 115200
   - Click "Apply On-Demand Scanner"
   ```

3. **Configure Head B (Left Side)**
   - Repeat configuration for Head B with different ports
   - Use different local ports to avoid conflicts
   - Example: Local ports 5001, 7001 for Head B

4. **Test Connectivity**
   - Click "🔄 Refresh Network & Scan IPs"
   - Wait for network scan completion
   - Verify green status indicators for reachable devices

5. **Change Default Password**
   - Scroll to "Security Settings" section
   - Enter current password: `admin123`
   - Set new secure password (minimum 6 characters)
   - Confirm password change

#### Step 3: File Management Setup
1. **Access File Management**
   - Close Network Configuration window
   - Click "Job & Log Management" on main dashboard

2. **Load CPD File for Head A**
   - In right panel (Head A), click "📁 Load Job File"
   - Select CPD file from file dialog
   - Choose card type (Single/Half/Quarter)
   - Set rebatch size if needed (optional)
   - Click "Load File"

3. **Configure Scan Settings**
   - Set scan direction: "🔄 Top → Bottom" or "🔄 Bottom → Top"
   - Configure checksum digits if needed (usually 0)
   - Preview file to verify correct loading

4. **Load CPD File for Head B**
   - Repeat process in left panel (Head B)
   - Can use same or different file
   - Configure independently from Head A

### Daily Operation Workflow

#### Step 1: System Startup and Verification
1. **Launch and Verify**
   - Start application
   - Check system status on main dashboard
   - Verify both heads show:
     - Scanner: Idle
     - File Loaded: [filename] (X cards)
     - Input Port: Connected (IP:Port)
     - Output Port: Connected (IP:Port)

2. **Pre-Validation Checks**
   - Ensure scanners are powered on
   - Verify network connectivity (green indicators)
   - Check PLC systems are ready to receive signals

#### Step 2: Start Validation Process
1. **Access Scanner Control**
   - Click "Scanner Control" on main dashboard
   - Scanner Logging window opens with dual panels

2. **Start Validation for Head A**
   - In right panel, click "▶ Start Validation"
   - System begins listening for scanner input
   - Status changes to "Scanning"
   - "Last Scanned ID" shows "Awaiting Scan Input..."

3. **Start Validation for Head B**
   - In left panel, click "▶ Start Validation"
   - Both heads now operate independently
   - Monitor status for both simultaneously

#### Step 3: Normal Validation Operation
1. **Scan Processing**
   - Scanner sends QR code data via UDP
   - System validates against expected sequence
   - Results displayed in real-time:
     - ✅ "OK" - Correct card in sequence
     - ❌ "NOT OK" - Wrong card or error
     - ⚠️ "OK (JUMPED)" - Approved skip-ahead

2. **Monitor Progress**
   - Watch "Current Card Index" increment
   - Monitor "Next Expected ID" for guidance
   - Check log table for validation history

3. **Handle Mismatches**
   - When mismatch occurs, dialog appears:
     ```
     Sequence Mismatch Detected
     Expected: 89012345678901234567
     Scanned: 89012345678901234999
     
     Options:
     [Skip and Continue] [Retry Scan] [Cancel]
     ```
   - Choose appropriate action based on situation

#### Step 4: Completion and Log Management
1. **Automatic Completion**
   - System detects when last card is scanned
   - Displays completion dialog with statistics:
     ```
     Validation Complete - Head A
     
     File: production_batch_001.cpd
     
     Total Scans: 1000
     Successful: 995
     Failed: 3
     Skipped: 2
     ```

2. **Export Logs**
   - In File Management window, click "💾 Download and Clear Logs"
   - Choose export location
   - CSV file created with validation history
   - Logs cleared for next session

### Advanced Workflows

#### Workflow 1: Card Detail Investigation
**Use Case**: Investigate specific card information or troubleshoot scanning issues

1. **Access Card Details**
   - In File Management, scroll to "Scan Card Details"
   - Click "Scan Card" button
   - Status shows "Waiting for card scan..."

2. **Scan or Enter Card**
   - Use on-demand scanner to scan card
   - OR manually enter ICCID in text field
   - Card information displays:
     ```
     Card Number: 150
     Left ICCID: 89012345678901234567
     Right ICCID: 89012345678901234568
     Position: 150 of 1000 cards
     ```

3. **Use Information**
   - Verify card is in correct sequence
   - Check for data integrity issues
   - Document findings for quality control

#### Workflow 2: Range Counting for Inventory
**Use Case**: Count cards in specific ICCID range for inventory verification

1. **Access Range Counting**
   - In File Management, scroll to "Count Card Range"
   - Click "Scan Range" button

2. **Define Range**
   - Scan first card in range (or enter ICCID manually)
   - Scan last card in range (or enter ICCID manually)
   - Click "Calculate Range"

3. **Review Results**
   - Total count displays in "Total" field
   - Verify count matches expected inventory
   - Use for batch verification and quality control

#### Workflow 3: Session Recovery After Interruption
**Use Case**: Resume validation after power loss or application crash

1. **Restart Application**
   - Launch application normally
   - File Management shows: "Not loaded: [filename] (Click 'Load File' to continue)"

2. **Reload Previous File**
   - Click "📁 Load Job File"
   - Dialog appears: "Load Previous File"
   - Click "Load Previous" to use same file

3. **Choose Recovery Option**
   - If logs exist, dialog shows:
     ```
     Previous session logs found (150 entries)
     
     Continue from Last Use: Resume from card 151
     Fresh Start (Clear Logs): Start from beginning
     ```
   - Choose based on situation:
     - **Continue**: Resume where you left off
     - **Fresh Start**: Clear logs and restart validation

#### Workflow 4: Multi-Head Coordination
**Use Case**: Coordinate validation across both heads for synchronized operation

1. **Synchronized Setup**
   - Load related files on both heads
   - Configure similar scan directions
   - Verify network settings don't conflict

2. **Coordinated Start**
   - Start validation on Head B first
   - Start validation on Head A second
   - Monitor both panels simultaneously

3. **Manage Completion**
   - Heads may complete at different times
   - Export logs separately for each head
   - Combine data for comprehensive reporting

### Common Procedures

#### Procedure 1: Changing Scan Direction Mid-Session
1. Stop current validation
2. Go to File Management window
3. Click scan direction toggle button
4. Clear logs if needed (fresh start)
5. Restart validation with new direction

#### Procedure 2: Handling Network Connectivity Issues
1. Check physical network connections
2. Open Network Configuration window
3. Click "🔄 Refresh Network & Scan IPs"
4. Verify IP addresses and ports
5. Test connectivity with ping
6. Reconfigure if necessary

#### Procedure 3: Switching Between Card Types
1. Stop validation if running
2. In File Management, click "🗑 Clear" to unload current file
3. Click "📁 Load Job File"
4. Select new file and card type
5. Configure checksum settings if needed
6. Preview and start validation

#### Procedure 4: Exporting Logs for Analysis
1. Complete validation session or stop manually
2. In File Management, click "💾 Download and Clear Logs"
3. Choose export location (default: Desktop\csv_logs\)
4. File saved as: `logs_head_A_YYYYMMDD_HHMMSS.csv`
5. Open in Excel or analysis software
6. Logs automatically cleared after export

### Best Practices

#### Operational Best Practices
1. **Pre-Shift Checklist**
   - Verify network connectivity
   - Check scanner power and alignment
   - Test with known good cards
   - Verify PLC communication

2. **During Operation**
   - Monitor both heads continuously
   - Address mismatches promptly
   - Keep backup files available
   - Document any issues

3. **End-of-Shift Procedures**
   - Export logs before closing
   - Document completion statistics
   - Report any anomalies
   - Prepare for next shift

#### Troubleshooting Best Practices
1. **Network Issues**
   - Check cables and connections first
   - Verify IP address conflicts
   - Test with ping commands
   - Restart network equipment if needed

2. **Scanning Issues**
   - Clean scanner lenses
   - Check card positioning
   - Verify QR code quality
   - Test with manual input

3. **File Issues**
   - Verify file format and encoding
   - Check for missing or corrupt data
   - Validate card type selection
   - Test with known good files

#### Performance Optimization
1. **System Performance**
   - Close unnecessary applications
   - Monitor memory usage
   - Use SSD storage for better I/O
   - Regular system maintenance

2. **Network Performance**
   - Use dedicated network interfaces
   - Configure QoS for UDP traffic
   - Monitor network utilization
   - Minimize network congestion

3. **Application Performance**
   - Export logs regularly
   - Clear cache periodically
   - Monitor auto-save frequency
   - Optimize checksum settings

### Error Recovery Procedures

#### Recovery 1: Application Crash During Validation
1. **Immediate Actions**
   - Restart application
   - Check system status
   - Verify network connections

2. **Data Recovery**
   - Load previous file when prompted
   - Choose "Continue from Last Use" if logs exist
   - Verify scan position is correct
   - Resume validation

3. **Prevention**
   - Monitor system resources
   - Keep application updated
   - Regular system maintenance

#### Recovery 2: Network Connection Loss
1. **Detection**
   - Status indicators turn red/orange
   - Validation stops or errors occur
   - Network diagnostic messages appear

2. **Recovery Steps**
   - Check physical connections
   - Restart network equipment
   - Refresh network configuration
   - Test connectivity
   - Resume validation

#### Recovery 3: File Corruption or Loading Errors
1. **Symptoms**
   - File loading fails
   - Validation errors increase
   - Unexpected scan results

2. **Recovery Actions**
   - Try reloading file
   - Verify file integrity
   - Use backup file if available
   - Contact system administrator

### Quality Control Procedures

#### Daily Quality Checks
1. **System Verification**
   - Test known good cards
   - Verify output signals
   - Check log accuracy
   - Validate completion detection

2. **Data Integrity**
   - Compare scan counts with production
   - Verify export file completeness
   - Check for missing sequences
   - Validate statistical accuracy

#### Weekly Maintenance
1. **System Maintenance**
   - Clean scanner equipment
   - Check network performance
   - Update system if needed
   - Backup configuration files

2. **Performance Review**
   - Analyze validation statistics
   - Review error patterns
   - Optimize configuration
   - Plan improvements

---

*This user guide provides comprehensive workflows for all common operations and scenarios in the Card Sequence Validator system.*