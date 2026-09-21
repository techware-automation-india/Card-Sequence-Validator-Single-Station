# Checksum Feature Implementation

## Overview
The checksum feature allows the system to handle scanned QR codes that have checksum digits appended to the end. The file ICCIDs do NOT contain checksums, but the physical cards being scanned may have 1-3 checksum digits added.

## How It Works

### Configuration
- Located in the **File Management** window under "Checksum Configuration"
- Options: 0 (None), 1, 2, or 3 digits
- Default: 0 (no checksum stripping)
- Settings are saved independently for HEAD A and HEAD B

### Processing Flow

1. **Scanner reads QR code** with checksum appended
   - Example: `89012345678901234567890123` (ICCID + 3 digit checksum)

2. **System strips checksum** before validation
   - If checksum_digits = 3: `89012345678901234567890123` → `89012345678901234567`

3. **Validation** against file ICCID (without checksum)
   - File contains: `89012345678901234567`
   - Stripped code: `89012345678901234567`
   - Match: ✓ OK

4. **Logging** uses trimmed value only
   - Log entry shows: `89012345678901234567` (without checksum)
   - Original checksum is discarded

### Key Points

✅ **File ICCIDs are NEVER modified** - they remain without checksums
✅ **Scanned codes are trimmed** before any comparison
✅ **Logs show trimmed values** - checksum is not stored
✅ **Independent configuration** for each head (A and B)
✅ **Applies to all scan types**:
   - Main scanning (validation)
   - On-demand card details scan
   - Card range counting

## UI Components

### Checksum Configuration Section
Located in File Management window between "Sequence File Operations" and "Sequence Control Tools":

```
┌─────────────────────────────────────┐
│ Checksum Configuration              │
├─────────────────────────────────────┤
│ Strip checksum digits from the end  │
│ of scanned codes before validation. │
│                                     │
│ Checksum Digits: [0 (None) ▼]      │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Example:                        │ │
│ │ Scanned: 123456789              │ │
│ │ Validated: 123456789            │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### Example Display
The example updates dynamically based on selection:
- **0 digits**: Scanned: 123456789 → Validated: 123456789
- **1 digit**: Scanned: 123456789 → Validated: 12345678
- **2 digits**: Scanned: 123456789 → Validated: 1234567
- **3 digits**: Scanned: 123456789 → Validated: 123456

## Implementation Details

### Code Changes

#### 1. AppState (`src/app_state.py`)

**Added checksum configuration:**
```python
self.checksum_digits = 0  # Number of digits to strip (0-3)
```

**Added strip_checksum method:**
```python
def strip_checksum(self, code):
    """Strip checksum digits from the end of a scanned code."""
    if self.checksum_digits > 0 and len(code) > self.checksum_digits:
        return code[:-self.checksum_digits]
    return code
```

**Modified handle_main_scan:**
- Strips checksum at the beginning
- Uses trimmed code for all comparisons
- Logs trimmed code only

**Modified handle_ondemand_scan:**
- Strips checksum for on-demand scans
- Card details show trimmed values
- Card counting uses trimmed values

#### 2. File Management UI (`src/ui/file_management_dual.py`)

**Added checksum section:**
- `create_checksum_section(head_id)` - Creates UI section
- `update_checksum_digits(head_id, index)` - Handles selection changes
- Updates example text dynamically

**Modified update_ui:**
- Restores checksum combo box selection from cache

### Persistence

Checksum configuration is saved to cache:
```json
{
  "head_a": {
    "checksum_digits": 2,
    ...
  },
  "head_b": {
    "checksum_digits": 0,
    ...
  }
}
```

## Use Cases

### Use Case 1: No Checksum
- Configuration: 0 digits
- Scanned: `89012345678901234567`
- File: `89012345678901234567`
- Result: Direct match ✓

### Use Case 2: 1 Digit Checksum
- Configuration: 1 digit
- Scanned: `890123456789012345679` (with checksum `9`)
- File: `89012345678901234567`
- Trimmed: `89012345678901234567`
- Result: Match ✓

### Use Case 3: 3 Digit Checksum
- Configuration: 3 digits
- Scanned: `89012345678901234567123` (with checksum `123`)
- File: `89012345678901234567`
- Trimmed: `89012345678901234567`
- Result: Match ✓

### Use Case 4: Mismatch Detection
- Configuration: 2 digits
- Scanned: `8901234567890123456712` (with checksum `12`)
- File expects: `89012345678901234568`
- Trimmed: `89012345678901234567`
- Result: NOT OK (wrong ICCID) ✗

## Testing Recommendations

1. **Test with no checksum (0 digits)**
   - Verify normal operation unchanged

2. **Test with 1 digit checksum**
   - Scan cards with 1 extra digit
   - Verify validation works correctly
   - Check logs show trimmed values

3. **Test with 2 digit checksum**
   - Scan cards with 2 extra digits
   - Verify validation works correctly

4. **Test with 3 digit checksum**
   - Scan cards with 3 extra digits
   - Verify validation works correctly

5. **Test on-demand features**
   - Card details scan
   - Card range counting
   - Verify trimmed values displayed

6. **Test dual-head independence**
   - Set HEAD A to 2 digits
   - Set HEAD B to 0 digits
   - Verify each head uses its own setting

7. **Test persistence**
   - Configure checksum settings
   - Restart application
   - Verify settings restored correctly

## Benefits

✅ **Flexibility** - Supports cards with or without checksums
✅ **Clean logs** - Only relevant ICCID data stored
✅ **No file changes** - Existing files work without modification
✅ **Independent heads** - Each head can have different checksum lengths
✅ **Easy configuration** - Simple dropdown selection
✅ **Visual feedback** - Example shows exactly what will happen

## Limitations

- Maximum 3 checksum digits supported
- Checksum digits must be at the END of the code
- No checksum validation performed (digits are simply discarded)
- All QR codes on a card must have the same checksum length

## Summary

The checksum feature provides a clean, flexible way to handle QR codes with appended checksum digits. By stripping the checksum before validation and logging, the system maintains clean data while supporting various card formats. The feature is fully integrated into all scanning operations and persists across application restarts.
