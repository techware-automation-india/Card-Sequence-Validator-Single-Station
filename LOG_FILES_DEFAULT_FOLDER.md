# Log Files Default Folder Feature

## Overview
All download log operations now default to saving files in a `csv_logs` folder on the desktop, which is automatically created if it doesn't exist.

## Implementation Details

### Files Modified
1. `src/ui/file_management_dual.py` - `download_logs()` method
2. `src/ui/scanner_logging_dual.py` - `download_logs_for_head()` method

### Changes Made

#### Both Methods Now Include:
1. **Automatic Folder Creation**
   ```python
   desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
   log_dir = os.path.join(desktop_path, "csv_logs")
   if not os.path.exists(log_dir):
       os.makedirs(log_dir)
   ```

2. **Default File Path in csv_logs Directory on Desktop**
   ```python
   default_filename = f"logs_head_{head_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
   default_path = os.path.join(log_dir, default_filename)
   ```

3. **File Dialog Opens in csv_logs Directory on Desktop**
   ```python
   file_path, _ = QFileDialog.getSaveFileName(
       self, f"Save Logs - Head {head_id}",
       default_path,  # Opens in csv_logs folder on desktop
       "CSV Files (*.csv)"
   )
   ```

## User Experience

### Before
- File dialog opened in application root directory
- Users had to manually navigate to desired save location
- No default folder structure for logs

### After
- File dialog opens in `csv_logs` directory on desktop by default
- `csv_logs` folder is automatically created on desktop on first download
- Default filename includes head ID and timestamp: `logs_head_A_20260301_164634.csv`
- Users can still navigate to other folders if desired

## Affected Operations

### 1. File Management Window
- "Download and Clear Logs" button for both Head A and Head B
- Located in "Validation Log Management" section

### 2. Scanner Logging Window
- "Download, Clear & Start" option when starting validation with existing logs
- Triggered from "Start Validation" button when logs are present

## Benefits
1. **Organization**: All logs are centralized in one folder
2. **Convenience**: No need to navigate folders every time
3. **Automatic Setup**: Folder is created automatically when needed
4. **Flexibility**: Users can still choose different locations if needed
5. **Consistency**: Same behavior across both download methods

## Technical Notes
- Uses `os.makedirs()` to create folder if missing
- No error if folder already exists
- Timestamp format: `YYYYMMDD_HHMMSS`
- File naming convention: `logs_head_{A|B}_{timestamp}.csv`
