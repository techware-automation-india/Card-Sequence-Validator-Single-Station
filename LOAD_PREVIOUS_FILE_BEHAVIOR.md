# Load Previous File Behavior

## Overview
When a user selects "Load Previous" for a file that was previously loaded, the system automatically uses the cached card type and rebatch size settings, skipping the Card Type Selector dialog entirely.

## Workflow

### Scenario 1: Loading Previous File
1. User clicks "Load Job File"
2. System detects `selected_file_path` exists but `expected_cards` is empty
3. Dialog appears: "Load Previous" or "Select New File"
4. User clicks "Load Previous"
5. System retrieves cached settings:
   - `card_type` (SINGLE, HALF, or QUARTER)
   - `rebatch_size` (batch size value or None)
6. Card Type Selector dialog is **skipped**
7. File loads directly with cached settings
8. If logs exist, user is asked to continue or start fresh
9. Success message displayed

### Scenario 2: Loading New File
1. User clicks "Load Job File"
2. User selects a different CPD file
3. System counts total cards in file
4. Card Type Selector dialog appears
5. User selects card type and enters rebatch size
6. File loads with new settings
7. New settings are cached for future use

## Benefits

### User Experience
- Faster workflow when reloading the same file
- No need to re-enter card type and rebatch size
- Consistent settings across sessions
- Reduces user errors from re-entering settings

### System Behavior
- Settings are persisted in cache
- Each head (A and B) maintains independent settings
- Settings are restored on application restart
- File path, card type, and rebatch size are all cached together

## Implementation Details

### Cache Storage
Settings stored in unified cache file:
```json
{
  "head_a": {
    "selected_file_path": "path/to/file.cpd",
    "card_type": "half",
    "rebatch_size": 2000
  }
}
```

### Code Flow
```python
if load_previous_clicked:
    use_cached_settings = True
    selected_card_type = head.card_type
    rebatch_size = head.rebatch_size
    # Skip card type selector dialog
```
