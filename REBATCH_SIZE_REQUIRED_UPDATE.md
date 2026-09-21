# Rebatch Size - Required Field Update

## Summary
The rebatch size field has been updated to be **required and bold** for HALF and QUARTER card types, with real-time validation to ensure users cannot proceed without entering a valid batch size.

## UI Changes

### Visual Enhancements
1. **Title**: "Rebatch Size" (simplified)
   - Bold, larger font (14px)
   - Orange color (#FF9800) for high visibility

2. **Label**: "Batch Size: *" 
   - Bold font (13px)
   - Asterisk (*) indicates required field

3. **Placeholder**: "Enter batch size" (simplified)

4. **No description text** - clean, minimal interface

### Validation Features

#### Real-Time Validation
- Input field connected to `validate_input()` method via `textChanged` signal
- Validates on every keystroke
- Continue button state updates immediately

#### Validation Rules
1. **Empty Input**: 
   - Error: "⚠ Batch size is required"
   - Continue button: Disabled

2. **Invalid Number**:
   - Error: "⚠ Please enter a valid number"
   - Continue button: Disabled

3. **Zero or Negative**:
   - Error: "⚠ Batch size must be greater than 0"
   - Continue button: Disabled

4. **Exceeds File Size**:
   - Error: "⚠ Batch size cannot exceed total cards (X)"
   - Continue button: Disabled

5. **Valid Input** (1 to total cards):
   - Error message: Hidden
   - Continue button: Enabled

#### Error Display
- Red, bold error label below the example text
- Dynamically shows/hides based on validation state
- Clear, actionable error messages with warning icon (⚠)

### Behavior by Card Type

#### SINGLE Cards
- Rebatch section: Hidden
- Continue button: Always enabled
- No validation required

#### HALF Cards
- Rebatch section: Visible
- Continue button: Disabled until valid batch size entered
- Real-time validation active

#### QUARTER Cards
- Rebatch section: Visible
- Continue button: Disabled until valid batch size entered
- Real-time validation active

## Code Changes

### src/ui/card_type_selector.py

#### New Method: `validate_input()`
```python
def validate_input(self):
    """Validate rebatch input and enable/disable continue button"""
    # Checks card type
    # Validates batch size for HALF/QUARTER
    # Updates continue button state
    # Shows/hides error messages
```

#### Updated Method: `on_card_type_changed()`
```python
def on_card_type_changed(self):
    """Show/hide rebatch section based on selected card type"""
    # Shows/hides rebatch frame
    # Clears error label
    # Calls validate_input()
```

#### Updated Method: `accept()`
```python
def accept(self):
    """Store the selected card type and rebatch size, then close dialog"""
    # Additional validation before accepting
    # Prevents dialog close if validation fails
    # Shows error messages if needed
```

#### New UI Elements
- `self.error_label`: QLabel for displaying validation errors
- Connected `textChanged` signal to `validate_input()`

## User Experience Flow

### Loading Previous File (Cached Settings)
1. User clicks "Load Job File"
2. System detects previous file path in cache
3. Dialog: "Load Previous" or "Select New File"
4. User clicks "Load Previous"
5. **System automatically uses cached card type and rebatch size** (no dialog shown)
6. If logs exist: Dialog asks "Continue from Last Use" or "Fresh Start"
7. File loads with previous settings
8. Success message displayed

### Loading New File
1. User clicks "Load Job File"
2. User selects a CPD file from file browser
3. System counts total cards in the file
4. Card Type Selector dialog appears
5. User selects card type (HALF or QUARTER)
6. Rebatch section appears with orange "Rebatch Size" title
7. Continue button is disabled (grayed out)
8. User enters batch size (validated against file size)
9. Real-time validation occurs:
   - Invalid input → Error message appears, button stays disabled
   - Valid input → Error message disappears, button becomes enabled
10. User clicks Continue
11. File loads with specified settings
12. Success message displayed

### Loading SINGLE Card File
1. User selects SINGLE card type
2. Rebatch section is hidden
3. Continue button is enabled immediately
4. User clicks Continue
5. File loads without rebatch logic

## Benefits

### For Users
- **Clear Requirement**: Bold, orange title makes it obvious the field is required
- **Immediate Feedback**: Real-time validation prevents submission errors
- **Guided Input**: Error messages explain exactly what's wrong
- **Prevented Errors**: Cannot proceed with invalid or missing batch size

### For System
- **Data Integrity**: Ensures valid batch sizes are always provided
- **Consistent Behavior**: HALF and QUARTER cards always use rebatch logic
- **Error Prevention**: Validation happens before file processing begins
- **Better UX**: Users understand requirements before attempting to continue

## Testing Scenarios

### Test 1: Empty Input
1. Select HALF card type
2. Leave batch size empty
3. Expected: Error message shown, Continue button disabled

### Test 2: Invalid Characters
1. Select QUARTER card type
2. Type "abc" in batch size
3. Expected: Validator prevents non-numeric input

### Test 3: Zero Value
1. Select HALF card type
2. Type "0" in batch size
3. Expected: Error "must be greater than 0", button disabled

### Test 4: Valid Input
1. Select QUARTER card type
2. Type "2000" in batch size
3. Expected: No error, Continue button enabled

### Test 5: Card Type Switch
1. Select HALF card type (rebatch visible)
2. Switch to SINGLE card type
3. Expected: Rebatch section hidden, button enabled

### Test 6: Large Number
1. Select HALF card type
2. Type "999999" in batch size
3. Expected: Accepted (within validator range)

### Test 7: Too Large Number
1. Select QUARTER card type
2. Type "9999999" (7 digits)
3. Expected: Validator limits to 999999

## Backward Compatibility

### Cache Files
- Old cache files without rebatch_size will load with `rebatch_size = None`
- When reloading such files, user will be prompted to enter batch size
- No data loss or corruption

### Existing Workflows
- SINGLE card workflows: Unchanged (rebatch not applicable)
- HALF/QUARTER workflows: Now require batch size input
- Users must adapt to new requirement (intentional design change)

## Documentation Updates
- REBATCH_SIZE_FEATURE.md updated to reflect required field
- User guide should be updated to mention required batch size
- Training materials should emphasize the new requirement
