# UI/UX Documentation

## Interface Components Description

### Main Application Window

#### Header Section
**Location**: Top of main window
**Components**:
- **Application Logo**: Animated logo with scaling effects during startup
- **Title**: "Card Sequence Validator - Dual Head"
- **Subtitle**: "Automated Quality Control - Head A & Head B"
- **Clock Widget**: Real-time digital clock display
- **Theme Toggle Button**: Switch between Dark/Light modes

**Screenshot Location**: `screenshots/main-header.png`

#### Welcome Section
**Location**: Below header
**Components**:
- **Welcome Panel**: Accent-colored panel with introduction text
- **Welcome Title**: "Welcome to the Validation Control Panel"
- **Description**: Brief system overview and purpose
- **Visual Design**: Centered text with accent background

**Screenshot Location**: `screenshots/welcome-section.png`

#### Feature Cards Section
**Location**: Center of main window
**Components**:
- **Three Feature Cards** arranged horizontally:
  1. **Live Status and Logs** (📱 icon)
     - Description: "Live scanner input and validation logging"
     - Button: "Scanner Control"
  2. **Network & COM Setup** (🔧 icon)
     - Description: "Configure network and serial connections"
     - Button: "Configuration"
  3. **Job Management** (📁 icon)
     - Description: "Manage card job files and logs"
     - Button: "Job & Log Management"

**Visual Design**: Cards with icons, descriptions, and action buttons
**Screenshot Location**: `screenshots/feature-cards.png`

#### System Status Section
**Location**: Bottom of main window
**Components**:
- **Dual-Head Status Display**:
  - **Head A (Right)** - Green color theme
  - **Head B (Left)** - Blue color theme
- **Status Indicators** for each head:
  - Scanner Status (Idle/Scanning)
  - Input Port Status (IP:Port or Not Set)
  - Output Port Status (IP:Port or Not Set)
  - Scan Card Port Status (COM Port or Not Set)
  - File Loaded Status (Filename with card count or No File)

**Color Coding**:
- 🟢 Green: Connected/OK status
- 🟡 Orange: Warning/Partial status
- 🔴 Red: Error/Not connected
- ⚪ Gray: Idle/Neutral status

**Screenshot Location**: `screenshots/system-status.png`

### Network & COM Port Configuration Window

#### Window Layout
**Design**: Full-screen window with split-panel design
**Security**: Password-protected access with auto-close on focus loss

#### Header Section
**Components**:
- **Title**: "Network & COM Port Configuration - Dual Head"
- **Subtitle**: Configuration instructions
- **Clock Widget**: Consistent with main window

#### Split Configuration Panel
**Layout**: Horizontal split with vertical separator

##### Head B Panel (Left Side)
**Color Theme**: Blue accents and headers
**Sections**:
1. **Main Scanner Input (UDP)**
   - Local IP dropdown with auto-detected interfaces
   - Local Port field (default: 5000)
   - Remote IP field for scanner
   - Remote Port field (default: 6000)
   - Status indicator and Apply button

2. **Output Configuration (UDP)**
   - Local IP dropdown
   - Local Port field (default: 7000)
   - Remote IP field for PLC
   - Remote Port field (default: 8000)
   - Status indicator and Apply button

3. **On-Demand Scanner (Serial)**
   - COM Port dropdown with detected ports
   - Baud Rate selection (default: 115200)
   - Status indicator and Apply button

4. **Action Buttons**
   - Disconnect Head B button

##### Head A Panel (Right Side)
**Color Theme**: Green accents and headers
**Sections**: Identical to Head B but with different default ports
**Screenshot Location**: `screenshots/network-config-split.png`

#### Status Log Section
**Components**:
- **Header with Action Buttons**:
  - "🔄 Refresh Network & Scan IPs" button
  - "⏹ Cancel Scan" button
  - "🔍 Debug Cache" button
  - "🔧 Fix Cache" button
- **Log Text Area**: Scrollable text display with network operations
- **Real-time Updates**: Live status messages and ping results

**Screenshot Location**: `screenshots/network-status-log.png`

#### Security Settings Section
**Components**:
- **Password Change Form**:
  - Current Password field (masked input)
  - New Password field (masked input)
  - Confirm Password field (masked input)
  - "🔒 Change Password" button
- **Default Password Warning**: Shown if password is still default
- **Password Requirements**: Minimum 6 characters

**Screenshot Location**: `screenshots/security-settings.png`

### File Management Window

#### Window Layout
**Design**: Scrollable window with dual-panel split design
**Purpose**: Independent file operations for both validation heads

#### Header Section
**Components**:
- **Title**: "Job Management - Dual Head"
- **Subtitle**: "Manage job files for Head A (Right) and Head B (Left)"
- **Clock Widget**: Consistent timing display

#### Split Panels Layout

##### Head B Panel (Left Side)
**Color Theme**: Blue headers and accents
**Sections**:

1. **Job File Operations**
   - "📁 Load Job File" button
   - File status display
   - Scan direction toggle: "🔄 Top → Bottom" / "🔄 Bottom → Top"
   - "👁 Preview" and "🗑 Clear" buttons

2. **Checksum Configuration**
   - Dropdown: "0 (None)" to "5 (Last 5 digits)"
   - Example display showing before/after processing
   - Real-time example updates

3. **Sequence Control Tools**
   - **Card Details Subsection**:
     - Manual ICCID input field
     - "Scan Card" and "Cancel" buttons
     - Card information display fields
   - **Range Counting Subsection**:
     - First/Last card ICCID fields
     - "Scan Range" and "Calculate Range" buttons
     - Total count display

4. **Validation Log Management**
   - "💾 Download and Clear Logs" button
   - Statistics display (Total/Successful/Failed/Skipped)

##### Head A Panel (Right Side)
**Color Theme**: Green headers and accents
**Sections**: Identical layout to Head B
**Screenshot Location**: `screenshots/file-management-split.png`

#### Start Validation Section
**Location**: Bottom of window
**Components**:
- **Information Label**: "Ready to start validation? Click below to begin scanning."
- **Dual Start Buttons**:
  - "▶ Start Validation - Head B" with status indicator
  - "▶ Start Validation - Head A" with status indicator
- **Status Messages**: Requirements validation for each head

**Screenshot Location**: `screenshots/start-validation.png`

### Scanner Logging Window

#### Window Layout
**Design**: Real-time monitoring interface with dual-head display
**Purpose**: Live validation monitoring and control

#### Header Section
**Components**:
- **Title**: "Scanner Logging - Dual Head"
- **Subtitle**: Real-time validation monitoring
- **Clock Widget**: Timing reference

#### Dual Logging Panels

##### Head B Panel (Left Side)
**Color Theme**: Blue headers and status indicators
**Components**:

1. **Control Section**
   - "▶ Start Validation" / "⏸ Pause Validation" / "⏹ Stop Validation" buttons
   - Validation status display

2. **Current Status Display**
   - Last Scanned ID field
   - Previous Validated ID field
   - Next Expected ID field
   - Current progress information

3. **Log Table**
   - Columns: Timestamp, Scanned Code, Expected Code, Status, Card Index
   - Real-time log entries
   - Color-coded status indicators
   - Pagination controls

4. **Statistics Panel**
   - Total Scans counter
   - Success/Failure counters
   - Real-time statistics

##### Head A Panel (Right Side)
**Color Theme**: Green headers and status indicators
**Components**: Identical layout to Head B
**Screenshot Location**: `screenshots/scanner-logging-dual.png`

#### Mismatch Resolution Dialog
**Trigger**: Appears when sequence mismatch is detected
**Components**:
- **Title**: "Sequence Mismatch Detected - Head X"
- **Information Display**:
  - Expected card information
  - Scanned card information
  - Mismatch details
- **Action Buttons**:
  - "Skip and Continue" - Mark as approved jump
  - "Retry Scan" - Wait for correct card
  - "Cancel" - Stop validation
- **Visual Design**: Modal dialog with clear action choices

**Screenshot Location**: `screenshots/mismatch-dialog.png`

#### Completion Dialog
**Trigger**: Appears when validation sequence is complete
**Components**:
- **Title**: "Validation Complete - Head X (Side)"
- **Summary Information**:
  - File name and completion message
  - Validation statistics breakdown
  - Success/failure/skip counts
- **Action Button**: "OK" to acknowledge completion

**Screenshot Location**: `screenshots/completion-dialog.png`

## UI Section Explanations

### Navigation Flow
```
Main Dashboard → Feature Cards → Specific Windows
     ↓              ↓              ↓
Status Display → Configuration → Detailed Operations
     ↓              ↓              ↓
Quick Access → Secure Setup → Operational Control
```

### Color Coding System

#### Head Identification
- **Head A (Right)**: Green theme (#4CAF50)
  - Headers, buttons, and status indicators
  - Consistent across all windows
  - Associated with "Right" side operations

- **Head B (Left)**: Blue theme (#2196F3)
  - Headers, buttons, and status indicators
  - Consistent across all windows
  - Associated with "Left" side operations

#### Status Indicators
- **🟢 Green (statusOK)**: Connected, successful, operational
- **🟡 Orange (statusWarning)**: Partial connection, warnings, attention needed
- **🔴 Red (statusError)**: Disconnected, failed, error state
- **⚪ Gray (statusIdle)**: Idle, neutral, not applicable
- **🔵 Blue (statusNeutral)**: Unknown status, pending

#### Theme Support
- **Dark Theme**: Default for low-light environments
  - Dark backgrounds with light text
  - Reduced eye strain
  - Professional appearance

- **Light Theme**: Alternative for bright environments
  - Light backgrounds with dark text
  - High contrast for visibility
  - Traditional appearance

### Responsive Design Elements

#### Window Sizing
- **Main Window**: Maximized by default, scalable interface
- **Configuration Windows**: Full-screen with fixed size for security
- **Dialog Windows**: Centered, appropriately sized for content

#### Font Scaling
- **Headers**: Scalable font sizes (h1: 24px, h2: 18px)
- **Body Text**: Standard readable sizes (14px default)
- **Status Text**: Smaller informational text (11-12px)

#### Layout Adaptation
- **Split Panels**: Equal width distribution with separator
- **Button Sizing**: Consistent minimum widths for usability
- **Input Fields**: Appropriate sizing for expected content

### Accessibility Features

#### Keyboard Navigation
- **Tab Order**: Logical progression through interface elements
- **Enter Key**: Activates primary buttons and confirms inputs
- **Escape Key**: Cancels dialogs and operations

#### Visual Accessibility
- **High Contrast**: Clear distinction between elements
- **Color Independence**: Status communicated through text and icons
- **Font Clarity**: Readable fonts with appropriate sizing

#### User Feedback
- **Status Messages**: Clear communication of system state
- **Progress Indicators**: Visual feedback for operations
- **Error Messages**: Descriptive and actionable error information

## Screenshot Requirements

### Main Application Screenshots
1. **main-dashboard-overview.png**: Complete main window with all sections
2. **main-header.png**: Header section with logo and navigation
3. **welcome-section.png**: Welcome panel and description
4. **feature-cards.png**: Three feature cards with icons and buttons
5. **system-status.png**: Dual-head status display with indicators
6. **theme-comparison.png**: Side-by-side dark and light themes

### Network Configuration Screenshots
7. **network-config-overview.png**: Complete network configuration window
8. **network-config-split.png**: Split panel showing both heads
9. **network-status-log.png**: Status log section with operations
10. **security-settings.png**: Password change section
11. **connectivity-testing.png**: Network scan in progress

### File Management Screenshots
12. **file-management-overview.png**: Complete file management window
13. **file-management-split.png**: Dual panels with file operations
14. **checksum-config.png**: Checksum configuration section
15. **card-details-scan.png**: Card detail scanning interface
16. **range-counting.png**: Range counting tools
17. **start-validation.png**: Start validation section

### Scanner Logging Screenshots
18. **scanner-logging-overview.png**: Complete scanner logging window
19. **scanner-logging-dual.png**: Dual logging panels active
20. **log-table-active.png**: Log table with real-time entries
21. **mismatch-dialog.png**: Sequence mismatch resolution dialog
22. **completion-dialog.png**: Validation completion dialog

### Operational Screenshots
23. **validation-in-progress.png**: System during active validation
24. **error-handling.png**: Error states and recovery options
25. **export-process.png**: Log export dialog and process
26. **session-recovery.png**: Session recovery options

### Configuration Screenshots
27. **initial-setup.png**: First-time configuration process
28. **password-protection.png**: Password entry dialog
29. **file-preview.png**: CPD file preview window
30. **statistics-display.png**: Validation statistics panel

## User Experience Guidelines

### Workflow Optimization
- **Minimal Clicks**: Common operations accessible within 2-3 clicks
- **Logical Grouping**: Related functions grouped in same interface areas
- **Progressive Disclosure**: Advanced features available but not overwhelming

### Error Prevention
- **Input Validation**: Real-time validation of user inputs
- **Confirmation Dialogs**: Critical actions require confirmation
- **Undo Capabilities**: Reversible operations where possible

### Performance Feedback
- **Immediate Response**: UI updates within 100ms for user actions
- **Progress Indication**: Long operations show progress feedback
- **Status Communication**: Clear indication of system state at all times

### Consistency Standards
- **Visual Consistency**: Consistent styling across all windows
- **Behavioral Consistency**: Similar operations work the same way
- **Terminology Consistency**: Same terms used throughout interface

---

*This UI/UX documentation provides comprehensive guidance for understanding and maintaining the user interface design and user experience standards of the Card Sequence Validator system.*