"""
Build script for creating executable using PyInstaller
Run this script to build the Card Sequence Validator executable
"""

import os
import sys
import subprocess
import shutil

def clean_build_folders():
    """Remove old build folders"""
    print("Cleaning old build folders...")
    folders_to_remove = ['build', 'dist']
    for folder in folders_to_remove:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f"  Removed: {folder}")
            except PermissionError:
                print(f"  Warning: Could not remove {folder} (permission denied)")
            except Exception as e:
                print(f"  Warning: Could not remove {folder}: {e}")
    
    # Remove .spec file if exists
    spec_file = "CardSequenceValidator.spec"
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"  Removed: {spec_file}")
        except Exception as e:
            print(f"  Warning: Could not remove {spec_file}: {e}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n" + "="*60)
    print("Building Card Sequence Validator Executable")
    print("="*60 + "\n")
    
    # PyInstaller command - use Python module execution
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--name=CardSequenceValidator',
        '--onefile',                    # Single executable file
        '--windowed',                   # No console window (GUI only)
        '--icon=assets/Icon.png',       # Application icon
        
        # Add data files
        '--add-data=assets;assets',
        '--add-data=card_example;card_example',
        '--add-data=output_formats.json;.',
        
        # Hidden imports (if needed)
        '--hidden-import=PyQt6',
        '--hidden-import=serial',
        '--hidden-import=appdirs',
        '--hidden-import=cryptography',
        
        # Exclude unnecessary modules to reduce size
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=pandas',
        '--exclude-module=scipy',
        '--exclude-module=PIL',
        
        # Main entry point
        'main.py'
    ]
    
    print("Running PyInstaller with the following command:")
    print(" ".join(cmd))
    print("\nThis may take a few minutes...\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        print("\n" + "="*60)
        print("✓ Build completed successfully!")
        print("="*60)
        print(f"\nExecutable location: dist\\CardSequenceValidator.exe")
        print(f"File size: {os.path.getsize('dist/CardSequenceValidator.exe') / (1024*1024):.2f} MB")
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "="*60)
        print("✗ Build failed!")
        print("="*60)
        print(f"\nError: {e}")
        print(f"\nOutput: {e.stdout}")
        print(f"\nError output: {e.stderr}")
        return False

def create_installer_info():
    """Create a README for the installer"""
    readme_content = """
# Card Sequence Validator - Executable

## Installation Instructions

1. Copy `CardSequenceValidator.exe` to your desired location
2. Run the executable - no installation required!

## First Run

On first run, the application will:
- Create configuration folders in: `C:\\Users\\<YourName>\\AppData\\Local\\YourCompany\\CardSequenceValidator\\`
- Create separate folders for Head A (instance_1) and Head B (instance_2)
- Load default settings

## System Requirements

- Windows 10 or later
- Network connection (for UDP communication)
- Serial ports (for on-demand scanners)

## File Locations

### Configuration Files
- Head A: `AppData\\Local\\YourCompany\\CardSequenceValidator\\instance_1\\app_cache.json`
- Head B: `AppData\\Local\\YourCompany\\CardSequenceValidator\\instance_2\\app_cache.json`

### Log Files
Logs are stored in memory and can be exported to CSV from the File Management window.

## Troubleshooting

### Antivirus Warning
Some antivirus software may flag the executable as suspicious. This is a false positive.
To resolve:
1. Add the executable to your antivirus whitelist
2. Or run the Python version directly

### Missing DLL Errors
If you get DLL errors, install:
- Microsoft Visual C++ Redistributable (latest version)
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

### License Issues
If you get a license error:
1. Ensure `license.dat` is in the same folder as the executable
2. Contact support for a valid license

## Support

For issues or questions, contact your system administrator.
"""
    
    with open('dist/README.txt', 'w') as f:
        f.write(readme_content)
    print("\n✓ Created README.txt in dist folder")

def main():
    """Main build process"""
    print("\n" + "="*60)
    print("Card Sequence Validator - Build Script")
    print("="*60 + "\n")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found!")
        print("\nInstalling PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
        print("✓ PyInstaller installed")
    
    # Clean old builds
    clean_build_folders()
    
    # Build executable
    if build_executable():
        create_installer_info()
        print("\n" + "="*60)
        print("Build Process Complete!")
        print("="*60)
        print("\nNext steps:")
        print("1. Test the executable: dist\\CardSequenceValidator.exe")
        print("2. Copy license.dat to the dist folder (if needed)")
        print("3. Distribute the dist folder to users")
        print("\n")
    else:
        print("\nBuild failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
