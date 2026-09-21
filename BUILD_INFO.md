# Card Sequence Validator - Build Information

## Build Date
Built on: March 2, 2026

## Version Changes in This Build

### 1. Fixed Bottom-to-Top Scanning Bug
- **Issue**: When scanning bottom-to-top and skipping a card, the log showed the wrong ICCID for the skipped card
- **Fix**: Corrected the range calculation in `_perform_mismatch_resolution()` function
- **Impact**: Skipped cards now display the correct ICCID in the log

### 2. Added Default Log Location Configuration
- **New Feature**: Added configurable default log directory
- **Location**: Constants file now includes `get_default_log_directory()` function
- **Options Available**:
  - Documents folder: `~/Documents/CardSequenceValidator/Logs` (default)
  - AppData folder: Can be enabled by uncommenting in constants.py
  - Custom fixed location: Can be set to any path
- **Control**: `FORCE_DEFAULT_LOG_LOCATION` flag to enforce default location

## File Locations

### Executable
- **Location**: `dist/CardSequenceValidator.exe`
- **Size**: 40.70 MB
- **Type**: Single-file executable (no installation required)

### Cache Files
- **Location**: `C:\Users\<Username>\AppData\Local\YourCompany\CardSequenceValidator\`
- **File**: `app_cache_unified.json`
- **Purpose**: Stores application settings, network configurations, and scan state for both Head A and Head B

### Log Files (When Exported)
- **Default Location**: `C:\Users\<Username>\Desktop\csv_logs\`
- **Format**: CSV files with timestamp
- **Naming**: `logs_head_A_YYYYMMDD_HHMMSS.csv` or `logs_head_B_YYYYMMDD_HHMMSS.csv`
- **Note**: Logs are stored in memory during operation and exported to CSV on demand

## How to Use the Executable

1. Navigate to the `dist` folder
2. Copy `CardSequenceValidator.exe` to your desired location
3. (Optional) Copy `license.dat` if license validation is required
4. Run the executable - no installation needed!

## Distribution

To distribute to users:
1. Copy the entire `dist` folder OR just the `CardSequenceValidator.exe` file
2. Include `README.txt` for user instructions
3. Ensure users have Windows 10 or later

## Testing Checklist

Before distributing, test the following:
- [ ] Application launches without errors
- [ ] Both Head A and Head B can load CPD files
- [ ] Network scanning works (UDP)
- [ ] Serial port scanning works (COM ports)
- [ ] Bottom-to-top scanning correctly identifies skipped cards
- [ ] Top-to-bottom scanning works as expected
- [ ] Log export saves to correct location
- [ ] Settings persist after closing and reopening
- [ ] License validation works (if applicable)

## Known Issues

None in this build.

## Technical Details

### Build Configuration
- **Tool**: PyInstaller 6.15.0
- **Python Version**: 3.13
- **Build Type**: Single-file executable (--onefile)
- **GUI Mode**: Windowed (no console)
- **Icon**: assets/Icon.png

### Included Dependencies
- PyQt6 (GUI framework)
- serial (COM port communication)
- appdirs (cross-platform directory paths)
- cryptography (license validation)
- platformdirs (user data directories)

### Excluded Modules (for smaller size)
- matplotlib
- numpy
- pandas
- scipy
- PIL

## Support

For issues or questions:
1. Check the README.txt in the dist folder
2. Review the log files for error messages
3. Contact your system administrator
