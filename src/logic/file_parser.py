# logic/file_parser.py
import os
from ..services.utilities import parse_cpd_cards
from ..card_types import CardType

def parse_file(file_path, card_type, rebatch_size=None):
    """
    Parse CPD file based on card type.
    card_type must be provided (no auto-detection).
    Returns (card_data, card_type)
    
    Args:
        file_path: Path to CPD file
        card_type: CardType enum (required)
        rebatch_size: Optional batch size for HALF/QUARTER cards
    """
    if card_type is None:
        raise ValueError("Card type must be specified. Auto-detection has been removed.")
    
    _, file_extension = os.path.splitext(file_path)
    
    if file_extension.lower() == '.cpd':
        card_data = parse_cpd_cards(file_path, card_type, rebatch_size)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Only CPD files are supported.")
    
    return card_data, card_type