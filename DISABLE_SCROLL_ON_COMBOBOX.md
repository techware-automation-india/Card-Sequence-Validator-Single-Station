# Disable Scroll Wheel on ComboBox Fields

## Overview
The Network Setup window now prevents accidental value changes when scrolling over input fields. All combo box fields (IP addresses, ports, COM ports, baud rates) now ignore mouse wheel events.

## Problem
Previously, when hovering over a combo box field and scrolling with the mouse wheel, the value would change unintentionally. This could lead to:
- Accidental IP address changes
- Unintended port number modifications
- Incorrect COM port selection
- Wrong baud rate settings

## Solution
Created a custom `NoScrollComboBox` class that inherits from `QComboBox` and overrides the `wheelEvent` method to ignore scroll wheel events.

## Implementation

### Custom Widget Class
```python
class NoScrollComboBox(QComboBox):
    """QComboBox that ignores scroll wheel events"""
    def wheelEvent(self, event):
        # Ignore wheel events to prevent accidental value changes
        event.ignore()
```

### Applied To
All combo box fields in the Network Setup window:

**Main Scanner Configuration (Both Heads):**
- Local IP
- Local Port
- Remote IP
- Remote Port

**Output Configuration (Both Heads):**
- Local IP
- Local Port
- Remote IP
- Remote Port

**On-Demand Scanner Configuration (Both Heads):**
- COM Port
- Baud Rate

## Behavior

### Before Fix
```
User hovers over "Local Port" field showing "5000"
User scrolls mouse wheel down
Value changes to "5001" (unintended)
User scrolls again
Value changes to "5002" (unintended)
```

### After Fix
```
User hovers over "Local Port" field showing "5000"
User scrolls mouse wheel down
Value remains "5000" (scroll ignored)
User scrolls again
Value remains "5000" (scroll ignored)
Page scrolls instead (expected behavior)
```

## User Experience

### Changing Values
Users can still change values using:
- ✅ Typing directly in the field
- ✅ Clicking the dropdown arrow and selecting
- ✅ Using keyboard up/down arrows when field is focused
- ✅ Clicking and using keyboard to type

### Scrolling Page
- ✅ Scrolling over fields now scrolls the page
- ✅ No accidental value changes
- ✅ More predictable behavior

## Benefits

✅ **Prevents accidental changes**: No more unintended value modifications
✅ **Better UX**: Scrolling behaves as expected (scrolls page, not values)
✅ **Safer configuration**: Reduces risk of incorrect network settings
✅ **Consistent behavior**: All combo boxes behave the same way
✅ **Easy to implement**: Simple custom class applied to all fields

## Technical Details

### Event Handling
- `wheelEvent(event)`: Called when mouse wheel is scrolled over widget
- `event.ignore()`: Tells Qt to ignore the event and pass it to parent
- Parent widget (scroll area) receives event and scrolls the page

### Inheritance
- `NoScrollComboBox` inherits all functionality from `QComboBox`
- Only overrides wheel event handling
- All other features remain unchanged

### Compatibility
- Works with editable and non-editable combo boxes
- Compatible with validators (IP and port validators)
- Maintains dropdown functionality
- Preserves keyboard navigation

## Testing

**Test 1: Scroll Over Field**
1. Hover over any combo box field
2. Scroll mouse wheel
3. Verify value doesn't change
4. Verify page scrolls instead

**Test 2: Dropdown Still Works**
1. Click dropdown arrow on combo box
2. Verify dropdown opens
3. Select value from list
4. Verify value changes correctly

**Test 3: Typing Still Works**
1. Click in combo box field
2. Type new value
3. Verify value updates correctly

**Test 4: Keyboard Navigation**
1. Tab to combo box field
2. Use up/down arrow keys
3. Verify value changes with keyboard
4. Verify scroll wheel still ignored

**Test 5: All Fields**
1. Test each combo box field in window
2. Verify scroll is disabled on all
3. Verify all other functionality works

## Code Changes

**File**: `src/ui/network_setup_dual.py`

**Added**:
- `NoScrollComboBox` class definition
- Import of `QEvent` from `PyQt6.QtCore`

**Modified**:
- All `QComboBox()` instantiations replaced with `NoScrollComboBox()`
- Approximately 12 combo box fields updated

## Summary

The scroll wheel disable feature improves the user experience in the Network Setup window by preventing accidental value changes when scrolling. Users can still modify values through typing, dropdown selection, and keyboard navigation, while scrolling now behaves predictably by scrolling the page instead of changing field values.
