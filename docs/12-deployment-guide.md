# Deployment Guide

## Deployment Overview

The Card Sequence Validator is deployed as a standalone Windows executable with minimal dependencies, designed for easy distribution and installation in manufacturing environments.

### Deployment Architecture
```
Development Environment → Build Process → Distribution Package → Target Systems
        ↓                      ↓                    ↓                ↓
   Source Code          PyInstaller Build    Executable + Assets   Production Use
   Dependencies         Asset Bundling       License Files         End Users
   Configuration        Optimization         Documentation         Support
```

## Build Process

### Prerequisites for Building

#### Development Environment Setup
```bash
# Required software
Python 3.12+
PyInstaller 6.0+
Git (for version control)
Windows 10+ (for Windows builds)

# Required Python packages
pip install -r requirements.txt
pip install pyinstaller
```

#### Build Environment Verification
```python
# verify_build_environment.py
import sys
import subprocess
import importlib

def verify_python_version():
    """Verify Python version compatibility"""
    version = sys.version_info
    if version.major != 3 or version.minor < 12:
        raise Exception(f"Python 3.12+ required, found {version.major}.{version.minor}")
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")

def verify_dependencies():
    """Verify all required dependencies are installed"""
    required_packages = [
        'PyQt6', 'pyserial', 'cryptography', 'appdirs', 'pyinstaller'
    ]
    
    for package in required_packages:
        try:
            importlib.import_module(package.lower().replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            raise Exception(f"Missing required package: {package}")

if __name__ == "__main__":
    verify_python_version()
    verify_dependencies()
    print("Build environment verified successfully!")
```

### Automated Build Script

#### `build_exe.py` - Complete Build Process
```python
"""
Comprehensive build script for Card Sequence Validator
Handles cleaning, building, testing, and packaging
"""

import os
import sys
import subprocess
import shutil
import json
from datetime import datetime

class BuildManager:
    def __init__(self):
        self.build_info = {
            "build_date": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "build_machine": os.environ.get('COMPUTERNAME', 'Unknown'),
            "git_commit": self.get_git_commit(),
            "version": "3.1.0"
        }
        
    def get_git_commit(self):
        """Get current git commit hash"""
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True)
            return result.stdout.strip()[:8] if result.returncode == 0 else "Unknown"
        except:
            return "Unknown"
    
    def clean_build_directories(self):
        """Remove old build artifacts"""
        print("🧹 Cleaning build directories...")
        
        directories_to_clean = ['build', 'dist', '__pycache__']
        files_to_clean = ['*.spec']
        
        for directory in directories_to_clean:
            if os.path.exists(directory):
                try:
                    shutil.rmtree(directory)
                    print(f"  ✓ Removed {directory}/")
                except Exception as e:
                    print(f"  ⚠️ Could not remove {directory}: {e}")
        
        # Remove .spec files
        for spec_file in glob.glob("*.spec"):
            try:
                os.remove(spec_file)
                print(f"  ✓ Removed {spec_file}")
            except Exception as e:
                print(f"  ⚠️ Could not remove {spec_file}: {e}")
    
    def build_executable(self):
        """Build executable using PyInstaller"""
        print("🔨 Building executable...")
        
        # PyInstaller command configuration
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--name=CardSequenceValidator',
            '--onefile',                    # Single executable
            '--windowed',                   # No console window
            '--icon=assets/Icon.png',       # Application icon
            
            # Data files
            '--add-data=assets;assets',
            '--add-data=card_example;card_example',
            '--add-data=output_formats.json;.',
            '--add-data=docs;docs',
            
            # Hidden imports
            '--hidden-import=PyQt6.QtCore',
            '--hidden-import=PyQt6.QtWidgets',
            '--hidden-import=PyQt6.QtGui',
            '--hidden-import=serial',
            '--hidden-import=cryptography',
            
            # Optimizations
            '--optimize=2',
            '--strip',
            
            # Exclude unnecessary modules
            '--exclude-module=matplotlib',
            '--exclude-module=numpy',
            '--exclude-module=pandas',
            '--exclude-module=scipy',
            '--exclude-module=PIL',
            '--exclude-module=tkinter',
            
            # Entry point
            'main.py'
        ]
        
        print(f"Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✓ Build completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed!")
            print(f"Error: {e}")
            print(f"Output: {e.stdout}")
            print(f"Error output: {e.stderr}")
            return False
    
    def create_build_info_file(self):
        """Create build information file"""
        build_info_path = os.path.join('dist', 'build_info.json')
        
        with open(build_info_path, 'w') as f:
            json.dump(self.build_info, f, indent=4)
        
        print(f"✓ Created build info: {build_info_path}")
    
    def create_distribution_package(self):
        """Create complete distribution package"""
        print("📦 Creating distribution package...")
        
        # Copy additional files to dist
        additional_files = [
            ('license.dat', 'dist/license.dat'),
            ('README.md', 'dist/README.md'),
            ('CHANGELOG.md', 'dist/CHANGELOG.md')
        ]
        
        for src, dst in additional_files:
            if os.path.exists(src):
                try:
                    shutil.copy2(src, dst)
                    print(f"  ✓ Copied {src} → {dst}")
                except Exception as e:
                    print(f"  ⚠️ Could not copy {src}: {e}")
        
        # Create installation README
        self.create_installation_readme()
        
        # Create version info
        self.create_version_file()
    
    def create_installation_readme(self):
        """Create installation README for distribution"""
        readme_content = f"""
# Card Sequence Validator - Installation Guide

## Version Information
- Version: {self.build_info['version']}
- Build Date: {self.build_info['build_date'][:10]}
- Build ID: {self.build_info['git_commit']}

## System Requirements
- Windows 10 (64-bit) or later
- 4 GB RAM minimum, 8 GB recommended
- 500 MB free disk space
- Network adapter for UDP communication
- Serial ports for COM communication (optional)

## Installation Instructions

### Quick Installation
1. Copy `CardSequenceValidator.exe` to your desired location
2. Copy `license.dat` to the same directory (if provided)
3. Run the executable - no additional installation required!

### First Run Setup
1. Run `CardSequenceValidator.exe` as Administrator (first time only)
2. Configure network settings in "Network & COM Setup"
3. Load your CPD files in "Job Management"
4. Start validation in "Scanner Control"

## File Locations
- Configuration: `%LOCALAPPDATA%\\YourCompany\\CardSequenceValidator\\`
- Logs: Exported to Desktop or chosen location
- Cache: Automatically managed

## Troubleshooting
- **Antivirus Warning**: Add executable to whitelist
- **Missing DLL**: Install Visual C++ Redistributable
- **Permission Error**: Run as Administrator first time
- **Network Issues**: Check firewall settings for UDP ports

## Support
For technical support, contact your system administrator or refer to the documentation.

---
Build Information:
- Python Version: {self.build_info['python_version']}
- Build Machine: {self.build_info['build_machine']}
- Git Commit: {self.build_info['git_commit']}
"""
        
        with open('dist/INSTALLATION.txt', 'w') as f:
            f.write(readme_content)
        
        print("✓ Created installation guide")
    
    def verify_build(self):
        """Verify the built executable"""
        print("🔍 Verifying build...")
        
        exe_path = 'dist/CardSequenceValidator.exe'
        
        if not os.path.exists(exe_path):
            print("❌ Executable not found!")
            return False
        
        # Check file size (should be reasonable)
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"  📏 Executable size: {file_size:.2f} MB")
        
        if file_size < 20 or file_size > 100:
            print(f"  ⚠️ Unusual file size: {file_size:.2f} MB")
        
        # Test executable launch (quick test)
        try:
            result = subprocess.run([exe_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("  ✓ Executable launches successfully")
            else:
                print("  ⚠️ Executable launch test failed")
        except subprocess.TimeoutExpired:
            print("  ⚠️ Executable launch test timed out")
        except Exception as e:
            print(f"  ⚠️ Could not test executable: {e}")
        
        return True
    
    def run_full_build(self):
        """Execute complete build process"""
        print("🚀 Starting Card Sequence Validator build process")
        print("=" * 60)
        
        try:
            # Step 1: Clean
            self.clean_build_directories()
            
            # Step 2: Build
            if not self.build_executable():
                return False
            
            # Step 3: Create build info
            self.create_build_info_file()
            
            # Step 4: Package
            self.create_distribution_package()
            
            # Step 5: Verify
            if not self.verify_build():
                return False
            
            print("=" * 60)
            print("🎉 Build completed successfully!")
            print(f"📁 Distribution files: dist/")
            print(f"🚀 Executable: dist/CardSequenceValidator.exe")
            print(f"📋 Build info: dist/build_info.json")
            
            return True
            
        except Exception as e:
            print(f"❌ Build process failed: {e}")
            return False

if __name__ == "__main__":
    builder = BuildManager()
    success = builder.run_full_build()
    sys.exit(0 if success else 1)
```

## Distribution Package Structure

### Package Contents
```
CardSequenceValidator_v3.1.0/
├── 📄 CardSequenceValidator.exe     # Main executable (40-50 MB)
├── 📄 license.dat                   # Software license (if required)
├── 📄 INSTALLATION.txt              # Installation instructions
├── 📄 README.md                     # Project overview
├── 📄 CHANGELOG.md                  # Version history
├── 📄 build_info.json               # Build metadata
├── 📁 docs/                         # Complete documentation
│   ├── 📄 README.md
│   ├── 📄 01-project-overview.md
│   ├── 📄 02-system-architecture.md
│   └── ... (all documentation files)
├── 📁 card_example/                 # Sample CPD files
│   ├── 📁 single_card/
│   ├── 📁 half_Card/
│   └── 📁 quarter_card/
└── 📄 output_formats.json           # Output format configuration
```

### Distribution Checklist
- [ ] Executable builds without errors
- [ ] All assets bundled correctly
- [ ] License file included (if required)
- [ ] Documentation complete and up-to-date
- [ ] Sample files included
- [ ] Installation instructions clear
- [ ] Version information accurate
- [ ] File sizes reasonable (<100MB total)

## Installation Procedures

### Standard Installation Process

#### Step 1: Pre-Installation Checks
```powershell
# Check Windows version
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion

# Check available disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace(GB)";Expression={[math]::Round($_.FreeSpace/1GB,2)}}

# Check .NET Framework (if required)
Get-ItemProperty "HKLM:SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" -Name Release
```

#### Step 2: Installation Script
```batch
@echo off
echo Card Sequence Validator Installation
echo ===================================

REM Create installation directory
set INSTALL_DIR=C:\CardSequenceValidator
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying application files...
copy CardSequenceValidator.exe "%INSTALL_DIR%\"
copy license.dat "%INSTALL_DIR%\" 2>nul
copy output_formats.json "%INSTALL_DIR%\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Card Sequence Validator.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\CardSequenceValidator.exe'; $Shortcut.Save()"

REM Configure firewall
echo Configuring Windows Firewall...
netsh advfirewall firewall add rule name="Card Validator UDP" dir=in action=allow protocol=UDP localport=5000-8000
netsh advfirewall firewall add rule name="Card Validator UDP Out" dir=out action=allow protocol=UDP localport=5000-8000

echo Installation completed successfully!
echo Run the application from: %INSTALL_DIR%\CardSequenceValidator.exe
pause
```

#### Step 3: First Run Configuration
```python
# first_run_setup.py - Embedded in application
def perform_first_run_setup():
    """Perform first-run setup tasks"""
    setup_tasks = [
        create_cache_directories,
        initialize_default_configuration,
        validate_system_requirements,
        test_network_interfaces,
        create_sample_configuration
    ]
    
    for task in setup_tasks:
        try:
            task()
            print(f"✓ {task.__name__}")
        except Exception as e:
            print(f"⚠️ {task.__name__} failed: {e}")

def create_cache_directories():
    """Create application cache directories"""
    cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
    os.makedirs(cache_dir, exist_ok=True)
    
    # Create subdirectories
    subdirs = ['logs', 'temp', 'backups']
    for subdir in subdirs:
        os.makedirs(os.path.join(cache_dir, subdir), exist_ok=True)
```

### Enterprise Deployment

#### Group Policy Deployment
```xml
<!-- GPO Software Installation Package -->
<SoftwareInstallation>
    <Package>
        <Name>Card Sequence Validator</Name>
        <Version>3.1.0</Version>
        <Publisher>YourCompany</Publisher>
        <InstallPath>\\server\software\CardSequenceValidator\</InstallPath>
        <Arguments>/S /D=C:\CardSequenceValidator</Arguments>
        <RequiredOS>Windows 10</RequiredOS>
    </Package>
</SoftwareInstallation>
```

#### SCCM Deployment Package
```powershell
# SCCM Application Deployment Script
$AppName = "Card Sequence Validator"
$Version = "3.1.0"
$InstallCommand = "CardSequenceValidator_Setup.exe /S"
$UninstallCommand = "C:\CardSequenceValidator\Uninstall.exe /S"
$DetectionMethod = "File", "C:\CardSequenceValidator\CardSequenceValidator.exe"

# Create SCCM Application
New-CMApplication -Name $AppName -Description "Card validation system for manufacturing" -SoftwareVersion $Version

# Add deployment type
Add-CMScriptDeploymentType -ApplicationName $AppName -DeploymentTypeName "Windows Installer" -InstallCommand $InstallCommand -UninstallCommand $UninstallCommand
```

#### Silent Installation
```batch
REM Silent installation script for enterprise deployment
@echo off
setlocal

REM Configuration
set INSTALL_DIR=%ProgramFiles%\CardSequenceValidator
set LOG_FILE=%TEMP%\CardValidator_Install.log

REM Create installation directory
mkdir "%INSTALL_DIR%" 2>nul

REM Copy files silently
echo %DATE% %TIME% - Starting installation >> "%LOG_FILE%"
xcopy /Y /Q CardSequenceValidator.exe "%INSTALL_DIR%\" >> "%LOG_FILE%" 2>&1
xcopy /Y /Q license.dat "%INSTALL_DIR%\" >> "%LOG_FILE%" 2>&1
xcopy /Y /Q output_formats.json "%INSTALL_DIR%\" >> "%LOG_FILE%" 2>&1

REM Configure firewall silently
netsh advfirewall firewall add rule name="Card Validator UDP In" dir=in action=allow protocol=UDP localport=5000-8000 >> "%LOG_FILE%" 2>&1
netsh advfirewall firewall add rule name="Card Validator UDP Out" dir=out action=allow protocol=UDP localport=5000-8000 >> "%LOG_FILE%" 2>&1

REM Create registry entries
reg add "HKLM\SOFTWARE\YourCompany\CardSequenceValidator" /v "InstallPath" /t REG_SZ /d "%INSTALL_DIR%" /f >> "%LOG_FILE%" 2>&1
reg add "HKLM\SOFTWARE\YourCompany\CardSequenceValidator" /v "Version" /t REG_SZ /d "3.1.0" /f >> "%LOG_FILE%" 2>&1

echo %DATE% %TIME% - Installation completed >> "%LOG_FILE%"
exit /b 0
```

## Environment-Specific Configurations

### Development Environment
```json
{
  "environment": "development",
  "debug_mode": true,
  "log_level": "DEBUG",
  "auto_save_interval": 10,
  "network_timeout": 30,
  "cache_location": "./dev_cache",
  "license_check": false
}
```

### Testing Environment
```json
{
  "environment": "testing",
  "debug_mode": true,
  "log_level": "INFO",
  "auto_save_interval": 30,
  "network_timeout": 15,
  "cache_location": "%TEMP%/CardValidator_Test",
  "license_check": true,
  "test_mode": true
}
```

### Production Environment
```json
{
  "environment": "production",
  "debug_mode": false,
  "log_level": "WARNING",
  "auto_save_interval": 60,
  "network_timeout": 10,
  "cache_location": "%LOCALAPPDATA%/YourCompany/CardSequenceValidator",
  "license_check": true,
  "performance_monitoring": true
}
```

## Update and Maintenance Procedures

### Application Update Process

#### Automatic Update Check
```python
class UpdateManager:
    def __init__(self):
        self.current_version = "3.1.0"
        self.update_server = "https://updates.yourcompany.com/cardvalidator"
        
    def check_for_updates(self):
        """Check for available updates"""
        try:
            response = requests.get(f"{self.update_server}/version.json", timeout=10)
            latest_info = response.json()
            
            latest_version = latest_info["version"]
            if self.is_newer_version(latest_version, self.current_version):
                return {
                    "update_available": True,
                    "latest_version": latest_version,
                    "download_url": latest_info["download_url"],
                    "release_notes": latest_info["release_notes"],
                    "required": latest_info.get("required", False)
                }
            
            return {"update_available": False}
            
        except Exception as e:
            return {"error": f"Update check failed: {e}"}
    
    def download_update(self, download_url, progress_callback=None):
        """Download update package"""
        try:
            response = requests.get(download_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            update_file = os.path.join(tempfile.gettempdir(), "CardValidator_Update.exe")
            
            with open(update_file, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return {"success": True, "file_path": update_file}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
```

#### Update Installation Process
```python
def install_update(update_file_path):
    """Install downloaded update"""
    try:
        # Backup current installation
        backup_dir = create_backup()
        
        # Prepare update script
        update_script = create_update_script(update_file_path, backup_dir)
        
        # Launch update script and exit application
        subprocess.Popen([update_script], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        # Exit current application
        sys.exit(0)
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_update_script(update_file, backup_dir):
    """Create update installation script"""
    script_content = f"""
@echo off
echo Updating Card Sequence Validator...

REM Wait for main application to close
timeout /t 3 /nobreak

REM Backup current version
if exist "CardSequenceValidator.exe" (
    copy "CardSequenceValidator.exe" "{backup_dir}\\CardSequenceValidator_backup.exe"
)

REM Install update
copy "{update_file}" "CardSequenceValidator.exe"

REM Clean up
del "{update_file}"

REM Restart application
start "" "CardSequenceValidator.exe"

REM Clean up script
del "%~f0"
"""
    
    script_path = "update_install.bat"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    return script_path
```

### Maintenance Procedures

#### Regular Maintenance Tasks
```python
class MaintenanceManager:
    def __init__(self):
        self.maintenance_tasks = [
            self.cleanup_old_logs,
            self.optimize_cache,
            self.check_disk_space,
            self.validate_configuration,
            self.update_network_settings
        ]
    
    def run_maintenance(self):
        """Run all maintenance tasks"""
        results = {}
        
        for task in self.maintenance_tasks:
            try:
                result = task()
                results[task.__name__] = result
            except Exception as e:
                results[task.__name__] = {"error": str(e)}
        
        return results
    
    def cleanup_old_logs(self):
        """Clean up old log files"""
        log_dir = os.path.join(os.path.expanduser("~"), "Desktop", "csv_logs")
        if not os.path.exists(log_dir):
            return {"status": "No log directory found"}
        
        cutoff_date = datetime.now() - timedelta(days=30)
        cleaned_files = 0
        
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    cleaned_files += 1
        
        return {"status": f"Cleaned {cleaned_files} old log files"}
    
    def optimize_cache(self):
        """Optimize cache file"""
        cache_file = get_unified_cache_file_path()
        if not os.path.exists(cache_file):
            return {"status": "No cache file found"}
        
        # Load, validate, and rewrite cache
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Remove old or invalid entries
            optimized_data = self.optimize_cache_data(cache_data)
            
            # Rewrite cache atomically
            atomic_write_cache(cache_file, optimized_data)
            
            return {"status": "Cache optimized successfully"}
            
        except Exception as e:
            return {"error": f"Cache optimization failed: {e}"}
```

## Rollback Procedures

### Version Rollback Process
```python
class RollbackManager:
    def __init__(self):
        self.backup_dir = os.path.join(os.path.dirname(sys.executable), "backups")
        
    def create_rollback_point(self, version_info):
        """Create rollback point before update"""
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"rollback_{version_info['version']}_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Backup executable and configuration
            shutil.copy2(sys.executable, os.path.join(backup_path, "CardSequenceValidator.exe"))
            
            # Backup configuration
            cache_file = get_unified_cache_file_path()
            if os.path.exists(cache_file):
                shutil.copy2(cache_file, os.path.join(backup_path, "app_cache_unified.json"))
            
            # Create rollback info
            rollback_info = {
                "version": version_info["version"],
                "backup_date": datetime.now().isoformat(),
                "executable_path": sys.executable,
                "cache_path": cache_file
            }
            
            with open(os.path.join(backup_path, "rollback_info.json"), 'w') as f:
                json.dump(rollback_info, f, indent=4)
            
            return {"success": True, "backup_path": backup_path}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def perform_rollback(self, backup_path):
        """Perform rollback to previous version"""
        try:
            # Validate backup
            rollback_info_path = os.path.join(backup_path, "rollback_info.json")
            if not os.path.exists(rollback_info_path):
                raise Exception("Invalid backup: rollback info not found")
            
            with open(rollback_info_path, 'r') as f:
                rollback_info = json.load(f)
            
            # Create rollback script
            script_content = f"""
@echo off
echo Rolling back Card Sequence Validator...

REM Wait for application to close
timeout /t 3 /nobreak

REM Restore executable
copy "{os.path.join(backup_path, 'CardSequenceValidator.exe')}" "{rollback_info['executable_path']}"

REM Restore configuration
copy "{os.path.join(backup_path, 'app_cache_unified.json')}" "{rollback_info['cache_path']}"

echo Rollback completed successfully!
echo Restarting application...

REM Restart application
start "" "{rollback_info['executable_path']}"

REM Clean up script
del "%~f0"
"""
            
            script_path = "rollback.bat"
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Execute rollback script
            subprocess.Popen([script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            return {"success": True, "message": "Rollback initiated"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
```

## Monitoring and Health Checks

### Deployment Health Monitoring
```python
class DeploymentMonitor:
    def __init__(self):
        self.health_checks = [
            self.check_application_startup,
            self.check_network_connectivity,
            self.check_file_permissions,
            self.check_license_validity,
            self.check_system_resources
        ]
    
    def run_health_check(self):
        """Run comprehensive health check"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "HEALTHY",
            "checks": {}
        }
        
        for check in self.health_checks:
            try:
                result = check()
                results["checks"][check.__name__] = result
                
                if result["status"] != "OK":
                    results["overall_status"] = "UNHEALTHY"
                    
            except Exception as e:
                results["checks"][check.__name__] = {
                    "status": "ERROR",
                    "message": str(e)
                }
                results["overall_status"] = "UNHEALTHY"
        
        return results
    
    def check_application_startup(self):
        """Check if application can start successfully"""
        try:
            # Test application launch with version check
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {"status": "OK", "message": "Application starts successfully"}
            else:
                return {"status": "ERROR", "message": "Application startup failed"}
                
        except subprocess.TimeoutExpired:
            return {"status": "ERROR", "message": "Application startup timeout"}
        except Exception as e:
            return {"status": "ERROR", "message": f"Startup test failed: {e}"}
```

---

*This comprehensive deployment guide provides detailed procedures for building, distributing, installing, and maintaining the Card Sequence Validator system in various environments.*