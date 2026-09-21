# styles.py

DARK_THEME_STYLESHEET = """
/* ---- Main Window & General Widgets ---- */
QMainWindow, QDialog {
    background-color: #21252b; /* Darker background */
    color: #e0e0e0;
    font-family: Segoe UI, Arial, sans-serif;
}

QWidget {
    color: #e0e0e0;
    font-family: Segoe UI, Arial, sans-serif;
    background-color: #21252b; /* Darker background */
}

/* ---- Scroll Area Fix ---- */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollArea > QWidget > QWidget {
    background-color: #21252b; /* Darker background */
}


/* ---- Frames and Panels ---- */
QFrame#panel, QFrame#section {
    background-color: #282c34; /* Darker panel color */
    border-radius: 8px;
    border: 1px solid #3c424e;
}

QFrame#accentPanel {
    background-color: #3c424e; /* Darker accent panel */
    border-radius: 8px;
}

/* ---- Labels ---- */
QLabel#h1 {
    font-size: 22px; /* Slightly smaller than mainTitle */
    font-weight: bold;
    color: #ffffff;
    background-color: transparent;
}
QLabel#mainTitle {
    font-size: 36px; /* Larger title */
    font-weight: bold;
    color: #ffffff;
    background-color: transparent;
}
QLabel#h2 {
    font-size: 16px;
    font-weight: bold;
    color: #e0e0e0;
    background-color: transparent;
}
QLabel#subtitle {
    font-size: 13px; /* Slightly smaller than mainSubtitle */
    color: #a0a0a0;
    background-color: transparent;
}
QLabel#mainSubtitle {
    font-size: 18px; /* Larger subtitle */
    color: #a0a0a0;
    background-color: transparent;
}
QLabel#accent {
    font-size: 18px;
    color: #00aaff;
    font-weight: bold;
    background-color: transparent;
}
QLabel {
    background-color: transparent;
}
QLabel#clock_display {
    font-size: 18px;
    font-weight: bold;
    color: #00aaff;
    background-color: transparent;
}

/* ---- Buttons ---- */
QPushButton {
    border: 2px solid transparent;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}

/* Primary Button Style */
QPushButton#primary {
    background-color: #00aaff;
    color: #ffffff;
    border: 2px solid #0088cc;
}
QPushButton#primary:hover {
    background-color: #33bbff;
    border: 2px solid #00aaff;
}
QPushButton#primary:pressed {
    background-color: #0088cc;
    border: 2px solid #006699;
}
QPushButton#primary:disabled {
    background-color: #4a5160;
    color: #808080;
    border: 2px solid #3c424e;
}

/* Secondary Button Style */
QPushButton#secondary {
    background-color: #555c6b;
    color: #e0e0e0;
    border: 2px solid #444a57;
}
QPushButton#secondary:hover {
    background-color: #666e7f;
    border: 2px solid #555c6b;
}
QPushButton#secondary:pressed {
    background-color: #444a57;
    border: 2px solid #353b48;
}
QPushButton#secondary:disabled {
    background-color: #353b48;
    color: #6a6a6a;
    border: 2px solid #2c313c;
}

/* Theme Toggle Button Styles */
QPushButton#dark_theme_toggle {
    background-color: #00aaff; /* Blue for dark theme toggle */
    color: #ffffff;
    border: 2px solid #0088cc;
}
QPushButton#dark_theme_toggle:hover {
    background-color: #33bbff;
    border: 2px solid #00aaff;
}
QPushButton#dark_theme_toggle:pressed {
    background-color: #0088cc;
    border: 2px solid #006699;
}

QPushButton#light_theme_toggle {
    background-color: #007bff; /* Blue for light theme toggle */
    color: #ffffff;
    border: 2px solid #0056b3;
}
QPushButton#light_theme_toggle:hover {
    background-color: #0056b3;
    border: 2px solid #004085;
}
QPushButton#light_theme_toggle:pressed {
    background-color: #004085;
    border: 2px solid #003366;
}

/* Instance Toggle Button Styles - Dark Theme */
QPushButton#instanceToggle {
    background-color: #555c6b;
    color: #e0e0e0;
    border: 2px solid #555c6b;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}
QPushButton#instanceToggle:hover {
    background-color: #666e7f;
    border: 2px solid #666e7f;
}
QPushButton#instanceToggle:checked {
    background-color: #00aaff;
    color: #ffffff;
    border: 2px solid #00aaff;
}
QPushButton#instanceToggle:checked:hover {
    background-color: #33bbff;
    border: 2px solid #33bbff;
}

/* ---- Inputs & Dropdowns ---- */
QComboBox, QLineEdit {
    background-color: #2c313c;
    border: 1px solid #4a5160;
    border-radius: 4px;
    padding: 8px;
    color: #e0e0e0;
}
QComboBox:focus, QLineEdit:focus {
    border: 1px solid #00aaff;
}
QComboBox::drop-down {
    border: none;
}

/* ---- Tables & Logs ---- */
QTableWidget {
    background-color: #2c313c;
    alternate-background-color: #313640; /* BUG FIX 4: Added for contrast */
    border: 1px solid #4a5160;
    border-radius: 4px;
    gridline-color: #4a5160;
    selection-background-color: #00aaff; /* Selection background */
    selection-color: #ffffff; /* Selection text color */
}
QTableWidget::item {
    padding: 8px;
    border: none;
}
QTableWidget::item:hover {
    background-color: #3c424e; /* Hover background */
    color: #ffffff; /* Hover text color */
}
QTableWidget::item:selected {
    background-color: #00aaff; /* Selected background */
    color: #ffffff; /* Selected text color */
}
QTableWidget::item:selected:hover {
    background-color: #33bbff; /* Selected + hover background */
    color: #ffffff; /* Selected + hover text color */
}
QHeaderView::section {
    background-color: #353b48;
    color: #e0e0e0;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #4a5160;
    font-weight: bold;
}
QTextEdit {
    background-color: #252932;
    border: 1px solid #4a5160;
    border-radius: 4px;
    color: #00aaff;
    font-family: Consolas, monospace;
}

/* ---- Status Labels ---- */
QLabel#statusOK, QLabel#statusReady {
    background-color: #27ae60;
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}
QLabel#statusError, QLabel#statusDisconnected {
    background-color: #c0392b;
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}
QLabel#statusWarning, QLabel#statusIdle {
    background-color: #f39c12;
    color: #2c313c;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}
QLabel#statusNeutral {
    background-color: #4a5160;
    color: #e0e0e0;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

/* ---- Message Box Buttons ---- */
QMessageBox {
    background-color: #21252b;
}
QMessageBox QLabel {
    color: #e0e0e0;
}
QMessageBox QPushButton {
    background-color: #555c6b;
    color: #e0e0e0;
    border: 2px solid #444a57;
    border-radius: 6px;
    padding: 12px 30px;
    font-size: 13px;
    font-weight: bold;
    min-width: 180px;
    min-height: 40px;
    max-height: none;
}
QMessageBox QPushButton:hover {
    background-color: #666e7f;
    border: 2px solid #555c6b;
}
QMessageBox QPushButton:pressed {
    background-color: #444a57;
    border: 2px solid #353b48;
}
QMessageBox QPushButton:default {
    background-color: #00aaff;
    color: #ffffff;
    border: 2px solid #0088cc;
}
QMessageBox QPushButton:default:hover {
    background-color: #33bbff;
    border: 2px solid #00aaff;
}
QMessageBox QPushButton:default:pressed {
    background-color: #0088cc;
    border: 2px solid #006699;
}

/* ---- Radio Buttons (for dialogs) ---- */
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #4a5160;
    background-color: #2c313c;
}
QRadioButton::indicator:hover {
    border: 2px solid #00aaff;
}
QRadioButton::indicator:checked {
    background-color: #00aaff;
    border: 2px solid #0088cc;
    background-image: radial-gradient(circle, #ffffff 0%, #ffffff 35%, transparent 40%, transparent 100%);
}
QRadioButton::indicator:checked:hover {
    background-color: #33bbff;
    border: 2px solid #00aaff;
}
"""

LIGHT_THEME_STYLESHEET = """
/* ---- Main Window & General Widgets ---- */
QMainWindow, QDialog {
    background-color: #f0f0f0; /* Lighter background */
    color: #333333;
    font-family: Segoe UI, Arial, sans-serif;
}

QWidget {
    color: #333333;
    font-family: Segoe UI, Arial, sans-serif;
    background-color: #f0f0f0; /* Lighter background */
}

/* ---- Scroll Area Fix ---- */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollArea > QWidget > QWidget {
    background-color: #f0f0f0; /* Lighter background */
}


/* ---- Frames and Panels ---- */
QFrame#panel, QFrame#section {
    background-color: #ffffff; /* Lighter panel color */
    border-radius: 8px;
    border: 1px solid #cccccc;
}

QFrame#accentPanel {
    background-color: #e0e0e0; /* Lighter accent panel */
    border-radius: 8px;
}

/* ---- Labels ---- */
QLabel#h1 {
    font-size: 22px;
    font-weight: bold;
    color: #333333;
    background-color: transparent;
}
QLabel#mainTitle {
    font-size: 36px;
    font-weight: bold;
    color: #333333;
    background-color: transparent;
}
QLabel#h2 {
    font-size: 16px;
    font-weight: bold;
    color: #333333;
    background-color: transparent;
}
QLabel#subtitle {
    font-size: 13px;
    color: #666666;
    background-color: transparent;
}
QLabel#mainSubtitle {
    font-size: 18px;
    color: #666666;
    background-color: transparent;
}
QLabel#accent {
    font-size: 18px;
    color: #007bff; /* Blue accent for light theme */
    font-weight: bold;
    background-color: transparent;
}
QLabel {
    background-color: transparent;
}
QLabel#clock_display {
    font-size: 18px;
    font-weight: bold;
    color: #007bff;
    background-color: transparent;
}

/* ---- Buttons ---- */
QPushButton {
    border: 2px solid transparent;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}

/* Primary Button Style */
QPushButton#primary {
    background-color: #007bff; /* Blue primary */
    color: #ffffff;
    border: 2px solid #0056b3;
}
QPushButton#primary:hover {
    background-color: #0056b3;
    border: 2px solid #004085;
}
QPushButton#primary:pressed {
    background-color: #004085;
    border: 2px solid #003366;
}
QPushButton#primary:disabled {
    background-color: #cccccc;
    color: #999999;
    border: 2px solid #b0b0b0;
}

/* Secondary Button Style */
QPushButton#secondary {
    background-color: #6c757d; /* Gray secondary */
    color: #ffffff;
    border: 2px solid #5a6268;
}
QPushButton#secondary:hover {
    background-color: #5a6268;
    border: 2px solid #494f54;
}
QPushButton#secondary:pressed {
    background-color: #494f54;
    border: 2px solid #3d4349;
}
QPushButton#secondary:disabled {
    background-color: #e0e0e0;
    color: #b0b0b0;
    border: 2px solid #cccccc;
}

/* Theme Toggle Button Styles */
QPushButton#dark_theme_toggle {
    background-color: #00aaff; /* Blue for dark theme toggle */
    color: #ffffff;
    border: 2px solid #0088cc;
}
QPushButton#dark_theme_toggle:hover {
    background-color: #33bbff;
    border: 2px solid #00aaff;
}
QPushButton#dark_theme_toggle:pressed {
    background-color: #0088cc;
    border: 2px solid #006699;
}

QPushButton#light_theme_toggle {
    background-color: #007bff; /* Blue for light theme toggle */
    color: #ffffff;
    border: 2px solid #0056b3;
}
QPushButton#light_theme_toggle:hover {
    background-color: #0056b3;
    border: 2px solid #004085;
}
QPushButton#light_theme_toggle:pressed {
    background-color: #004085;
    border: 2px solid #003366;
}

/* Instance Toggle Button Styles - Light Theme */
QPushButton#instanceToggle {
    background-color: #6c757d;
    color: #ffffff;
    border: 2px solid #6c757d;
    border-radius: 4px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: bold;
    min-width: 100px;
}
QPushButton#instanceToggle:hover {
    background-color: #5a6268;
    border: 2px solid #5a6268;
}
QPushButton#instanceToggle:checked {
    background-color: #007bff;
    color: #ffffff;
    border: 2px solid #007bff;
}
QPushButton#instanceToggle:checked:hover {
    background-color: #0056b3;
    border: 2px solid #0056b3;
}

/* ---- Inputs & Dropdowns ---- */
QComboBox, QLineEdit {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    padding: 8px;
    color: #333333;
}
QComboBox:focus, QLineEdit:focus {
    border: 1px solid #007bff;
}
QComboBox::drop-down {
    border: none;
}

/* ---- Tables & Logs ---- */
QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f8f8f8;
    border: 1px solid #cccccc;
    border-radius: 4px;
    gridline-color: #cccccc;
    selection-background-color: #007bff; /* Selection background */
    selection-color: #ffffff; /* Selection text color */
}
QTableWidget::item {
    padding: 8px;
    border: none;
}
QTableWidget::item:hover {
    background-color: #e9ecef; /* Hover background */
    color: #333333; /* Hover text color */
}
QTableWidget::item:selected {
    background-color: #007bff; /* Selected background */
    color: #ffffff; /* Selected text color */
}
QTableWidget::item:selected:hover {
    background-color: #0056b3; /* Selected + hover background */
    color: #ffffff; /* Selected + hover text color */
}
QHeaderView::section {
    background-color: #e9ecef;
    color: #333333;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #cccccc;
    font-weight: bold;
}
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #cccccc;
    border-radius: 4px;
    color: #007bff;
    font-family: Consolas, monospace;
}

/* ---- Status Labels ---- */
QLabel#statusOK, QLabel#statusReady {
    background-color: #28a745; /* Green */
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}
QLabel#statusError, QLabel#statusDisconnected {
    background-color: #dc3545; /* Red */
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}
QLabel#statusWarning, QLabel#statusIdle {
    background-color: #ffc107; /* Yellow */
    color: #333333;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}
QLabel#statusNeutral {
    background-color: #6c757d; /* Gray */
    color: #ffffff;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}

/* ---- Message Box Buttons ---- */
QMessageBox {
    background-color: #f0f0f0;
}
QMessageBox QLabel {
    color: #333333;
}
QMessageBox QPushButton {
    background-color: #6c757d;
    color: #ffffff;
    border: 2px solid #5a6268;
    border-radius: 6px;
    padding: 12px 30px;
    font-size: 13px;
    font-weight: bold;
    min-width: 180px;
    min-height: 40px;
    max-height: none;
}
QMessageBox QPushButton:hover {
    background-color: #5a6268;
    border: 2px solid #494f54;
}
QMessageBox QPushButton:pressed {
    background-color: #494f54;
    border: 2px solid #3d4349;
}
QMessageBox QPushButton:default {
    background-color: #007bff;
    color: #ffffff;
    border: 2px solid #0056b3;
}
QMessageBox QPushButton:default:hover {
    background-color: #0056b3;
    border: 2px solid #004085;
}
QMessageBox QPushButton:default:pressed {
    background-color: #004085;
    border: 2px solid #003366;
}

/* ---- Radio Buttons (for dialogs) ---- */
QRadioButton {
    color: #333333;
    spacing: 8px;
}
QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #cccccc;
    background-color: #ffffff;
}
QRadioButton::indicator:hover {
    border: 2px solid #007bff;
}
QRadioButton::indicator:checked {
    background-color: #007bff;
    border: 2px solid #0056b3;
    background-image: radial-gradient(circle, #ffffff 0%, #ffffff 35%, transparent 40%, transparent 100%);
}
QRadioButton::indicator:checked:hover {
    background-color: #0056b3;
    border: 2px solid #004085;
}
"""