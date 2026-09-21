# File Recovery After Crash/Restart

## Behavior

When the application crashes or is abruptly closed, the file management window will remember the last file path that was being used, but the file will NOT be automatically loaded. All file data is cleared on restart.

## User Experience

### On Restart

1. After restart, the file status will show: `Not loaded: [filename] (Click 'Load File' to continue)`
2. The "Start Scanning" button will be disabled (no file loaded)
3. The user must click the "Load File" button to continue working

### When Loading Previous File

When clicking "Load File" after restart, the user will see:

1. **First Dialog**: "Load Previous File"
   - Load Previous
   - Select New File
   - Cancel

2. If "Load Previous" is selected:
   - **Card Type Selection**: Choose Single/Half/Quarter card type
   
3. If logs exist from previous session:
   - **Resume Session Dialog**: "Previous session logs found (X entries)"
     - **Continue from Last Use**: Keeps existing logs AND restores scan position to continue from where you left off
     - **Fresh Start (Clear Logs)**: Clears all logs and starts validation from the beginning
     - Cancel

### Continue from Last Use Behavior

When "Continue from Last Use" is selected:
- Existing logs are preserved
- Scan state is restored from logs
- Current card index is set to the next card after the last successfully scanned card
- Validation continues from that position (not from the beginning)
- Success message shows: "Resumed from card index X"

**How it works**:
1. System searches logs in reverse order for last successful scan (status "OK" or "OK (JUMPED)")
2. Finds the card index of that scan
3. Sets current_card_index to next card (last_index + 1)
4. If all cards were scanned, starts from beginning
5. If no successful scans found, starts from beginning

### Fresh Start Behavior

When "Fresh Start (Clear Logs)" is selected:
- All logs are cleared
- Scan state is reset to beginning
- Validation starts from card index 0
- Treats file as newly loaded

### When Loading a Different File

If selecting a new file (not the previous one) and logs exist:
- **Unsaved Log Data Dialog**: "Unsaved log data detected"
  - Export and Clear
  - Clear and Continue
  - Cancel

## What is Preserved

- File path: `selected_file_path` (displayed but not loaded)
- Log data: Previous scan logs are preserved
- Network configuration: All UDP/COM settings
- Checksum settings: Number of checksum digits
- Theme preference: Dark/Light theme

## What is Cleared on Restart

- File data: `expected_cards` array is emptied
- QR lookups: `qr_to_index` and `numcard_to_qrs` dictionaries cleared
- Scan state: `current_card_index`, `start_card_has_been_scanned` reset
- Start card: `start_card_code` cleared
- On-demand scan state: All waiting flags reset

## What is Restored with "Continue from Last Use"

- Scan position: `current_card_index` set to next unscanned card
- Scan flags: `start_card_has_been_scanned` and `first_scan_received` updated
- Log data: All previous logs retained
- File data: `expected_cards` and lookup dictionaries rebuilt from file

## Implementation Details

- File path is persisted in cache: `selected_file_path`
- File data is NOT auto-loaded on startup (no automatic call to `load_file()`)
- All file-related data structures are explicitly cleared in `load_cache()`
- UI distinguishes between:
  - File loaded: `has_file = bool(head.expected_cards)`
  - File path exists but not loaded: `has_file_path = bool(head.selected_file_path)`
- Clear button remains enabled even when file is not loaded (to clear the remembered path)
- `is_reloading_previous` flag determines which log dialog to show
- `should_restore_state` flag triggers scan state restoration
- `restore_scan_state_from_logs()` method analyzes logs to find resume position

## Benefits

- Prevents automatic loading of potentially corrupted state after crash
- Gives user control over whether to continue with previous file
- Allows resuming work from exact position where they left off
- Allows fresh start if needed (clearing logs)
- Requires explicit card type selection to ensure correct configuration
- Maintains file path for convenience while ensuring data integrity
- Prevents accidental scanning with stale data
- Different handling for reloading vs loading new file
- Intelligent resume: continues from next unscanned card, not from beginning
- No duplicate scans when resuming
