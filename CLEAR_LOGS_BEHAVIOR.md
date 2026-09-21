# Clear Logs Behavior

## Overview
When logs are cleared, the system now performs a complete reset of the scanning state, treating the loaded file as fresh and ready for a new scanning session.

## What Gets Reset

### 1. Log Data
- All scan log entries are cleared
- Log table is emptied
- Pagination is reset to page 0

### 2. Display Fields (Scanner Logging Window)
- **Last Scanned ID**: Reset to "Awaiting Scan Input..."
- **Previous Validated ID**: Reset to "N/A"
- **Next Expected ID**: Reset to appropriate message based on file status

### 3. Scanning State (AppState)
- `current_card_index`: Reset to 0
- `start_card_has_been_scanned`: Reset to False
- `first_scan_received`: Reset to True
- `start_card_code`: Reset to None

### 4. On-Demand Scanning State
- `is_waiting_for_start_card`: Reset to False
- `is_waiting_for_count_card_1`: Reset to False
- `is_waiting_for_count_card_2`: Reset to False
- `first_card_index`: Reset to -1

## What Does NOT Get Reset

### Preserved Settings
- ✅ Loaded file path and sequence data
- ✅ Network configuration (UDP/COM ports)
- ✅ Card type selection
- ✅ Scan direction (top-to-bottom or bottom-to-top)
- ✅ Checksum configuration
- ✅ Output format selection
- ✅ Theme settings

## User Experience

### Before Clear Logs
```
Scanner State:
- Current Card Index: 150
- Start Card: 89012345678901234567
- Start Card Scanned: Yes
- Logs: 150 entries

Display:
- Last Scanned ID: 89012345678901234717
- Previous Validated ID: 89012345678901234716
- Next Expected ID: 89012345678901234718
```

### After Clear Logs
```
Scanner State:
- Current Card Index: 0
- Start Card: None
- Start Card Scanned: No
- Logs: 0 entries

Display:
- Last Scanned ID: Awaiting Scan Input...
- Previous Validated ID: N/A
- Next Expected ID: Start scanning to set start card
```

### Next Scan After Clear
```
First scan will:
1. Set the start card (any card from the file)
2. Determine scan side automatically
3. Begin validation from that card
4. Continue in the configured scan direction
```

## Use Cases

### Use Case 1: Restart Validation
**Scenario**: User completed scanning 500 cards but wants to scan them again
1. Click "Clear Logs" in File Management window
2. Confirm clear action
3. All logs cleared, state reset
4. Click "Start Validation" in Scanner Logging window
5. First scan sets new start card
6. Validation continues from there

### Use Case 2: Switch Scan Direction Mid-Session
**Scenario**: User realizes they need to scan in opposite direction
1. Stop scanning
2. Clear logs (resets state)
3. Change scan direction in File Management window
4. Start scanning again
5. First scan sets start card for new direction

### Use Case 3: Recover from Errors
**Scenario**: Many validation errors occurred, user wants fresh start
1. Clear logs
2. State is reset
3. File remains loaded
4. Start scanning with clean slate

### Use Case 4: Multiple Runs on Same File
**Scenario**: Quality control requires multiple validation passes
1. Complete first pass (all cards scanned)
2. Clear logs
3. Start second pass
4. Each pass is independent

## Implementation Details

### clear_logs() Method
```python
def clear_logs(self):
    """Clear logs and reset scanning state to treat file as fresh"""
    self.log_data = []
    
    # Reset scanning state
    self.current_card_index = 0
    self.start_card_has_been_scanned = False
    self.first_scan_received = True
    self.start_card_code = None
    
    # Reset on-demand scanning state
    self.is_waiting_for_start_card = False
    self.is_waiting_for_count_card_1 = False
    self.is_waiting_for_count_card_2 = False
    self.first_card_index = -1
    
    self.log_cleared.emit()
    self.state_changed.emit()
    self.save_cache()
```

### Signal Flow
1. `clear_logs()` is called
2. State variables are reset
3. `log_cleared` signal is emitted
4. Scanner Logging window receives signal
5. Display fields are cleared
6. `state_changed` signal is emitted
7. UI updates to reflect fresh state
8. Cache is saved with reset state

## Benefits

✅ **Clean slate**: Each scanning session starts fresh
✅ **No residual state**: Previous scan doesn't affect new scan
✅ **Flexible start point**: Can start from any card in sequence
✅ **Direction changes**: Can change scan direction between sessions
✅ **Error recovery**: Easy to recover from problematic scans
✅ **Multiple passes**: Same file can be scanned multiple times independently

## Testing Recommendations

**Test 1: Basic Clear and Restart**
1. Load file and scan 50 cards
2. Clear logs
3. Verify all display fields reset
4. Start scanning again
5. Verify first scan sets new start card

**Test 2: Clear During Active Scan**
1. Start scanning
2. Scan 10 cards
3. Clear logs while scanning
4. Verify scanning stops or continues correctly
5. Verify state is reset

**Test 3: Clear with No File**
1. Clear logs when no file is loaded
2. Verify no errors occur
3. Verify display shows "No file loaded"

**Test 4: Clear and Change Direction**
1. Scan top-to-bottom for 50 cards
2. Clear logs
3. Change to bottom-to-top
4. Start scanning
5. Verify new direction is used

**Test 5: Multiple Clears**
1. Clear logs
2. Scan 10 cards
3. Clear logs again
4. Verify state resets each time

**Test 6: Dual Head Independence**
1. Scan on HEAD A
2. Clear logs on HEAD A only
3. Verify HEAD B is unaffected
4. Verify HEAD A state is reset

**Test 7: Persistence After Clear**
1. Clear logs
2. Close application
3. Reopen application
4. Verify state remains reset (not restored to pre-clear state)

## Edge Cases

### Edge Case 1: Clear During Mismatch Dialog
- If mismatch approval dialog is open
- User clears logs from another window
- Dialog should close or handle gracefully

### Edge Case 2: Clear with Unsaved Logs
- Warning dialog asks to export first
- User chooses to clear without exporting
- State is reset, logs are lost

### Edge Case 3: Clear After Sequence Complete
- All cards have been scanned
- User clears logs
- Can start scanning again from any card

## Summary

The clear logs functionality now provides a complete reset of the scanning state, allowing users to start fresh validation sessions without reloading the file. This improves flexibility, error recovery, and supports multiple validation passes on the same card sequence. The file and configuration remain intact, while all scanning progress and state are reset to initial values.
