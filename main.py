import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QLockFile, QDir
import os
import json

# Only import the necessary components to start the application
from src.app_state import AppState
from src.ui.main_application import HomePage
from src.ui.card_type_selector import CardTypeSelector
from src.card_types import CardType

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def check_single_instance():
    """
    Check if another instance of the application is already running.
    Returns (lock_file, is_locked) tuple.
    """
    # Use temp directory for lock file
    temp_dir = QDir.tempPath()
    lock_file_path = os.path.join(temp_dir, "CardSequenceValidatorSingleStation.lock")
    
    lock_file = QLockFile(lock_file_path)
    lock_file.setStaleLockTime(0)  # Don't consider any lock as stale
    
    # Try to acquire the lock
    if not lock_file.tryLock(100):  # Try for 100ms
        return lock_file, False
    
    return lock_file, True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("assets/Icon.png")))
    
    # Check for single instance
    lock_file, is_locked = check_single_instance()
    
    if not is_locked:
        # Another instance is already running
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Application Already Running")
        msg.setText("Card Sequence Validator Single Station is already running.")
        msg.setInformativeText("Only one instance of the application can run at a time.\n\nPlease use the existing window or close it before starting a new instance.")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        sys.exit(1)

    # Initialize single station AppState
    app_state = AppState(card_type=CardType.HALF)
    app_state.ping_remote_devices()

    # Create and show the main window, passing the AppState to it
    window = HomePage(app_state)
    window.showMaximized()

    exit_code = app.exec()
    
    # Release the lock when application exits
    lock_file.unlock()
    
    sys.exit(exit_code)