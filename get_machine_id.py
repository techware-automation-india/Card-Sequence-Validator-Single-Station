import hashlib
import json
import subprocess
import tkinter as tk
from tkinter import messagebox
import winreg

def get_machine_fingerprint():
    """
    Generates a unique machine fingerprint based on hardware serial numbers and system GUID.
    Uses modern Windows CIM/WMI queries and Registry to ensure compatibility across Windows 10/11.
    """
    try:
        # 1. Get Windows Machine GUID from Registry (fast, reliable, and unique)
        machine_guid = ""
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

def copy_to_clipboard(root, text):
    """Copies the given text to the system clipboard."""
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Copied", "Machine ID copied to clipboard!")

def main():
    """Main function to create and run the GUI."""
    machine_id, error = get_machine_fingerprint()

    if not machine_id:
        # Hide root window during error popup
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Could not generate Machine ID.\n\nDetails: {error}")
        root.destroy()
        return

    # --- GUI Setup ---
    root = tk.Tk()
    root.title("Machine ID Generator")
    root.geometry("520x160")
    root.resizable(False, False)

    label_info = tk.Label(root, text="Please copy this ID and send it to the software vendor:", wraplength=480)
    label_info.pack(pady=(12, 6))

    # Use an Entry widget to make text selectable
    id_entry = tk.Entry(root, font=('Courier', 10), width=66, relief='solid', justify='center')
    id_entry.insert(0, machine_id)
    id_entry.config(state='readonly')  # Make it non-editable
    id_entry.pack(pady=5, padx=10)

    copy_button = tk.Button(root, text="Copy ID to Clipboard", command=lambda: copy_to_clipboard(root, machine_id))
    copy_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()

