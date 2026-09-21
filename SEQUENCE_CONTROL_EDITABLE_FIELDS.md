# Sequence Control Tools - Editable Fields Feature

## Overview
Updated the Sequence Control Tools section to allow users to manually enter or edit text in the input fields when the COM port is connected and the tools are active.

## Changes Made

### 1. Card Details Fields - Now Editable
**Fields affected:**
- Card Number
- All QR code fields (Left ICCID, Right ICCID, etc.)
- Position

**Previous behavior:**
- Fields were `setReadOnly(True)` - completely read-only
- Could not enter or edit text even when buttons were active

**New behavior:**
- Fields are `setReadOnly(False)` - allow editing
- Fields are `setEnabled(False)` by default - disabled when no COM port
- Fields become `setEnabled(True)` when COM port is connected
- Users can type or paste text into fields when enabled

### 2. Card Count Fields - Now Editable
**Fields affected:**
- First Card
- Last Card
- Total

**Previous behavior:**
- Fields were `setReadOnly(True)` - completely read-only
- Could not enter or edit text

**New behavior:**
- Fields are `setReadOnly(False)` - allow editing
- Fields are `setEnabled(False)` by default - disabled when no COM port
- Fields become `setEnabled(True)` when COM port is connected
- Users can manually enter card numbers or ranges

## Enable/Disable Logic

### Fields are ENABLED when:
- ✅ File is loaded (`has_file = True`)
- ✅ COM port is connected (`has_ondemand = True`)
- ✅ Not currently scanning (`is_scanning = False`)

### Fields are DISABLED when:
- ❌ No file loaded
- ❌ No COM port connected
- ❌ Currently scanning

### Implementation
```python
fields_enabled = has_file and has_ondemand and not is_scanning

# Enable/disable all card details fields
getattr(self, f'card_number_field_{head_id}').setEnabled(fields_enabled)
getattr(self, f'position_field_{head_id}').setEnabled(fields_enabled)
for qr_field in getattr(self, f'qr_fields_{head_id}'):
    qr_field.setEnabled(fields_enabled)

# Enable/disable all card count fields
getattr(self, f'first_card_field_{head_id}').setEnabled(fields_enabled)
getattr(self, f'last_card_field_{head_id}').setEnabled(fields_enabled)
getattr(self, f'total_count_field_{head_id}').setEnabled(fields_enabled)
```

## User Experience

### Before COM Port Connection
- Fields appear grayed out (disabled)
- Cannot click or type in fields
- Buttons are also disabled
- Clear visual indication that tools are not ready

### After COM Port Connection
- Fields become white/active (enabled)
- Can click into fields and type
- Can select text, copy, paste
- Buttons become active
- Ready for manual input or scanning

### During Scanning
- Fields become disabled again
- Prevents accidental edits during validation
- Buttons also disabled during scan

## Use Cases

### Use Case 1: Manual Entry
1. Connect COM port
2. Load file
3. Fields become editable
4. User manually types card number
5. User manually types QR codes
6. User can verify or modify data

### Use Case 2: Scan and Edit
1. Connect COM port
2. Load file
3. Click "Scan Card" button
4. Scanner fills in fields automatically
5. User can edit any field if needed
6. Useful for corrections or adjustments

### Use Case 3: Manual Card Range
1. Connect COM port
2. Load file
3. Click "Count Range" button
4. Scanner fills in first and last card
5. User can manually adjust range if needed
6. Total is calculated automatically

## Visual States

### Disabled State (No COM Port)
```
Card Number: [          ] (grayed out, cannot type)
Left ICCID:  [          ] (grayed out, cannot type)
Right ICCID: [          ] (grayed out, cannot type)
Position:    [          ] (grayed out, cannot type)
```

### Enabled State (COM Port Connected)
```
Card Number: [          ] (white, can type)
Left ICCID:  [          ] (white, can type)
Right ICCID: [          ] (white, can type)
Position:    [          ] (white, can type)
```

### Filled State (After Scan or Manual Entry)
```
Card Number: [12345     ] (white, can edit)
Left ICCID:  [8901234...] (white, can edit)
Right ICCID: [8905678...] (white, can edit)
Position:    [1 of 5000 ] (white, can edit)
```

## Technical Details

### Field Configuration
```python
# Create field as editable but disabled
field = QLineEdit()
field.setReadOnly(False)  # Allow editing when enabled
field.setEnabled(False)   # Disabled by default
```

### Dynamic Enable/Disable
Fields are updated in the `update_ui()` method which is called:
- When file is loaded/cleared
- When COM port connects/disconnects
- When scanning starts/stops
- When card type changes

### Rebuild on Card Type Change
The `rebuild_card_details_fields()` method also creates fields as editable but disabled, ensuring consistency when card type changes.

## Benefits

### For Users
- **Flexibility**: Can manually enter data when needed
- **Corrections**: Can fix scanner errors or typos
- **Verification**: Can review and modify scanned data
- **Manual Mode**: Can use tools without scanner if needed

### For System
- **Consistent State**: Fields match button states
- **Clear Feedback**: Visual indication of readiness
- **Safe Operation**: Disabled during scanning prevents errors
- **Dual Mode**: Supports both automatic and manual workflows

## Files Modified
- `src/ui/file_management_dual.py`:
  - Updated `create_sequence_tools_section()` - changed fields from read-only to editable
  - Updated `rebuild_card_details_fields()` - changed fields from read-only to editable
  - Updated `update_ui()` - added logic to enable/disable fields based on COM port connection

## Testing Scenarios

### Test 1: No COM Port
1. Load file
2. Expected: Fields are disabled (grayed out)
3. Try to click in field
4. Expected: Cannot type

### Test 2: COM Port Connected
1. Load file
2. Connect COM port
3. Expected: Fields become enabled (white)
4. Click in field and type
5. Expected: Can enter text

### Test 3: During Scanning
1. Load file and connect COM port
2. Start validation
3. Expected: Fields become disabled
4. Stop validation
5. Expected: Fields become enabled again

### Test 4: Scan and Edit
1. Load file and connect COM port
2. Click "Scan Card"
3. Scanner fills fields
4. Click in a field and edit text
5. Expected: Can modify scanned data

## Status
**COMPLETED** - All sequence control fields are now editable when COM port is connected and tools are active.
