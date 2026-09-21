import subprocess
import hashlib
import json
import sys
import os
try:
    import winreg
except ImportError:
    winreg = None
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

# IMPORTANT: This public key must be replaced with the content of your public_key.pem file.
PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3ceSF2w0VpTGwSzRBvkj
+sTqDWQT5zfKwzL14zHLEHWrt4oh6MT9jSvkvYPa2h/DqzFapwRCyicCeR86PbtS
OPVntSv7eRCjWsBw7Edys06Nd+dA0UXwt9cF8ig2b8N9aXlmgdfi9P/4+Jl53WtU
CFQvbNXIpuaqS7kz+mnO6ouPrQbl7Sv/Q5pfXXWOyHrSt1o39XjgxVsn9ilQ6XJc
fH8Ar0VDOIhCliYG/jwImMgzKij4fsOSxqD+BVwg+G3th+Bl+6s5/x6mecCq/OGV
ciDlr3ucaE4UmhtB4tv/hCtbkKr5MssL6sgiIol3p+Tfic9K3bN6mRI90UwxwrxP
bQIDAQAB
-----END PUBLIC KEY-----"""

def get_machine_fingerprint():
    """
    Generates a unique machine fingerprint based on hardware serial numbers and system GUID.
    Uses modern Windows CIM/WMI queries and Registry to ensure compatibility across Windows 10/11.
    """
    try:
        # 1. Get Windows Machine GUID from Registry (fast, reliable, and unique)
        machine_guid = ""
        if winreg:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                    machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            except Exception:
                pass

        # 2. Query hardware details via PowerShell Get-CimInstance (replaces deprecated wmic)
        ps_script = (
            "$bb = (Get-CimInstance Win32_BaseBoard).SerialNumber; "
            "$cpu = (Get-CimInstance Win32_Processor | Select-Object -First 1).ProcessorId; "
            "$disk = (Get-CimInstance Win32_DiskDrive | Where-Object { $_.MediaType -like '*Fixed*' } | Select-Object -First 1).SerialNumber; "
            "@{bb=$bb; cpu=$cpu; disk=$disk} | ConvertTo-Json -Compress"
        )

        output = subprocess.check_output(
            ["powershell", "-NoProfile", "-Command", ps_script],
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        ).decode("utf-8", errors="ignore").strip()

        hardware_data = json.loads(output) if output else {}
        motherboard_serial = (hardware_data.get("bb") or "UNKNOWN_MB").strip()
        cpu_serial = (hardware_data.get("cpu") or "UNKNOWN_CPU").strip()
        disk_serial = (hardware_data.get("disk") or "UNKNOWN_DISK").strip()

        # Combine the identifiers and hash them
        combined_serials = f"{machine_guid}-{motherboard_serial}-{cpu_serial}-{disk_serial}"
        fingerprint = hashlib.sha256(combined_serials.encode("utf-8")).hexdigest()
        return fingerprint, None
    except Exception as e:
        return None, f"Error generating machine fingerprint: {e}"

def validate_license():
    """
    Validates the license file. If the license is valid, it returns (True, message, machine_id).
    If the license is invalid or not found, it returns (False, message, machine_id).
    """
    machine_fingerprint, error_msg = get_machine_fingerprint()
    if machine_fingerprint is None:
        return False, f"Could not generate a machine ID. {error_msg}", "N/A"

    try:
        # Search for license.dat in candidate locations
        license_path = None
        candidates = [
            'license.dat',
            os.path.join(os.path.abspath("."), 'license.dat'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'license.dat'),
            os.path.join(getattr(sys, '_MEIPASS', ''), 'license.dat'),
            os.path.join(os.path.dirname(sys.executable), 'license.dat')
        ]
        for c in candidates:
            if c and os.path.exists(c):
                license_path = c
                break

        if not license_path:
            return False, "License file not found.", machine_fingerprint

        with open(license_path, 'r') as f:
            file_content = f.read().strip()
            # DEBUG PRINT: print(f"DEBUG: Raw license file content: '{file_content}'")
            parts = file_content.split(':')
            if len(parts) != 2:
                raise ValueError(f"License file malformed: Expected 2 parts separated by ':', got {len(parts)}")
            license_fingerprint, signature_hex = parts
        
        signature = bytes.fromhex(signature_hex)

        public_key = serialization.load_pem_public_key(
            PUBLIC_KEY_PEM.encode()
        )

        # Verify the signature
        public_key.verify(
            signature,
            license_fingerprint.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        # Check if the fingerprint in the license matches the current machine's fingerprint
        if license_fingerprint == machine_fingerprint:
            return True, "License is valid.", machine_fingerprint
        else:
            return False, "License is for a different machine.", machine_fingerprint

    except InvalidSignature:
        return False, "Invalid license signature. The license file may be corrupt or tampered with.", machine_fingerprint
    except FileNotFoundError:
        return False, "License file not found.", machine_fingerprint
    except Exception as e:
        return False, f"An error occurred during license validation: {e}", machine_fingerprint
