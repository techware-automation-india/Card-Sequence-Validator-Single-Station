# Rebatch Size Feature

## Overview
The rebatch size feature allows users to divide large CPD files into smaller batches before applying the scan side logic for HALF and QUARTER card types. This provides more flexibility in managing card sequences.

## How It Works

### For HALF Cards (2 QR codes per card)
Without rebatch:
- File is divided in half: first 50% = Left, second 50% = Right

With rebatch (e.g., batch size = 2000):
- File is divided into batches of 2000 cards each
- Within each batch, first 50% = Left, second 50% = Right
- Example: 5000 cards with batch size 2000
  - Batch 1 (cards 1-2000): cards 1-1000 Left, cards 1001-2000 Right
  - Batch 2 (cards 2001-4000): cards 2001-3000 Left, cards 3001-4000 Right
  - Batch 3 (cards 4001-5000): cards 4001-4500 Left, cards 4501-5000 Right

### For QUARTER Cards (4 QR codes per card)
Without rebatch:
- File is divided into quarters: 1st=BL, 2nd=TL, 3rd=TR, 4th=BR

With rebatch (e.g., batch size = 2000):
- File is divided into batches of 2000 cards each
- Within each batch, divide into quarters: 1st=BL, 2nd=TL, 3rd=TR, 4th=BR
- Example: 5000 cards with batch size 2000
  - Batch 1 (cards 1-2000): 1-500 BL, 501-1000 TL, 1001-1500 TR, 1501-2000 BR
  - Batch 2 (cards 2001-4000): 2001-2500 BL, 2501-3000 TL, 3001-3500 TR, 3501-4000 BR
  - Batch 3 (cards 4001-5000): 4001-4250 BL, 4251-4500 TL, 4501-4750 TR, 4751-5000 BR

### For SINGLE Cards
Rebatch size is not applicable and will be ignored.

## User Interface

### When Loading a File
1. User clicks "Load Job File"
2. Selects a CPD file
3. System counts total cards in the file
4. Card Type Selector dialog appears with:
   - Radio buttons for card type selection (SINGLE, HALF, QUARTER)
   - Rebatch Size section (visible only for HALF and QUARTER)
   - **Bold, required** input field for batch size
   - Real-time validation with error messages
   - Continue button disabled until valid batch size entered
   - Batch size limited to total cards in file

### Rebatch Input
- **Required field for HALF and QUARTER cards** - must enter a value to continue
- Not applicable for SINGLE cards (field is hidden)
- Accepts positive integers only (1 to total cards in file)
- Placeholder: "Enter batch size"
- Continue button is disabled until valid batch size is entered
- Real-time validation with error messages
- **Cannot exceed total number of cards in the file**

## Backend Implementation

### Modified Files
1. **src/app_state.py**
   - Added `rebatch_size` attribute to AppState
   - Updated `load_file()` to accept and pass rebatch_size parameter
   - Added rebatch_size to cache persistence

2. **src/services/utilities.py**
   - Updated `parse_cpd_cards()` to accept rebatch_size parameter
   - Implemented batch calculation logic for HALF cards
   - Implemented batch calculation logic for QUARTER cards

3. **src/logic/file_parser.py**
   - Updated `parse_file()` to accept and pass rebatch_size parameter

4. **src/ui/card_type_selector.py**
   - Added rebatch configuration section
   - Added input field with integer validation
   - Added `get_rebatch_size()` method
   - Show/hide rebatch section based on card type

5. **src/ui/file_management_dual.py**
   - Updated file loading to retrieve rebatch_size from dialog
   - Pass rebatch_size to `head.load_file()`

## Batch Calculation Logic

### HALF Cards
```python
batch_num = (card_index - 1) // rebatch_size
position_in_batch = ((card_index - 1) % rebatch_size) + 1

batch_start = batch_num * rebatch_size + 1
batch_end = min((batch_num + 1) * rebatch_size, total_cards)
current_batch_size = batch_end - batch_start + 1

half_point = current_batch_size // 2

if position_in_batch <= half_point:
    # Left side
else:
    # Right side
```

### QUARTER Cards
```python
batch_num = (card_index - 1) // rebatch_size
position_in_batch = ((card_index - 1) % rebatch_size) + 1

batch_start = batch_num * rebatch_size + 1
batch_end = min((batch_num + 1) * rebatch_size, total_cards)
current_batch_size = batch_end - batch_start + 1

quarter_size = current_batch_size // 4

if position_in_batch <= quarter_size:
    # Bottom-Left
elif position_in_batch <= 2 * quarter_size:
    # Top-Left
elif position_in_batch <= 3 * quarter_size:
    # Top-Right
else:
    # Bottom-Right
```

## Persistence
- Rebatch size is saved to cache when file is loaded
- Card type is saved to cache when file is loaded
- Restored on application restart
- **When loading previous file, cached card type and rebatch size are automatically used**
- No need to re-enter settings when reloading the same file
- Stored per head (Head A and Head B have independent settings)

## Logging
- No changes to logging behavior
- Logs continue to show scanned side (Left/Right for HALF, BL/TL/TR/BR for QUARTER)
- Scan validation logic remains unchanged

## Example Use Cases

### Use Case 1: Large Production Run
- Total cards: 10,000
- Card type: HALF
- Rebatch size: 2,500
- Result: 4 batches of 2,500 cards each, with Left/Right split within each batch

### Use Case 2: Multiple Smaller Batches
- Total cards: 5,000
- Card type: QUARTER
- Rebatch size: 1,000
- Result: 5 batches of 1,000 cards each, with BL/TL/TR/BR split within each batch

### Use Case 3: Single Card Type (No Rebatching)
- Total cards: 3,000
- Card type: SINGLE
- Rebatch size: N/A (not applicable for single cards)
- Result: All 3,000 cards processed individually

## Notes
- **Rebatch size is required for HALF and QUARTER card types**
- Rebatch size is entered only once per file load
- Cannot be changed without reloading the file
- Last batch may be smaller if total cards don't divide evenly
- Rebatch logic is applied in the backend during file parsing
- No impact on UI display or logging format
- Continue button is disabled until valid batch size is entered
- Real-time validation prevents invalid input
