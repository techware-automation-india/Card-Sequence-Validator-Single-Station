# System Architecture

## Overall Architecture Explanation

The Card Sequence Validator employs a **dual-head desktop architecture** built on PyQt6 framework, designed for high-performance, real-time validation of card sequences in manufacturing environments. The system follows a modular, event-driven architecture that supports simultaneous operation of two independent validation heads.

### Architecture Principles
- **Separation of Concerns**: Clear separation between UI, business logic, and data layers
- **Event-Driven Design**: Asynchronous communication using PyQt signals and slots
- **Dual-Head Independence**: Each head operates independently with its own state and configuration
- **Thread-Safe Operations**: Multi-threaded design with proper synchronization mechanisms
- **Modular Components**: Loosely coupled modules for maintainability and extensibility

## Components Involved

### Frontend Components

#### 1. User Interface Layer (PyQt6)
- **Main Application Window** (`src/ui/main_application.py`)
  - Central dashboard with dual-head status display
  - Navigation to different functional modules
  - Real-time system status indicators
  - Theme management and clock widget

- **Network Setup Window** (`src/ui/network_setup_dual.py`)
  - Split-panel configuration for Head A and Head B
  - UDP and COM port configuration interfaces
  - Real-time connectivity testing and validation
  - Password-protected access control

- **File Management Window** (`src/ui/file_management_dual.py`)
  - Dual-panel file operations for both heads
  - CPD file loading and preview functionality
  - Checksum configuration and scan direction settings
  - Log management and export capabilities

- **Scanner Logging Window** (`src/ui/scanner_logging_dual.py`)
  - Real-time validation logging display
  - Scan control and monitoring interfaces
  - Mismatch resolution dialogs
  - Statistical reporting and completion detection

#### 2. UI Components and Widgets (`src/ui/`)
- **Custom Widgets** (`widgets.py`): Specialized UI components
- **Styling System** (`styles.py`): Theme management and CSS styling
- **Card Type Selector** (`card_type_selector.py`): Card configuration interface

### Backend Components

#### 1. Core Application State (`src/app_state.py`)
- **AppState Class**: Central state management for each validation head
- **Configuration Management**: Settings persistence and cache handling
- **Validation Logic**: Core card sequence validation algorithms
- **Event System**: PyQt signal/slot communication framework

#### 2. Dual Head Manager (`src/dual_head_manager.py`)
- **DualHeadManager Class**: Coordinates two independent AppState instances
- **Instance Management**: Handles Head A (Instance 1) and Head B (Instance 2)
- **Unified Operations**: Provides centralized control for dual-head operations

#### 3. Business Logic Layer (`src/logic/`)
- **File Parser** (`file_parser.py`): CPD file processing and validation
- **Card Types** (`src/card_types.py`): Card type definitions and configurations

#### 4. Service Layer (`src/services/`)
- **UDP Reader** (`udp_reader.py`): Network scanner communication
- **UDP Writer** (`udp_writer.py`): Output signal transmission
- **COM Writer** (`com_writer.py`): Serial port communication
- **Utilities** (`utilities.py`): Helper functions and network operations
- **Licensing** (`licensing.py`): Software license validation

### Hardware Integration

#### 1. Network Scanners
- **UDP Communication**: Receives QR code data via UDP packets
- **Multi-Interface Support**: Handles multiple network adapters
- **Remote Device Validation**: Ping-based connectivity testing

#### 2. Serial Devices
- **COM Port Scanners**: On-demand scanning via serial communication
- **Configurable Parameters**: Baud rate, data bits, parity, stop bits
- **Real-time Data Processing**: Immediate QR code processing

#### 3. Output Devices
- **PLC Integration**: Sends validation results to Programmable Logic Controllers
- **Signal Formats**: Configurable output formats (integers, custom protocols)
- **Network Output**: UDP-based result transmission

### Data Storage

#### 1. Configuration Storage
- **Unified Cache System**: JSON-based configuration persistence
- **Location**: `%LOCALAPPDATA%\YourCompany\CardSequenceValidator\`
- **Atomic Writes**: Power-loss protection with temporary file operations
- **Thread-Safe Access**: RLock-based concurrent access protection

#### 2. File Processing
- **CPD Files**: Card Production Data in semicolon-delimited format
- **Output Formats**: JSON configuration for validation result formats
- **Log Export**: CSV format for validation history export

## Data Flow Explanation

### 1. Initialization Flow
```
Application Start → License Validation → Dual Head Manager Creation → 
AppState Initialization (Head A & B) → Cache Loading → UI Initialization → 
Network Validation → Ready State
```

### 2. Configuration Flow
```
User Input → UI Validation → AppState Update → Cache Persistence → 
Hardware Connection → Status Update → UI Refresh
```

### 3. File Loading Flow
```
File Selection → Format Validation → Card Type Selection → 
File Parsing → Data Structure Creation → Lookup Table Generation → 
UI Update → Ready for Validation
```

### 4. Validation Flow
```
Scanner Input → Data Reception → Checksum Processing → 
Sequence Validation → Status Determination → Output Signal → 
Log Entry Creation → UI Update → Cache Auto-Save
```

### 5. Error Handling Flow
```
Error Detection → Error Classification → Recovery Attempt → 
User Notification → Log Entry → System State Preservation
```

## Technologies Used

### Core Framework
- **PyQt6**: Primary GUI framework for desktop application development
- **Python 3.12+**: Core programming language with modern features
- **Threading**: Multi-threaded architecture for concurrent operations

### Communication Protocols
- **UDP (User Datagram Protocol)**: Network communication with scanners and PLCs
- **Serial Communication**: RS-232/USB serial interface for hardware devices
- **JSON**: Configuration data serialization and API communication

### Data Processing
- **CSV Processing**: Log export and data analysis capabilities
- **Regular Expressions**: Data validation and cleaning operations
- **File I/O**: Efficient file processing with encoding support

### System Integration
- **Windows Registry**: System theme detection and OS integration
- **Windows API**: Single instance control and system resource management
- **Network APIs**: IP validation, ping operations, and interface detection

### Development Tools
- **PyInstaller**: Executable packaging and distribution
- **Threading.RLock**: Thread-safe operations and resource protection
- **AppDirs**: Cross-platform application data directory management

### Security and Licensing
- **Cryptography**: License validation and security operations
- **Password Protection**: Secure access to configuration settings
- **Input Validation**: Protection against injection attacks and data corruption

## Architecture Benefits

### Scalability
- **Modular Design**: Easy addition of new features and components
- **Independent Heads**: Horizontal scaling through additional validation heads
- **Plugin Architecture**: Extensible for new card types and protocols

### Reliability
- **Error Isolation**: Failures in one head don't affect the other
- **Graceful Degradation**: System continues operation with reduced functionality
- **Recovery Mechanisms**: Automatic recovery from common failure scenarios

### Maintainability
- **Clear Separation**: Well-defined boundaries between components
- **Event-Driven**: Loose coupling through signal/slot communication
- **Comprehensive Logging**: Detailed debugging and monitoring capabilities

### Performance
- **Asynchronous Operations**: Non-blocking UI with background processing
- **Efficient Data Structures**: Optimized lookup tables for fast validation
- **Resource Management**: Proper cleanup and resource utilization

---

*This architecture supports the dual-head validation requirements while maintaining flexibility for future enhancements and integrations.*