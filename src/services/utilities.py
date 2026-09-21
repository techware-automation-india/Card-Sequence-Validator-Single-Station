# services/utilities.py
import csv
import subprocess
import threading
import platform
from ..card_types import CardType

def ping_remote_ip_sync(remote_ip, timeout=5):
    """
    Ping a remote IP address synchronously and return the result.
    
    Args:
        remote_ip (str): IP address to ping
        timeout (int): Timeout in seconds for the ping operation (default: 5)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Determine OS and set appropriate ping command
        if platform.system().lower() == 'windows':
            # Windows: ping 1 time with 2 second timeout for faster response
            cmd = f'ping -n 1 -w 2000 {remote_ip}'
        else:
            # Linux/Mac: ping 1 time with 2 second timeout
            cmd = f'ping -c 1 -W 2 {remote_ip}'
        
        # Run ping command
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system().lower() == 'windows' else 0
        )
        
        # Wait for process to complete with timeout
        stdout, stderr = process.communicate(timeout=timeout)
        
        # Decode output for analysis
        stdout_text = stdout.decode('utf-8', errors='ignore') if stdout else ""
        stderr_text = stderr.decode('utf-8', errors='ignore') if stderr else ""
        
        # Check if ping was successful
        success = process.returncode == 0
        
        if success:
            message = f"Remote IP {remote_ip} is reachable (ping successful)"
        else:
            # Analyze the output to provide more specific error messages
            if "Request timed out" in stdout_text or "timeout" in stdout_text.lower():
                message = f"Remote IP {remote_ip} - Request timed out (device may be offline or blocking ping)"
            elif "Destination host unreachable" in stdout_text:
                message = f"Remote IP {remote_ip} - Destination host unreachable (routing issue)"
            elif "could not find host" in stdout_text.lower() or "ping request could not find host" in stdout_text.lower():
                message = f"Remote IP {remote_ip} - Host not found (DNS resolution failed)"
            elif "General failure" in stdout_text:
                message = f"Remote IP {remote_ip} - General failure (network adapter issue)"
            else:
                message = f"Remote IP {remote_ip} is not reachable (ping failed)"
        
        return success, message
        
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except:
            pass
        return False, f"Ping to {remote_ip} timed out after {timeout} seconds"
    except Exception as e:
        return False, f"Ping to {remote_ip} failed with error: {str(e)}"


def ping_remote_ip_async(remote_ip, callback=None):
    """
    Ping a remote IP address in a background thread.
    Opens command prompt, runs ping, and closes it automatically.
    
    Args:
        remote_ip (str): IP address to ping
        callback (callable): Optional callback function to call when ping completes
                           Receives (success: bool, message: str) as arguments
    """
    def ping_worker():
        try:
            # Determine OS and set appropriate ping command
            if platform.system().lower() == 'windows':
                # Windows: ping 4 times and close
                cmd = f'ping -n 4 {remote_ip}'
                # Use CREATE_NEW_CONSOLE to open in new command prompt window
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # Linux/Mac: ping 4 times
                cmd = f'ping -c 4 {remote_ip}'
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            # Wait for process to complete
            stdout, stderr = process.communicate(timeout=30)
            
            # Check if ping was successful
            success = process.returncode == 0
            
            if success:
                message = f"Ping to {remote_ip} successful"
            else:
                message = f"Ping to {remote_ip} failed - Device may be unreachable"
            
            # Call callback if provided
            if callback:
                callback(success, message)
                
        except subprocess.TimeoutExpired:
            process.kill()
            if callback:
                callback(False, f"Ping to {remote_ip} timed out")
    # Start ping in background thread
    thread = threading.Thread(target=ping_worker, daemon=True)
    thread.start()

def parse_cpd_cards(file_path, card_type=CardType.HALF, rebatch_size=None):
    """Parse CPD file based on card type with rebatch logic - using only ICCID
    
    Args:
        file_path: Path to CPD file
        card_type: CardType enum (SINGLE, HALF, QUARTER)
        rebatch_size: Optional batch size for HALF/QUARTER cards. If provided, file is divided
                     into batches of this size, then each batch is divided by 2 (HALF) or 4 (QUARTER)
    """
    card_data = []
    start_reading = False
    total_cards = 0
    header = None
    numcard_idx = None
    iccid_idx = None
    
    # First pass: validate format and count total cards
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Validate file is not empty
            if not lines:
                raise ValueError("CPD file is empty.")
            
            # Find and validate header
            header_found = False
            for line_num, line in enumerate(lines, start=1):
                line = line.strip()
                if line.startswith("NUMCARD"):
                    header_found = True
                    header = line.split(";")
                    
                    # Validate header is not empty
                    if not header or all(not h.strip() for h in header):
                        raise ValueError("CPD file has an empty or invalid header row.")
                    
                    # Check for NUMCARD column (required)
                    try:
                        numcard_idx = header.index("NUMCARD")
                    except ValueError:
                        raise ValueError("CPD file header must contain 'NUMCARD' column.")
                    
                    # Find ICCID column (required)
                    iccid_idx = next((i for i, h in enumerate(header) if "ICCID" in h), None)
                    if iccid_idx is None:
                        raise ValueError("CPD file header must contain 'ICCID' column.")
                    
                    start_reading = True
                    continue
                
                if start_reading and line and not line.startswith("NUMCARD"):
                    # Validate row has correct number of fields
                    parts = line.split(";")
                    if len(parts) != len(header):
                        raise ValueError(f"CPD file line {line_num} has {len(parts)} fields, but header has {len(header)} fields. All rows must match the header.")
                    total_cards += 1
            
            # Validate header was found
            if not header_found:
                raise ValueError("CPD file must contain a header row starting with 'NUMCARD'.")
            
            # Validate file has data rows
            if total_cards == 0:
                raise ValueError("CPD file has no data rows (only header).")
    
    except UnicodeDecodeError:
        raise ValueError("CPD file has invalid encoding. File must be UTF-8 encoded text.")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Error reading CPD file: {str(e)}")
    
    # Second pass: parse with positioning logic
    start_reading = False
    with open(file_path, mode='r', encoding='utf-8') as f:
        line_num = 0
        for line in f:
            line_num += 1
            line = line.strip()
            if line.startswith("NUMCARD"):
                start_reading = True
                continue
            
            if start_reading and line and not line.startswith("NUMCARD"):
                parts = line.split(";")
                numcard = parts[numcard_idx].strip()
                
                # Validate NUMCARD is not empty
                if not numcard:
                    raise ValueError(f"CPD file line {line_num}: NUMCARD is empty.")
                
                # Validate NUMCARD is numeric
                try:
                    card_index = int(numcard)
                except ValueError:
                    raise ValueError(f"CPD file line {line_num}: NUMCARD '{numcard}' is not a valid number.")
                
                # Get ICCID as the QR code
                qr_code = parts[iccid_idx].strip() if iccid_idx is not None else ""
                
                # Validate ICCID is not empty
                if not qr_code:
                    raise ValueError(f"CPD file line {line_num}: ICCID is empty for card {numcard}.")
                
                if card_type == CardType.SINGLE:
                    # Single card: use ICCID as the single QR
                    card_data.append((numcard, qr_code))
                    
                elif card_type == CardType.HALF:
                    # Half card with rebatch logic
                    if rebatch_size and rebatch_size > 0:
                        # Determine which batch this card belongs to
                        batch_num = (card_index - 1) // rebatch_size  # 0-indexed batch number
                        position_in_batch = ((card_index - 1) % rebatch_size) + 1  # 1-indexed position within batch
                        
                        # Calculate batch size (last batch may be smaller)
                        batch_start = batch_num * rebatch_size + 1
                        batch_end = min((batch_num + 1) * rebatch_size, total_cards)
                        current_batch_size = batch_end - batch_start + 1
                        
                        # Within each batch, divide by 2 for left/right
                        half_point = current_batch_size // 2
                        
                        if position_in_batch <= half_point:
                            # Left side of this batch
                            card_data.append((numcard, qr_code, "LEFT"))
                        else:
                            # Right side of this batch
                            corresponding_left = batch_start + (position_in_batch - half_point - 1)
                            card_data.append((str(corresponding_left), qr_code, "RIGHT"))
                    else:
                        # Original logic: divide entire file by 2
                        half_point = total_cards // 2
                        if card_index <= half_point:
                            card_data.append((numcard, qr_code, "LEFT"))
                        else:
                            corresponding_left = card_index - half_point
                            card_data.append((str(corresponding_left), qr_code, "RIGHT"))
                        
                elif card_type == CardType.QUARTER:
                    # Quarter card with rebatch logic
                    if rebatch_size and rebatch_size > 0:
                        # Determine which batch this card belongs to
                        batch_num = (card_index - 1) // rebatch_size
                        position_in_batch = ((card_index - 1) % rebatch_size) + 1
                        
                        # Calculate batch size (last batch may be smaller)
                        batch_start = batch_num * rebatch_size + 1
                        batch_end = min((batch_num + 1) * rebatch_size, total_cards)
                        current_batch_size = batch_end - batch_start + 1
                        
                        # Within each batch, divide by 4 for BL/TL/TR/BR
                        quarter_size = current_batch_size // 4
                        
                        if position_in_batch <= quarter_size:
                            position = "BL"
                            base_card = batch_start + (position_in_batch - 1)
                        elif position_in_batch <= 2 * quarter_size:
                            position = "TL"
                            base_card = batch_start + (position_in_batch - quarter_size - 1)
                        elif position_in_batch <= 3 * quarter_size:
                            position = "TR"
                            base_card = batch_start + (position_in_batch - 2 * quarter_size - 1)
                        else:
                            position = "BR"
                            base_card = batch_start + (position_in_batch - 3 * quarter_size - 1)
                        
                        card_data.append((str(base_card), qr_code, position))
                    else:
                        # Original logic: divide entire file by 4
                        quarter_size = total_cards // 4
                        if card_index <= quarter_size:
                            position = "BL"
                            base_card = card_index
                        elif card_index <= 2 * quarter_size:
                            position = "TL"
                            base_card = card_index - quarter_size
                        elif card_index <= 3 * quarter_size:
                            position = "TR"
                            base_card = card_index - 2 * quarter_size
                        else:
                            position = "BR"
                            base_card = card_index - 3 * quarter_size
                        
                        card_data.append((str(base_card), qr_code, position))
    
    # Post-process half and quarter cards to merge into single entries
    if card_type == CardType.HALF:
        merged_cards = {}
        for numcard, qr_code, position in card_data:
            if numcard not in merged_cards:
                merged_cards[numcard] = {"LEFT": "", "RIGHT": ""}
            merged_cards[numcard][position] = qr_code
        
        # Convert back to list format
        card_data = []
        for numcard in sorted(merged_cards.keys(), key=int):
            card = merged_cards[numcard]
            card_data.append((numcard, card["LEFT"], card["RIGHT"]))
    
    elif card_type == CardType.QUARTER:
        merged_cards = {}
        for numcard, qr_code, position in card_data:
            if numcard not in merged_cards:
                merged_cards[numcard] = {"BL": "", "TL": "", "TR": "", "BR": ""}
            merged_cards[numcard][position] = qr_code
        
        # Convert back to list format with new order: BL, TL, TR, BR
        card_data = []
        for numcard in sorted(merged_cards.keys(), key=int):
            card = merged_cards[numcard]
            card_data.append((numcard, card["BL"], card["TL"], card["TR"], card["BR"]))
    
    return card_data
