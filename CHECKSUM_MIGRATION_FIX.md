# Checksum Configuration Migration Fix

## Issue
Head B was not stripping the secret checksum bit because it had an old cached value of `checksum_digits = 0` from before the secret increment feature was implemented.

## Root Cause
- The application loads cached configuration values on startup
- Head B had `checksum_digits: 0` saved in the unified cache file
- This old value overrode the new default of `checksum_digits: 1`
- Cache file location: `C:\Users\[username]\AppData\Local\YourCompany\CardSequenceValidator\app_cache_unified.json`

## Solution Implemented

### Automatic Migration (src/app_state.py, Line 375-382)

Added automatic migration logic when loading cache:

```python
# Restore checksum configuration with migration
cached_checksum = cache.get('checksum_digits', 1)
# Migrate old value: if cached value is 0, update to new default of 1
if cached_checksum == 0:
    self.checksum_digits = 1
    # Save the migrated value immediately
    self.save_cache()
else:
    self.checksum_digits = cached_checksum
```

### How It Works

1. **On Application Startup**:
   - Each head (A and B) loads its cached configuration
   - If `checksum_digits == 0` is found (old default), it's automatically updated to `1` (new default)
   - The updated value is immediately saved to cache

2. **Migration is Automatic**:
   - No user action required
   - Happens once per head on first startup after update
   - Future startups will load the correct value

3. **Preserves User Settings**:
   - Only migrates the old default value of `0`
   - If user has set any other value (1-5), it's preserved
   - User can still manually change checksum configuration

## Verification

After this fix, both Head A and Head B will:
- Default to `checksum_digits = 1` (strips 1 digit for main scanner)
- Display "0 (None)" in UI (user sees no stripping)
- Actually strip 1 digit in backend (secret increment)

### Testing
1. Start the application
2. Check Job Management window for both heads
3. Verify "Checksum Digits" dropdown shows "0 (None)" selected
4. Backend will strip 1 digit for main scanner validation
5. On-demand scanner will strip 0 digits (uses UI value)

## Manual Fix (If Needed)

If automatic migration doesn't work, manually edit the cache file:

1. Close the application
2. Navigate to: `C:\Users\[YourUsername]\AppData\Local\YourCompany\CardSequenceValidator\`
3. Open `app_cache_unified.json` in a text editor
4. Find the `head_b` section
5. Change `"checksum_digits": 0` to `"checksum_digits": 1`
6. Save the file
7. Restart the application

## Cache File Structure

```json
{
  "head_a": {
    "checksum_digits": 1,
    ...
  },
  "head_b": {
    "checksum_digits": 1,
    ...
  }
}
```

## Related Files
- `src/app_state.py` - Migration logic
- `src/ui/file_management_dual.py` - UI display with offset
- `CHECKSUM_FEATURE.md` - Original checksum feature documentation
- `USER_GUIDE.md` - User-facing documentation

## Date
2026-03-01
