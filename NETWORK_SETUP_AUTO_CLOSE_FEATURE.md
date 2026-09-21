# Network Setup Window Auto-Close Security Feature

**Date:** March 31, 2026  
**Feature:** Automatic window closure when focus is lost  
**Purpose:** Enhanced security for password-protected configuration

---

## Overview

The Network Setup window now automatically closes when the user switches to another window, requiring password re-entry each time the window is accessed. This prevents unauthorized access if the user leaves the window open in the background.

---

## Implementation Details

### 1. Window Event Handling

**File:** `src/ui/network_setup_dual.py`

Added `changeEvent()` method to detect when the window loses focus:

```python
def changeEvent(self, event):
    """Handle window state changes - close window when switching to other windows"""
    if event.type() == QEvent.Type.WindowDeactivate:
        # Check if a dialog is active (don't close for dialogs)
        active_modal = QApplication.activeModalWidget()
        active_popup = QApplication.activePopupWidget()
        
        # Only close if no modal dialog or popup is active
        # This means user switched to another main window
        if active_modal is None and active_popup is None:
            self.add_log_entry("Switching to another window - closing for security", "orange")
            # Use QTimer to delay close slightly to avoid issues
            QTimer.singleShot(100, self.close)
    
    super().changeEvent(event)
```

**Key Features:**
- Detects `WindowDeactivate` event when window loses focus
- Checks if a modal dialog or popup is active
- Only closes if switching to another main window (not for dialogs)
- Uses QTimer with 100ms delay for smooth closing
- Logs the closure event for audit trail

### 2. Window Recreation on Each Access

**File:** `src/ui/main_application.py`

Modified `open_com_port_setup()` to always create a fresh window instance:

```python
def open_com_port_setup(self):
    # Show password dialog
    password_dialog = PasswordDialog(self)
    
    # ... password validation ...
    
    if password_correct:
        # Close existing window if it exists
        if self.com_port_window is not None:
            try:
                self.com_port_window.close()
            except:
                pass
        
        # Create fresh window instance
        self.com_port_window = NetworkSetupWindow(self.dual_head_manager)
        self.com_port_window.showMaximized()
        self.com_port_window.raise_()
        self.com_port_window.activateWindow()
```

**Changes:**
- Always creates a new window instance (no reuse)
- Closes any existing window before creating new one
- Ensures clean state on each access

### 3. Import Updates

**File:** `src/ui/network_setup_dual.py`

Added required imports:
```python
from PyQt6.QtCore import Qt, QRegularExpression, QEvent, QTimer
```

---

## Behavior

### When Window Closes Automatically

The window will close when:
1. User clicks on another window (File Management, Scanner Logging, Main Window)
2. User switches to a different application
3. User minimizes the window (triggers deactivation)

### When Window Stays Open

The window will NOT close when:
1. User opens a QMessageBox dialog (validation errors, confirmations)
2. User opens the password change dialog
3. User interacts with combo boxes or other UI elements within the window
4. Network scan is running (dialogs are modal)

---

## Security Benefits

1. **Prevents Unauthorized Access:** If user walks away with window open, it automatically closes
2. **Requires Re-authentication:** Each access requires password entry
3. **Audit Trail:** Window closure is logged for security monitoring
4. **No Background Access:** Cannot switch back to window without re-entering password

---

## User Experience

### Before This Feature
- User enters password once
- Window stays open in background
- Can switch back anytime without password
- Security risk if user walks away

### After This Feature
- User enters password each time
- Window closes when switching away
- Must re-enter password to access again
- Enhanced security with minimal inconvenience

---

## Technical Considerations

### Dialog Handling

The implementation intelligently distinguishes between:
- **Modal Dialogs:** Window stays open (user is still working in the window)
- **Window Switching:** Window closes (user moved to different window)

This is achieved by checking:
```python
active_modal = QApplication.activeModalWidget()
active_popup = QApplication.activePopupWidget()

if active_modal is None and active_popup is None:
    # No dialog active, user switched windows
    self.close()
```

### Delayed Closure

Uses `QTimer.singleShot(100, self.close)` to:
- Avoid race conditions with event processing
- Ensure smooth UI transitions
- Prevent premature closure during dialog transitions

### Window Recreation

Always creates fresh window instance to:
- Ensure clean state
- Prevent stale data display
- Avoid memory leaks from old instances

---

## Testing Scenarios

### Test Case 1: Switch to File Management
1. Open Network Setup (enter password)
2. Click on File Management window
3. **Expected:** Network Setup closes automatically
4. Click Network Setup button again
5. **Expected:** Password dialog appears

### Test Case 2: Validation Error Dialog
1. Open Network Setup (enter password)
2. Enter invalid IP address
3. Click Apply
4. **Expected:** Error dialog appears, window stays open
5. Click OK on dialog
6. **Expected:** Window still open, can continue editing

### Test Case 3: Password Change
1. Open Network Setup (enter password)
2. Click "Change Password" button
3. **Expected:** Password dialog appears, window stays open
4. Enter new password
5. **Expected:** Success message, window still open

### Test Case 4: Network Scan
1. Open Network Setup (enter password)
2. Click "Scan Network" button
3. **Expected:** Scan runs, window stays open
4. Scan completes
5. **Expected:** Results shown, window still open

### Test Case 5: Minimize Window
1. Open Network Setup (enter password)
2. Minimize the window
3. **Expected:** Window closes (deactivation event)
4. Click Network Setup button
5. **Expected:** Password dialog appears

---

## Configuration Options

Currently, the auto-close behavior is always enabled. Future enhancements could include:

1. **Configurable Timeout:** Close after X seconds of inactivity
2. **Session-Based:** Stay open for entire session
3. **Role-Based:** Different behavior for admin vs. operator
4. **Disable Option:** Allow disabling for trusted environments

---

## Logging

The feature logs closure events:
```
[timestamp] Switching to another window - closing for security
```

This provides an audit trail for security monitoring.

---

## Known Limitations

1. **No Timeout:** Window doesn't close based on inactivity time
2. **No Session Management:** Each access requires password (no session tokens)
3. **No Remember Me:** Cannot stay logged in across window switches

These are intentional design decisions for maximum security.

---

## Future Enhancements

### Potential Improvements

1. **Inactivity Timeout**
   - Close window after X minutes of no interaction
   - Configurable timeout period

2. **Session Management**
   - Allow "Remember for this session" option
   - Session expires on application close

3. **Biometric Authentication**
   - Support fingerprint/face recognition
   - Faster re-authentication

4. **Activity Logging**
   - Log all configuration changes
   - Track who made what changes when

5. **Multi-Factor Authentication**
   - Require second factor for sensitive operations
   - Email/SMS verification codes

---

## Related Files

- `src/ui/network_setup_dual.py` - Window implementation
- `src/ui/main_application.py` - Window opening logic
- `src/ui/widgets.py` - PasswordDialog implementation
- `constants.py` - MASTER_PASSWORD definition

---

## Conclusion

This feature significantly enhances the security of the Network Setup configuration by ensuring that password protection is enforced on every access, not just the first time. The implementation is smart enough to distinguish between legitimate dialog interactions and actual window switching, providing security without compromising usability.

**Security Level:** HIGH  
**User Impact:** MINIMAL  
**Implementation Complexity:** LOW  
**Maintenance:** LOW

---

**Document Version:** 1.0  
**Last Updated:** March 31, 2026
