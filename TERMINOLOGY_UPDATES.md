# Terminology Updates

## Overview

The application terminology has been updated to better reflect the business domain and improve user understanding.

## Changes Made

### 1. File Management → Job Management

**Old Term**: File Management
**New Term**: Job Management

**Rationale**: Better reflects that users are managing validation jobs, not just files.

**Changes**:
- Window title: "Job Management - Dual Head"
- Main menu card: "Job Management"
- Card description: "Manage card job files and logs"
- Button text: "Job & Log Management"
- Window class documentation updated
- All references in dialogs and messages

### 2. Sequence File → Job File

**Old Term**: Sequence File
**New Term**: Job File

**Rationale**: Aligns with "Job Management" terminology and is more business-friendly.

**Changes**:
- Section title: "Job File Operations"
- Button text: "📁 Load Job File"
- Status messages: "No job file loaded"
- Error messages: "A job file must be loaded before..."
- All file-related references updated

### 3. Single Card → ISO Card

**Old Term**: Single Card
**New Term**: ISO Card

**Rationale**: More specific and industry-standard terminology for card type.

**Changes**:
- Card type selector: "ISO Card"
- Card type names in messages: "ISO Card"
- Description remains: "One ICCID per card"
- Internal enum value unchanged (CardType.SINGLE)

### 4. Scanner & Logging → Live Status and Logs

**Old Term**: Scanner & Logging
**New Term**: Live Status and Logs

**Rationale**: More descriptive of what the window shows - live validation status and log entries.

**Changes**:
- Main menu card title: "Live Status and Logs"
- Description unchanged: "Live scanner input and validation logging"
- Button text unchanged: "Scanner Control"

### 5. File Management Window References

**Old**: "use the File Management window"
**New**: "use the Job Management window"

**Changes**:
- All dialog messages referring to the window
- Documentation references
- Help text

## Files Modified

### UI Files
- `src/ui/main_application.py`: Main menu cards
- `src/ui/file_management_dual.py`: Window title, headers, labels, buttons
- `src/ui/card_type_selector.py`: Card type option text
- `src/ui/scanner_logging_dual.py`: Dialog messages

### Logic Files
- `src/app_state.py`: Error messages, card type names

## User-Facing Changes

### Main Menu
```
Before:
- Scanner & Logging
- File Management

After:
- Live Status and Logs
- Job Management
```

### Job Management Window
```
Before:
- Title: "File Management - Dual Head"
- Section: "Sequence File Operations"
- Button: "📁 Load Sequence File"
- Status: "No sequence file loaded"

After:
- Title: "Job Management - Dual Head"
- Section: "Job File Operations"
- Button: "📁 Load Job File"
- Status: "No job file loaded"
```

### Card Type Selector
```
Before:
- Single Card
- Half Card
- Quarter Card

After:
- ISO Card
- Half Card
- Quarter Card
```

### Messages
```
Before:
- "A sequence file must be loaded..."
- "Please load a sequence file..."
- "use the File Management window"

After:
- "A job file must be loaded..."
- "Please load a job file..."
- "use the Job Management window"
```

## Internal Code

### No Changes to:
- File names (file_management_dual.py remains)
- Class names (FileManagementWindow remains)
- Function names (select_file, load_file, etc.)
- Variable names (selected_file_path, etc.)
- Enum values (CardType.SINGLE remains)

**Rationale**: Internal code structure remains stable for maintainability. Only user-facing text is updated.

## Benefits

✅ **Clearer Purpose**: "Job Management" better describes the workflow
✅ **Industry Standard**: "ISO Card" is recognized terminology
✅ **Better UX**: "Live Status and Logs" is more descriptive
✅ **Consistency**: All related terms updated together
✅ **Professional**: More business-appropriate language

## Migration Notes

- No database or file format changes required
- No configuration changes needed
- Existing cache files work without modification
- Users will see new terminology immediately
- No breaking changes to functionality

## Documentation Updates Needed

The following documentation should be updated to reflect new terminology:
- User manual
- Training materials
- Help documentation
- README files
- API documentation (if any)
- Build scripts (build_exe.py)

## Testing Checklist

- [ ] Verify all menu items show new names
- [ ] Check Job Management window title
- [ ] Verify button labels are updated
- [ ] Test card type selector shows "ISO Card"
- [ ] Check all error messages use new terms
- [ ] Verify dialog messages are updated
- [ ] Test in both dark and light themes
- [ ] Verify no broken references
- [ ] Check all tooltips (if any)
- [ ] Review all user-facing text

## Summary

All user-facing terminology has been updated to be more professional, descriptive, and aligned with industry standards. The changes improve user understanding while maintaining internal code stability.
