# COM Port Persistence Fix

## Issue
The application was not restoring previously selected COM ports on startup, even though the configuration was being saved to cache. The system was only attempting to restore UDP connections, ignoring serial COM port configurations.

## Root Cause
In the `__init__` method of `AppState`, the code that restores connections from cache was only calling `connect_ondemand_udp()`, which expects UDP configuration parameters (local_ip, local_port, etc.). When the cached configuration contained serial COM port settings (port, baudrate, etc.), these were being ignored.

## Solution

### 1. Updated Connection Restoration Logic
Modified the connection restoration code to detect whether the cached configuration is for UDP or serial COM port:

```python
if self.ondemand_scanner_config:
    config = self.ondemand_scanner_config
    # Check if it's a serial COM port or UDP configuration
    if 'port' in config:
        # Serial COM port configuration
        self.connect_ondemand_serial(
            config.get('port'),
            config.get('baudrate', 115200),
            config.get('bytesize', 8),
            config.get('parity', 'N'),
            config.get('stopbits', 1),
            config.get('timeout', 1)
        )
    elif 'local_ip' in config:
        # UDP configuration
        self.connect_ondemand_udp(
            config.get('local_ip'), config.get('local_port'),
            config.get('remote_ip'), config.get('remote_port')
        )
```

### 2. Detection Logic
- **Serial COM Port**: Detected by presence of `'port'` key in config
- **UDP**: Detected by presence of `'local_ip'` key in config

### 3. Updated Migration Code
Also updated the `_migrate_old_cache()` method to handle both serial and UDP configurations when migrating from old cache files.

## Configuration Storage

### Serial COM Port Config
```json
{
  "ondemand_scanner_config": {
    "port": "COM3",
    "baudrate": 115200,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
    "timeout": 1
  }
}
```

### UDP Config
```json
{
  "ondemand_scanner_config": {
    "local_ip": "192.168.1.100",
    "local_port": 5000,
    "remote_ip": "192.168.1.50",
    "remote_port": 6000
  }
}
```

## Behavior After Fix

### On Application Startup
1. System loads cache from unified cache file
2. Checks `ondemand_scanner_config` for connection settings
3. Detects configuration type (serial or UDP)
4. Calls appropriate connection method
5. If COM port is still available, connection is established
6. If COM port is no longer available, connection fails gracefully
7. User sees connection status in UI

### COM Port Availability
- **Port Available**: Automatically reconnects, status shows "Connected to COMX"
- **Port Unavailable**: Connection fails, status shows "Not Connected"
- **Port Changed**: User must manually select new port in Network Setup

## Benefits

### User Experience
- No need to reconfigure COM port after restart
- Seamless workflow continuation
- Settings persist across sessions
- Works for both heads independently

### System Behavior
- Graceful handling of unavailable ports
- Clear status indication
- Automatic reconnection when possible
- Maintains backward compatibility

## Testing Scenarios

### Test 1: COM Port Available
1. Configure COM port (e.g., COM3)
2. Close application
3. Reopen application
4. Expected: COM port automatically reconnects

### Test 2: COM Port Unavailable
1. Configure COM port (e.g., COM3)
2. Close application
3. Disconnect device or change port
4. Reopen application
5. Expected: Connection fails, status shows "Not Connected"

### Test 3: UDP Configuration
1. Configure UDP scanner
2. Close application
3. Reopen application
4. Expected: UDP connection automatically restores

### Test 4: Mixed Configuration
1. Head A: COM port
2. Head B: UDP
3. Close application
4. Reopen application
5. Expected: Both restore correctly

## Files Modified
- `src/app_state.py`: Updated connection restoration logic in `__init__` and `_migrate_old_cache`

## Related Components
- `ComPortReader`: Handles serial COM port reading
- `UDPReader`: Handles UDP network reading
- Cache system: Stores and restores configurations
- Network Setup UI: Allows manual configuration
