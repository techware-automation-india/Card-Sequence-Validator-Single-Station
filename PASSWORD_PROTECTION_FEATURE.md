# Password Protection Feature

## Overview
The Network Configuration window is now protected with password authentication. Only users with the correct password can access network and COM port settings, preventing unauthorized changes to critical system configurations.

## Features

### 1. Password Dialog
- Appears when attempting to open Network Configuration window
- Modal dialog that blocks access until authenticated
- Password input is masked (hidden characters)
- Maximum 3 attempts before access is denied
- Cancel button to abort authentication

### 2. Password Management
- Default password: `admin123`
- Password can be changed from within Network Configuration window
- Password is stored in application cache
- Both HEAD A and HEAD B share the same password
- Password persists across application restarts

### 3. Security Settings Section
Located at the bottom of the Network Configuration window:
- Change password functionality
- Requires current password verification
- New password confirmation
- Minimum password length: 6 characters
- Visual feedback for password changes
- Default password warning (hidden after password is changed)

## User Experience

### Accessing Network Configuration

1. **Click "Network & COM Port Configuration" button** on home page

2. **Password Dialog appears:**
   ```
   ┌─────────────────────────────────────┐
   │  Authentication Required            │
   ├─────────────────────────────────────┤
   │  Network Configuration Access       │
   │                                     │
   │  Please enter the password to       │
   │  access network configuration       │
   │  settings.                          │
   │                                     │
   │  [••••••••••]                       │
   │                                     │
   │  [  OK  ]  [ Cancel ]               │
   └─────────────────────────────────────┘
   ```

3. **Enter password** (default: `admin123`)

4. **Three possible outcomes:**
   - ✅ **Correct password**: Window opens immediately
   - ❌ **Incorrect password**: Error message shows remaining attempts
   - 🚫 **3 failed attempts**: Access denied, dialog closes

### Changing Password

1. **Open Network Configuration** (requires authentication)

2. **Scroll to "Security Settings" section** at bottom

3. **Fill in the form:**
   - Current Password: Enter existing password
   - New Password: Enter desired new password (min 6 chars)
   - Confirm Password: Re-enter new password

4. **Click "🔒 Change Password"**

5. **Validation checks:**
   - All fields must be filled
   - Current password must be correct
   - New passwords must match
   - New password must be at least 6 characters

6. **Success**: Password updated and saved to cache

7. **Default password warning disappears** (if changing from default)

## Implementation Details

### Components

#### 1. PasswordDialog (`src/ui/widgets.py`)
```python
class PasswordDialog(QDialog):
    - Modal dialog for password entry
    - Masked password input
    - Error message display
    - OK/Cancel buttons
```

**Methods:**
- `get_password()`: Returns entered password
- `show_error(message)`: Displays error message
- `clear_error()`: Clears error message

#### 2. AppState Password Storage (`src/app_state.py`)
```python
self.network_config_password = "admin123"  # Default
```

**Persistence:**
- Saved in cache under `network_config_password`
- Loaded on application startup
- Shared between HEAD A and HEAD B

#### 3. Authentication Logic (`src/ui/main_application.py`)
```python
def open_com_port_setup(self):
    - Shows password dialog
    - Validates entered password
    - Allows 3 attempts
    - Opens window on success
```

#### 4. Password Change UI (`src/ui/network_setup_dual.py`)
```python
def create_password_section(self, parent_layout):
    - Creates security settings section
    - Password change form
    - Validation and update logic
    - Dynamic default password warning

def update_password_info_visibility(self):
    - Shows warning only if password is still "admin123"
    - Hides warning after password is changed
```

### Security Features

✅ **Password masking**: Input characters hidden
✅ **Attempt limiting**: Maximum 3 tries
✅ **Validation**: Current password verification
✅ **Confirmation**: New password must be entered twice
✅ **Minimum length**: 6 characters required
✅ **Persistence**: Password saved across sessions
✅ **Shared password**: Both heads use same password

### Cache Structure

```json
{
  "head_a": {
    "network_config_password": "admin123",
    ...
  },
  "head_b": {
    "network_config_password": "admin123",
    ...
  }
}
```

## Use Cases

### Use Case 1: First Time Access
1. User clicks "Network & COM Port Configuration"
2. Password dialog appears
3. User enters default password: `admin123`
4. Window opens successfully

### Use Case 2: Incorrect Password
1. User clicks "Network & COM Port Configuration"
2. Password dialog appears
3. User enters wrong password
4. Error: "Incorrect password. 2 attempt(s) remaining."
5. User tries again with correct password
6. Window opens successfully

### Use Case 3: Maximum Attempts Exceeded
1. User clicks "Network & COM Port Configuration"
2. Password dialog appears
3. User enters wrong password 3 times
4. Warning: "Maximum password attempts exceeded. Access denied."
5. Dialog closes, window does not open

### Use Case 4: Changing Password
1. User authenticates and opens Network Configuration
2. Scrolls to "Security Settings" section
3. Sees warning: "⚠️ Default password: admin123"
4. Enters:
   - Current Password: `admin123`
   - New Password: `myNewPass123`
   - Confirm Password: `myNewPass123`
5. Clicks "🔒 Change Password"
6. Success message: "Password changed successfully!"
7. Warning "⚠️ Default password: admin123" disappears
8. Next time, must use `myNewPass123` to access

### Use Case 5: Password Mismatch
1. User tries to change password
2. Enters:
   - Current Password: `admin123`
   - New Password: `newPass123`
   - Confirm Password: `newPass456` (different)
3. Warning: "New password and confirmation do not match."
4. New password fields cleared, user tries again

### Use Case 6: Weak Password
1. User tries to change password
2. Enters new password: `abc` (too short)
3. Warning: "Password must be at least 6 characters long."
4. User enters longer password

## Security Considerations

### Current Implementation
- Password stored in plain text in cache file
- No encryption applied
- Suitable for basic access control
- Not suitable for high-security environments

### Recommendations for Enhanced Security
1. **Hash passwords** using bcrypt or similar
2. **Encrypt cache file** to prevent plain text storage
3. **Add password complexity requirements** (uppercase, numbers, symbols)
4. **Implement account lockout** after failed attempts
5. **Add password expiration** policy
6. **Log authentication attempts** for audit trail
7. **Add two-factor authentication** for critical systems

### Current Limitations
- ⚠️ Password visible in cache file (plain text)
- ⚠️ No password recovery mechanism
- ⚠️ No password history (can reuse old passwords)
- ⚠️ No session timeout (once authenticated, stays open)
- ⚠️ No audit log of access attempts

## Testing Recommendations

1. **Test default password access**
   - Verify `admin123` works on first launch

2. **Test incorrect password handling**
   - Enter wrong password
   - Verify error message and attempt counter

3. **Test maximum attempts**
   - Enter wrong password 3 times
   - Verify access denied message

4. **Test password change**
   - Change password successfully
   - Verify new password works
   - Verify old password no longer works

5. **Test password validation**
   - Try changing with wrong current password
   - Try mismatched new passwords
   - Try password shorter than 6 characters

6. **Test persistence**
   - Change password
   - Restart application
   - Verify new password still works

7. **Test cancel functionality**
   - Click cancel on password dialog
   - Verify window doesn't open

8. **Test dual-head consistency**
   - Change password
   - Verify both heads use same password

## User Instructions

### For Administrators

**Initial Setup:**
1. First time opening Network Configuration, use password: `admin123`
2. Immediately change to a secure password
3. Share new password only with authorized personnel

**Changing Password:**
1. Open Network Configuration (authenticate)
2. Scroll to bottom "Security Settings" section
3. Enter current password
4. Enter new password (min 6 characters)
5. Confirm new password
6. Click "🔒 Change Password"

**If Password Forgotten:**
- Contact system administrator
- May require manual cache file editing or reset
- Default password can be restored by deleting cache file

### For Users

**Accessing Network Configuration:**
1. Click "Network & COM Port Configuration" button
2. Enter password when prompted
3. Click OK
4. You have 3 attempts to enter correct password

**If Access Denied:**
- Contact administrator for correct password
- Wait and try again later
- Do not attempt to bypass security

## Benefits

✅ **Prevents unauthorized changes** to network settings
✅ **Protects critical configurations** from accidental modification
✅ **Simple to use** - single password for access
✅ **Customizable** - password can be changed anytime
✅ **Persistent** - password saved across sessions
✅ **User-friendly** - clear error messages and feedback
✅ **Flexible** - can be easily enhanced with stronger security

## Summary

The password protection feature adds a security layer to the Network Configuration window, ensuring only authorized users can modify critical network and COM port settings. With a simple password dialog, attempt limiting, and password management capabilities, the system balances security with usability. The default password (`admin123`) should be changed immediately in production environments.
