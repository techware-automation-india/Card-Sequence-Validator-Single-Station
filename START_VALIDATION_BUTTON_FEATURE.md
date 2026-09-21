# Start Validation Button in File Management Window

## Overview

A "Start Validation" button has been added to the bottom of the File Management window for both Head A and Head B. This button allows users to start validation directly from the file management page and automatically switches to the Scanner Logging page.

## Location

The buttons are located at the bottom of the File Management window in an accent panel:
- Left button: "▶ Start Validation - Head B"
- Right button: "▶ Start Validation - Head A"

## Functionality

### Button Behavior

1. **When File is Loaded**:
   - Button is enabled
   - Shows: "▶ Start Validation - Head X"
   - Clicking starts validation and switches to Scanner Logging page

2. **When File is Not Loaded**:
   - Button is disabled
   - Warning shown: "Please load a sequence file before starting validation"

3. **When Validation is Running**:
   - Button text changes to: "▶ Validation Running - Head X"
   - Clicking switches to Scanner Logging page (doesn't restart validation)

### Validation Start Logic

The button uses the same logic as the "Start Validation" button in the Scanner Logging window:

1. **Check if file is loaded**:
   - If no file: Show warning and return
   - If file loaded: Continue

2. **Check if already scanning**:
   - If already scanning: Show info message and switch to Scanner Logging
   - If not scanning: Continue

3. **Check for existing logs**:
   - If logs exist: Show dialog with options:
     - "Clear Logs and Start": Clears logs and starts validation
     - "Continue with Existing Logs": Keeps logs and starts validation
     - "Cancel": Cancels operation
   - If no logs: Start validation immediately

4. **Switch to Scanner Logging page**:
   - After starting validation (or if already running)
   - Uses `open_scanner_callback` to switch pages

## User Experience

### Scenario 1: Starting Fresh Validation
1. User loads a file in File Management window
2. User clicks "▶ Start Validation - Head A"
3. If no logs exist: Validation starts immediately
4. Window switches to Scanner Logging page
5. User sees validation in progress

### Scenario 2: Starting with Existing Logs
1. User loads a file in File Management window
2. User clicks "▶ Start Validation - Head A"
3. Dialog appears: "Existing Logs Found"
4. User chooses:
   - Clear Logs and Start: Logs cleared, validation starts
   - Continue with Existing Logs: Validation continues with existing logs
   - Cancel: Returns to File Management window
5. If not cancelled: Window switches to Scanner Logging page

### Scenario 3: Validation Already Running
1. Validation is already in progress
2. User opens File Management window
3. Button shows: "▶ Validation Running - Head A"
4. User clicks button
5. Info message: "Validation is already in progress"
6. Window switches to Scanner Logging page

### Scenario 4: No File Loaded
1. User hasn't loaded a file yet
2. Button is disabled (grayed out)
3. User clicks button
4. Warning: "Please load a sequence file before starting validation"
5. User remains in File Management window

## Implementation Details

### New Methods

**`create_start_validation_section(parent_layout)`**:
- Creates the button section at bottom of window
- Adds info label and two buttons (Head A and Head B)
- Buttons styled as primary buttons with minimum width 220px

**`start_validation_and_switch(head_id)`**:
- Handles button click for specified head
- Checks if file is loaded
- Checks if already scanning
- Handles existing logs dialog
- Starts validation
- Switches to Scanner Logging page via callback

### UI Updates

**`update_ui(head_id)`** method updated to:
- Enable/disable start validation button based on file loaded state
- Update button text based on scanning state:
  - Not scanning: "▶ Start Validation - Head X"
  - Scanning: "▶ Validation Running - Head X"

### Button References

Buttons stored as instance attributes:
- `self.start_validation_btn_A`
- `self.start_validation_btn_B`

## Visual Design

- Buttons placed in accent panel (`accentPanel` object name)
- Primary button style (blue background)
- Play icon (▶) prefix for visual clarity
- Minimum width: 220px for consistent sizing
- Info label on left: "Ready to start validation? Click below to begin scanning."

## Benefits

✅ **Quick Access**: Start validation without switching windows first
✅ **Consistent Logic**: Same behavior as Scanner Logging start button
✅ **Clear Feedback**: Button text changes based on state
✅ **Automatic Navigation**: Switches to Scanner Logging automatically
✅ **Dual Head Support**: Separate buttons for each head
✅ **Safe Operation**: Checks for file loaded before starting
✅ **Log Handling**: Prompts user about existing logs

## Integration

The feature integrates with:
- File Management window layout
- Scanner Logging window (via callback)
- App state scanning logic
- Existing log handling system
- UI update system

## Files Modified

- `src/ui/file_management_dual.py`:
  - Added `create_start_validation_section()` method
  - Added `start_validation_and_switch()` method
  - Updated `update_ui()` method
  - Modified `__init__()` to include button section
