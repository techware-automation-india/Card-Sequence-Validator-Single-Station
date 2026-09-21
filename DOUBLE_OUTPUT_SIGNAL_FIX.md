# Double Output Signal Fix - Jump Dialog Issue

## Issue Description
When scanning a card that's ahead in the sequence (triggering the jump dialog), the system was sending TWO output signals:
1. First output signal sent immediately
2. Second output signal sent after user responds to the dialog

This caused duplicate signals to be sent to the output device, which is incorrect behavior.

## Specific Scenario
1. User is at card position X
2. User scans a wrong card → receives "NOT OK"
3. User scans the last card (which is ahead in sequence)
4. System detects card is ahead → pauses and shows jump dialog
5. **BUG**: System sends first output signal
6. User clicks "Jump to Card" on dialog
7. **BUG**: System sends second output signal (duplicate)

## Root Cause

In `src/app_state.py`, the `_perform_mismatch_resolution()` method had incorrect placement of `resume_scanning()`:

### Before Fix:
```python
def _perform_mismatch_resolution(self, scanned_code, approved, future_index):
    # ... processing logic ...
    
    if approved and future_index != -1:
        # Handle approved jump
        # ... skip cards logic ...
        self.send_output_signal(status)  # Send output
        self.log_updated.emit(log_entries)
        self.state_changed.emit()
        return  # Exit without resuming
    else:
        # Handle cancelled jump
        self.send_output_signal("NOT OK")
    
    self.log_updated.emit(log_entries)
    self.resume_scanning()  # ❌ WRONG: Resumes for both approved and cancelled
    self.state_changed.emit()
```

### Problem:
- When jump was approved, the method returned early WITHOUT calling `resume_scanning()`
- When jump was cancelled, `resume_scanning()` was called at the end
- This caused scanning to remain paused after approved jumps
- OR if there was a race condition, the same card could be processed twice

## Solution Implemented

### After Fix:
```python
def _perform_mismatch_resolution(self, scanned_code, approved, future_index):
    # ... processing logic ...
    
    if approved and future_index != -1:
        # Handle approved jump (both top-to-bottom and bottom-to-top)
        # ... skip cards logic ...
        self.send_output_signal(status)  # Send output ONCE
        
        # ✓ Resume scanning after successful jump
        self.resume_scanning()
        
        self.log_updated.emit(log_entries)
        self.state_changed.emit()
        return
    else:
        # Handle cancelled jump
        self.send_output_signal("NOT OK")
        
        # ✓ Resume scanning only when jump is cancelled
        self.resume_scanning()
    
    self.log_updated.emit(log_entries)
    self.state_changed.emit()
```

### Changes Made:

1. **Top-to-Bottom Jump (Line 1368-1374)**:
   - Added `self.resume_scanning()` after sending output signal
   - Ensures scanning resumes immediately after approved jump

2. **Bottom-to-Top Jump (Line 1343-1349)**:
   - Added `self.resume_scanning()` after sending output signal
   - Ensures scanning resumes immediately after approved jump

3. **Cancelled Jump (Line 1380-1383)**:
   - Moved `self.resume_scanning()` inside the else block
   - Only resumes when user cancels the jump

## Expected Behavior After Fix

### Scenario 1: User Approves Jump
1. Card detected ahead in sequence
2. Scanning pauses
3. Dialog shown to user
4. User clicks "Jump to Card"
5. System sends **ONE** output signal (OK (JUMPED) or LAST OK (JUMPED))
6. Scanning resumes automatically
7. User can continue scanning next cards

### Scenario 2: User Cancels Jump
1. Card detected ahead in sequence
2. Scanning pauses
3. Dialog shown to user
4. User clicks "Cancel"
5. System sends **ONE** output signal (NOT OK)
6. Scanning resumes automatically
7. User stays at current expected position

## Output Signals

### Single Card Mode:
- Approved Jump: `17\r\n` (OK (JUMPED)) or `19\r\n` (LAST OK (JUMPED))
- Cancelled Jump: `18\r\n` (NOT OK)

### Half Card Mode:
- Approved Jump: `09\r\n` (OK (JUMPED)) or `11\r\n` (LAST OK (JUMPED))
- Cancelled Jump: `10\r\n` (NOT OK)

### Quarter Card Mode:
- Approved Jump: `05\r\n` (OK (JUMPED)) or `07\r\n` (LAST OK (JUMPED))
- Cancelled Jump: `06\r\n` (NOT OK)

## Testing Recommendations

1. **Test Approved Jump**:
   - Load a sequence file
   - Skip a few cards
   - Scan a card that's ahead in sequence
   - Click "Jump to Card"
   - Verify only ONE output signal is sent
   - Verify scanning continues normally

2. **Test Cancelled Jump**:
   - Load a sequence file
   - Skip a few cards
   - Scan a card that's ahead in sequence
   - Click "Cancel"
   - Verify only ONE "NOT OK" signal is sent
   - Verify you stay at current position

3. **Test Last Card Jump**:
   - Load a sequence file
   - Skip to near the end
   - Scan the last card (ahead in sequence)
   - Click "Jump to Card"
   - Verify only ONE "LAST OK (JUMPED)" signal is sent
   - Verify sequence completes properly

4. **Test Both Heads**:
   - Repeat above tests for Head A
   - Repeat above tests for Head B
   - Verify both behave identically

## Related Files
- `src/app_state.py` - Main fix location (_perform_mismatch_resolution method)
- `src/ui/scanner_logging_dual.py` - Dialog display (show_approval_dialog method)
- `src/services/udp_reader.py` - Pause/resume mechanism
- `USER_GUIDE.md` - User documentation (Scenario 3: Card Found Ahead in Sequence)

## Date
2026-03-01
