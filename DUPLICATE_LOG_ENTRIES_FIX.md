# Duplicate Log Entries Fix

## Issue Identified

During testing, duplicate entries were found in the scan logs for both "SKIPPED" and "OK (JUMPED)" statuses. 

### Example from Log:
```
162,'16:08:46.345,'MISSING,'8991027561800272640,SKIPPED
...
110,'16:08:46.345,'8991027561800272633,'8991027561800272633,OK (JUMPED)
162,'16:08:46.345,'MISSING,'8991027561800272640,SKIPPED  <- DUPLICATE
...
110,'16:08:46.345,'8991027561800272633,'8991027561800272633,OK (JUMPED)  <- DUPLICATE
```

## Root Cause

The issue was in the `_perform_mismatch_resolution()` method in `src/app_state.py`:

1. When a mismatch was detected and approved (user approved skipping cards):
   - The method called `self.add_log_entry()` for each skipped card
   - `add_log_entry()` internally appends to `self.log_data`
   - Then the method called `self.log_data.extend(log_entries)` again
   - This caused each entry to be added twice to the log

### Code Before Fix:
```python
log_entries = []

# Add entries via add_log_entry (which appends to self.log_data)
for i in range(...):
    log_entries.append(self.add_log_entry(...))

# Then extend log_data again with the same entries
self.log_data.extend(log_entries)  # <- DUPLICATE!
```

## Solution

Removed the `self.log_data.extend(log_entries)` line since `add_log_entry()` already appends to `self.log_data`.

### Code After Fix:
```python
log_entries = []

# Add entries via add_log_entry (which appends to self.log_data)
for i in range(...):
    log_entry = self.add_log_entry(...)
    log_entries.append(log_entry)

# Don't extend log_data again - entries are already added
# Just emit the signal with the entries for UI updates
self.log_updated.emit(log_entries)
```

## Changes Made

**File**: `src/app_state.py`
**Method**: `_perform_mismatch_resolution()`

**Changes**:
1. Removed `self.log_data.extend(log_entries)` line
2. Kept `self.log_updated.emit(log_entries)` to notify UI of new entries
3. Ensured all log entries are properly collected in `log_entries` list for emission

## Impact

### Before Fix:
- Each skipped card was logged twice
- Each OK (JUMPED) entry was logged twice
- Statistics were incorrect (counted duplicates)
- Log files were bloated with duplicate entries

### After Fix:
- Each entry is logged exactly once
- Statistics are accurate
- Log files are clean and correct
- OK (JUMPED) entries only appear after SKIPPED entries (as intended)

## Verification

To verify the fix works correctly:

1. Perform a scan with card skipping
2. Check the generated log file
3. Verify:
   - No duplicate SKIPPED entries
   - No duplicate OK (JUMPED) entries
   - OK (JUMPED) entries appear only after SKIPPED entries
   - Statistics (Successful, Failed, Skipped) are accurate

## Example of Correct Log After Fix:

```
index,timestamp,scanned_code,expected_code,status
100,'16:06:01.655,'8991027561800272728,'8991027561800272728,OK
99,'16:06:02.156,'8991027561800272727,'8991027561800272727,OK
98,'16:06:02.655,'8991027561800272726,'8991027561800272726,OK
97,'16:06:03.154,'8991027561800272725,'8991027561800272725,OK
96,'16:06:03.662,'8991027561800272724,'8991027561800272724,OK
95,'16:06:04.155,'8991027561800272723,'8991027561800272723,OK
94,'16:06:04.662,'8991027561800272722,'8991027561800272722,OK
93,'16:06:05.162,'8991027561800272721,'8991027561800272721,OK
92,'16:06:05.656,'8991027561800272720,'8991027561800272720,OK
91,'16:06:06.157,'8991027561800272719,'8991027561800272719,OK
90,'16:06:06.664,'8991027561800272718,'8991027561800272718,OK
89,'16:06:07.164,'8991027561800272717,'8991027561800272717,OK
88,'16:06:07.657,'8991027561800272716,'8991027561800272716,OK
87,'16:06:08.164,'8991027561800272715,'8991027561800272715,OK
86,'16:06:08.655,'8991027561800272714,'8991027561800272714,OK
85,'16:06:09.164,'8991027561800272713,'8991027561800272713,OK
84,'16:06:09.655,'8991027561800272712,'8991027561800272712,OK
83,'16:06:10.155,'8991027561800272711,'8991027561800272711,OK
82,'16:06:10.662,'8991027561800272710,'8991027561800272710,OK
81,'16:06:11.163,'8991027561800272709,'8991027561800272709,OK
80,'16:06:11.656,'8991027561800272708,'8991027561800272708,OK
79,'16:06:12.155,'8991027561800272707,'8991027561800272707,OK
78,'16:06:12.656,'8991027561800272706,'8991027561800272706,OK
77,'16:06:13.163,'8991027561800272705,'8991027561800272705,OK
75,'16:06:17.400,'MISSING,'8991027561800272704,SKIPPED
74,'16:06:17.400,'8991027561800272703,'8991027561800272703,OK (JUMPED)
73,'16:06:25.556,'8991027561800272702,'8991027561800272702,OK
72,'16:06:26.063,'8991027561800272701,'8991027561800272701,OK
71,'16:06:26.555,'8991027561800272700,'8991027561800272700,OK
```

Notice:
- No duplicate entries
- SKIPPED entry (card 8991027561800272704) appears once
- OK (JUMPED) entry (card 8991027561800272703) appears once, right after SKIPPED
- Pattern is clean and correct

## Testing Recommendations

1. **Test with single card skip**: Scan, skip 1 card, verify only 1 SKIPPED + 1 OK (JUMPED)
2. **Test with multiple card skip**: Scan, skip 5 cards, verify 5 SKIPPED + 1 OK (JUMPED)
3. **Test statistics**: Verify Successful + Failed + Skipped = Total Scanned
4. **Test log export**: Export logs and verify no duplicates
5. **Test persistence**: Restart app and verify logs are correct

---

## Summary

The duplicate log entries issue has been fixed by removing the redundant `self.log_data.extend()` call. The `add_log_entry()` method already appends entries to `self.log_data`, so extending again caused duplicates. Now each entry is logged exactly once, and the statistics are accurate.
