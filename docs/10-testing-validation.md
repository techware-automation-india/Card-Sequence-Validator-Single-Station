# Testing & Validation

## Test Cases and Scenarios

### Core Validation Testing

#### Test Case 1: Normal Sequential Validation
**Objective**: Verify correct validation of cards in proper sequence
**Preconditions**: 
- CPD file loaded with 100 cards
- Network scanner configured and connected
- Scan direction set to "Top → Bottom"

**Test Steps**:
1. Start validation process
2. Scan cards 1-100 in sequential order
3. Verify each scan shows "OK" status
4. Confirm output signals sent to PLC
5. Check completion dialog appears after card 100

**Expected Results**:
- All scans show "OK" status
- Current card index increments correctly (1→100)
- Output signals: "09\r\n" for each successful scan
- Completion dialog shows: Total: 100, Successful: 100, Failed: 0, Skipped: 0

**Test Data**:
```
Card 1: 89012345678901234567
Card 2: 89012345678901234568
Card 3: 89012345678901234569
...
Card 100: 89012345678901234666
```

#### Test Case 2: Out-of-Sequence Detection
**Objective**: Verify detection and handling of out-of-sequence scans
**Preconditions**: Same as Test Case 1

**Test Steps**:
1. Start validation process
2. Scan cards 1-10 in sequence
3. Skip cards 11-15, scan card 16
4. Verify mismatch dialog appears
5. Choose "Skip and Continue" option
6. Continue scanning cards 17-20

**Expected Results**:
- Cards 1-10: "OK" status
- Card 16: Mismatch dialog appears
- After skip approval: Cards 11-15 marked as "SKIPPED"
- Card 16: "OK (JUMPED)" status
- Cards 17-20: "OK" status

#### Test Case 3: Wrong Card Detection
**Objective**: Verify detection of completely wrong cards
**Preconditions**: Same as Test Case 1

**Test Steps**:
1. Start validation process
2. Scan cards 1-5 in sequence
3. Scan a card not in the file (e.g., "99999999999999999999")
4. Verify "NOT IN SEQUENCE" status
5. Scan correct card 6
6. Verify validation continues normally

**Expected Results**:
- Cards 1-5: "OK" status
- Wrong card: "NOT IN SEQUENCE" status, no output signal
- Card 6: "OK" status
- Validation continues from card 7

### Card Type Testing

#### Test Case 4: Single Card Validation
**Objective**: Test validation with single QR code cards
**Test Data**: Single card CPD file with 50 cards

**Test Steps**:
1. Load single card CPD file
2. Verify card type selection shows "Single"
3. Start validation
4. Scan all 50 cards
5. Verify output signals use single card format

**Expected Results**:
- Output signals: "17\r\n" for OK, "18\r\n" for NOT OK
- All cards validate with single QR code
- Completion statistics accurate

#### Test Case 5: Half Card Validation
**Objective**: Test validation with dual QR code cards
**Test Data**: Half card CPD file with left/right ICCIDs

**Test Steps**:
1. Load half card CPD file
2. Set scan side to "Left" 
3. Start validation
4. Scan left ICCIDs for all cards
5. Verify validation uses left QR codes only

**Expected Results**:
- Validation uses left ICCID column
- Output signals: "09\r\n" for OK, "10\r\n" for NOT OK
- Right ICCIDs ignored during validation

#### Test Case 6: Quarter Card Validation
**Objective**: Test validation with four QR code cards
**Test Data**: Quarter card CPD file with BL/TL/TR/BR ICCIDs

**Test Steps**:
1. Load quarter card CPD file
2. Set scan side to "Bottom-Left"
3. Start validation
4. Scan bottom-left ICCIDs
5. Verify correct QR position validation

**Expected Results**:
- Validation uses bottom-left ICCID column
- Output signals: "05\r\n" for OK, "06\r\n" for NOT OK
- Other QR positions ignored

### Scan Direction Testing

#### Test Case 7: Bottom-to-Top Scanning
**Objective**: Verify reverse scanning functionality
**Preconditions**: CPD file with 50 cards loaded

**Test Steps**:
1. Set scan direction to "Bottom → Top"
2. Start validation
3. Scan card 50 first (sets start position)
4. Scan cards 49, 48, 47... down to card 1
5. Verify completion after scanning card 1

**Expected Results**:
- First scan (card 50): "OK" status, sets start position
- Subsequent scans: Cards 49→1 show "OK" status
- Completion dialog appears after card 1
- Statistics show all 50 cards validated

#### Test Case 8: Direction Change Mid-Session
**Objective**: Test changing scan direction during validation
**Preconditions**: Validation in progress, 25 cards scanned

**Test Steps**:
1. Stop current validation
2. Clear logs
3. Change scan direction from "Top → Bottom" to "Bottom → Top"
4. Restart validation
5. Verify new direction is used

**Expected Results**:
- Previous logs cleared
- New validation starts with selected direction
- First scan sets new start position
- Validation proceeds in new direction

### Checksum Processing Testing

#### Test Case 9: Checksum Stripping Validation
**Objective**: Verify checksum digit stripping functionality
**Test Data**: QR codes with 2-digit checksums appended

**Test Steps**:
1. Configure checksum digits to "2 (Last 2 digits)"
2. Load CPD file with ICCIDs without checksums
3. Scan QR codes with 2-digit checksums appended
4. Verify validation matches after stripping

**Test Data**:
```
File ICCID: 89012345678901234567
Scanned QR: 8901234567890123456712 (with checksum "12")
Expected: Match after stripping checksum
```

**Expected Results**:
- Scanned code "8901234567890123456712" → stripped to "89012345678901234567"
- Validation shows "OK" status
- Log entries show stripped values only

#### Test Case 10: Variable Checksum Lengths
**Objective**: Test different checksum digit configurations
**Test Scenarios**: 0, 1, 2, 3, 4, 5 digit configurations

**Test Steps**:
1. For each checksum length (0-5):
   - Configure checksum digits
   - Scan test QR codes with appropriate checksums
   - Verify correct stripping and validation

**Expected Results**:
- 0 digits: No stripping, direct validation
- 1 digit: Last 1 digit stripped
- 2 digits: Last 2 digits stripped
- 3 digits: Last 3 digits stripped
- 4 digits: Last 4 digits stripped
- 5 digits: Last 5 digits stripped

### Network Communication Testing

#### Test Case 11: UDP Scanner Communication
**Objective**: Test UDP network scanner integration
**Preconditions**: Network scanner configured at 192.168.1.50:6000

**Test Steps**:
1. Configure main scanner UDP settings
2. Test connectivity with ping
3. Start validation
4. Send QR codes via UDP from scanner
5. Verify real-time processing

**Expected Results**:
- Ping test shows "Device reachable"
- UDP packets received and processed
- Validation occurs in real-time
- Network status shows "Connected"

#### Test Case 12: Serial COM Port Communication
**Objective**: Test serial scanner integration
**Preconditions**: Serial scanner connected to COM3

**Test Steps**:
1. Configure on-demand scanner for COM3 @ 115200 baud
2. Test connection status
3. Use "Scan Card Details" function
4. Scan QR code with serial scanner
5. Verify card information displays

**Expected Results**:
- COM port status shows "Connected to COM3"
- Serial data received and processed
- Card details display correctly
- No communication errors

#### Test Case 13: Output Signal Transmission
**Objective**: Test PLC output signal transmission
**Preconditions**: PLC configured at 192.168.1.200:8000

**Test Steps**:
1. Configure output UDP settings
2. Start validation with half cards
3. Scan correct card (expect "OK" status)
4. Scan wrong card (expect "NOT OK" status)
5. Monitor PLC for received signals

**Expected Results**:
- Correct card: "09\r\n" signal sent to PLC
- Wrong card: "10\r\n" signal sent to PLC
- PLC receives signals correctly
- Output status shows "Connected"

### File Processing Testing

#### Test Case 14: CPD File Format Validation
**Objective**: Test CPD file parsing and validation
**Test Files**: Various CPD file formats and error conditions

**Test Scenarios**:
1. **Valid CPD File**: Standard format with NUMCARD and ICCID columns
2. **Missing Header**: File without NUMCARD header row
3. **Missing ICCID Column**: Header without ICCID column
4. **Empty File**: Zero-byte file
5. **Corrupted Data**: File with invalid characters or encoding
6. **Mismatched Columns**: Data rows with different column counts

**Expected Results**:
- Valid file: Loads successfully with correct card count
- Invalid files: Show appropriate error messages
- Error messages are user-friendly and actionable
- Application remains stable after errors

#### Test Case 15: Large File Processing
**Objective**: Test performance with large CPD files
**Test Data**: CPD file with 10,000+ cards

**Test Steps**:
1. Load large CPD file (10,000 cards)
2. Monitor loading time and memory usage
3. Start validation
4. Perform random sampling of validations
5. Monitor performance during operation

**Expected Results**:
- File loads within 5 seconds
- Memory usage remains reasonable (<500MB)
- Validation response time <100ms
- No performance degradation over time

### Dual-Head Testing

#### Test Case 16: Independent Head Operation
**Objective**: Verify independent operation of both validation heads
**Preconditions**: Different CPD files loaded on Head A and Head B

**Test Steps**:
1. Load different files on Head A (100 cards) and Head B (50 cards)
2. Configure different network settings for each head
3. Start validation on both heads simultaneously
4. Perform validation on both heads concurrently
5. Verify independent operation and logging

**Expected Results**:
- Both heads operate independently
- No interference between heads
- Separate log files and statistics
- Independent completion detection

#### Test Case 17: Dual-Head Configuration Isolation
**Objective**: Verify configuration isolation between heads
**Test Steps**:
1. Configure Head A with specific settings (checksum: 2, direction: top-bottom)
2. Configure Head B with different settings (checksum: 0, direction: bottom-top)
3. Restart application
4. Verify settings are restored correctly for each head

**Expected Results**:
- Head A retains its configuration
- Head B retains its different configuration
- No configuration cross-contamination
- Settings persist across restarts

### Error Handling Testing

#### Test Case 18: Network Disconnection Recovery
**Objective**: Test recovery from network connectivity loss
**Test Steps**:
1. Start validation with network scanner
2. Disconnect network cable during validation
3. Verify error detection and user notification
4. Reconnect network
5. Test recovery and resumption

**Expected Results**:
- Network disconnection detected within 5 seconds
- User notified with clear error message
- Validation pauses or stops gracefully
- Recovery possible after reconnection

#### Test Case 19: File Corruption Handling
**Objective**: Test handling of file corruption during operation
**Test Steps**:
1. Load valid CPD file and start validation
2. Simulate file corruption (delete/modify file)
3. Continue validation attempts
4. Verify graceful error handling

**Expected Results**:
- File corruption detected
- Clear error message displayed
- Application remains stable
- User can load new file to continue

#### Test Case 20: Memory Exhaustion Testing
**Objective**: Test behavior under memory pressure
**Test Steps**:
1. Run validation for extended period (8+ hours)
2. Monitor memory usage over time
3. Perform thousands of validations
4. Check for memory leaks or degradation

**Expected Results**:
- Memory usage remains stable
- No significant memory leaks
- Performance maintained over time
- Automatic log rotation if needed

## Edge Cases

### Edge Case 1: Empty CPD File
**Scenario**: User loads CPD file with header but no data rows
**Expected Behavior**: 
- Error message: "CPD file has no data rows (only header)"
- File loading fails gracefully
- User can select different file

### Edge Case 2: Single Card File
**Scenario**: CPD file contains only one card
**Expected Behavior**:
- File loads successfully
- Validation works for single card
- Completion detected after first successful scan
- Statistics show: Total: 1, Successful: 1

### Edge Case 3: Duplicate ICCIDs in File
**Scenario**: CPD file contains duplicate ICCID values
**Expected Behavior**:
- File loads with warning message
- First occurrence takes precedence
- Validation may show unexpected results
- User advised to fix file

### Edge Case 4: Very Long ICCID Values
**Scenario**: ICCIDs longer than typical 19-20 characters
**Expected Behavior**:
- Values accepted if within reasonable limits (30 chars)
- Validation works normally
- Display truncated in UI if necessary

### Edge Case 5: Network Port Conflicts
**Scenario**: Multiple applications using same UDP port
**Expected Behavior**:
- Port binding fails with clear error message
- User advised to change port number
- Alternative ports suggested

### Edge Case 6: COM Port Access Conflicts
**Scenario**: Another application using same COM port
**Expected Behavior**:
- COM port access fails
- Error message: "Port in use by another application"
- User advised to close other applications

### Edge Case 7: Rapid Scanning
**Scenario**: Scanner sends data faster than processing capability
**Expected Behavior**:
- All scans processed in order
- No data loss or corruption
- Performance monitoring shows any delays

### Edge Case 8: Invalid QR Code Characters
**Scenario**: QR codes contain special characters or Unicode
**Expected Behavior**:
- Non-printable characters filtered out
- Unicode characters handled gracefully
- Validation continues with cleaned data

### Edge Case 9: System Clock Changes
**Scenario**: System time changed during operation
**Expected Behavior**:
- Timestamps in logs remain consistent
- No impact on validation logic
- Cache operations continue normally

### Edge Case 10: Disk Space Exhaustion
**Scenario**: Disk space runs out during log export
**Expected Behavior**:
- Export operation fails with clear error
- Partial files cleaned up
- User advised of disk space issue

## Sample Inputs and Outputs

### Valid Validation Sequence
**Input Sequence**:
```
Scan 1: 89012345678901234567 → Expected: 89012345678901234567
Scan 2: 89012345678901234568 → Expected: 89012345678901234568
Scan 3: 89012345678901234569 → Expected: 89012345678901234569
```

**Output Log Entries**:
```csv
Timestamp,Scanned Code,Expected Code,Status,Card Index,Direction
2026-04-15 14:30:25,89012345678901234567,89012345678901234567,OK,1,top_to_bottom
2026-04-15 14:30:26,89012345678901234568,89012345678901234568,OK,2,top_to_bottom
2026-04-15 14:30:27,89012345678901234569,89012345678901234569,OK,3,top_to_bottom
```

**PLC Output Signals**:
```
Signal 1: "09\r\n" (Half card OK)
Signal 2: "09\r\n" (Half card OK)
Signal 3: "09\r\n" (Half card OK)
```

### Mismatch Resolution Sequence
**Input Sequence**:
```
Scan 1: 89012345678901234567 → Expected: 89012345678901234567 (OK)
Scan 2: 89012345678901234569 → Expected: 89012345678901234568 (Mismatch)
User Action: Skip and Continue
Scan 3: 89012345678901234570 → Expected: 89012345678901234570 (OK)
```

**Output Log Entries**:
```csv
Timestamp,Scanned Code,Expected Code,Status,Card Index,Direction
2026-04-15 14:30:25,89012345678901234567,89012345678901234567,OK,1,top_to_bottom
2026-04-15 14:30:26,89012345678901234568,,SKIPPED,2,top_to_bottom
2026-04-15 14:30:27,89012345678901234569,89012345678901234569,OK (JUMPED),3,top_to_bottom
2026-04-15 14:30:28,89012345678901234570,89012345678901234570,OK,4,top_to_bottom
```

### Checksum Processing Example
**Configuration**: Checksum digits = 2
**Input/Output**:
```
Scanned: 8901234567890123456712 (with 2-digit checksum "12")
Processed: 89012345678901234567 (checksum stripped)
File ICCID: 89012345678901234567
Result: OK (Match after checksum removal)
```

### Error Condition Examples
**Network Error**:
```
Input: Scanner sends data to unreachable IP
Output: "Network error: Connection timeout"
Status: Scanner shows "Not Connected"
```

**File Error**:
```
Input: Load corrupted CPD file
Output: "CPD file has invalid encoding. File must be UTF-8 encoded text."
Status: File loading fails, user can select different file
```

**Validation Error**:
```
Input: Scan card not in sequence
Scanned: 99999999999999999999
Output: Status "NOT IN SEQUENCE", no PLC signal sent
Log: Card marked as not found in file
```

## Performance Benchmarks

### Response Time Benchmarks
- **Validation Processing**: <50ms from scan to result
- **Network Communication**: <100ms UDP round-trip
- **File Loading**: <2 seconds for 10,000 cards
- **UI Updates**: <100ms for status changes
- **Cache Operations**: <500ms for save operations

### Throughput Benchmarks
- **Scan Rate**: 60+ scans per minute sustained
- **Concurrent Heads**: Both heads at full speed simultaneously
- **Network Bandwidth**: <1KB per validation transaction
- **Memory Usage**: <200MB for typical operation

### Reliability Benchmarks
- **Uptime**: 24+ hours continuous operation
- **Error Recovery**: <5 seconds for network reconnection
- **Data Integrity**: 100% log accuracy under normal conditions
- **Cache Corruption**: <0.1% occurrence with atomic writes

---

*This comprehensive testing and validation documentation ensures thorough verification of all system functionality, edge cases, and performance characteristics.*