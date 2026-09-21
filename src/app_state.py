# src/app_state.py
import serial
import serial.tools.list_ports
import threading
import re
import json
import os
import sys
import time
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
from appdirs import user_data_dir
import winreg

from .ui.widgets import ApprovalDialog
import constants
from .logic.file_parser import parse_file
from .services.udp_reader import UDPReader
from .services.udp_writer import UDPWriter
from .card_types import CardType

APP_NAME = "CardSequenceValidator"
APP_AUTHOR = "Techware Automation"

APP_NAME = "CardSequenceValidator"
APP_AUTHOR = "Techware Automation"

_cache_lock = threading.RLock()  # RLock for thread-safe caching

def get_cache_file_path():
    """Get the cache file path for Single Station"""
    cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
    try:
        os.makedirs(cache_dir, exist_ok=True)
    except PermissionError:
        import tempfile
        cache_dir = os.path.join(tempfile.gettempdir(), APP_NAME)
        os.makedirs(cache_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create cache directory: {e}")
    
    return os.path.join(cache_dir, "app_cache_single.json")

def get_unified_cache_file_path():
    """Compatibility alias for get_cache_file_path"""
    return get_cache_file_path()

def atomic_write_cache(cache_file_path, cache_data):
    """Write cache atomically to prevent corruption on power loss.
    
    Uses temp file + rename pattern to ensure either old or new data exists,
    never partial/corrupted data.
    """
    temp_file_path = cache_file_path + ".tmp"
    try:
        # Write to temporary file
        with open(temp_file_path, 'w') as f:
            json.dump(cache_data, f, indent=4)
            f.flush()  # Flush Python buffer to OS
            os.fsync(f.fileno())  # Force OS to write to physical disk
        
        # Atomic rename (replaces old file with new one)
        # On Windows, this removes the old file and renames temp to final name
        if os.path.exists(cache_file_path):
            os.replace(temp_file_path, cache_file_path)
        else:
            os.rename(temp_file_path, cache_file_path)
        
        # Sync the directory to ensure rename is persisted (Windows-safe)
        try:
            dir_path = os.path.dirname(cache_file_path)
            if dir_path and os.path.exists(dir_path):
                dir_fd = os.open(dir_path, os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
        except (OSError, NotImplementedError):
            # Directory sync not supported on this OS/filesystem, skip it
            pass
    except Exception as e:
        # Clean up temp file if it exists
        try:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        except:
            pass
        raise e

def get_windows_theme():
    if sys.platform == 'win32' and sys.getwindowsversion().major < 10:
        return "light"
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        theme_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return "light" if theme_value == 1 else "dark"
    except Exception:
        return "dark"

class ComPortReader:
    """Serial COM port reader for receiving QR code data from scanners."""
    def __init__(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=0.1, callback=None, error_callback=None):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        self.callback = callback
        self.error_callback = error_callback
        self.running = False
        self.thread = None
        self.serial_instance = None
        self.paused = threading.Event()
        self.paused.set()

    def start_reading(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.read_loop, daemon=True)
        self.thread.start()

    def stop_reading(self):
        self.running = False
        self.resume()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        if self.serial_instance and self.serial_instance.is_open:
            try:
                self.serial_instance.close()
            except:
                pass

    def pause(self):
        self.paused.clear()

    def resume(self):
        if self.serial_instance:
            try:
                self.serial_instance.reset_input_buffer()
            except:
                pass
        self.paused.set()

    def read_loop(self):
        try:
            self.serial_instance = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.bytesize,
                parity=self.parity,
                stopbits=self.stopbits,
                timeout=self.timeout,
                inter_byte_timeout=0.05
            )
            if self.error_callback:
                self.error_callback(f"Connected to {self.port}", "green")

            while self.running:
                self.paused.wait()
                if not self.running:
                    break

                if self.serial_instance.in_waiting > 0:
                    raw_data = self.serial_instance.read(256)
                    decoded_data = raw_data.decode(errors='ignore').strip()
                    decoded_data = re.sub(r'[^\x20-\x7E]', '', decoded_data)
                    if decoded_data and self.callback:
                        self.callback(decoded_data)
        except serial.SerialException as e:
            if self.error_callback:
                self.error_callback(f"Error connecting to {self.port}: {e}", "red")
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"Unexpected error: {e}", "red")
        finally:
            self.running = False
            if self.error_callback and self.port:
                self.error_callback("Not Connected", "red")

class AppState(QObject):
    log_updated = pyqtSignal(list)
    log_cleared = pyqtSignal()
    state_changed = pyqtSignal()
    com_status_changed = pyqtSignal(str, str)
    output_com_status_changed = pyqtSignal(str, str)
    ondemand_scan_status_update = pyqtSignal(str, str)
    theme_changed = pyqtSignal(str)
    start_card_scan_complete = pyqtSignal(str, bool)
    card_type_changed = pyqtSignal(object)  # Emits CardType enum
    scan_completed = pyqtSignal()  # Emitted when scan is complete

    mismatch_found_in_sequence = pyqtSignal(str, int, int)
    card_count_update = pyqtSignal(str, str)

    def __init__(self, card_type=CardType.HALF):
        super().__init__()
        
        self.card_type = card_type
        self.main_port_reader = None
        self.ondemand_port_reader = None
        self.output_udp_writer = UDPWriter()

        # Instance tracking
        self.current_instance = 1

        # UDP Configuration (replaces COM port configuration)
        self.main_scanner_config = None  # {'local_ip': str, 'local_port': int, 'remote_ip': str, 'remote_port': int}
        self.ondemand_scanner_config = None
        self.output_config = None
        
        # Connectivity status tracking
        self.main_scanner_remote_reachable = None  # True/False/None (unknown)
        self.output_remote_reachable = None  # True/False/None (unknown)
        
        self.is_scanning = False
        self.output_formats = {}
        self.selected_output_format = ""
        self.scan_side = CardType.get_default_scan_side(card_type)
        self.selected_file_path = ""
        self.expected_cards = []
        
        # Dynamic QR code lookup dictionaries based on card type
        self.qr_to_index = {}  # Generic lookup: qr_code -> (index, position)
        self.numcard_to_qrs = {}
        
        self.current_card_index = 0
        self.scan_direction = "top_to_bottom"  # "top_to_bottom" or "bottom_to_top"
        self.start_card_has_been_scanned = False
        self.first_scan_received = True
        self.log_data = []
        self.start_card_code = None
        
        # Legacy serial settings (kept for backward compatibility, not used with UDP)
        self.baud_rate, self.data_bits, self.parity, self.stop_bits, self.timeout = 115200, 8, 'N', 1, 1
        self.current_theme = None

        # Auto-save configuration for power loss protection
        self.last_save_time = time.time()
        self.scans_since_save = 0
        self.auto_save_interval = 60  # Save every 1 minute (was 5 minutes)
        self.auto_save_batch_size = 100  # Save every 100 scans (was 1000)

        # On-demand scanning state machine
        self.is_waiting_for_start_card = False
        self.is_waiting_for_count_card_1 = False
        self.is_waiting_for_count_card_2 = False
        self.first_card_index = -1

        # Checksum configuration
        self.checksum_digits = 1  # Number of digits to strip from end (1-6), default 1
        
        # Rebatch size for HALF/QUARTER cards (None = use entire file)
        self.rebatch_size = None
        
        # Network configuration password (default: "admin123")
        self.network_config_password = "admin123"
        
        # Strict ping validation (if True, prevents connection to unreachable IPs)
        self.strict_ping_validation = False  # Default to False for flexibility

        self.load_output_formats()
        self.load_cache()

        if self.current_theme is None:
            self.current_theme = get_windows_theme()
        
        # Restore connections from cache
        if self.ondemand_scanner_config:
            config = self.ondemand_scanner_config
            # Check if it's a serial COM port or UDP configuration
            if 'port' in config:
                # Serial COM port configuration
                self.connect_ondemand_serial(
                    config.get('port'),
                    config.get('baudrate', 115200),
                    config.get('bytesize', 8),
                    config.get('parity', 'N'),
                    config.get('stopbits', 1),
                    config.get('timeout', 1)
                )
            elif 'local_ip' in config:
                # UDP configuration
                self.connect_ondemand_udp(
                    config.get('local_ip'), config.get('local_port'),
                    config.get('remote_ip'), config.get('remote_port')
                )
        
        if self.output_config:
            config = self.output_config
            self.connect_output_udp(
                config.get('local_ip'), config.get('local_port'),
                config.get('remote_ip'), config.get('remote_port')
            )

        # Emit state_changed after all initial configurations
        self.state_changed.emit()
        self.theme_changed.emit(self.current_theme)

    def load_cache(self):
        """Load cache from single station cache file"""
        with _cache_lock:
            try:
                cache_file = get_cache_file_path()
                
                if not os.path.exists(cache_file):
                    print(f"[CACHE] No single-station cache found at {cache_file}, checking for previous cache...")
                    self._migrate_old_cache()
                    return

                try:
                    file_size = os.path.getsize(cache_file)
                    if file_size == 0:
                        print("[CACHE] Cache file is empty, removing and starting fresh")
                        os.remove(cache_file)
                        return
                except Exception as e:
                    print(f"[CACHE] Error checking cache file size: {e}")

                with open(cache_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return
                    
                    try:
                        raw_cache = json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"[CACHE] Cache file is corrupted (JSON decode error): {e}")
                        os.remove(cache_file)
                        return
                    
                    # If legacy unified cache was loaded directly, extract head_a
                    if "head_a" in raw_cache:
                        cache = raw_cache.get("head_a", {})
                    else:
                        cache = raw_cache
                    
                    # Load configurations
                    self.main_scanner_config = cache.get('main_scanner_config')
                    self.ondemand_scanner_config = cache.get('ondemand_scanner_config')
                    self.output_config = cache.get('output_config')
                    
                    self.baud_rate = cache.get('baud_rate', 115200)
                    self.data_bits = cache.get('data_bits', 8)
                    self.parity = cache.get('parity', 'N')
                    self.stop_bits = cache.get('stop_bits', 1)
                    self.timeout = cache.get('timeout', 1)
                    
                    self.selected_output_format = cache.get('selected_output_format', "")
                    self.current_theme = cache.get('current_theme', "dark")
                    self.start_card_code = cache.get('start_card_code')
                    self.scan_direction = cache.get('scan_direction', 'top_to_bottom')
                    
                    card_type_str = cache.get('card_type', 'half')
                    try:
                        self.card_type = CardType(card_type_str)
                    except ValueError:
                        self.card_type = CardType.HALF
                    
                    self.selected_file_path = cache.get('selected_file_path')
                    if self.selected_file_path and not os.path.exists(self.selected_file_path):
                        self.selected_file_path = ""
                    
                    self.current_card_index = 0
                    self.start_card_has_been_scanned = False
                    self.scan_side = 'top_to_bottom'
                    self.expected_cards = []
                    self.qr_to_index = {}
                    self.numcard_to_qrs = {}
                    self.start_card_code = None
                    
                    self.log_data = cache.get('log_data', [])
                    
                    self.is_waiting_for_start_card = False
                    self.is_waiting_for_count_card_1 = False
                    self.is_waiting_for_count_card_2 = False
                    self.first_card_index = -1
                    
                    cached_checksum = cache.get('checksum_digits', 1)
                    self.checksum_digits = 1 if cached_checksum == 0 else cached_checksum
                    
                    self.rebatch_size = cache.get('rebatch_size', None)
                    self.network_config_password = cache.get('network_config_password', 'admin123')
                    
                    self.main_scanner_remote_reachable = cache.get('main_scanner_remote_reachable', None)
                    self.output_remote_reachable = cache.get('output_remote_reachable', None)
                    
                    if self.output_config:
                        config = self.output_config
                        try:
                            self.connect_output_udp(
                                config.get('local_ip'), config.get('local_port'),
                                config.get('remote_ip'), config.get('remote_port')
                            )
                        except Exception as udp_error:
                            print(f"Warning: Error connecting output UDP: {udp_error}")
                    
                    self.state_changed.emit()
            except (FileNotFoundError, json.JSONDecodeError):
                pass
            except Exception as e:
                print(f"Warning: Unexpected error loading cache: {e}")
    
    def ping_remote_devices(self):
        """Ping remote devices after loading configuration on startup and update reachability status"""
        from .services.utilities import ping_remote_ip_sync
        import threading
        
        def validate_in_background():
            """Run validation in background to avoid blocking startup"""
            # Validate Main Scanner
            if self.main_scanner_config:
                remote_ip = self.main_scanner_config.get('remote_ip')
                if remote_ip:
                    print(f"[Startup Validation] Checking Main Scanner: {remote_ip}")
                    success, msg = ping_remote_ip_sync(remote_ip, timeout=3)
                    self.main_scanner_remote_reachable = success
                    self.state_changed.emit()
            
            # Validate Output
            if self.output_config:
                remote_ip = self.output_config.get('remote_ip')
                if remote_ip:
                    print(f"[Startup Validation] Checking Output: {remote_ip}")
                    success, msg = ping_remote_ip_sync(remote_ip, timeout=3)
                    self.output_remote_reachable = success
                    self.state_changed.emit()
            
            print("[Startup Validation] Configuration validation complete")
        
        validation_thread = threading.Thread(target=validate_in_background, daemon=True)
        validation_thread.start()
    
    def _migrate_old_cache(self):
        """Migrate from old unified or instance-specific cache files to single station cache"""
        try:
            cache_dir = user_data_dir(APP_NAME, APP_AUTHOR)
            old_unified = os.path.join(cache_dir, "app_cache_unified.json")
            old_inst1 = os.path.join(cache_dir, "app_cache_instance_1.json")
            
            old_cache = None
            if os.path.exists(old_unified):
                with open(old_unified, 'r') as f:
                    data = json.load(f)
                    old_cache = data.get("head_a", data)
            elif os.path.exists(old_inst1):
                with open(old_inst1, 'r') as f:
                    old_cache = json.load(f)
            
            if old_cache:
                self.main_scanner_config = old_cache.get('main_scanner_config')
                self.ondemand_scanner_config = old_cache.get('ondemand_scanner_config')
                self.output_config = old_cache.get('output_config')
                self.selected_output_format = old_cache.get('selected_output_format', "")
                self.current_theme = old_cache.get('current_theme', "dark")
                self.scan_direction = old_cache.get('scan_direction', 'top_to_bottom')
                self.checksum_digits = old_cache.get('checksum_digits', 1)
                self.network_config_password = old_cache.get('network_config_password', 'admin123')
                self.save_cache()
                print("[CACHE] Migrated previous settings to single station cache")
        except Exception as e:
            print(f"Warning: Could not migrate old cache: {e}")

    def save_cache(self):
        """Save cache to single station cache file"""
        with _cache_lock:
            cache_data = {
                'card_type': self.card_type.value,
                'main_scanner_config': self.main_scanner_config,
                'ondemand_scanner_config': self.ondemand_scanner_config,
                'output_config': self.output_config,
                'baud_rate': self.baud_rate,
                'data_bits': self.data_bits,
                'parity': self.parity,
                'stop_bits': self.stop_bits,
                'timeout': self.timeout,
                'selected_output_format': self.selected_output_format,
                'selected_file_path': self.selected_file_path,
                'start_card_code': self.start_card_code,
                'scan_direction': self.scan_direction,
                'log_data': self.log_data,
                'current_theme': self.current_theme,
                'current_card_index': self.current_card_index,
                'start_card_has_been_scanned': self.start_card_has_been_scanned,
                'scan_side': self.scan_side,
                'expected_cards': self.expected_cards,
                'is_waiting_for_start_card': self.is_waiting_for_start_card,
                'is_waiting_for_count_card_1': self.is_waiting_for_count_card_1,
                'is_waiting_for_count_card_2': self.is_waiting_for_count_card_2,
                'first_card_index': self.first_card_index,
                'checksum_digits': self.checksum_digits,
                'rebatch_size': self.rebatch_size,
                'network_config_password': self.network_config_password,
                'main_scanner_remote_reachable': getattr(self, 'main_scanner_remote_reachable', None),
                'output_remote_reachable': getattr(self, 'output_remote_reachable', None),
            }
            
            cache_file_path = get_cache_file_path()
            
            try:
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        atomic_write_cache(cache_file_path, cache_data)
                        with open(cache_file_path, 'r') as verify_file:
                            json.load(verify_file)
                        print("[CACHE] Successfully saved single station cache")
                        break
                    except (PermissionError, OSError) as e:
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                        else:
                            print(f"[CACHE ERROR] Permission/OS error after {max_retries} attempts: {e}")
                            raise
                    except json.JSONDecodeError as e:
                        print(f"[CACHE ERROR] Cache file corrupted after write: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                        else:
                            raise
                    except Exception as e:
                        print(f"[CACHE ERROR] Unexpected error during save: {e}")
                        if attempt < max_retries - 1:
                            time.sleep(0.1)
                        else:
                            raise
            except Exception as e:
                print(f"Warning: Failed to save cache: {e}")

    def load_output_formats(self):
        try:
            with open(constants.OUTPUT_FORMATS_PATH, 'r') as f:
                self.output_formats = json.load(f)
            if self.output_formats and not self.selected_output_format:
                self.selected_output_format = list(self.output_formats.keys())[0]
        except (FileNotFoundError, json.JSONDecodeError):
            self.output_formats = {}

    def start_scanning(self):
        if not self.main_scanner_config or self.is_scanning:
            return
        
        config = self.main_scanner_config
        self.main_port_reader = UDPReader(
            local_ip=config['local_ip'],
            local_port=config['local_port'],
            remote_ip=config.get('remote_ip'),
            remote_port=config.get('remote_port'),
            callback=self.handle_main_scan,
            error_callback=lambda msg, color: self.com_status_changed.emit(msg, color)
        )
        self.is_scanning = True
        self.main_port_reader.start_reading()
        
        bind_msg = f"Listening on {config['local_ip']}:{config['local_port']}"
        self.com_status_changed.emit(bind_msg, "green")
        
        # Set start card on first scan if not already set
        if not self.start_card_has_been_scanned:
            self.first_scan_received = True
        
        self.state_changed.emit()

    def stop_scanning(self):
        if self.main_port_reader:
            self.main_port_reader.stop_reading()
            self.com_status_changed.emit("Not Set", "red")
        self.main_port_reader = None
        self.is_scanning = False
        self.state_changed.emit()

    def strip_checksum(self, code, use_ui_value=False):
        """
        Strip checksum digits from the end of a scanned code.
        
        Args:
            code: The scanned QR code string
            use_ui_value: If True, use checksum_digits - 1 (the actual UI value without secret increment)
                         If False, use checksum_digits as-is (includes secret +1 for main scanning)
            
        Returns:
            The code with checksum digits removed (if checksum_digits > 0)
        """
        # For on-demand operations, use the actual UI value (subtract the secret increment)
        digits_to_strip = max(0, self.checksum_digits - 1) if use_ui_value else self.checksum_digits
        
        if digits_to_strip > 0 and len(code) > digits_to_strip:
            return code[:-digits_to_strip]
        return code

    def handle_main_scan(self, scanned_code):
        log_entry = None
        
        try:
            # Strip checksum digits if configured
            scanned_code_without_checksum = self.strip_checksum(scanned_code)
            
            # Get scan side label for logging
            scan_side_labels = {
                "single": "Single",
                "left": "Left",
                "right": "Right",
                "top_left": "Top-Left",
                "top_right": "Top-Right",
                "bottom_left": "Bottom-Left",
                "bottom_right": "Bottom-Right"
            }
            scanned_side = scan_side_labels.get(self.scan_side, self.scan_side.replace('_', ' ').title())
            
            # Auto-save after each scan for power loss protection
            self.scans_since_save += 1
            current_time = time.time()
            
            # Save if batch size reached or interval elapsed
            if (self.scans_since_save >= self.auto_save_batch_size or 
                current_time - self.last_save_time >= self.auto_save_interval):
                self.save_cache()
                self.scans_since_save = 0
                self.last_save_time = current_time

            # Set start card on first scan
            if self.first_scan_received and not self.start_card_has_been_scanned:
                if scanned_code_without_checksum in self.qr_to_index:
                    found_index, position = self.qr_to_index[scanned_code_without_checksum]
                    
                    # Set scan side based on position and card type
                    if self.card_type == CardType.SINGLE:
                        self.scan_side = "single"
                    elif self.card_type == CardType.HALF:
                        self.scan_side = "left" if position == 0 else "right"
                    elif self.card_type == CardType.QUARTER:
                        # Position in tuple: 0=BL, 1=TL, 2=TR, 3=BR
                        scan_sides = ["bottom_left", "top_left", "top_right", "bottom_right"]
                        self.scan_side = scan_sides[position] if position < len(scan_sides) else "bottom_left"
                    
                    self.set_start_index(found_index)
                    self.start_card_has_been_scanned = True
                    self.start_card_code = scanned_code_without_checksum
                    self.first_scan_received = False
                    scanned_side = scan_side_labels.get(self.scan_side, self.scan_side.replace('_', ' ').title())
                    
                    # Check if this first scan completes the sequence (single card file)
                    if self.is_scan_complete():
                        # Log the scan first with LAST OK status
                        log_entry = self.add_log_entry(scanned_code_without_checksum, scanned_code_without_checksum, "LAST OK", scanned_side)
                        if log_entry:
                            self.log_updated.emit([log_entry])
                        self.send_output_signal("LAST OK")
                        # Don't auto-stop - let user manually stop scanning
                        self.state_changed.emit()
                        return
                else:
                    # Card not found in sequence, log as error (use trimmed code)
                    log_entry = self.add_log_entry(scanned_code_without_checksum, "N/A", "NOT IN SEQUENCE", scanned_side)
                    if log_entry:
                        self.log_updated.emit([log_entry])
                    self.state_changed.emit()
                    return

            if not self.expected_cards:
                log_entry = self.add_log_entry(scanned_code_without_checksum, "N/A", "NO FILE", scanned_side)
            elif self.is_scan_complete():
                log_entry = self.add_log_entry(scanned_code_without_checksum, "End of Sequence", "EXTRA SCAN", scanned_side)
            else:
                # Get the actual card index based on scan direction
                actual_card_index = self.get_current_expected_card_index()
                
                # Bounds check
                if actual_card_index < 0 or actual_card_index >= len(self.expected_cards):
                    log_entry = self.add_log_entry(scanned_code_without_checksum, "N/A", "INDEX ERROR", scanned_side)
                    if log_entry:
                        self.log_updated.emit([log_entry])
                    self.state_changed.emit()
                    return
                
                # Get expected QR based on scan side and card type
                card = self.expected_cards[actual_card_index]
                if self.card_type == CardType.SINGLE:
                    expected_qr = card[1] if len(card) > 1 else None
                elif self.card_type == CardType.HALF:
                    qr_position = 1 if self.scan_side == 'left' else 2
                    expected_qr = card[qr_position] if len(card) > qr_position else None
                elif self.card_type == CardType.QUARTER:
                    position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
                    qr_position = position_map.get(self.scan_side, 1)
                    expected_qr = card[qr_position] if len(card) > qr_position else None
                else:
                    expected_qr = None
                
                if expected_qr is None:
                    log_entry = self.add_log_entry(scanned_code_without_checksum, "N/A", "DATA ERROR", scanned_side)
                    if log_entry:
                        self.log_updated.emit([log_entry])
                    self.state_changed.emit()
                    return
                
                if scanned_code_without_checksum == expected_qr:
                    # Check if this will be the last card after incrementing
                    will_be_complete = (self.current_card_index + 1) >= len(self.expected_cards)
                    status = "LAST OK" if will_be_complete else "OK"
                    
                    log_entry = self.add_log_entry(scanned_code_without_checksum, expected_qr, status, scanned_side)
                    self.send_output_signal(status)
                    self.increment_card_index()
                    
                    # Don't auto-stop - let user manually stop scanning
                else:
                    # Check if scanned code exists elsewhere in sequence
                    if scanned_code_without_checksum in self.qr_to_index:
                        future_match_index, scanned_position = self.qr_to_index[scanned_code_without_checksum]
                        
                        # Determine the expected position based on card type and scan side
                        if self.card_type == CardType.SINGLE:
                            expected_position = 0  # Only one position for single cards
                        elif self.card_type == CardType.HALF:
                            expected_position = 0 if self.scan_side == 'left' else 1
                        elif self.card_type == CardType.QUARTER:
                            position_map = {"bottom_left": 0, "top_left": 1, "top_right": 2, "bottom_right": 3}
                            expected_position = position_map.get(self.scan_side, 0)
                        else:
                            expected_position = 0
                        
                        # Check if the scanned QR is from the correct side
                        if scanned_position != expected_position:
                            # Wrong side scanned - just mark as NOT OK (simplified status)
                            status = "NOT OK"
                            log_entry = self.add_log_entry(scanned_code_without_checksum, expected_qr, status, scanned_side)
                            self.send_output_signal("NOT OK")
                        else:
                            # Correct side, check if it's ahead in sequence
                            # Compare actual array indices for both directions
                            if self.scan_direction == "bottom_to_top":
                                # For bottom-to-top, check if future card comes BEFORE current in array
                                if future_match_index < actual_card_index:
                                    # Calculate number of cards to skip (in scan order)
                                    num_skipped = actual_card_index - future_match_index
                                    # CRITICAL FIX: Pass the ARRAY INDEX, not scan position
                                    # The resolution method will handle the conversion
                                    self.pause_scanning()
                                    self.mismatch_found_in_sequence.emit(scanned_code_without_checksum, num_skipped, future_match_index)
                                else:
                                    status = "NOT OK"
                                    log_entry = self.add_log_entry(scanned_code_without_checksum, expected_qr, status, scanned_side)
                                    self.send_output_signal(status)
                            else:
                                # Top-to-bottom logic: check if future card comes AFTER current
                                if future_match_index > actual_card_index:
                                    num_skipped = future_match_index - actual_card_index
                                    self.pause_scanning()
                                    self.mismatch_found_in_sequence.emit(scanned_code_without_checksum, num_skipped, future_match_index)
                                else:
                                    status = "NOT OK"
                                    log_entry = self.add_log_entry(scanned_code_without_checksum, expected_qr, status, scanned_side)
                                    self.send_output_signal(status)
                    else:
                        status = "NOT OK"
                        log_entry = self.add_log_entry(scanned_code_without_checksum, expected_qr, status, scanned_side)
                        self.send_output_signal(status)
            
            if log_entry:
                self.log_updated.emit([log_entry])
            self.state_changed.emit()
        except Exception as e:
            print(f"Critical error in handle_main_scan: {e}")
            import traceback
            traceback.print_exc()
            # Log the error
            try:
                log_entry = self.add_log_entry(scanned_code if 'scanned_code' in locals() else "UNKNOWN", "N/A", "SCAN ERROR", "N/A")
                if log_entry:
                    self.log_updated.emit([log_entry])
            except:
                pass
            self.state_changed.emit()

    def connect_ondemand_udp(self, local_ip, local_port, remote_ip=None, remote_port=None):
        """Connect on-demand scanner via UDP"""
        if self.ondemand_port_reader:
            self.ondemand_port_reader.stop_reading()
        
        if not local_ip or not local_port:
            self.ondemand_scanner_config = None
            self.ondemand_port_reader = None
            self.ondemand_scan_status_update.emit("Not Connected", "red")
            return

        self.ondemand_port_reader = UDPReader(
            local_ip=local_ip,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
            callback=self.handle_ondemand_scan,
            error_callback=lambda msg, color: self.ondemand_scan_status_update.emit(msg, color)
        )
        
        self.ondemand_scanner_config = {
            'local_ip': local_ip,
            'local_port': local_port,
            'remote_ip': remote_ip,
            'remote_port': remote_port
        }
        
        self.ondemand_port_reader.start_reading()
        self.ondemand_scan_status_update.emit(f"Connected to {local_ip}:{local_port}", "green")
        self.state_changed.emit()
        self.save_cache()

    def connect_ondemand_serial(self, port, baudrate=115200, bytesize=8, parity='N', stopbits=1, timeout=1):
        """Connect on-demand scanner via serial COM port"""
        if self.ondemand_port_reader:
            self.ondemand_port_reader.stop_reading()
        
        if not port:
            self.start_card_scan_port = None
            self.ondemand_port_reader = None
            self.ondemand_scanner_config = None
            self.ondemand_scan_status_update.emit("Not Connected", "red")
            self.state_changed.emit()
            self.save_cache()
            return

        # Update app_state attributes with the new settings
        self.baud_rate = baudrate
        self.data_bits = bytesize
        self.parity = parity
        self.stop_bits = stopbits
        self.timeout = timeout

        self.ondemand_port_reader = ComPortReader(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            callback=self.handle_ondemand_scan,
            error_callback=lambda msg, color: self.ondemand_scan_status_update.emit(msg, color)
        )
        
        self.start_card_scan_port = port
        
        # Save configuration to cache
        self.ondemand_scanner_config = {
            'port': port,
            'baudrate': baudrate,
            'bytesize': bytesize,
            'parity': parity,
            'stopbits': stopbits,
            'timeout': timeout
        }
        
        self.ondemand_port_reader.start_reading()
        self.ondemand_scan_status_update.emit(f"Connected to {port}", "green")
        self.state_changed.emit()
        self.save_cache()

    def connect_output_udp(self, local_ip, local_port, remote_ip, remote_port):
        """Connect output via UDP"""
        if self.output_udp_writer.is_connected:
            self.output_udp_writer.disconnect()
        
        if not remote_ip or not remote_port:
            self.output_config = None
            self.output_com_status_changed.emit("Not Connected", "red")
            self.state_changed.emit()
            self.save_cache()
            return
        
        success, message = self.output_udp_writer.connect(
            local_ip=local_ip or "0.0.0.0",
            local_port=local_port or 0,
            remote_ip=remote_ip,
            remote_port=remote_port
        )
        
        if success:
            self.output_config = {
                'local_ip': local_ip,
                'local_port': local_port,
                'remote_ip': remote_ip,
                'remote_port': remote_port
            }
            self.output_com_status_changed.emit(message, "green")
        else:
            self.output_config = None
            self.output_com_status_changed.emit(message, "red")
        
        self.state_changed.emit()
        self.save_cache()

    def disconnect_all_ports(self):
        self.stop_scanning()
        if self.ondemand_port_reader:
            self.ondemand_port_reader.stop_reading()
            self.ondemand_port_reader = None
            self.ondemand_scan_status_update.emit("Not Connected", "red")
        if self.output_udp_writer.is_connected:
            self.output_udp_writer.disconnect()
            self.output_com_status_changed.emit("Not Connected", "red")
        
        self.main_scanner_config = None
        self.ondemand_scanner_config = None
        self.output_config = None
        self.state_changed.emit()
        self.save_cache()

    def get_timestamp(self):
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    def add_log_entry(self, scanned_code, expected_code, status, scanned_side="N/A"):
        log_entry = {
            "timestamp": self.get_timestamp(),
            "scanned_code": scanned_code,
            "expected_code": expected_code,
            "status": status,
            "scanned_side": scanned_side,
            "instance": self.current_instance
        }
        self.log_data.append(log_entry)
        return log_entry

    def pause_scanning(self):
        if self.main_port_reader:
            self.main_port_reader.pause()

    def resume_scanning(self):
        if self.main_port_reader:
            self.main_port_reader.resume()

    def load_file(self, file_path, card_type=None, rebatch_size=None):
        """Load file with manually specified card type (no auto-detection)
        
        Args:
            file_path: Path to CPD file
            card_type: CardType enum (required)
            rebatch_size: Optional batch size for HALF/QUARTER cards
        """
        if card_type is None:
            return False, "Card type must be selected manually. Please choose Single, Half, or Quarter card type."
        
        try:
            # Store rebatch size for this file load
            self.rebatch_size = rebatch_size
            
            # Parse file with specified card type and rebatch size
            self.expected_cards, _ = parse_file(file_path, card_type, rebatch_size)
            
            # Update card type
            old_card_type = self.card_type
            self.card_type = card_type
            
            # Reset scan side to default for new card type
            self.scan_side = CardType.get_default_scan_side(self.card_type)
            
            # Emit signal if card type changed
            if old_card_type != self.card_type:
                self.card_type_changed.emit(self.card_type)
            
            # Build QR lookup dictionaries based on card type
            self.qr_to_index = {}
            self.numcard_to_qrs = {}
            
            for i, card in enumerate(self.expected_cards):
                numcard = card[0]
                qr_codes = card[1:]  # All QR codes after numcard
                
                # Map each QR code to its index and position
                for pos, qr_code in enumerate(qr_codes):
                    self.qr_to_index[qr_code] = (i, pos)
                
                # Map numcard to all its QR codes
                self.numcard_to_qrs[numcard] = qr_codes
            
            self.selected_file_path = file_path
            self.current_card_index = 0
            self.start_card_has_been_scanned = False
            self.first_scan_received = True

            if self.start_card_code:
                is_valid = self.start_card_code in self.qr_to_index
                if is_valid:
                    found_index, _ = self.qr_to_index[self.start_card_code]
                    self.set_start_index(found_index)
                    self.start_card_has_been_scanned = True
                else:
                    self.start_card_code = None
            
            self.state_changed.emit()
            
            # Get card type name for user feedback
            card_type_names = {
                CardType.SINGLE: "ISO Card",
                CardType.HALF: "Half Card",
                CardType.QUARTER: "Quarter Card"
            }
            card_type_name = card_type_names.get(self.card_type, "Unknown")
            
            return True, f"Loaded {len(self.expected_cards)} cards as {card_type_name} type."
        except Exception as e:
            self.selected_file_path = ""
            self.expected_cards = []
            self.qr_to_index = {}
            self.numcard_to_qrs = {}
            self.state_changed.emit()
            return False, f"Error loading file: {e}"

    def restore_scan_state_from_logs(self):
        """Restore scan state from existing logs to continue from last position"""
        if not self.log_data or not self.expected_cards:
            return
        
        # Find the last successfully scanned card index
        last_ok_index = -1
        for log_entry in reversed(self.log_data):
            status = log_entry.get("status", "")
            expected_code = log_entry.get("expected_code", "")
            
            # Look for successful scans (OK, OK (JUMPED), LAST OK, or LAST OK (JUMPED))
            if status in ("OK", "OK (JUMPED)", "LAST OK", "LAST OK (JUMPED)") and expected_code:
                # Find this card's index in expected_cards
                if expected_code in self.qr_to_index:
                    card_index, _ = self.qr_to_index[expected_code]
                    last_ok_index = card_index
                    break
        
        # Set current index to continue from next card after last successful scan
        if last_ok_index >= 0:
            # Move to next card
            next_index = last_ok_index + 1
            if next_index < len(self.expected_cards):
                self.current_card_index = next_index
                self.start_card_has_been_scanned = True
                self.first_scan_received = False
            else:
                # All cards were scanned, start from beginning
                self.current_card_index = 0
                self.start_card_has_been_scanned = False
                self.first_scan_received = True
        else:
            # No successful scans found, start from beginning
            self.current_card_index = 0
            self.start_card_has_been_scanned = False
            self.first_scan_received = True
        
        self.state_changed.emit()

    def clear_file(self):
        self.selected_file_path = ""
        self.expected_cards = []
        self.qr_to_index = {}
        self.numcard_to_qrs = {}
        self.current_card_index = 0
        self.start_card_code = None
        self.start_card_has_been_scanned = False
        self.first_scan_received = True
        self.state_changed.emit()
        self.save_cache()

    def set_start_index(self, index):
        """Set the start card index based on scan direction"""
        if 0 <= index < len(self.expected_cards):
            # For top-to-bottom: current_card_index = array_index
            # For bottom-to-top: current_card_index = scan_position (total - 1 - array_index)
            if self.scan_direction == "bottom_to_top":
                self.current_card_index = len(self.expected_cards) - 1 - index
            else:
                self.current_card_index = index
            
            # For bottom-to-top, convert array index to scan position
            if self.scan_direction == "bottom_to_top":
                # If we found card at array index 75 in a 100-card file,
                # the scan position should be 24 (100 - 1 - 75)
                self.current_card_index = len(self.expected_cards) - 1 - index
            else:
                # For top-to-bottom, scan position = array index
                self.current_card_index = index
            self.first_scan_received = True
            self.state_changed.emit()

    def clear_logs(self):
        """Clear logs and reset scanning state to treat file as fresh"""
        self.log_data = []
        
        # Reset scanning state
        self.current_card_index = 0
        self.start_card_has_been_scanned = False
        self.first_scan_received = True
        self.start_card_code = None
        
        # Reset on-demand scanning state
        self.is_waiting_for_start_card = False
        self.is_waiting_for_count_card_1 = False
        self.is_waiting_for_count_card_2 = False
        self.first_card_index = -1
        
        self.log_cleared.emit()
        self.state_changed.emit()
        self.save_cache()

    def set_theme(self, theme_name):
        self.current_theme = theme_name
        self.save_cache()
        self.theme_changed.emit(theme_name)

    def scan_and_get_card_details(self):
        if not self.ondemand_port_reader:
            QMessageBox.warning(None, "Configuration Error", "The 'On-Demand Scanner Port' must be configured in COM Port Setup before this action can be performed.")
            return
        if not self.expected_cards:
            QMessageBox.warning(None, "File Error", "A job file must be loaded before scanning card details.")
            return
        self.is_waiting_for_start_card = True
        self.ondemand_scan_status_update.emit("active", "Scan a card to view its details...")

    def start_card_counting(self):
        if not self.ondemand_port_reader:
            QMessageBox.warning(None, "Configuration Error", "The 'On-Demand Scanner Port' must be configured in COM Port Setup before this action can be performed.")
            return
        if not self.expected_cards:
            QMessageBox.warning(None, "File Error", "A job file must be loaded before counting cards.")
            return
        
        self.is_waiting_for_count_card_1 = True
        self.card_count_update.emit('clear', '')
        self.ondemand_scan_status_update.emit("active", "Scan the FIRST card...")

    def _reset_ondemand_scan_state(self):
        self.is_waiting_for_start_card = False
        self.is_waiting_for_count_card_1 = False
        self.is_waiting_for_count_card_2 = False
        self.first_card_index = -1
        self.card_count_update.emit('clear', '')
        self.ondemand_scan_status_update.emit("", "Scan cancelled. Click a button to start.")

    def cancel_card_details_scan(self):
        self.is_waiting_for_start_card = False
        self._reset_ondemand_scan_state()

    def cancel_count_card_range_scan(self):
        self.is_waiting_for_count_card_1 = False
        self.is_waiting_for_count_card_2 = False
        self.first_card_index = -1
        self._reset_ondemand_scan_state()

    def handle_ondemand_scan(self, scanned_code):
        # Strip checksum digits using UI value (without secret increment)
        scanned_code = self.strip_checksum(scanned_code, use_ui_value=True)
        
        # Auto-save on-demand scan state
        self.scans_since_save += 1
        current_time = time.time()
        
        if (self.scans_since_save >= self.auto_save_batch_size or 
            current_time - self.last_save_time >= self.auto_save_interval):
            self.save_cache()
            self.scans_since_save = 0
            self.last_save_time = current_time
        
        if self.is_waiting_for_start_card:
            self.process_start_card_scan(scanned_code)
        elif self.is_waiting_for_count_card_1:
            self.process_count_card_1(scanned_code)
        elif self.is_waiting_for_count_card_2:
            self.process_count_card_2(scanned_code)

    def process_start_card_scan(self, scanned_code):
        self.is_waiting_for_start_card = False
        try:
            if scanned_code in self.qr_to_index:
                found_index, _ = self.qr_to_index[scanned_code]
                card = self.expected_cards[found_index]
                card_num = card[0]
                qr_codes = card[1:]  # All QR codes after numcard
                
                # Build details string based on card type
                qr_labels = CardType.get_qr_labels(self.card_type)
                details = f"Card Number: {card_num}\n"
                
                # Safely iterate through QR codes and labels
                for i, label in enumerate(qr_labels):
                    if i < len(qr_codes):
                        details += f"{label}: {qr_codes[i]}\n"
                    else:
                        details += f"{label}: N/A\n"
                
                details += f"Position: {found_index + 1} of {len(self.expected_cards)}"
                self.start_card_scan_complete.emit(details, True)
                self.ondemand_scan_status_update.emit("", "Scan complete.")  # Reset UI state
            else:
                self.start_card_scan_complete.emit(f"Scanned card {scanned_code} not found in file.", False)
                self.ondemand_scan_status_update.emit("", "Scan complete.")
        except Exception as e:
            error_msg = f"Error processing card details: {str(e)}"
            self.start_card_scan_complete.emit(error_msg, False)
            self.ondemand_scan_status_update.emit("", "Error occurred.")
        finally:
            self.state_changed.emit()

    def process_count_card_1(self, scanned_code):
        self.is_waiting_for_count_card_1 = False
        scanned_index = -1
        
        if scanned_code in self.qr_to_index:
            scanned_index, _ = self.qr_to_index[scanned_code]

        if scanned_index == -1:
            self.card_count_update.emit('error', f"First card '{scanned_code}' not found.")
            self.ondemand_scan_status_update.emit("", "Error. Try again.")
        else:
            self.first_card_index = scanned_index
            self.card_count_update.emit('first_card', scanned_code)
            self.is_waiting_for_count_card_2 = True
            self.ondemand_scan_status_update.emit("active", "Scan the LAST card...")

    def process_count_card_2(self, scanned_code):
        self.is_waiting_for_count_card_2 = False
        scanned_index = -1
        
        if scanned_code in self.qr_to_index:
            scanned_index, _ = self.qr_to_index[scanned_code]

        if scanned_index == -1:
            self.card_count_update.emit('error', f"Last card '{scanned_code}' not found.")
            self.ondemand_scan_status_update.emit("", "Error. Try again.")
        else:
            self.card_count_update.emit('last_card', scanned_code)
            # Calculate range regardless of order (first or last can be scanned first)
            start_index = min(self.first_card_index, scanned_index)
            end_index = max(self.first_card_index, scanned_index)
            count = end_index - start_index + 1
            self.card_count_update.emit('total', str(count))
            self.ondemand_scan_status_update.emit("", f"Successfully counted {count} cards.")
        
        self.first_card_index = -1

    def get_current_expected_card_index(self):
        """Get the current card index based on scan direction"""
        if self.scan_direction == "bottom_to_top":
            # For bottom-to-top, start from the end and work backwards
            return len(self.expected_cards) - 1 - self.current_card_index
        else:
            # For top-to-bottom, use normal indexing
            return self.current_card_index
    
    def increment_card_index(self):
        """Increment card index (same for both directions)"""
        self.current_card_index += 1
    
    def is_scan_complete(self):
        """Check if scanning is complete"""
        return self.current_card_index >= len(self.expected_cards)
    
    def get_scan_direction_description(self):
        """Get user-friendly description of current scan direction"""
        if self.scan_direction == "bottom_to_top":
            return "Bottom → Top (Last card first)"
        else:
            return "Top → Bottom (First card first)"

    def send_output_signal(self, status):
        if not self.output_udp_writer.is_connected:
            return
        
        # Get card type key for output format lookup
        card_type_key = self.card_type.value  # "single", "half", or "quarter"
        
        # Get the format for this card type and status
        format_config = self.output_formats.get(self.selected_output_format, {})
        card_type_config = format_config.get(card_type_key, {})
        output_signal = card_type_config.get(status)
        
        if output_signal:
            # Send as ASCII text string (not binary)
            self.output_udp_writer.send(output_signal, as_binary_int=False)

    def resolve_mismatch(self, scanned_code, approved, future_index):
        thread = threading.Thread(target=self._perform_mismatch_resolution, args=(scanned_code, approved, future_index))
        thread.daemon = True
        thread.start()

    def _perform_mismatch_resolution(self, scanned_code, approved, future_index):
        # Get the actual card index based on scan direction
        actual_card_index = self.get_current_expected_card_index()
        
        # Get expected QR based on card type and scan side
        if self.card_type == CardType.SINGLE:
            qr_position = 1
        elif self.card_type == CardType.HALF:
            qr_position = 1 if self.scan_side == 'left' else 2
        elif self.card_type == CardType.QUARTER:
            position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
            qr_position = position_map.get(self.scan_side, 1)
        
        expected_qr = self.expected_cards[actual_card_index][qr_position]
        
        # Get scan side label
        scan_side_labels = {
            "single": "Single",
            "left": "Left",
            "right": "Right",
            "top_left": "Top-Left",
            "top_right": "Top-Right",
            "bottom_left": "Bottom-Left",
            "bottom_right": "Bottom-Right"
        }
        scanned_side = scan_side_labels.get(self.scan_side, self.scan_side.replace('_', ' ').title())
        log_entries = []

        if approved and future_index != -1:
            # Handle skipping based on scan direction
            if self.scan_direction == "bottom_to_top":
                # For bottom-to-top: future_index is the ARRAY INDEX of the scanned card
                # We need to convert it to scan position for proper handling
                actual_future_index = future_index  # This is already the array index
                
                # Debug output
                print(f"[DEBUG] Bottom-to-top skip:")
                print(f"  current_card_index (scan position): {self.current_card_index}")
                print(f"  actual_card_index (array index): {actual_card_index}")
                print(f"  future_index (array index): {future_index}")
                print(f"  total cards: {len(self.expected_cards)}")
                
                # Skip cards from current array position down to future array position (exclusive)
                # LOGIC: Same as top-to-bottom - include current expected, exclude jumped-to
                # ORDER: Descending (natural bottom-to-top order)
                # Example: current=90, future=80 -> skip 90,89,88,87,86,85,84,83,82,81 (10 cards descending)
                if actual_card_index > actual_future_index:
                    # Generate skipped entries in DESCENDING order (natural scan direction)
                    # range(90, 80, -1) = [90, 89, 88, 87, 86, 85, 84, 83, 82, 81]
                    # This matches top-to-bottom logic: range(start, end) includes start, excludes end
                    for i in range(actual_card_index, actual_future_index, -1):
                        if i >= 0 and i < len(self.expected_cards):  # Bounds check
                            skipped_qr = self.expected_cards[i][qr_position]
                            log_entry = self.add_log_entry("MISSING", skipped_qr, "SKIPPED", scanned_side)
                            log_entries.append(log_entry)
                            print(f"  [SKIPPED] Card at array index {i}: {skipped_qr}")
                
                expected_jumped_qr = self.expected_cards[actual_future_index][qr_position]
                
                # Check if this jump will complete the sequence
                # For bottom-to-top, we're complete when we've scanned all cards from end to beginning
                future_scan_position = len(self.expected_cards) - 1 - actual_future_index
                will_be_complete = (future_scan_position + 1) >= len(self.expected_cards)
                status = "LAST OK (JUMPED)" if will_be_complete else "OK (JUMPED)"
                
                log_entry = self.add_log_entry(scanned_code, expected_jumped_qr, status, scanned_side)
                log_entries.append(log_entry)
                self.send_output_signal(status)
                
                # CRITICAL FIX: Set current_card_index to the NEXT scan position after the jumped card
                # For bottom-to-top: 
                #   - We just scanned card at array index actual_future_index
                #   - That's scan position (len - 1 - actual_future_index)
                #   - Next scan position is (len - 1 - actual_future_index) + 1
                #   - Which equals (len - actual_future_index)
                self.current_card_index = len(self.expected_cards) - actual_future_index
                
                print(f"  new current_card_index (scan position): {self.current_card_index}")
                print(f"  next expected array index: {self.get_current_expected_card_index()}")
                
                # Resume scanning after successful jump
                self.resume_scanning()
                
                # Don't auto-stop - let user manually stop scanning
                self.log_updated.emit(log_entries)
                self.state_changed.emit()
                return
            else:
                # Top-to-bottom: future_index is already array index
                # Skip cards from current array position up to future array position
                for i in range(actual_card_index, future_index):
                    skipped_qr = self.expected_cards[i][qr_position]
                    log_entry = self.add_log_entry("MISSING", skipped_qr, "SKIPPED", scanned_side)
                    log_entries.append(log_entry)
                
                expected_jumped_qr = self.expected_cards[future_index][qr_position]
                
                # Check if this jump will complete the sequence
                will_be_complete = (future_index + 1) >= len(self.expected_cards)
                status = "LAST OK (JUMPED)" if will_be_complete else "OK (JUMPED)"
                
                log_entry = self.add_log_entry(scanned_code, expected_jumped_qr, status, scanned_side)
                log_entries.append(log_entry)
                self.send_output_signal(status)
                # Set current_card_index to scan position after the jumped card
                # For top-to-bottom: array index equals scan position
                self.current_card_index = future_index + 1
                
                # Resume scanning after successful jump
                self.resume_scanning()
                
                # Don't auto-stop - let user manually stop scanning
                self.log_updated.emit(log_entries)
                self.state_changed.emit()
                return
        else:
            # User cancelled the jump
            log_entry = self.add_log_entry(scanned_code, expected_qr, "NOT OK", scanned_side)
            log_entries.append(log_entry)
            self.send_output_signal("NOT OK")
            # Resume scanning only when jump is cancelled
            self.resume_scanning()
        
        # Don't extend log_data again since add_log_entry already added entries
        self.log_updated.emit(log_entries)
        self.state_changed.emit()