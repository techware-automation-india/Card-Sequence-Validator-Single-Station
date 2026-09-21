# src/card_types.py
from enum import Enum

class CardType(Enum):
    """Enum for different card types supported by the application"""
    SINGLE = "single"      # One QR code per card
    HALF = "half"          # Two QR codes per card (Left/Right)
    QUARTER = "quarter"    # Four QR codes per card (TL/TR/BL/BR)
    
    @staticmethod
    def get_qr_count(card_type):
        """Return the number of QR codes for a given card type"""
        counts = {
            CardType.SINGLE: 1,
            CardType.HALF: 2,
            CardType.QUARTER: 4
        }
        return counts.get(card_type, 2)
    
    @staticmethod
    def get_qr_labels(card_type):
        """Return the labels for QR codes based on card type - all using ICCID"""
        labels = {
            CardType.SINGLE: ["ICCID"],
            CardType.HALF: ["Left ICCID", "Right ICCID"],
            CardType.QUARTER: ["Bottom-Left ICCID", "Top-Left ICCID", "Top-Right ICCID", "Bottom-Right ICCID"]
        }
        return labels.get(card_type, labels[CardType.HALF])
    
    @staticmethod
    def get_scan_sides(card_type):
        """Return the scan side options for a given card type"""
        sides = {
            CardType.SINGLE: ["single"],
            CardType.HALF: ["left", "right"],
            CardType.QUARTER: ["bottom_left", "top_left", "top_right", "bottom_right"]
        }
        return sides.get(card_type, sides[CardType.HALF])
    
    @staticmethod
    def get_default_scan_side(card_type):
        """Return the default scan side for a given card type"""
        defaults = {
            CardType.SINGLE: "single",
            CardType.HALF: "left",
            CardType.QUARTER: "bottom_left"
        }
        return defaults.get(card_type, "left")
    
    @staticmethod
    def from_string(value):
        """Convert string to CardType enum"""
        for card_type in CardType:
            if card_type.value == value:
                return card_type
        return CardType.HALF  # Default
