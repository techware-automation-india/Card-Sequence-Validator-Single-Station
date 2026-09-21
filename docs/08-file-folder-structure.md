# File & Folder Structure

## Project Directory Structure

```
card_sequence_validator_v3/
├── 📁 assets/                          # Application assets and resources
│   ├── 🖼️ favicon.ico                  # Application icon (Windows)
│   ├── 🎬 gear_loader.gif              # Loading animation
│   ├── 🖼️ Icon.png                     # Main application icon
│   └── 🖼️ logo.png                     # Application logo
│
├── 📁 build/                           # PyInstaller build artifacts (generated)
│   ├── 📁 CardSequenceValidator/       # Build intermediate files
│   └── 📄 *.spec                       # PyInstaller specification files
│
├── 📁 card_example/                    # Sample CPD files for testing
│   ├── 📁 half_Card/                   # Half card examples
│   │   ├── 📄 IN_450056520_00001_96855_OR_3568474_M_WDOM_RAW_28022024103318.CPD
│   │   └── 📄 RILS5622.CPD
│   ├── 📁 quarter_card/                # Quarter card examples
│   │   └── 📄 HESH1356.CPD
│   └── 📁 single_card/                 # Single card examples
│       └── 📄 HESH1355.CPD
│
├── 📁 dist/                            # Distribution files (generated)
│   ├── 🚀 CardSequenceValidator.exe    # Main executable
│   └── 📄 README.txt                   # Distribution readme
│
├── 📁 docs/                            # Project documentation
│   ├── 📄 README.md                    # Documentation index
│   ├── 📄 01-project-overview.md       # Project overview
│   ├── 📄 02-system-architecture.md    # System architecture
│   ├── 📄 03-installation-setup.md     # Installation guide
│   ├── 📄 04-features-functionality.md # Features documentation
│   ├── 📄 05-user-guide-workflow.md    # User guide
│   ├── 📄 06-ui-ux-documentation.md    # UI/UX documentation
│   ├── 📄 07-core-logic-algorithms.md  # Core algorithms
│   ├── 📄 08-file-folder-structure.md  # This file
│   ├── 📄 09-apis-integrations.md      # APIs and integrations
│   ├── 📄 10-testing-validation.md     # Testing documentation
│   ├── 📄 11-logging-error-handling.md # Logging and errors
│   ├── 📄 12-deployment-guide.md       # Deployment guide
│   ├── 📄 13-security-considerations.md # Security documentation
│   ├── 📄 14-future-enhancements.md    # Future enhancements
│   └── 📄 15-contributors-license.md    # Contributors and license
│
├── 📁 gen_log_eg/                      # Generated log examples
│   └── 📄 logs_head_A_20260217_161328.csv # Sample log export
│
├── 📁 src/                             # Source code directory
│   ├── 📁 __pycache__/                 # Python bytecode cache (generated)
│   ├── 📁 logic/                       # Business logic layer
│   │   ├── 📁 __pycache__/             # Python bytecode cache
│   │   ├── 📄 __init__.py              # Package initialization
│   │   └── 📄 file_parser.py           # File parsing logic
│   ├── 📁 services/                    # Service layer components
│   │   ├── 📁 __pycache__/             # Python bytecode cache
│   │   ├── 📄 __init__.py              # Package initialization
│   │   ├── 📄 com_writer.py            # Serial COM port writer
│   │   ├── 📄 licensing.py             # License validation service
│   │   ├── 📄 udp_reader.py            # UDP network reader
│   │   ├── 📄 udp_writer.py            # UDP network writer
│   │   └── 📄 utilities.py             # Utility functions
│   ├── 📁 ui/                          # User interface components
│   │   ├── 📁 __pycache__/             # Python bytecode cache
│   │   ├── 📄 __init__.py              # Package initialization
│   │   ├── 📄 card_type_selector.py    # Card type selection dialog
│   │   ├── 📄 file_management_dual.py  # File management interface
│   │   ├── 📄 main_application.py      # Main application window
│   │   ├── 📄 network_setup_dual.py    # Network configuration interface
│   │   ├── 📄 scanner_logging_dual.py  # Scanner logging interface
│   │   ├── 📄 styles.py                # UI styling and themes
│   │   └── 📄 widgets.py               # Custom UI widgets
│   ├── 📄 __init__.py                  # Source package initialization
│   ├── 📄 app_state.py                 # Core application state management
│   ├── 📄 card_types.py                # Card type definitions
│   └── 📄 dual_head_manager.py         # Dual head coordination
│
├── 📁 tests/                           # Test files and utilities
│   └── 📄 udp_listener_terminal.py     # UDP testing utility
│
├── 📄 .gitignore                       # Git ignore patterns
├── 📄 build_exe.py                     # Executable build script
├── 📄 constants.py                     # Application constants
├── 📄 desktop.ini                      # Windows folder customization
├── 📄 license.dat                      # Software license file
├── 📄 main.py                          # Application entry point
├── 📄 output_formats.json              # Output signal format definitions
├── 📄 requirements.txt                 # Python dependencies
└── 📄 *.md                             # Various documentation files
```

## Important Files and Their Purposes

### Core Application Files

#### `main.py` - Application Entry Point
**Purpose**: Main application launcher and initialization
**Key Functions**:
- License validation on startup
- Single instance control using QLockFile
- Resource path resolution for PyInstaller
- Dual head manager initialization
- Application window creation and display

**Code Structure**:
```python
# Resource path handling for PyInstaller
def resource_path(relative_path)

# Single instance enforcement
def check_single_instance()

# Main execution
if __name__ == "__main__":
    # Application setup and launch
```

#### `constants.py` - Application Constants
**Purpose**: Centralized configuration and constant definitions
**Key Constants**:
- `LOGO_PATH`: Application logo file path
- `OUTPUT_FORMATS_PATH`: Output format configuration file
- `FILE_FILTER`: File dialog filter for CPD files
- `CACHE_FILE_PATH`: Application cache file location
- `MASTER_PASSWORD`: Emergency access password

#### `output_formats.json` - Signal Format Configuration
**Purpose**: Defines output signal formats for different card types
**Structure**:
```json
{
  "Integers": {
    "single": {"OK": "17\r\n", "NOT OK": "18\r\n"},
    "half": {"OK": "09\r\n", "NOT OK": "10\r\n"},
    "quarter": {"OK": "05\r\n", "NOT OK": "06\r\n"}
  }
}
```

#### `requirements.txt` - Python Dependencies
**Purpose**: Defines required Python packages and versions
**Key Dependencies**:
- PyQt6: GUI framework
- pyserial: Serial communication
- cryptography: License validation
- appdirs: Cross-platform directory paths

### Source Code Organization

#### `src/app_state.py` - Core State Management
**Purpose**: Central application state and validation logic
**Key Classes**:
- `AppState`: Main state management class
- `ComPortReader`: Serial communication handler

**Key Responsibilities**:
- Validation logic implementation
- Configuration persistence
- Network and serial communication
- Log data management
- Cache operations with thread safety

#### `src/dual_head_manager.py` - Dual Head Coordination
**Purpose**: Manages two independent AppState instances
**Key Functions**:
- Head A and Head B instance management
- Unified operations across both heads
- Signal coordination and forwarding
- Startup validation orchestration

#### `src/card_types.py` - Card Type Definitions
**Purpose**: Defines supported card types and their properties
**Supported Types**:
- `SINGLE`: One QR code per card
- `HALF`: Two QR codes per card (Left/Right)
- `QUARTER`: Four QR codes per card (BL/TL/TR/BR)

### User Interface Layer

#### `src/ui/main_application.py` - Main Window
**Purpose**: Primary application interface and navigation
**Key Components**:
- Animated logo and startup sequence
- Feature card navigation
- Dual-head status display
- Theme management
- Clock widget integration

#### `src/ui/network_setup_dual.py` - Network Configuration
**Purpose**: Network and COM port configuration interface
**Key Features**:
- Split-panel dual-head configuration
- Real-time connectivity testing
- Password-protected access
- Network device discovery
- Security settings management

#### `src/ui/file_management_dual.py` - File Operations
**Purpose**: File loading, configuration, and log management
**Key Features**:
- CPD file loading and preview
- Checksum configuration
- Scan direction settings
- Card detail scanning
- Range counting tools
- Log export functionality

#### `src/ui/scanner_logging_dual.py` - Validation Monitoring
**Purpose**: Real-time validation monitoring and control
**Key Features**:
- Live validation logging
- Scan control (start/pause/stop)
- Mismatch resolution dialogs
- Statistics display
- Completion detection

#### `src/ui/styles.py` - UI Styling
**Purpose**: Centralized styling and theme management
**Contents**:
- Dark theme stylesheet definitions
- Light theme stylesheet definitions
- Color scheme constants
- Font and sizing specifications

#### `src/ui/widgets.py` - Custom Widgets
**Purpose**: Reusable UI components
**Custom Widgets**:
- `ClockWidget`: Real-time clock display
- `ScalableLabel`: Responsive image labels
- `PasswordDialog`: Secure password input
- `ApprovalDialog`: Mismatch resolution interface

### Service Layer

#### `src/services/udp_reader.py` - UDP Communication
**Purpose**: Network-based scanner communication
**Key Features**:
- Multi-interface UDP binding
- Remote IP/port filtering
- Thread-safe operation
- Error handling and recovery
- Real-time data processing

#### `src/services/udp_writer.py` - UDP Output
**Purpose**: Network-based output signal transmission
**Key Features**:
- Configurable output formats
- PLC communication
- Connection management
- Error handling and retry logic

#### `src/services/com_writer.py` - Serial Output
**Purpose**: Serial port output communication
**Key Features**:
- Configurable serial parameters
- Connection management
- Error handling
- Status reporting

#### `src/services/utilities.py` - Utility Functions
**Purpose**: Common utility functions and helpers
**Key Functions**:
- `ping_remote_ip_sync()`: Synchronous network testing
- `ping_remote_ip_async()`: Asynchronous network testing
- `parse_cpd_cards()`: CPD file parsing with rebatch logic

#### `src/services/licensing.py` - License Management
**Purpose**: Software license validation and protection
**Key Features**:
- Machine ID generation
- License file validation
- Cryptographic verification
- Expiration checking

### Business Logic Layer

#### `src/logic/file_parser.py` - File Processing
**Purpose**: File parsing and validation logic
**Key Functions**:
- `parse_file()`: Main file parsing entry point
- CPD format validation
- Card type-specific processing
- Error handling and reporting

### Build and Distribution

#### `build_exe.py` - Build Script
**Purpose**: PyInstaller build automation
**Key Features**:
- Automated executable creation
- Asset bundling
- Dependency management
- Build optimization
- Distribution preparation

**Build Process**:
1. Clean old build artifacts
2. Configure PyInstaller parameters
3. Bundle assets and dependencies
4. Create single-file executable
5. Generate distribution readme

#### `dist/` Directory - Distribution Files
**Contents**:
- `CardSequenceValidator.exe`: Main executable (40-50 MB)
- `README.txt`: Installation and usage instructions
- License files (if required)

### Configuration and Cache

#### Cache File Location
**Path**: `%LOCALAPPDATA%\YourCompany\CardSequenceValidator\app_cache_unified.json`
**Purpose**: Persistent configuration storage
**Structure**:
```json
{
  "head_a": {
    "card_type": "half",
    "main_scanner_config": {...},
    "ondemand_scanner_config": {...},
    "output_config": {...},
    "selected_file_path": "...",
    "log_data": [...],
    "checksum_digits": 1,
    "network_config_password": "...",
    "current_theme": "dark"
  },
  "head_b": {
    // Similar structure for Head B
  }
}
```

### Sample Data and Examples

#### `card_example/` Directory
**Purpose**: Sample CPD files for testing and demonstration
**Organization**:
- `single_card/`: Examples of single QR code cards
- `half_Card/`: Examples of dual QR code cards
- `quarter_card/`: Examples of four QR code cards

**File Naming Convention**:
- Production files: `IN_[batch]_[sequence]_[date].CPD`
- Test files: `[identifier][number].CPD`

### Documentation Structure

#### `docs/` Directory
**Purpose**: Comprehensive project documentation
**Organization**: 15 numbered documentation files covering all aspects
**Format**: Markdown files with consistent structure
**Navigation**: Central README.md with links to all sections

### Testing and Development

#### `tests/` Directory
**Purpose**: Testing utilities and scripts
**Contents**:
- `udp_listener_terminal.py`: Network testing utility
- Unit test files (when implemented)
- Integration test scripts

### Generated Files and Directories

#### Build Artifacts
- `build/`: PyInstaller intermediate files
- `src/__pycache__/`: Python bytecode cache
- `*.pyc`: Compiled Python files

#### Runtime Files
- `debug_output.txt`: Application debug log (if enabled)
- Temporary cache files during atomic operations
- Lock files for single instance control

## Code Organization Patterns

### Package Structure
```python
src/
├── __init__.py              # Package marker
├── app_state.py             # Core state management
├── dual_head_manager.py     # Coordination layer
├── card_types.py            # Data definitions
├── logic/                   # Business logic
│   ├── __init__.py
│   └── file_parser.py
├── services/                # External integrations
│   ├── __init__.py
│   ├── udp_reader.py
│   ├── udp_writer.py
│   ├── com_writer.py
│   ├── utilities.py
│   └── licensing.py
└── ui/                      # User interface
    ├── __init__.py
    ├── main_application.py
    ├── network_setup_dual.py
    ├── file_management_dual.py
    ├── scanner_logging_dual.py
    ├── card_type_selector.py
    ├── styles.py
    └── widgets.py
```

### Import Patterns
```python
# Relative imports within package
from .app_state import AppState
from .ui.main_application import HomePage
from ..services.udp_reader import UDPReader

# External library imports
from PyQt6.QtWidgets import QApplication
import serial
import json
```

### Configuration File Patterns
```python
# Constants file pattern
RESOURCE_PATH = resource_path("assets/logo.png")
CONFIG_PATH = resource_path("config.json")

# JSON configuration pattern
{
  "section_name": {
    "parameter": "value",
    "nested_config": {
      "sub_parameter": "sub_value"
    }
  }
}
```

## File Naming Conventions

### Python Files
- **Snake case**: `file_management_dual.py`
- **Descriptive names**: Clearly indicate purpose
- **Module organization**: Group related functionality

### Asset Files
- **Descriptive names**: `logo.png`, `gear_loader.gif`
- **Standard extensions**: `.png`, `.ico`, `.gif`
- **Consistent naming**: Avoid spaces and special characters

### Documentation Files
- **Numbered sequence**: `01-project-overview.md`
- **Descriptive titles**: Clear indication of content
- **Markdown format**: Consistent `.md` extension

### Configuration Files
- **JSON format**: `.json` extension for structured data
- **Descriptive names**: `output_formats.json`
- **Standard locations**: Root directory for global configs

## Directory Access Patterns

### Resource Access
```python
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller bundle
    except Exception:
        base_path = os.path.abspath(".")  # Development
    return os.path.join(base_path, relative_path)
```

### Cache Directory Access
```python
def get_cache_directory():
    """Get platform-appropriate cache directory"""
    return user_data_dir(APP_NAME, APP_AUTHOR)
```

### Temporary File Handling
```python
def atomic_file_operation(file_path, data):
    """Atomic file write with temporary file"""
    temp_path = file_path + ".tmp"
    try:
        with open(temp_path, 'w') as f:
            json.dump(data, f)
        os.replace(temp_path, file_path)  # Atomic rename
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

---

*This file and folder structure documentation provides comprehensive understanding of the project organization, file purposes, and code organization patterns used in the Card Sequence Validator system.*