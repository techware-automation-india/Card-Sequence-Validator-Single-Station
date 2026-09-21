# Application State Persistence Analysis

## Summary
Your application has **partial persistence** but is **missing critical auto-save functionality** during active scanning. While configuration and logs are saved to cache, they are **NOT automatically saved during scanning operations**, which means data loss can occur if the system crashes mid-scan.

---

## What IS Being Saved ✅

### 1. Configuration Settings (Saved Immediately)
The following settings are saved to cache whenever they change:
- **Network Configuration**: Main scanner, on-demand scanner, and output UDP settings
- **File Path**: Currently loaded file path
- **Card Type**: Selected card type (Single, Half, Quarter)
- **Scan Direction**: Top-to-bottom or bottom-to-top
- **Output Format**: Selected output format
- **Theme**: Current UI theme
- **Start Card Code**: The first card scanned
- **Serial Settings**: Baud rate, data bits, parity, stop bits (legacy)

**Trigger Points**: Configuration is saved when:
- Network settings are applied
- File is loaded
- Theme is changed
- Ports are connected/disconnected
- Output format is changed

### 2. Log Data (Saved to Memory Only)
Log entries are stored in `self.log_data` list:
```python
log_entry = {
    "timestamp": self.get_timestamp(),
    "scanned_code": scanned_code,
    "expected_code": expected_code,
    "status": status,
    "scanned_side": scanned_side,
    "instance": self.current_instance
}
self.log_data.append(log_entry)
```

**Current Behavior**: Logs are added to memory but **NOT automatically saved to cache during scanning**.

---

## What IS NOT Being Saved ❌

### 1. **Auto-Save During Scanning (CRITICAL ISSUE)**
The code has auto-save configuration defined but **never implemented**:
```python
# Auto-save configuration for power loss protection
self.last_save_time = time.time()
self.scans_since_save = 0
self.auto_save_interval = 300  # Save every 5 minutes (300 seconds)
self.auto_save_batch_size = 1000  # Save every 1000 scans
```

**Problem**: These variables are initialized but **never used**. There is no code that:
- Checks if `scans_since_save >= auto_save_batch_size`
- Checks if `time.time() - last_save_time >= auto_save_interval`
- Calls `save_cache()` during scanning

### 2. **Scan State During Active Scanning**
The following critical state is NOT saved during scanning:
- `current_card_index`: Current position in the sequence
- `start_card_has_been_scanned`: Whether the start card was found
- `scan_side`: Which side of the card is being scanned
- `expected_cards`: The loaded card sequence (saved only on file load)
- `log_data`: All scan logs (saved only on manual save or app exit)

### 3. **On-Demand Scanning State**
The on-demand scanning state machine is NOT persisted:
```python
self.is_waiting_for_start_card = False
self.is_waiting_for_count_card_1 = False
self.is_waiting_for_count_card_2 = False
self.first_card_index = -1
```

---

## Data Loss Scenarios

### Scenario 1: System Crash During Scanning
**What happens:**
1. User is scanning cards (100 scans completed)
2. System crashes or power loss occurs
3. Application restarts
4. **Result**: All 100 scan logs are lost, current_card_index is reset to 0

### Scenario 2: Application Crash During Scanning
**What happens:**
1. User is scanning cards (50 scans completed)
2. Application crashes
3. Application restarts
4. **Result**: All 50 scan logs are lost, scan progress is lost

### Scenario 3: Mid-Scan Configuration Change
**What happens:**
1. User is scanning with file loaded
2. User changes network settings
3. Application crashes before scan completes
4. **Result**: New network settings are saved, but scan logs are lost

---

## Recommendations to Fix

### 1. **Implement Auto-Save During Scanning** (HIGH PRIORITY)
Add this to `handle_main_scan()` method:

```python
def handle_main_scan(self, scanned_code):
    # ... existing scan logic ...
    
    # Auto-save after each scan
    self.scans_since_save += 1
    current_time = time.time()
    
    # Save if batch size reached or interval elapsed
    if (self.scans_since_save >= self.auto_save_batch_size or 
        current_time - self.last_save_time >= self.auto_save_interval):
        self.save_cache()
        self.scans_since_save = 0
        self.last_save_time = current_time
```

### 2. **Save Scan State** (HIGH PRIORITY)
Extend `save_cache()` to include scan state:

```python
instance_data = {
    # ... existing fields ...
    'current_card_index': self.current_card_index,
    'start_card_has_been_scanned': self.start_card_has_been_scanned,
    'scan_side': self.scan_side,
    'expected_cards': self.expected_cards,
    'log_data': self.log_data,
    # On-demand state
    'is_waiting_for_start_card': self.is_waiting_for_start_card,
    'is_waiting_for_count_card_1': self.is_waiting_for_count_card_1,
    'is_waiting_for_count_card_2': self.is_waiting_for_count_card_2,
    'first_card_index': self.first_card_index,
}
```

### 3. **Restore Scan State on Startup** (HIGH PRIORITY)
Add to `load_cache()` method:

```python
# Restore scan state
self.current_card_index = cache.get('current_card_index', 0)
self.start_card_has_been_scanned = cache.get('start_card_has_been_scanned', False)
self.scan_side = cache.get('scan_side', 'top_to_bottom')
self.expected_cards = cache.get('expected_cards', [])
self.log_data = cache.get('log_data', [])

# Restore on-demand state
self.is_waiting_for_start_card = cache.get('is_waiting_for_start_card', False)
self.is_waiting_for_count_card_1 = cache.get('is_waiting_for_count_card_1', False)
self.is_waiting_for_count_card_2 = cache.get('is_waiting_for_count_card_2', False)
self.first_card_index = cache.get('first_card_index', -1)
```

### 4. **Add Recovery UI** (MEDIUM PRIORITY)
When app restarts with incomplete scan:
- Show dialog asking if user wants to resume or start fresh
- Display how many scans were completed before crash
- Allow user to continue from where they left off

### 5. **Increase Auto-Save Frequency** (MEDIUM PRIORITY)
Current settings are too conservative:
```python
self.auto_save_interval = 60  # Save every 1 minute (was 5 minutes)
self.auto_save_batch_size = 100  # Save every 100 scans (was 1000)
```

---

## Current Save Locations

Cache files are stored at:
- **Windows**: `C:\Users\[username]\AppData\Local\YourCompany\CardSequenceValidator\app_cache_unified.json`

Structure:
```json
{
  "head_a": {
    "card_type": "half",
    "main_scanner_config": {...},
    "ondemand_scanner_config": {...},
    "output_config": {...},
    "selected_file_path": "...",
    "start_card_code": "...",
    "scan_direction": "top_to_bottom",
    "log_data": [],
    "current_theme": "dark"
  },
  "head_b": { ... }
}
```

---

## Testing Recommendations

1. **Test Power Loss Scenario**:
   - Start scanning 100 cards
   - After 50 scans, force kill the application
   - Restart and verify logs are recovered

2. **Test Configuration Persistence**:
   - Change network settings
   - Restart application
   - Verify settings are restored

3. **Test Dual-Head Persistence**:
   - Scan on both heads simultaneously
   - Crash one head
   - Verify other head continues and both recover correctly

4. **Test Large Scan Sessions**:
   - Scan 10,000+ cards
   - Verify auto-save doesn't cause performance issues
   - Check cache file size growth

---

## Summary Table

| Feature | Status | Auto-Save | Recovery |
|---------|--------|-----------|----------|
| Network Config | ✅ Saved | On change | ✅ Yes |
| File Path | ✅ Saved | On load | ✅ Yes |
| Card Type | ✅ Saved | On change | ✅ Yes |
| Scan Logs | ⚠️ In Memory | ❌ No | ❌ No |
| Scan Progress | ⚠️ In Memory | ❌ No | ❌ No |
| On-Demand State | ⚠️ In Memory | ❌ No | ❌ No |
| Theme | ✅ Saved | On change | ✅ Yes |

