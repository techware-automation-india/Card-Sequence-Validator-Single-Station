# Installation & Setup Guide

## Prerequisites

### System Requirements

#### Minimum Requirements
- **Operating System**: Windows 10 (64-bit) or later
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 500 MB free disk space
- **Network**: Ethernet adapter for UDP communication
- **Display**: 1366x768 minimum resolution, 1920x1080 recommended

#### Recommended Requirements
- **Operating System**: Windows 11 (64-bit)
- **RAM**: 16 GB for optimal performance
- **Storage**: 2 GB free disk space (for logs and cache)
- **Network**: Gigabit Ethernet for high-speed communication
- **Display**: Dual monitor setup for enhanced productivity

### Hardware Prerequisites

#### Network Infrastructure
- **Ethernet Network**: Configured network with scanner devices
- **IP Address Range**: Available IP addresses for scanner communication
- **Network Switches**: Managed switches for optimal performance
- **Firewall Configuration**: UDP ports 5000-8000 accessible

#### Serial Communication (Optional)
- **COM Ports**: Available serial ports for on-demand scanners
- **USB-to-Serial Adapters**: If native COM ports are not available
- **Serial Cables**: Appropriate cables for device connections

#### Scanner Hardware
- **Network Scanners**: UDP-capable QR code scanners
- **Serial Scanners**: RS-232 or USB serial QR code scanners
- **PLC Integration**: Programmable Logic Controllers for output signals

### Software Dependencies

#### Runtime Dependencies (Included in Executable)
- Python 3.12+ runtime
- PyQt6 GUI framework
- Serial communication libraries
- Cryptography libraries
- Network utilities

#### Development Dependencies (For Source Code)
```bash
# Core dependencies
PyQt6>=6.5.0
pyserial>=3.5
cryptography>=3.4.8
appdirs>=1.4.4

# Development tools
PyInstaller>=5.0
pytest>=7.0
```

## Step-by-Step Installation Instructions

### Option 1: Executable Installation (Recommended)

#### Step 1: Download the Application
1. Obtain the `CardSequenceValidator.exe` file from the distribution package
2. Verify the file size (approximately 40-50 MB)
3. Check the file version and build date

#### Step 2: Create Installation Directory
```cmd
# Create application directory
mkdir C:\CardSequenceValidator
cd C:\CardSequenceValidator

# Copy executable
copy CardSequenceValidator.exe C:\CardSequenceValidator\
```

#### Step 3: License File Setup (If Required)
```cmd
# Copy license file to application directory
copy license.dat C:\CardSequenceValidator\
```

#### Step 4: First Run
1. Right-click `CardSequenceValidator.exe`
2. Select "Run as administrator" (first run only)
3. Allow Windows Defender/Antivirus if prompted
4. Wait for application initialization

#### Step 5: Verify Installation
- Application window should open with dual-head interface
- Check system status indicators
- Verify cache directory creation: `%LOCALAPPDATA%\YourCompany\CardSequenceValidator\`

### Option 2: Source Code Installation (Development)

#### Step 1: Clone Repository
```bash
git clone <repository-url>
cd card_sequence_validator
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source .venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
pip list
```

#### Step 4: Run from Source
```bash
# Run application
python main.py
```

#### Step 5: Build Executable (Optional)
```bash
# Build executable using PyInstaller
python build_exe.py

# Executable will be created in dist/ directory
```

## Environment Setup

### Network Configuration

#### Step 1: Identify Network Interfaces
1. Open Command Prompt as Administrator
2. Run `ipconfig /all` to list network adapters
3. Note the IP addresses of Ethernet adapters
4. Ensure scanners are on the same network segment

#### Step 2: Configure Firewall
```cmd
# Allow UDP ports for scanner communication
netsh advfirewall firewall add rule name="Card Validator UDP In" dir=in action=allow protocol=UDP localport=5000-8000
netsh advfirewall firewall add rule name="Card Validator UDP Out" dir=out action=allow protocol=UDP localport=5000-8000
```

#### Step 3: Test Network Connectivity
```cmd
# Test ping to scanner devices
ping 192.168.1.100
ping 192.168.1.101

# Test UDP port availability
netstat -an | findstr :5000
```

### Serial Port Configuration

#### Step 1: Identify COM Ports
1. Open Device Manager (`devmgmt.msc`)
2. Expand "Ports (COM & LPT)"
3. Note available COM port numbers
4. Install drivers if devices show as "Unknown"

#### Step 2: Test Serial Communication
```cmd
# Use built-in Windows tools or third-party terminal
# Verify COM port accessibility and baud rate settings
```

### Application Configuration

#### Step 1: Initial Configuration
1. Launch the application
2. Navigate to "Network & COM Setup"
3. Enter the default password: `admin123`
4. Configure network settings for both heads

#### Step 2: Change Default Password
1. In Network Setup window, scroll to "Security Settings"
2. Enter current password: `admin123`
3. Set a new secure password (minimum 6 characters)
4. Confirm the password change

#### Step 3: Configure Scanner Connections
```
Head A (Right):
- Main Scanner: UDP configuration
- Output: PLC connection settings
- On-Demand Scanner: COM port or UDP

Head B (Left):
- Main Scanner: UDP configuration  
- Output: PLC connection settings
- On-Demand Scanner: COM port or UDP
```

## How to Run the Project Locally

### Running the Executable

#### Standard Execution
```cmd
# Navigate to installation directory
cd C:\CardSequenceValidator

# Run application
CardSequenceValidator.exe
```

#### Command Line Options
```cmd
# Run with debug output
CardSequenceValidator.exe --debug

# Run with specific configuration
CardSequenceValidator.exe --config custom_config.json
```

### Running from Source Code

#### Development Mode
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run with debug output
python main.py

# Run with specific Python version
python3.12 main.py
```

#### Debug Mode
```bash
# Run with verbose logging
python main.py --verbose

# Run with specific log level
python main.py --log-level DEBUG
```

### Verification Steps

#### Step 1: Application Startup
- [ ] Application launches without errors
- [ ] Dual-head interface displays correctly
- [ ] System status shows "Idle" for both heads
- [ ] Clock widget displays current time

#### Step 2: Network Configuration
- [ ] Network Setup window opens with password
- [ ] Network interfaces are detected
- [ ] IP validation works correctly
- [ ] Ping tests show connectivity status

#### Step 3: File Operations
- [ ] File Management window opens
- [ ] CPD files can be loaded
- [ ] File preview displays correctly
- [ ] Card type selection works

#### Step 4: Scanner Integration
- [ ] Scanner Logging window opens
- [ ] Network scanners connect successfully
- [ ] Serial scanners are detected
- [ ] Test scans process correctly

## Troubleshooting Common Issues

### Installation Issues

#### Antivirus False Positive
```
Problem: Antivirus software blocks the executable
Solution: 
1. Add CardSequenceValidator.exe to antivirus whitelist
2. Temporarily disable real-time protection during installation
3. Download from trusted source only
```

#### Missing DLL Errors
```
Problem: "MSVCP140.dll not found" or similar
Solution:
1. Install Microsoft Visual C++ Redistributable
2. Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
3. Restart computer after installation
```

#### Permission Errors
```
Problem: "Access denied" during first run
Solution:
1. Run as Administrator (first time only)
2. Ensure user has write access to %LOCALAPPDATA%
3. Check Windows UAC settings
```

### Network Configuration Issues

#### Scanner Not Detected
```
Problem: Network scanner not responding
Solution:
1. Verify IP address and port configuration
2. Check network cable connections
3. Test with ping command
4. Verify firewall settings
5. Check scanner power and network settings
```

#### COM Port Access Denied
```
Problem: Cannot access COM port
Solution:
1. Close other applications using the COM port
2. Check Device Manager for port conflicts
3. Reinstall COM port drivers
4. Try different COM port number
```

### Application Issues

#### Cache Corruption
```
Problem: Application fails to start or loses settings
Solution:
1. Delete cache file: %LOCALAPPDATA%\YourCompany\CardSequenceValidator\app_cache_unified.json
2. Restart application
3. Reconfigure settings
```

#### License Validation Failure
```
Problem: "License Error" on startup
Solution:
1. Ensure license.dat is in application directory
2. Check license file permissions
3. Contact support for license renewal
4. Verify system date/time is correct
```

## Performance Optimization

### System Optimization
- Disable unnecessary Windows services
- Set application to "High" priority in Task Manager
- Use SSD storage for better I/O performance
- Ensure adequate RAM for large file processing

### Network Optimization
- Use dedicated network interface for scanner communication
- Configure Quality of Service (QoS) for UDP traffic
- Use managed switches with IGMP snooping
- Monitor network utilization and latency

### Application Optimization
- Regular cache cleanup and log export
- Monitor memory usage during long sessions
- Use appropriate checksum settings for performance
- Configure auto-save intervals based on usage patterns

---

*This installation guide ensures proper setup and configuration of the Card Sequence Validator system for optimal performance and reliability.*