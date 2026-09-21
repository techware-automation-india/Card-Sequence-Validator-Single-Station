# Visual Guide: Skip Logic for Both Scan Directions

## Top-to-Bottom Skip Logic

### Scenario
```
File: 100 cards
Current Position: Entry 10 (expecting this card)
Scanned Card: Entry 20
```

### Visual Representation
```
┌─────────────────────────────────────────────────────────────┐
│                    TOP-TO-BOTTOM SCAN                        │
└─────────────────────────────────────────────────────────────┘

Entry:    1  2  3  4  5  6  7  8  9  [10] 11 12 13 14 15 16 17 18 19 [20] 21 22 ... 100
                                      ▲                                ▲
                                      │                                │
                                   Expected                         Scanned
                                   (current)                        (jumped to)

Array Index: 0  1  2  3  4  5  6  7  8   9  10 11 12 13 14 15 16 17 18  19  20 21 ... 99

┌──────────────────────────────────────────────────────────────────────────────┐
│ SKIP LOGIC: range(9, 19)                                                     │
│ Generates: [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]                          │
└──────────────────────────────────────────────────────────────────────────────┘

SKIPPED ENTRIES (10 cards):
  ┌─────────────────────────────────────────────────────────┐
  │ Entry 10 (array index 9)  ← Current expected card       │
  │ Entry 11 (array index 10)                               │
  │ Entry 12 (array index 11)                               │
  │ Entry 13 (array index 12)                               │
  │ Entry 14 (array index 13)                               │
  │ Entry 15 (array index 14)                               │
  │ Entry 16 (array index 15)                               │
  │ Entry 17 (array index 16)                               │
  │ Entry 18 (array index 17)                               │
  │ Entry 19 (array index 18)                               │
  └─────────────────────────────────────────────────────────┘

JUMPED TO:
  ┌─────────────────────────────────────────────────────────┐
  │ Entry 20 (array index 19) ← Scanned card (OK JUMPED)    │
  └─────────────────────────────────────────────────────────┘

NEXT EXPECTED:
  Entry 21 (array index 20)
```

---

## Bottom-to-Top Skip Logic

### Scenario
```
File: 100 cards
Current Position: Entry 91 (expecting this card)
Scanned Card: Entry 81
```

### Visual Representation
```
┌─────────────────────────────────────────────────────────────┐
│                   BOTTOM-TO-TOP SCAN                         │
└─────────────────────────────────────────────────────────────┘

Entry:    1  2  3 ... 79 80 [81] 82 83 84 85 86 87 88 89 90 [91] 92 93 ... 100
                           ▲                                ▲
                           │                                │
                        Scanned                          Expected
                       (jumped to)                       (current)

Array Index: 0  1  2 ... 78 79  80  81 82 83 84 85 86 87 88 89  90  91 92 ... 99

Scan Position: 99 98 97... 21 20  19  18 17 16 15 14 13 12 11 10  9   8  7 ...  0
                                   ▲                                ▲
                                   │                                │
                                Scanned                          Expected
                               (jumped to)                       (current)

┌──────────────────────────────────────────────────────────────────────────────┐
│ SKIP LOGIC: range(90, 80, -1)                                                │
│ Generates: [90, 89, 88, 87, 86, 85, 84, 83, 82, 81]                         │
└──────────────────────────────────────────────────────────────────────────────┘

SKIPPED ENTRIES (10 cards):
  ┌─────────────────────────────────────────────────────────┐
  │ Entry 91 (array index 90) ← Current expected card       │
  │ Entry 90 (array index 89)                               │
  │ Entry 89 (array index 88)                               │
  │ Entry 88 (array index 87)                               │
  │ Entry 87 (array index 86)                               │
  │ Entry 86 (array index 85)                               │
  │ Entry 85 (array index 84)                               │
  │ Entry 84 (array index 83)                               │
  │ Entry 83 (array index 82)                               │
  │ Entry 82 (array index 81)                               │
  └─────────────────────────────────────────────────────────┘

JUMPED TO:
  ┌─────────────────────────────────────────────────────────┐
  │ Entry 81 (array index 80) ← Scanned card (OK JUMPED)    │
  └─────────────────────────────────────────────────────────┘

NEXT EXPECTED:
  Entry 80 (array index 79)
```

---

## Side-by-Side Comparison

```
┌─────────────────────────────────┬─────────────────────────────────┐
│      TOP-TO-BOTTOM              │      BOTTOM-TO-TOP              │
├─────────────────────────────────┼─────────────────────────────────┤
│ Expected: Entry 10              │ Expected: Entry 91              │
│ Scanned:  Entry 20              │ Scanned:  Entry 81              │
│ Jump:     +10 cards forward     │ Jump:     +10 cards forward     │
│                                 │         (in scan direction)     │
├─────────────────────────────────┼─────────────────────────────────┤
│ SKIPPED: 10, 11, 12, 13, 14,    │ SKIPPED: 91, 90, 89, 88, 87,    │
│          15, 16, 17, 18, 19     │          86, 85, 84, 83, 82     │
├─────────────────────────────────┼─────────────────────────────────┤
│ OK (JUMPED): Entry 20           │ OK (JUMPED): Entry 81           │
├─────────────────────────────────┼─────────────────────────────────┤
│ Next Expected: Entry 21         │ Next Expected: Entry 80         │
├─────────────────────────────────┼─────────────────────────────────┤
│ Total SKIPPED: 10 cards         │ Total SKIPPED: 10 cards         │
│ Includes current: YES ✓         │ Includes current: YES ✓         │
│ Excludes jumped: YES ✓          │ Excludes jumped: YES ✓          │
└─────────────────────────────────┴─────────────────────────────────┘
```

---

## Code Implementation

### Top-to-Bottom (Line 1571-1574)
```python
for i in range(actual_card_index, future_index):
    # range(9, 19) = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    skipped_qr = self.expected_cards[i][qr_position]
    log_entry = self.add_log_entry("MISSING", skipped_qr, "SKIPPED", scanned_side)
    log_entries.append(log_entry)
```

### Bottom-to-Top (Line 1520-1528)
```python
for i in range(actual_card_index, actual_future_index, -1):
    # range(90, 80, -1) = [90, 89, 88, 87, 86, 85, 84, 83, 82, 81]
    if i >= 0 and i < len(self.expected_cards):
        skipped_qr = self.expected_cards[i][qr_position]
        log_entry = self.add_log_entry("MISSING", skipped_qr, "SKIPPED", scanned_side)
        log_entries.append(log_entry)
```

---

## Key Insight

**Both directions use the SAME logic:**
- `range(start, end)` for top-to-bottom (step = +1)
- `range(start, end, -1)` for bottom-to-top (step = -1)

**Both are EXCLUSIVE of the end value:**
- Top-to-bottom: `range(9, 19)` excludes 19 (the jumped-to card)
- Bottom-to-top: `range(90, 80, -1)` excludes 80 (the jumped-to card)

**Both INCLUDE the start value:**
- Top-to-bottom: `range(9, 19)` includes 9 (the current expected card)
- Bottom-to-top: `range(90, 80, -1)` includes 90 (the current expected card)

**Result: EQUIVALENT BEHAVIOR** ✅

---

**Date**: April 24, 2026  
**Status**: ✅ VERIFIED - Equivalent skip logic for both directions
