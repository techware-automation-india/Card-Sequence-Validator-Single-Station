# src/ui/card_type_selector.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QRadioButton, QButtonGroup, QFrame, QLineEdit, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator

class CardTypeSelector(QDialog):
    """Dialog for selecting the card type at application startup"""
    
    def __init__(self, parent=None, total_cards=None):
        super().__init__(parent)
        self.setWindowTitle("Card Type Selection")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.selected_card_type = None
        self.rebatch_size = None
        self.total_cards = total_cards  # Total number of cards in the file
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Select Card Type")
        title.setObjectName("h1")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Choose the type of cards you will be validating in this session.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Radio button group
        self.button_group = QButtonGroup(self)
        self.button_group.buttonClicked.connect(self.on_card_type_changed)
        
        # ISO Card Option
        self.single_card_option = self.create_card_option(
            "ISO Card",
            "One ICCID per card",
            "single"
        )
        layout.addWidget(self.single_card_option)
        
        # Half Card Option (Default)
        self.half_card_option = self.create_card_option(
            "Half Card (Default)",
            "Two ICCIDs per card: Left and Right positions",
            "half"
        )
        layout.addWidget(self.half_card_option)
        
        # Quarter Card Option
        self.quarter_card_option = self.create_card_option(
            "Quarter Card",
            "Four ICCIDs per card: Bottom-Left, Top-Left, Top-Right, Bottom-Right",
            "quarter"
        )
        layout.addWidget(self.quarter_card_option)
        
        # Set default selection
        self.half_card_option.findChild(QRadioButton).setChecked(True)
        
        layout.addSpacing(10)
        
        # Rebatch Size Section (for HALF and QUARTER cards only)
        self.rebatch_frame = QFrame()
        self.rebatch_frame.setObjectName("accentPanel")
        rebatch_layout = QVBoxLayout(self.rebatch_frame)
        rebatch_layout.setContentsMargins(20, 15, 20, 15)
        rebatch_layout.setSpacing(10)
        
        rebatch_title = QLabel("Rebatch Size")
        rebatch_title.setStyleSheet("font-weight: bold; font-size: 14px; color: #FF9800;")
        rebatch_layout.addWidget(rebatch_title)
        
        # Rebatch size input
        input_layout = QHBoxLayout()
        input_label = QLabel("Batch Size: *")
        input_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        self.rebatch_input = QLineEdit()
        self.rebatch_input.setPlaceholderText("Enter batch size")
        
        # Set validator based on total cards if available
        if self.total_cards:
            self.rebatch_input.setValidator(QIntValidator(1, self.total_cards))
        else:
            self.rebatch_input.setValidator(QIntValidator(1, 999999))
        
        self.rebatch_input.setMinimumWidth(200)
        self.rebatch_input.textChanged.connect(self.validate_input)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.rebatch_input)
        input_layout.addStretch()
        
        rebatch_layout.addLayout(input_layout)
        
        # Error message label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f44336; font-weight: bold;")
        self.error_label.setVisible(False)
        rebatch_layout.addWidget(self.error_label)
        
        layout.addWidget(self.rebatch_frame)
        
        # Initially hide rebatch frame (will be shown if HALF or QUARTER is selected)
        self.rebatch_frame.setVisible(False)
        
        layout.addSpacing(10)
        
        # Buttons (create before calling on_card_type_changed)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.confirm_button = QPushButton("Continue")
        self.confirm_button.setObjectName("primary")
        self.confirm_button.setMinimumWidth(120)
        self.confirm_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.confirm_button)
        layout.addLayout(button_layout)
        
        # Update visibility based on initial selection (after button is created)
        self.on_card_type_changed()
        
    def on_card_type_changed(self):
        """Show/hide rebatch section based on selected card type"""
        checked_button = self.button_group.checkedButton()
        if checked_button:
            card_type = checked_button.property("card_type")
            # Show rebatch section only for HALF and QUARTER cards
            self.rebatch_frame.setVisible(card_type in ["half", "quarter"])
            # Clear error when card type changes
            self.error_label.setVisible(False)
            # Validate input state
            self.validate_input()
    
    def validate_input(self):
        """Validate rebatch input and enable/disable continue button"""
        checked_button = self.button_group.checkedButton()
        if checked_button:
            card_type = checked_button.property("card_type")
            
            # For HALF and QUARTER, rebatch size is required
            if card_type in ["half", "quarter"]:
                rebatch_text = self.rebatch_input.text().strip()
                if not rebatch_text:
                    self.confirm_button.setEnabled(False)
                    self.error_label.setText("⚠ Batch size is required")
                    self.error_label.setVisible(True)
                else:
                    try:
                        batch_size = int(rebatch_text)
                        if batch_size <= 0:
                            self.confirm_button.setEnabled(False)
                            self.error_label.setText("⚠ Batch size must be greater than 0")
                            self.error_label.setVisible(True)
                        elif self.total_cards and batch_size > self.total_cards:
                            self.confirm_button.setEnabled(False)
                            self.error_label.setText(f"⚠ Batch size cannot exceed total cards ({self.total_cards})")
                            self.error_label.setVisible(True)
                        else:
                            self.confirm_button.setEnabled(True)
                            self.error_label.setVisible(False)
                    except ValueError:
                        self.confirm_button.setEnabled(False)
                        self.error_label.setText("⚠ Please enter a valid number")
                        self.error_label.setVisible(True)
            else:
                # For SINGLE cards, no validation needed
                self.confirm_button.setEnabled(True)
                self.error_label.setVisible(False)
        
    def create_card_option(self, title, description, card_type):
        """Create a card option frame with radio button"""
        frame = QFrame()
        frame.setObjectName("panel")
        frame.setCursor(Qt.CursorShape.PointingHandCursor)
        
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(20, 15, 20, 15)
        
        # Radio button
        radio = QRadioButton()
        radio.setProperty("card_type", card_type)
        self.button_group.addButton(radio)
        frame_layout.addWidget(radio)
        
        # Text content
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setObjectName("h2")
        
        desc_label = QLabel(description)
        desc_label.setObjectName("subtitle")
        desc_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        
        frame_layout.addLayout(text_layout, 1)
        
        # Make frame clickable
        def on_frame_click(event, r=radio):
            r.setChecked(True)
            self.on_card_type_changed()
        
        frame.mousePressEvent = on_frame_click
        
        return frame
    
    def accept(self):
        """Store the selected card type and rebatch size, then close dialog"""
        checked_button = self.button_group.checkedButton()
        if checked_button:
            self.selected_card_type = checked_button.property("card_type")
            
            # Get rebatch size if applicable
            if self.selected_card_type in ["half", "quarter"]:
                rebatch_text = self.rebatch_input.text().strip()
                if not rebatch_text:
                    # Should not happen due to validation, but safety check
                    self.error_label.setText("⚠ Batch size is required")
                    self.error_label.setVisible(True)
                    return
                try:
                    self.rebatch_size = int(rebatch_text)
                    if self.rebatch_size <= 0:
                        self.error_label.setText("⚠ Batch size must be greater than 0")
                        self.error_label.setVisible(True)
                        return
                    if self.total_cards and self.rebatch_size > self.total_cards:
                        self.error_label.setText(f"⚠ Batch size cannot exceed total cards ({self.total_cards})")
                        self.error_label.setVisible(True)
                        return
                except ValueError:
                    self.error_label.setText("⚠ Please enter a valid number")
                    self.error_label.setVisible(True)
                    return
            else:
                self.rebatch_size = None
                
        super().accept()
    
    def get_selected_card_type(self):
        """Return the selected card type"""
        return self.selected_card_type
    
    def get_rebatch_size(self):
        """Return the rebatch size (None if not specified)"""
        return self.rebatch_size
