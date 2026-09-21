# src/ui/widgets.py
from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout, QDialogButtonBox, QPushButton
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import QTimer, QTime, pyqtSignal, Qt
from datetime import datetime

class ClockWidget(QLabel):
    """A QLabel widget that displays the current date and time, updated continuously."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("clock_display") # Use a specific style for the clock

        # Set up a timer to update the clock every 100 milliseconds
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(100)

        # Initial call to display time immediately
        self.update_time()

    def update_time(self):
        """Fetches the current time and updates the label's text."""
        now = datetime.now()
        # Format: YYYY-MM-DD | HH:MM:SS.ms TZ
        # Slicing microseconds to get 3-digit milliseconds
        formatted_time = now.strftime("%Y-%m-%d | %H:%M:%S.%f")[:-3] + now.strftime(" %Z")
        self.setText(formatted_time)

class ScalableLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(1, 1)

    def paintEvent(self, event):
        if self.pixmap():
            pm = self.pixmap()
            if not pm.isNull():
                painter = QPainter(self)
                if painter.isActive():
                    try:
                        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                        target_rect = self.rect()
                        scaled_pixmap = pm.scaled(target_rect.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        x = (target_rect.width() - scaled_pixmap.width()) / 2
                        y = (target_rect.height() - scaled_pixmap.height()) / 2
                        painter.drawPixmap(int(x), int(y), scaled_pixmap)
                    finally:
                        painter.end()
        else:
            super().paintEvent(event)

# --- NEW DIALOG CLASS ---
class ApprovalDialog(QDialog):
    """A simple dialog to ask for user approval."""
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        # Safely inherit styles from parent if available
        if parent and hasattr(parent, 'styleSheet'):
            try:
                self.setStyleSheet(parent.styleSheet())
            except:
                pass  # Ignore style errors

        layout = QVBoxLayout(self)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setObjectName("subtitle")

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(message_label)
        layout.addWidget(button_box)

        # Set minimum size for better readability
        self.setMinimumWidth(400)
        self.setMinimumHeight(150)

class ScanPromptDialog(QDialog):
    """A non-modal dialog to prompt the user to scan a card."""
    cancelled = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scan Prompt")
        self.setWindowModality(Qt.WindowModality.NonModal)

        if parent and hasattr(parent, 'styleSheet'):
            try:
                self.setStyleSheet(parent.styleSheet())
            except: pass

        layout = QVBoxLayout(self)
        self.prompt_label = QLabel("Please scan a card to proceed.")
        self.prompt_label.setWordWrap(True)
        self.prompt_label.setObjectName("h2")
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("secondary")
        cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.prompt_label)
        layout.addWidget(cancel_button)
        self.setMinimumWidth(400)

    def update_prompt(self, message):
        self.prompt_label.setText(message)

    def reject(self):
        self.cancelled.emit()
        super().reject()


class PasswordDialog(QDialog):
    """A password dialog to protect access to sensitive windows."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Authentication Required")
        self.setModal(True)
        
        # Inherit styles from parent
        if parent and hasattr(parent, 'styleSheet'):
            try:
                self.setStyleSheet(parent.styleSheet())
            except:
                pass
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Network Configuration Access")
        title_label.setObjectName("h2")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Message
        message_label = QLabel("Please enter the password to access network configuration settings.")
        message_label.setWordWrap(True)
        message_label.setObjectName("subtitle")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        
        # Password input
        from PyQt6.QtWidgets import QLineEdit
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.returnPressed.connect(self.accept)
        layout.addWidget(self.password_input)
        
        # Error label (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setObjectName("subtitle")
        self.error_label.setStyleSheet("color: #f44336;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
    
    def get_password(self):
        """Return the entered password."""
        return self.password_input.text()
    
    def show_error(self, message):
        """Display an error message."""
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        self.password_input.clear()
        self.password_input.setFocus()
    
    def clear_error(self):
        """Clear the error message."""
        self.error_label.setVisible(False)
        self.error_label.setText("")