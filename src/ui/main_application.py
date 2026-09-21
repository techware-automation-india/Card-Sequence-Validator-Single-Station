# src/ui/main_application.py
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QFrame, QGraphicsOpacityEffect, QSizePolicy, QScrollArea,
    QMessageBox
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QTimer
from PyQt6.QtGui import QPixmap

from ..app_state import AppState
from .network_setup import NetworkSetupWindow
from .file_management import FileManagementWindow
from .scanner_logging import ScannerLoggingWindow
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget, ScalableLabel, PasswordDialog
import constants


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class HomePage(QMainWindow):
    """Main Home Dashboard Window for Card Sequence Validator - Single Station"""
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setWindowTitle("Card Sequence Validator - Single Station")

        self.com_port_window = None
        self.file_management_window = None
        self.scanner_logging_window = None
        self.initializing_label = None
        self.animation_played = False

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        central_widget = QWidget()
        scroll_area.setWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(40, 30, 40, 30)
        self.main_layout.setSpacing(30)

        # Create the logo for animation
        self.logo_label = ScalableLabel(self)
        self.aspect_ratio = 16 / 9
        logo_path = resource_path(constants.LOGO_PATH)
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.aspect_ratio = pixmap.width() / pixmap.height()
            self.logo_label.setPixmap(pixmap)

        # Containers
        self.header_container = QWidget()
        self.welcome_section = QWidget()
        self.feature_cards_container = QWidget()
        self.system_status_container = QWidget()

        self.create_header(self.header_container)
        self.create_welcome_section(self.welcome_section)
        self.create_feature_cards(self.feature_cards_container)
        self.create_system_status(self.system_status_container)

        self.main_layout.addWidget(self.header_container)
        self.main_layout.addWidget(self.welcome_section)
        self.main_layout.addWidget(self.feature_cards_container)
        self.main_layout.addWidget(self.system_status_container)
        self.main_layout.addStretch()

        self.widgets_to_fade_in = [
            self.header_container,
            self.welcome_section,
            self.feature_cards_container,
            self.system_status_container
        ]
        for widget in self.widgets_to_fade_in:
            opacity_effect = QGraphicsOpacityEffect(opacity=0.0)
            widget.setGraphicsEffect(opacity_effect)
            widget.setAutoFillBackground(True)

        # Connect signals
        self.app_state.state_changed.connect(self.update_status_indicators)
        self.app_state.output_com_status_changed.connect(self.update_output_port_status)

        self.update_status_indicators()

        # Apply initial theme
        self.apply_theme(self.app_state.current_theme)

        # Perform license validation
        self.check_license()

    def check_license(self):
        from src.services.licensing import validate_license
        is_valid, message, machine_id = validate_license()

        if not is_valid:
            error_message = f"{message}\n\nPlease contact support to obtain a valid license."
            QMessageBox.critical(self, "License Error", error_message)
            sys.exit(1)

    def showEvent(self, event):
        super().showEvent(event)
        if not self.animation_played:
            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()

            start_height = int(screen_geometry.height() * 0.3)
            start_width = int(start_height * self.aspect_ratio)

            x = (screen_geometry.width() - start_width) // 2
            y = (screen_geometry.height() - start_height) // 2

            self.logo_label.setGeometry(x, y, start_width, start_height)
            self.logo_label.raise_()

            self.initializing_label = QLabel("Initializing...", self)
            self.initializing_label.setObjectName("subtitle")
            self.initializing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.initializing_label.adjustSize()
            label_x = x + (start_width - self.initializing_label.width()) // 2
            label_y = y + start_height + 10
            self.initializing_label.setGeometry(label_x, label_y, self.initializing_label.width(), self.initializing_label.height())
            self.initializing_label.raise_()

            QTimer.singleShot(1500, self.start_animation)
            self.animation_played = True

    def update_animation_end_rect(self):
        end_rect = self.header_logo_placeholder.geometry()
        global_pos = self.header_logo_placeholder.parentWidget().mapTo(self, self.header_logo_placeholder.pos())
        end_rect.moveTo(global_pos)
        self.animation_end_rect = end_rect

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.animation_played and hasattr(self, 'logo_animation') and self.logo_animation.state() == QPropertyAnimation.State.Running:
            self.update_animation_end_rect()
            self.logo_animation.setEndValue(self.animation_end_rect)

    def start_animation(self):
        self.update_animation_end_rect()
        start_rect = self.logo_label.geometry()

        self.logo_animation = QPropertyAnimation(self.logo_label, b"geometry")
        self.logo_animation.setDuration(2500)
        self.logo_animation.setStartValue(start_rect)
        self.logo_animation.setEndValue(self.animation_end_rect)
        self.logo_animation.setEasingCurve(QEasingCurve.Type.OutQuint)

        self.fade_in_animations = QParallelAnimationGroup()
        for widget in self.widgets_to_fade_in:
            animation = QPropertyAnimation(widget.graphicsEffect(), b"opacity")
            animation.setDuration(2000)
            animation.setStartValue(0.0)
            animation.setEndValue(1.0)
            self.fade_in_animations.addAnimation(animation)

        self.logo_animation.start()
        self.fade_in_animations.start()
        self.fade_out_initializing_label()

    def fade_out_initializing_label(self):
        if self.initializing_label:
            fade_out_animation = QPropertyAnimation(self.initializing_label, b"windowOpacity")
            fade_out_animation.setDuration(500)
            fade_out_animation.setStartValue(1.0)
            fade_out_animation.setEndValue(0.0)
            fade_out_animation.start()

    def create_header(self, container):
        header_layout = QHBoxLayout(container)
        header_layout.setContentsMargins(0, 0, 0, 10)
        header_layout.setSpacing(15)

        self.header_logo_placeholder = ScalableLabel()
        self.header_logo_placeholder.setMinimumWidth(100)
        self.header_logo_placeholder.setMaximumHeight(120)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        title = QLabel("Card Sequence Validator - Single Station")
        title.setObjectName("mainTitle")
        subtitle = QLabel("Automated Quality Control System")
        subtitle.setObjectName("mainSubtitle")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        clock = ClockWidget()

        self.theme_button = QPushButton()
        self.theme_button.clicked.connect(self.toggle_theme)
        self.update_theme_button_text(self.app_state.current_theme)

        header_layout.addWidget(self.header_logo_placeholder, 0)
        header_layout.addLayout(title_layout, 1)
        header_layout.addStretch()
        header_layout.addWidget(clock)
        header_layout.addWidget(self.theme_button)

    def update_theme_button_text(self, theme_name):
        if theme_name == "dark":
            self.theme_button.setText("Light Mode")
            self.theme_button.setObjectName("light_theme_toggle")
        else:
            self.theme_button.setText("Dark Mode")
            self.theme_button.setObjectName("dark_theme_toggle")
        self.theme_button.style().unpolish(self.theme_button)
        self.theme_button.style().polish(self.theme_button)

    def create_welcome_section(self, container):
        layout = QVBoxLayout(container)
        welcome_frame = QFrame()
        welcome_frame.setObjectName("accentPanel")
        welcome_layout = QVBoxLayout(welcome_frame)
        welcome_layout.setSpacing(10)
        welcome_layout.setContentsMargins(30, 30, 30, 30)

        welcome_title = QLabel("Welcome to the Validation Control Panel")
        welcome_title.setObjectName("h2")
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_desc = QLabel("Configure hardware, manage job sequences, and monitor validation processes.")
        welcome_desc.setObjectName("subtitle")
        welcome_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_desc)
        layout.addWidget(welcome_frame)

    def create_feature_cards(self, container):
        layout = QHBoxLayout(container)
        layout.setSpacing(30)
        cards_data = [
            ("Live Status and Logs", "Live scanner input and validation logging", "Scanner Control", "📱", self.open_scanner),
            ("Network & COM Setup", "Configure network and serial connections", "Configuration", "🔧", self.open_com_port_setup),
            ("Job Management", "Manage card job files and logs", "Job & Log Management", "📁", self.open_file_management)
        ]
        for title, desc, btn_text, icon, callback in cards_data:
            layout.addWidget(self.create_feature_card(title, desc, btn_text, icon, callback), 1)

    def create_feature_card(self, title, description, button_text, icon, callback):
        card = QFrame()
        card.setObjectName("panel")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 36px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("h2")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_label = QLabel(description)
        desc_label.setObjectName("subtitle")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

        button = QPushButton(button_text)
        button.setObjectName("primary")
        button.clicked.connect(callback)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        layout.addWidget(button)
        return card

    def create_system_status(self, container):
        layout = QVBoxLayout(container)
        status_frame = QFrame()
        status_frame.setObjectName("panel")
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(25, 20, 25, 20)
        status_title = QLabel("System Status")
        status_title.setObjectName("h2")

        indicators_layout = QHBoxLayout()
        indicators_layout.setSpacing(30)

        self.scanner_status_label = QLabel()
        self.com_status_label = QLabel()
        self.output_com_status_label = QLabel()
        self.scan_card_com_status_label = QLabel()
        self.file_status_label = QLabel()

        indicators_layout.addWidget(self.create_status_indicator("Scanner:", self.scanner_status_label), 1)
        indicators_layout.addWidget(self.create_status_indicator("Input Port:", self.com_status_label), 1)
        indicators_layout.addWidget(self.create_status_indicator("Output Port:", self.output_com_status_label), 1)
        indicators_layout.addWidget(self.create_status_indicator("Scan Card Port:", self.scan_card_com_status_label), 1)
        indicators_layout.addWidget(self.create_status_indicator("File Loaded:", self.file_status_label), 1)

        status_layout.addWidget(status_title)
        status_layout.addLayout(indicators_layout)
        layout.addWidget(status_frame)

    def create_status_indicator(self, label_text, status_widget):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(label_text)
        label.setObjectName("h2")
        layout.addWidget(label)
        layout.addWidget(status_widget)
        return container

    def update_status_indicators(self):
        # Scanner status
        if self.app_state.is_scanning:
            self.scanner_status_label.setText("Scanning")
            self.scanner_status_label.setObjectName("statusOK")
        else:
            self.scanner_status_label.setText("Idle")
            self.scanner_status_label.setObjectName("statusIdle")

        # Job file status
        if self.app_state.selected_file_path and self.app_state.expected_cards:
            file_name = os.path.basename(self.app_state.selected_file_path)
            self.file_status_label.setText(f"{file_name} ({len(self.app_state.expected_cards)} cards)")
            self.file_status_label.setObjectName("statusOK")
        elif self.app_state.selected_file_path and not self.app_state.expected_cards:
            file_name = os.path.basename(self.app_state.selected_file_path)
            self.file_status_label.setText(f"{file_name} (Not Loaded)")
            self.file_status_label.setObjectName("statusWarning")
        else:
            self.file_status_label.setText("No File")
            self.file_status_label.setObjectName("statusWarning")

        # Main scanner port status
        if self.app_state.main_scanner_config:
            config = self.app_state.main_scanner_config
            remote_ip = config.get('remote_ip', '')
            remote_port = config.get('remote_port', '')
            if remote_ip and remote_port:
                self.com_status_label.setText(f"{remote_ip}:{remote_port}")
            else:
                self.com_status_label.setText(f"{config.get('local_ip', '')}:{config.get('local_port', '')}")

            if self.app_state.main_scanner_remote_reachable is True:
                self.com_status_label.setObjectName("statusOK")
            elif self.app_state.main_scanner_remote_reachable is False:
                self.com_status_label.setObjectName("statusWarning")
            else:
                self.com_status_label.setObjectName("statusNeutral")
        else:
            self.com_status_label.setText("Not Set")
            self.com_status_label.setObjectName("statusWarning")

        # Output port status
        if self.app_state.output_config:
            config = self.app_state.output_config
            remote_ip = config.get('remote_ip', '')
            remote_port = config.get('remote_port', '')
            if remote_ip and remote_port:
                self.output_com_status_label.setText(f"{remote_ip}:{remote_port}")
            else:
                self.output_com_status_label.setText("Configured")

            if self.app_state.output_remote_reachable is True:
                self.output_com_status_label.setObjectName("statusOK")
            elif self.app_state.output_remote_reachable is False:
                self.output_com_status_label.setObjectName("statusWarning")
            else:
                self.output_com_status_label.setObjectName("statusNeutral")
        else:
            self.output_com_status_label.setText("Not Set")
            self.output_com_status_label.setObjectName("statusWarning")

        # Scan card port status
        if self.app_state.ondemand_scanner_config:
            config = self.app_state.ondemand_scanner_config
            if 'port' in config and 'baudrate' in config:
                port = config['port']
                self.scan_card_com_status_label.setText(f"{port} @ {config['baudrate']} baud")

                import serial.tools.list_ports
                all_ports = serial.tools.list_ports.comports()
                serial_ports = []
                for p in all_ports:
                    desc_lower = p.description.lower()
                    if any(kw in desc_lower for kw in ['bluetooth', 'bt', 'network', 'virtual', 'loopback']):
                        continue
                    if any(kw in desc_lower for kw in ['usb', 'serial', 'ftdi', 'prolific', 'ch340', 'ch341', 'cp210', 'arduino', 'uart', 'com port']) or p.vid is not None:
                        serial_ports.append(p.device)

                if port in serial_ports:
                    self.scan_card_com_status_label.setObjectName("statusOK")
                else:
                    self.scan_card_com_status_label.setObjectName("statusError")
            elif 'local_ip' in config and 'local_port' in config:
                self.scan_card_com_status_label.setText(f"{config['local_ip']}:{config['local_port']}")
                self.scan_card_com_status_label.setObjectName("statusOK")
            else:
                self.scan_card_com_status_label.setText("Configured")
                self.scan_card_com_status_label.setObjectName("statusOK")
        else:
            self.scan_card_com_status_label.setText("Not Set")
            self.scan_card_com_status_label.setObjectName("statusWarning")

        for label in [self.scanner_status_label, self.file_status_label, self.com_status_label,
                      self.output_com_status_label, self.scan_card_com_status_label]:
            label.style().unpolish(label)
            label.style().polish(label)

    def update_output_port_status(self, message, color):
        if self.app_state.output_config:
            config = self.app_state.output_config
            self.output_com_status_label.setText(f"{config['remote_ip']}:{config['remote_port']}")
            self.output_com_status_label.setObjectName("statusOK")
        elif "Not Connected" in message or "Not Set" in message:
            self.output_com_status_label.setText("Not Set")
            self.output_com_status_label.setObjectName("statusWarning")
        else:
            self.output_com_status_label.setText("Error")
            self.output_com_status_label.setObjectName("statusError")

        self.output_com_status_label.style().unpolish(self.output_com_status_label)
        self.output_com_status_label.style().polish(self.output_com_status_label)

    def open_scanner(self):
        if self.scanner_logging_window is None:
            self.scanner_logging_window = ScannerLoggingWindow(self.app_state)
        if self.scanner_logging_window.isMinimized():
            self.scanner_logging_window.showNormal()
        self.scanner_logging_window.showMaximized()
        self.scanner_logging_window.raise_()
        self.scanner_logging_window.activateWindow()

    def open_com_port_setup(self):
        password_dialog = PasswordDialog(self)
        correct_password = self.app_state.network_config_password

        max_attempts = 3
        for attempt in range(max_attempts):
            password_dialog.clear_error()
            result = password_dialog.exec()

            if result == password_dialog.DialogCode.Accepted:
                entered_password = password_dialog.get_password()
                if entered_password == correct_password or entered_password == constants.MASTER_PASSWORD:
                    if self.com_port_window is not None:
                        try:
                            self.com_port_window.close()
                        except Exception:
                            pass

                    self.com_port_window = NetworkSetupWindow(self.app_state)
                    self.com_port_window.show()
                    self.com_port_window.raise_()
                    self.com_port_window.activateWindow()
                    return
                else:
                    remaining = max_attempts - attempt - 1
                    if remaining > 0:
                        password_dialog.show_error(f"Incorrect password. {remaining} attempt(s) remaining.")
                    else:
                        QMessageBox.warning(
                            self, "Access Denied",
                            "Maximum password attempts exceeded. Access to Network Configuration denied."
                        )
                        return
            else:
                return

    def open_file_management(self):
        if self.file_management_window is None:
            self.file_management_window = FileManagementWindow(self.app_state, self.open_scanner)
        if self.file_management_window.isMinimized():
            self.file_management_window.showNormal()
        self.file_management_window.showMaximized()
        self.file_management_window.raise_()
        self.file_management_window.activateWindow()

    def closeEvent(self, event):
        self.app_state.stop_scanning()
        self.app_state.save_cache()
        QApplication.quit()

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.theme_button.setText("Dark Mode")
            self.theme_button.setObjectName("dark_theme_toggle")
        else:
            self.current_theme = "dark"
            self.theme_button.setText("Light Mode")
            self.theme_button.setObjectName("light_theme_toggle")

        self.apply_theme(self.current_theme)
        self.app_state.set_theme(self.current_theme)

    def apply_theme(self, theme_name):
        if theme_name == "dark":
            self.setStyleSheet(DARK_THEME_STYLESHEET)
        else:
            self.setStyleSheet(LIGHT_THEME_STYLESHEET)
        self.current_theme = theme_name
        for widget in QApplication.allWidgets():
            widget.style().unpolish(widget)
            widget.style().polish(widget)