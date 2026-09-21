# Download Before Clear Feature

## Overview

All "Clear Logs" functionality has been updated to automatically download logs before clearing them. This prevents accidental data loss and ensures logs are always saved before being removed.

## Changes Made

### 1. File Management Window - Clear Logs Button

**Old Behavior**:
- Button text: "🗑 Clear Logs"
- Clicking would prompt: "Clear all logs?"
- Logs would be deleted without saving

**New Behavior**:
- Button text: "💾 Download & Clear Logs"
- Clicking prompts: "This will download the logs and then clear them. Do you want to continue?"
- If Yes: Opens save dialog, downloads logs, then clears
- If download is cancelled: Logs are NOT cleared
- Success message: "Logs downloaded and cleared"

### 2. File Management Window - Fresh Start Option

**Old Behavior**:
- Button text: "Fresh Start (Clear Logs)"
- Would clear logs immediately

**New Behavior**:
- Button text: "Fresh Start (Download & Clear)"
- Downloads logs first, then clears
- If download is cancelled: Operation is aborted, logs remain

### 3. File Management Window - Start Validation Dialog

**Old Behavior**:
- Button text: "Clear Logs and Start"
- Informative text: "Do you want to clear the logs before starting a new scan? You can save the logs from the File & Log Management window."

**New Behavior**:
- Button text: "Download, Clear & Start"
- Informative text: "Do you want to download and clear the logs before starting a new scan?"
- Downloads logs first, then clears and starts scanning
- If download is cancelled: Scanning does NOT start

### 4. Scanner Logging Window - Start Validation Dialog

**Old Behavior**:
- Button text: "Clear Logs and Start"
- Would clear logs and start scanning

**New Behavior**:
- Button text: "Clear and Start"
- Informative text: "To download logs, use the File Management window. Do you want to clear the logs and start a new scan?"
- Note: Scanner Logging window doesn't have download functionality, so it directs users to File Management window

## User Experience

### Scenario 1: Clearing Logs from File Management

1. User has 100 log entries
2. User clicks "💾 Download & Clear Logs"
3. Dialog appears: "This will download the logs and then clear them. Do you want to continue?"
4. User clicks "Yes"
5. Save file dialog appears
6. User selects location and saves file
7. Logs are downloaded as CSV
8. Logs are cleared from memory
9. Success message: "Logs downloaded and cleared"

### Scenario 2: User Cancels Download

1. User clicks "💾 Download & Clear Logs"
2. Dialog appears
3. User clicks "Yes"
4. Save file dialog appears
5. User clicks "Cancel" on save dialog
6. Warning message: "Logs were not cleared because download was cancelled"
7. Logs remain in memory (not cleared)

### Scenario 3: Fresh Start When Reloading File

1. User reopens app after crash
2. Previous logs exist (50 entries)
3. User clicks "Load File" and selects previous file
4. Dialog: "Previous session logs found (50 entries)"
5. User clicks "Fresh Start (Download & Clear)"
6. Save file dialog appears
7. User saves logs
8. Logs are cleared
9. File loads fresh from beginning

### Scenario 4: Starting Validation with Existing Logs

1. User has completed a scan (200 entries)
2. User clicks "▶ Start Validation"
3. Dialog: "Existing Logs Found - Do you want to download and clear the logs before starting a new scan?"
4. User clicks "Download, Clear & Start"
5. Save file dialog appears
6. User saves logs
7. Logs are cleared
8. New validation starts

## Implementation Details

### Clear Logs Method Update

**Before**:
```python
def clear_logs(self, head_id):
    head = self.head_a if head_id == 'A' else self.head_b
    reply = QMessageBox.question(self, "Confirm", f"Head {head_id}: Clear all logs?")
    if reply == QMessageBox.StandardButton.Yes:
        head.clear_logs()
        QMessageBox.information(self, "Success", f"Head {head_id}: Logs cleared.")
```

**After**:
```python
def clear_logs(self, head_id):
    head = self.head_a if head_id == 'A' else self.head_b
    
    if not head.log_data:
        QMessageBox.information(self, "No Logs", f"Head {head_id}: No logs to clear.")
        return
    
    reply = QMessageBox.question(
        self, 
        "Download and Clear Logs", 
        f"Head {head_id}: This will download the logs and then clear them.\n\nDo you want to continue?"
    )
    
    if reply == QMessageBox.StandardButton.Yes:
        # Download logs first
        if self.download_logs(head_id):
            # Only clear if download was successful
            head.clear_logs()
            QMessageBox.information(self, "Success", f"Head {head_id}: Logs downloaded and cleared.")
        else:
            # Download was cancelled or failed
            QMessageBox.warning(self, "Cancelled", f"Head {head_id}: Logs were not cleared because download was cancelled.")
```

### Fresh Start Logic Update

**Before**:
```python
if clicked_button == fresh_btn:
    head.clear_logs()
```

**After**:
```python
if clicked_button == fresh_btn:
    # Download logs first, then clear
    if self.download_logs(head_id):
        head.clear_logs()
    else:
        # Download cancelled, don't proceed
        return
```

### Start Validation Logic Update

**Before**:
```python
if clicked_button == clear_button:
    head.clear_logs()
    head.start_scanning()
```

**After**:
```python
if clicked_button == clear_button:
    # Download logs first, then clear and start
    if self.download_logs(head_id):
        head.clear_logs()
        head.start_scanning()
    else:
        # Download cancelled, don't proceed
        return
```

## Benefits

✅ **Prevents Data Loss**: Logs are always saved before clearing
✅ **User Control**: User can cancel download to keep logs
✅ **Clear Intent**: Button text clearly indicates download will happen
✅ **Consistent Behavior**: All clear operations work the same way
✅ **Safe Operation**: No accidental log deletion
✅ **Audit Trail**: All logs are preserved in files

## Edge Cases Handled

1. **No Logs to Clear**:
   - Shows message: "No logs to clear"
   - No download dialog appears

2. **Download Cancelled**:
   - Logs are NOT cleared
   - Warning message explains why
   - User can try again

3. **Download Failed**:
   - Logs are NOT cleared
   - User is notified
   - Can retry operation

4. **Scanner Logging Window**:
   - Doesn't have download functionality
   - Directs users to File Management window
   - Still allows clearing (with warning)

## Files Modified

- `src/ui/file_management_dual.py`:
  - Updated button text: "💾 Download & Clear Logs"
  - Updated `clear_logs()` method to download first
  - Updated "Fresh Start" button text and logic
  - Updated "Start Validation" dialog text and logic

- `src/ui/scanner_logging_dual.py`:
  - Updated dialog text to direct users to File Management
  - Updated button text to "Clear and Start"

## User Guidance

**Best Practice**:
- Use File Management window for log operations
- Download logs regularly during long validation sessions
- Review downloaded logs for quality assurance
- Keep downloaded logs for audit purposes

**When to Use**:
- After completing a validation session
- Before starting a new validation on same file
- When switching to a different file
- Before closing the application
