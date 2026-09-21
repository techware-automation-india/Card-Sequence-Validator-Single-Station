# Master Password Feature

## Overview

A master password has been implemented that provides universal access to the Network & COM Port Configuration window, regardless of the user-configured password.

## Master Password

```
iamyourmaster
```

## Functionality

The master password works in two scenarios:

1. **Accessing Network Setup Window**
   - When prompted for password to open Network & COM Port Configuration
   - Master password will grant access even if user has changed their password
   - Works alongside the regular user password

2. **Changing Password**
   - When changing password in the Network Setup window
   - Master password can be used in the "Current Password" field
   - Allows password reset even if user forgot their password

## Implementation Details

- Master password is defined in `constants.py` as `MASTER_PASSWORD = "iamyourmaster"`
- Password verification checks both user password and master password
- Master password cannot be changed or disabled
- Master password works independently of user password changes

## Security Note

The master password is hardcoded and provides backdoor access to network configuration. This is intended for administrative/recovery purposes.

## Usage Examples

### Scenario 1: User forgot their password
1. User tries to access Network Setup
2. User enters master password: `iamyourmaster`
3. Access granted

### Scenario 2: Resetting user password
1. User opens Network Setup (using master password if needed)
2. Goes to "Change Password" section
3. Enters master password in "Current Password" field
4. Sets new password
5. New password is now active (master password still works)

## Files Modified

- `constants.py` - Added MASTER_PASSWORD constant
- `src/ui/main_application.py` - Updated password verification for window access
- `src/ui/network_setup_dual.py` - Updated password verification for password change
