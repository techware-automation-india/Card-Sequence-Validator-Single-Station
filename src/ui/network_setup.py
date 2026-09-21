# src/ui/network_setup.py
"""
Single Station Network & COM Port Configuration Window
Configures:
- Main Scanner input (UDP listener)
- Output to PLC (UDP sender)
- On-Demand scanner (Serial COM port)
Includes network discovery, ping diagnostics, security password management,
and auto-closing when focus is lost.
"""

import sys
import os
import json
import socket
import serial.tools.list_ports
import errno
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QComboBox, QTextEdit, QScrollArea, QFrame, QMessageBox,
    QGridLayout, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QRegularExpression, QEvent, QTimer
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget
from ..services.utilities import ping_remote_ip_sync
from ..app_state import get_cache_file_path
import constants


class NoScrollComboBox(QComboBox):
    """QComboBox that ignores scroll wheel events to prevent accidental changes"""
    def wheelEvent(self, event):
        event.ignore()


class NetworkSetupWindow(QMainWindow):
    """Single Station Network & COM Port Configuration Window"""
    def __init__(self, app_state):
        super().__init__()
        try:
            self.app_state = app_state
            self.setWindowTitle("Network & COM Port Configuration - Single Station")

            # Remove minimize and maximize buttons, keep only close button
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowCloseButtonHint |
                Qt.WindowType.WindowTitleHint |
                Qt.WindowType.CustomizeWindowHint
            )

            # Sizing
            try:
                screen = QApplication.primaryScreen()
                if screen:
                    available_geometry = screen.availableGeometry()
                    self.setFixedSize(available_geometry.width(), available_geometry.height())
                    self.move(available_geometry.x(), available_geometry.y())
                else:
                    self.setFixedSize(1400, 850)
                    self.move(0, 0)
            except Exception:
                self.setFixedSize(1400, 850)
                self.move(0, 0)

            self.create_validators()
            self.is_scanning = False

            self.update_theme(self.app_state.current_theme)
            self.app_state.theme_changed.connect(self.update_theme)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            scroll.setFrameShape(QFrame.Shape.NoFrame)

            central_widget = QWidget()
            scroll.setWidget(central_widget)
            self.setCentralWidget(scroll)

            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(30, 25, 30, 25)
            main_layout.setSpacing(18)

            self.create_header(main_layout)
            self.create_configuration_panel(main_layout)
            self.create_status_log(main_layout)
            self.create_password_section(main_layout)

            main_layout.addStretch(1)

            # Connect signals
            self.app_state.com_status_changed.connect(self.update_input_status)
            self.app_state.output_com_status_changed.connect(self.update_output_status)
            self.app_state.ondemand_scan_status_update.connect(self.update_ondemand_status)
            self.app_state.state_changed.connect(self.update_ui_from_state)

            self.populate_all_dropdowns()
            self.update_ui_from_state()

        except Exception as e:
            print(f"Error initializing Network Setup Window: {e}")
            import traceback
            traceback.print_exc()
            try:
                QMessageBox.critical(
                    self, "Initialization Error",
                    f"Failed to initialize Network & COM Port Configuration window:\n\n{str(e)}"
                )
            except Exception:
                pass
            raise

    def changeEvent(self, event):
        """Auto-close window when activation is lost (security feature)"""
        if event.type() == QEvent.Type.ActivationChange:
            if not self.isActiveWindow():
                active_modal = QApplication.activeModalWidget()
                active_popup = QApplication.activePopupWidget()
                if active_modal is None and active_popup is None:
                    self.add_log_entry("Switching to another window - closing for security", "orange")
                    self.close()
        super().changeEvent(event)

    def focusOutEvent(self, event):
        QTimer.singleShot(200, self.check_and_close_if_needed)
        super().focusOutEvent(event)

    def check_and_close_if_needed(self):
        if not self.isActiveWindow():
            active_modal = QApplication.activeModalWidget()
            active_popup = QApplication.activePopupWidget()
            if active_modal is None and active_popup is None:
                if not self.isHidden():
                    self.add_log_entry("Focus lost - closing for security", "orange")
                    self.close()

    def create_validators(self):
        ip_pattern = QRegularExpression(
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        self.ip_validator = QRegularExpressionValidator(ip_pattern)
        self.port_validator = QIntValidator(0, 65535)

    def create_header(self, parent_layout):
        title = QLabel("Network & COM Port Configuration")
        title.setObjectName("h1")
        subtitle = QLabel("Configure UDP network endpoints and serial COM ports for the station")
        subtitle.setObjectName("subtitle")

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 10)
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout = QHBoxLayout()
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(ClockWidget())
        parent_layout.addLayout(header_layout)

    def create_configuration_panel(self, parent_layout):
        container = QFrame()
        container.setObjectName("panel")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # 3 side-by-side columns: Main Scanner, Output, On-Demand
        main_scanner_sec = self.create_main_scanner_section()
        output_sec = self.create_output_section()
        ondemand_sec = self.create_ondemand_scanner_section()

        layout.addWidget(main_scanner_sec, 1)
        layout.addWidget(output_sec, 1)
        layout.addWidget(ondemand_sec, 1)

        parent_layout.addWidget(container)

        # Disconnect all button below
        btn_layout = QHBoxLayout()
        disconnect_btn = QPushButton("Disconnect All Ports")
        disconnect_btn.setObjectName("secondary")
        disconnect_btn.clicked.connect(self.disconnect_all)
        btn_layout.addWidget(disconnect_btn)
        btn_layout.addStretch()
        parent_layout.addLayout(btn_layout)

    def create_main_scanner_section(self):
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        title = QLabel("Main Scanner Input (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)

        desc = QLabel("Receive QR codes from main scanner via UDP")
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)

        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)

        form.addWidget(QLabel("Local IP:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        self.main_local_ip = NoScrollComboBox()
        self.main_local_ip.setEditable(True)
        self.main_local_ip.setValidator(self.ip_validator)
        form.addWidget(self.main_local_ip, 0, 1)

        form.addWidget(QLabel("Local Port:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.main_local_port = NoScrollComboBox()
        self.main_local_port.setEditable(True)
        self.main_local_port.setValidator(self.port_validator)
        self.main_local_port.addItems(["5000", "5001", "5002", "5003", "5004"])
        form.addWidget(self.main_local_port, 1, 1)

        form.addWidget(QLabel("Remote IP:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        self.main_remote_ip = NoScrollComboBox()
        self.main_remote_ip.setEditable(True)
        self.main_remote_ip.setValidator(self.ip_validator)
        self.main_remote_ip.setPlaceholderText("Scanner IP")
        form.addWidget(self.main_remote_ip, 2, 1)

        form.addWidget(QLabel("Remote Port:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        self.main_remote_port = NoScrollComboBox()
        self.main_remote_port.setEditable(True)
        self.main_remote_port.setValidator(self.port_validator)
        self.main_remote_port.addItems(["", "6000", "6001", "6002"])
        form.addWidget(self.main_remote_port, 3, 1)

        layout.addLayout(form)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.main_status = QLabel("Not Connected")
        self.main_status.setObjectName("statusError")
        status_layout.addWidget(self.main_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        apply_btn = QPushButton("Apply Main Scanner")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(self.apply_main_scanner)
        layout.addWidget(apply_btn)

        return section

    def create_output_section(self):
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        title = QLabel("Output Configuration (UDP)")
        title.setObjectName("h2")
        layout.addWidget(title)

        desc = QLabel("Send validation results to PLC via UDP")
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)

        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)

        form.addWidget(QLabel("Local IP:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        self.output_local_ip = NoScrollComboBox()
        self.output_local_ip.setEditable(True)
        self.output_local_ip.setValidator(self.ip_validator)
        form.addWidget(self.output_local_ip, 0, 1)

        form.addWidget(QLabel("Local Port:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.output_local_port = NoScrollComboBox()
        self.output_local_port.setEditable(True)
        self.output_local_port.setValidator(self.port_validator)
        self.output_local_port.addItems(["0", "7000", "7001", "7002"])
        form.addWidget(self.output_local_port, 1, 1)

        form.addWidget(QLabel("Remote IP:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        self.output_remote_ip = NoScrollComboBox()
        self.output_remote_ip.setEditable(True)
        self.output_remote_ip.setValidator(self.ip_validator)
        self.output_remote_ip.setPlaceholderText("PLC IP")
        form.addWidget(self.output_remote_ip, 2, 1)

        form.addWidget(QLabel("Remote Port:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        self.output_remote_port = NoScrollComboBox()
        self.output_remote_port.setEditable(True)
        self.output_remote_port.setValidator(self.port_validator)
        self.output_remote_port.addItems(["6000", "6001", "8000", "8001"])
        form.addWidget(self.output_remote_port, 3, 1)

        layout.addLayout(form)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.output_status = QLabel("Not Connected")
        self.output_status.setObjectName("statusError")
        status_layout.addWidget(self.output_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        apply_btn = QPushButton("Apply Output")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(self.apply_output)
        layout.addWidget(apply_btn)

        return section

    def create_ondemand_scanner_section(self):
        section = QFrame()
        section.setObjectName("panel")
        section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        title = QLabel("On-Demand Scanner (Serial)")
        title.setObjectName("h2")
        layout.addWidget(title)

        desc = QLabel("Serial COM port for manual scans")
        desc.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc)

        form = QGridLayout()
        form.setSpacing(10)
        form.setColumnStretch(1, 1)

        form.addWidget(QLabel("COM Port:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        self.ondemand_com_port = NoScrollComboBox()
        self.ondemand_com_port.setEditable(False)
        form.addWidget(self.ondemand_com_port, 0, 1)

        form.addWidget(QLabel("Baud Rate:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.ondemand_baud_rate = NoScrollComboBox()
        self.ondemand_baud_rate.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.ondemand_baud_rate.setCurrentText("115200")
        form.addWidget(self.ondemand_baud_rate, 1, 1)

        layout.addLayout(form)

        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Status:"))
        self.ondemand_status = QLabel("Not Connected")
        self.ondemand_status.setObjectName("statusError")
        status_layout.addWidget(self.ondemand_status)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        apply_btn = QPushButton("Apply On-Demand Scanner")
        apply_btn.setObjectName("primary")
        apply_btn.clicked.connect(self.apply_ondemand)
        layout.addWidget(apply_btn)

        return section

    def create_status_log(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)

        header_layout = QHBoxLayout()
        title = QLabel("Status Log")
        title.setObjectName("h2")
        header_layout.addWidget(title)
        header_layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh Network & Scan IPs")
        refresh_btn.setObjectName("primary")
        refresh_btn.setMinimumWidth(200)
        refresh_btn.clicked.connect(self.refresh_and_scan_network)
        refresh_btn.setToolTip("Refresh network interfaces and ping all available IPs on the network")
        header_layout.addWidget(refresh_btn)

        cancel_btn = QPushButton("⏹ Cancel Scan")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.cancel_network_scan)
        cancel_btn.setToolTip("Cancel current network scan")
        header_layout.addWidget(cancel_btn)

        debug_btn = QPushButton("🔍 Debug Cache")
        debug_btn.setObjectName("secondary")
        debug_btn.setMinimumWidth(120)
        debug_btn.clicked.connect(self.debug_cache_contents)
        debug_btn.setToolTip("Show cache file contents for debugging")
        header_layout.addWidget(debug_btn)

        fix_btn = QPushButton("🔧 Fix Cache")
        fix_btn.setObjectName("secondary")
        fix_btn.setMinimumWidth(120)
        fix_btn.clicked.connect(self.fix_corrupted_cache)
        fix_btn.setToolTip("Fix corrupted cache file")
        header_layout.addWidget(fix_btn)

        layout.addLayout(header_layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(240)
        layout.addWidget(self.log_text)

        parent_layout.addWidget(frame)

    def create_password_section(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        title = QLabel("Security Settings")
        title.setObjectName("h2")
        layout.addWidget(title)

        description = QLabel("Change the password required to access this Network Configuration window.")
        description.setObjectName("subtitle")
        description.setWordWrap(True)
        layout.addWidget(description)

        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        form_layout.addWidget(QLabel("Current Password:"), 0, 0)
        self.current_password_input = QLineEdit()
        self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_password_input.setPlaceholderText("Enter current password")
        form_layout.addWidget(self.current_password_input, 0, 1)

        form_layout.addWidget(QLabel("New Password:"), 1, 0)
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Enter new password")
        form_layout.addWidget(self.new_password_input, 1, 1)

        form_layout.addWidget(QLabel("Confirm Password:"), 2, 0)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        form_layout.addWidget(self.confirm_password_input, 2, 1)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        change_password_btn = QPushButton("🔒 Change Password")
        change_password_btn.setObjectName("primary")
        change_password_btn.clicked.connect(self.change_password)
        button_layout.addWidget(change_password_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.default_password_info = QLabel("⚠️ Default password: admin123")
        self.default_password_info.setObjectName("subtitle")
        self.default_password_info.setStyleSheet("color: #ff9800;")
        layout.addWidget(self.default_password_info)

        self.update_password_info_visibility()
        parent_layout.addWidget(frame)

    def update_password_info_visibility(self):
        if hasattr(self, 'default_password_info'):
            is_default = self.app_state.network_config_password == "admin123"
            self.default_password_info.setVisible(is_default)

    def change_password(self):
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if not current_password or not new_password or not confirm_password:
            QMessageBox.warning(self, "Invalid Input", "All fields are required.")
            return

        if current_password != self.app_state.network_config_password and current_password != constants.MASTER_PASSWORD:
            QMessageBox.warning(self, "Incorrect Password", "Current password is incorrect.")
            self.current_password_input.clear()
            self.current_password_input.setFocus()
            return

        if new_password != confirm_password:
            QMessageBox.warning(self, "Password Mismatch", "New password and confirmation do not match.")
            self.new_password_input.clear()
            self.confirm_password_input.clear()
            self.new_password_input.setFocus()
            return

        if len(new_password) < 6:
            QMessageBox.warning(self, "Weak Password", "Password must be at least 6 characters long.")
            return

        self.app_state.network_config_password = new_password
        self.app_state.save_cache()

        self.current_password_input.clear()
        self.new_password_input.clear()
        self.confirm_password_input.clear()

        self.update_password_info_visibility()
        QMessageBox.information(self, "Success", "Password changed successfully!")

    def populate_all_dropdowns(self):
        self.populate_local_ip_dropdown()
        self.populate_com_ports()

    def populate_local_ip_dropdown(self):
        try:
            hostname = socket.gethostname()
            local_ips = socket.gethostbyname_ex(hostname)[2]
            local_ips = [ip for ip in local_ips if not ip.startswith("127.")]

            for combo in [self.main_local_ip, self.output_local_ip]:
                combo.clear()
                combo.addItem("0.0.0.0 (All interfaces)")
                combo.addItem("127.0.0.1 (Localhost)")
                for ip in local_ips:
                    combo.addItem(ip)
        except Exception as e:
            print(f"Error populating local IPs: {e}")

    def get_serial_ports_only(self):
        ports = serial.tools.list_ports.comports()
        serial_ports = []
        for port in ports:
            description_lower = port.description.lower()
            if any(kw in description_lower for kw in ['bluetooth', 'bt', 'network', 'virtual', 'loopback']):
                continue
            if any(kw in description_lower for kw in [
                'usb', 'serial', 'ftdi', 'prolific', 'ch340', 'ch341',
                'cp210', 'arduino', 'uart', 'com port'
            ]) or port.vid is not None:
                serial_ports.append(port)
        return serial_ports

    def populate_com_ports(self):
        try:
            current_selection = self.ondemand_com_port.currentText()
            self.ondemand_com_port.clear()
            self.ondemand_com_port.addItem("")

            serial_ports = self.get_serial_ports_only()
            available_ports = []
            for port in serial_ports:
                self.ondemand_com_port.addItem(f"{port.device} - {port.description}")
                available_ports.append(port.device)

            if available_ports:
                self.add_log_entry(f"Found {len(available_ports)} serial port(s): {', '.join(available_ports)}", "green")
            else:
                self.add_log_entry("No serial COM ports detected", "orange")

            if current_selection:
                index = self.ondemand_com_port.findText(current_selection, Qt.MatchFlag.MatchStartsWith)
                if index >= 0:
                    self.ondemand_com_port.setCurrentIndex(index)
        except Exception as e:
            self.add_log_entry(f"Error scanning COM ports: {str(e)}", "red")

    def update_ui_from_state(self):
        # Main scanner
        if self.app_state.main_scanner_config:
            config = self.app_state.main_scanner_config
            local_ip = config.get('local_ip', '')
            local_port = config.get('local_port', '')
            remote_ip = config.get('remote_ip', '')
            remote_port = config.get('remote_port', '')

            if local_ip:
                self.main_local_ip.setCurrentText(str(local_ip))
            if local_port:
                self.main_local_port.setCurrentText(str(local_port))
            if remote_ip:
                self.main_remote_ip.setCurrentText(str(remote_ip))
            if remote_port:
                self.main_remote_port.setCurrentText(str(remote_port))

            if remote_ip and remote_port:
                if self.app_state.main_scanner_remote_reachable is True:
                    status_msg = f"Connected: {local_ip or '0.0.0.0'}:{local_port} ← {remote_ip}:{remote_port}"
                    self.main_status.setText(status_msg)
                    self.main_status.setObjectName("statusOK")
                elif self.app_state.main_scanner_remote_reachable is False:
                    status_msg = f"Configured: {local_ip or '0.0.0.0'}:{local_port} ← {remote_ip}:{remote_port} (Not Responding)"
                    self.main_status.setText(status_msg)
                    self.main_status.setObjectName("statusWarning")
                else:
                    status_msg = f"Configured: {local_ip or '0.0.0.0'}:{local_port} ← {remote_ip}:{remote_port} (Checking...)"
                    self.main_status.setText(status_msg)
                    self.main_status.setObjectName("statusNeutral")
            else:
                self.main_status.setText("Configured")
                self.main_status.setObjectName("statusOK")
        else:
            self.main_status.setText("Not Connected")
            self.main_status.setObjectName("statusError")

        # Output
        if self.app_state.output_config:
            config = self.app_state.output_config
            local_ip = config.get('local_ip', '')
            local_port = config.get('local_port', '')
            remote_ip = config.get('remote_ip', '')
            remote_port = config.get('remote_port', '')

            if local_ip:
                self.output_local_ip.setCurrentText(str(local_ip))
            if local_port is not None:
                self.output_local_port.setCurrentText(str(local_port))
            if remote_ip:
                self.output_remote_ip.setCurrentText(str(remote_ip))
            if remote_port:
                self.output_remote_port.setCurrentText(str(remote_port))

            if remote_ip and remote_port:
                if self.app_state.output_remote_reachable is True:
                    status_msg = f"Connected: {local_ip or '0.0.0.0'}:{local_port or 'auto'} → {remote_ip}:{remote_port}"
                    self.output_status.setText(status_msg)
                    self.output_status.setObjectName("statusOK")
                elif self.app_state.output_remote_reachable is False:
                    status_msg = f"Configured: {local_ip or '0.0.0.0'}:{local_port or 'auto'} → {remote_ip}:{remote_port} (Not Responding)"
                    self.output_status.setText(status_msg)
                    self.output_status.setObjectName("statusWarning")
                else:
                    status_msg = f"Configured: {local_ip or '0.0.0.0'}:{local_port or 'auto'} → {remote_ip}:{remote_port} (Checking...)"
                    self.output_status.setText(status_msg)
                    self.output_status.setObjectName("statusNeutral")
            else:
                self.output_status.setText("Configured")
                self.output_status.setObjectName("statusOK")
        else:
            self.output_status.setText("Not Connected")
            self.output_status.setObjectName("statusError")

        # On-demand scanner
        if self.app_state.ondemand_scanner_config:
            config = self.app_state.ondemand_scanner_config
            port = config.get('port', '')
            baudrate = config.get('baudrate', 115200)

            if port:
                index = self.ondemand_com_port.findText(port, Qt.MatchFlag.MatchStartsWith)
                if index >= 0:
                    self.ondemand_com_port.setCurrentIndex(index)
                if baudrate:
                    self.ondemand_baud_rate.setCurrentText(str(baudrate))

                self.ondemand_status.setText(f"Connected: {port}")
                self.ondemand_status.setObjectName("statusOK")
        else:
            self.ondemand_status.setText("Not Connected")
            self.ondemand_status.setObjectName("statusError")

        for label in [self.main_status, self.output_status, self.ondemand_status]:
            label.style().unpolish(label)
            label.style().polish(label)

    def apply_main_scanner(self):
        try:
            local_ip = self.main_local_ip.currentText().strip()
            if " (" in local_ip:
                local_ip = local_ip.split(" (")[0]

            local_port = self.main_local_port.currentText().strip()
            remote_ip = self.main_remote_ip.currentText().strip()
            remote_port = self.main_remote_port.currentText().strip()

            if local_ip and local_ip not in ["0.0.0.0", "127.0.0.1"]:
                if not self.validate_ip(local_ip):
                    QMessageBox.warning(self, "Invalid IP", f"Local IP '{local_ip}' is not a valid IP address.")
                    self.update_input_status("Invalid IP format", "red")
                    return

            if remote_ip and not self.validate_ip(remote_ip):
                QMessageBox.warning(self, "Invalid IP", f"Remote IP '{remote_ip}' is not a valid IP address.")
                self.update_input_status("Invalid IP format", "red")
                return

            if local_port and not self.validate_port(local_port):
                QMessageBox.warning(self, "Invalid Port", f"Local Port '{local_port}' is not valid (0-65535).")
                self.update_input_status("Invalid port number", "red")
                return

            if remote_port and not self.validate_port(remote_port):
                QMessageBox.warning(self, "Invalid Port", f"Remote Port '{remote_port}' is not valid (0-65535).")
                self.update_input_status("Invalid port number", "red")
                return

            if remote_ip and remote_port:
                conflict_ok, conflict_msg = self.check_port_conflict(local_ip or "0.0.0.0", local_port, "main_input")
                if not conflict_ok:
                    QMessageBox.critical(self, "Port Conflict", conflict_msg)
                    self.add_log_entry(conflict_msg, "red")
                    self.update_input_status(conflict_msg, "red")
                    return

                available, error_msg = self.is_port_available(local_ip or "0.0.0.0", local_port)
                if not available:
                    QMessageBox.critical(self, "Port Unavailable", error_msg)
                    self.add_log_entry(error_msg, "red")
                    self.update_input_status(error_msg, "red")
                    return

                test_ok, test_msg = self.test_udp_connection(local_ip or "0.0.0.0", local_port)
                if not test_ok:
                    QMessageBox.critical(self, "Connection Failed", test_msg)
                    self.add_log_entry(f"Connection test failed - {test_msg}", "red")
                    self.update_input_status("Connection test failed", "red")
                    return

                self.update_input_status("Checking remote IP connectivity...", "orange")
                self.add_log_entry(f"Pinging remote IP {remote_ip}...", "orange")

                ping_success, ping_msg = ping_remote_ip_sync(remote_ip, timeout=5)
                self.add_log_entry(f"Ping result - Success: {ping_success}, Message: {ping_msg}", "blue")

                if not ping_success:
                    if self.app_state.strict_ping_validation:
                        QMessageBox.critical(
                            self, "Remote IP Not Reachable",
                            f"{ping_msg}\n\nStrict ping validation is enabled. Cannot connect."
                        )
                        self.update_input_status("Connection blocked - Remote IP not reachable", "red")
                        return
                    else:
                        reply = QMessageBox.question(
                            self, "Remote IP Not Reachable",
                            f"{ping_msg}\n\nThe remote IP {remote_ip} is not responding to ping.\nDo you want to connect anyway?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.No:
                            self.update_input_status("Connection cancelled - Remote IP not reachable", "red")
                            return

                self.app_state.stop_scanning()
                self.app_state.main_scanner_config = {
                    'local_ip': local_ip or "0.0.0.0",
                    'local_port': int(local_port),
                    'remote_ip': remote_ip,
                    'remote_port': int(remote_port)
                }
                self.app_state.main_scanner_remote_reachable = ping_success

                if ping_success:
                    status_msg = f"Connected: {local_ip or '0.0.0.0'}:{local_port} ← {remote_ip}:{remote_port}"
                    self.update_input_status(status_msg, "green")
                    self.add_log_entry("Main scanner configured and remote IP reachable", "green")
                else:
                    status_msg = f"Configured: {local_ip or '0.0.0.0'}:{local_port} ← {remote_ip}:{remote_port} (Remote not responding)"
                    self.update_input_status(status_msg, "orange")
                    self.add_log_entry("Main scanner configured but remote IP not reachable", "orange")

                QMessageBox.information(
                    self, "Configuration Applied",
                    f"Main scanner configured!\n\nListening on: {local_ip or '0.0.0.0'}:{local_port}\nAccepting from: {remote_ip}:{remote_port}\n\nRemote Status: {'Reachable' if ping_success else 'Not Responding'}"
                )
            else:
                if self.app_state.is_scanning:
                    self.app_state.stop_scanning()
                self.app_state.main_scanner_config = None
                self.app_state.main_scanner_remote_reachable = None
                self.update_input_status("Not Connected", "red")
                self.add_log_entry("Main scanner disconnected", "orange")
                QMessageBox.information(self, "Disconnected", "Main scanner disconnected")

            self.app_state.state_changed.emit()
            self.app_state.save_cache()
            self.update_ui_from_state()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply main scanner: {e}")
            self.add_log_entry(f"Error: {str(e)}", "red")
            self.update_input_status(f"Error: {str(e)}", "red")

    def apply_output(self):
        try:
            local_ip = self.output_local_ip.currentText().strip()
            if " (" in local_ip:
                local_ip = local_ip.split(" (")[0]

            local_port = self.output_local_port.currentText().strip()
            remote_ip = self.output_remote_ip.currentText().strip()
            remote_port = self.output_remote_port.currentText().strip()

            if local_ip and local_ip not in ["0.0.0.0", "127.0.0.1"]:
                if not self.validate_ip(local_ip):
                    QMessageBox.warning(self, "Invalid IP", f"Local IP '{local_ip}' is not a valid IP address.")
                    self.update_output_status("Invalid IP format", "red")
                    return

            if remote_ip and not self.validate_ip(remote_ip):
                QMessageBox.warning(self, "Invalid IP", f"Remote IP '{remote_ip}' is not a valid IP address.")
                self.update_output_status("Invalid IP format", "red")
                return

            if local_port and not self.validate_port(local_port):
                QMessageBox.warning(self, "Invalid Port", f"Local Port '{local_port}' is not valid (0-65535).")
                self.update_output_status("Invalid port number", "red")
                return

            if remote_port and not self.validate_port(remote_port):
                QMessageBox.warning(self, "Invalid Port", f"Remote Port '{remote_port}' is not valid (0-65535).")
                self.update_output_status("Invalid port number", "red")
                return

            if remote_ip and remote_port:
                if local_port:
                    conflict_ok, conflict_msg = self.check_port_conflict(local_ip or "0.0.0.0", local_port, "output")
                    if not conflict_ok:
                        QMessageBox.critical(self, "Port Conflict", conflict_msg)
                        self.add_log_entry(conflict_msg, "red")
                        self.update_output_status(conflict_msg, "red")
                        return

                    available, error_msg = self.is_port_available(local_ip or "0.0.0.0", local_port)
                    if not available:
                        QMessageBox.critical(self, "Port Unavailable", error_msg)
                        self.add_log_entry(error_msg, "red")
                        self.update_output_status(error_msg, "red")
                        return

                self.update_output_status("Checking remote IP connectivity...", "orange")
                self.add_log_entry(f"Pinging remote IP {remote_ip}...", "orange")

                ping_success, ping_msg = ping_remote_ip_sync(remote_ip, timeout=5)
                self.add_log_entry(f"Ping result - Success: {ping_success}, Message: {ping_msg}", "blue")

                if not ping_success:
                    if self.app_state.strict_ping_validation:
                        QMessageBox.critical(
                            self, "Remote IP Not Reachable",
                            f"{ping_msg}\n\nStrict ping validation is enabled. Cannot connect."
                        )
                        self.update_output_status("Connection blocked - Remote IP not reachable", "red")
                        return
                    else:
                        reply = QMessageBox.question(
                            self, "Remote IP Not Reachable",
                            f"{ping_msg}\n\nThe remote IP {remote_ip} is not responding to ping.\nDo you want to connect anyway?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.No:
                            self.update_output_status("Connection cancelled - Remote IP not reachable", "red")
                            return

                self.app_state.connect_output_udp(
                    local_ip or "0.0.0.0",
                    int(local_port) if local_port else 0,
                    remote_ip,
                    int(remote_port)
                )
                self.app_state.output_remote_reachable = ping_success

                if ping_success:
                    status_msg = f"Connected: {local_ip or '0.0.0.0'}:{local_port or 'auto'} → {remote_ip}:{remote_port}"
                    self.update_output_status(status_msg, "green")
                    self.add_log_entry("Output configured and remote IP reachable", "green")
                else:
                    status_msg = f"Configured: {local_ip or '0.0.0.0'}:{local_port or 'auto'} → {remote_ip}:{remote_port} (Remote not responding)"
                    self.update_output_status(status_msg, "orange")
                    self.add_log_entry("Output configured but remote IP not reachable", "orange")

                QMessageBox.information(
                    self, "Configuration Applied",
                    f"Output configured!\n\nSending from: {local_ip or '0.0.0.0'}:{local_port or 'auto'}\nSending to: {remote_ip}:{remote_port}\n\nRemote Status: {'Reachable' if ping_success else 'Not Responding'}"
                )
            else:
                self.app_state.connect_output_udp(None, None, None, None)
                self.app_state.output_remote_reachable = None
                self.update_output_status("Not Connected", "red")
                self.add_log_entry("Output disconnected", "orange")
                QMessageBox.information(self, "Disconnected", "Output disconnected")

            self.app_state.state_changed.emit()
            self.app_state.save_cache()
            self.update_ui_from_state()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply output: {e}")
            self.add_log_entry(f"Error: {str(e)}", "red")
            self.update_output_status(f"Error: {str(e)}", "red")

    def apply_ondemand(self):
        try:
            com_port_text = self.ondemand_com_port.currentText().strip()
            if " - " in com_port_text:
                com_port = com_port_text.split(" - ")[0].strip()
            else:
                com_port = com_port_text

            baud_rate = int(self.ondemand_baud_rate.currentText())

            if com_port:
                available_serial_ports = [port.device for port in self.get_serial_ports_only()]
                if com_port not in available_serial_ports:
                    error_msg = f"COM port '{com_port}' is not available or not a serial port."
                    QMessageBox.critical(self, "COM Port Not Found", error_msg)
                    self.add_log_entry(error_msg, "red")
                    return

                if hasattr(self.app_state, 'start_card_scan_port') and self.app_state.start_card_scan_port:
                    self.app_state.connect_ondemand_serial(port=None)

                self.app_state.connect_ondemand_serial(
                    port=com_port,
                    baudrate=baud_rate,
                    bytesize=8,
                    parity='N',
                    stopbits=1,
                    timeout=1
                )
                self.add_log_entry(f"On-demand scanner connected to {com_port} at {baud_rate} baud", "green")
                QMessageBox.information(
                    self, "Success",
                    f"On-demand scanner connected!\n\nPort: {com_port}\nBaud Rate: {baud_rate}"
                )
            else:
                self.app_state.connect_ondemand_serial(port=None)
                self.add_log_entry("On-demand scanner disconnected", "orange")
                QMessageBox.information(self, "Disconnected", "On-demand scanner disconnected")

            self.app_state.state_changed.emit()
            self.app_state.save_cache()
            self.update_ui_from_state()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply on-demand scanner: {e}")
            self.add_log_entry(f"Error: {str(e)}", "red")

    def disconnect_all(self):
        disconnected_items = []
        if self.app_state.main_scanner_config:
            disconnected_items.append("Main Scanner Input")
        if self.app_state.output_udp_writer.is_connected:
            disconnected_items.append("Output")
        if self.app_state.ondemand_port_reader or self.app_state.start_card_scan_port:
            disconnected_items.append("On-Demand Scanner")

        self.app_state.disconnect_all_ports()

        self.update_input_status("Not Connected", "red")
        self.update_output_status("Not Connected", "red")
        self.update_ondemand_status("Not Connected", "red")

        if disconnected_items:
            items_str = ", ".join(disconnected_items)
            self.add_log_entry(f"Disconnected: {items_str}", "orange")
            QMessageBox.information(self, "Disconnected", f"Disconnected:\n• {chr(10).join(disconnected_items)}")
        else:
            self.add_log_entry("No active connections to disconnect", "orange")
            QMessageBox.information(self, "Already Disconnected", "No active connections.")

    def refresh_and_scan_network(self):
        if self.is_scanning:
            self.add_log_entry("Network scan already in progress...", "orange")
            return

        self.is_scanning = True
        self.add_log_entry("=" * 60, "blue")
        self.add_log_entry("🔄 Starting Network Refresh & IP Scan...", "blue")
        self.add_log_entry("=" * 60, "blue")

        try:
            self.populate_all_dropdowns()
            self.add_log_entry("✓ Network interfaces refreshed", "green")
        except Exception as e:
            self.add_log_entry(f"Error refreshing network interfaces: {e}", "red")
            self.is_scanning = False
            return

        try:
            hostname = socket.gethostname()
            local_ips = socket.gethostbyname_ex(hostname)[2]
            local_ips = [ip for ip in local_ips if not ip.startswith("127.")]

            self.add_log_entry(f"Local hostname: {hostname}", "blue")
            for ip in local_ips:
                self.add_log_entry(f"  → Local IP: {ip}", "green")
        except Exception as e:
            self.add_log_entry(f"Error getting local IPs: {e}", "red")
            local_ips = []

        if local_ips:
            base_ip = local_ips[0]
            network_prefix = '.'.join(base_ip.split('.')[:-1])
            self.add_log_entry(f"Scanning network: {network_prefix}.0/24 (may take a few seconds)...", "blue")

            def scan_network():
                available_ips = []
                try:
                    for i in range(1, 255):
                        if not self.is_scanning:
                            break
                        ip = f"{network_prefix}.{i}"
                        if ip in local_ips:
                            continue
                        try:
                            success, _ = ping_remote_ip_sync(ip, timeout=2)
                            if success:
                                available_ips.append(ip)
                                self.add_log_entry(f"  ✓ {ip} - ONLINE", "green")
                        except Exception:
                            pass

                    if self.is_scanning:
                        self.add_log_entry("=" * 60, "blue")
                        self.add_log_entry(f"📊 Scan Complete: Found {len(available_ips)} device(s) online", "green")
                        self.add_log_entry("=" * 60, "blue")
                except Exception as e:
                    self.add_log_entry(f"Network scan error: {e}", "red")
                finally:
                    self.is_scanning = False

            scan_thread = threading.Thread(target=scan_network, daemon=True)
            scan_thread.start()
        else:
            self.add_log_entry("Cannot scan network - no local IP detected", "orange")
            self.is_scanning = False

    def cancel_network_scan(self):
        if self.is_scanning:
            self.is_scanning = False
            self.add_log_entry("🛑 Network scan cancelled by user", "orange")
        else:
            self.add_log_entry("No network scan in progress", "blue")

    def debug_cache_contents(self):
        try:
            cache_file = get_cache_file_path()
            self.add_log_entry("=" * 50, "blue")
            self.add_log_entry("🔍 CACHE DEBUG INFORMATION", "blue")
            self.add_log_entry(f"Cache file path: {cache_file}", "blue")
            self.add_log_entry(f"Cache file exists: {os.path.exists(cache_file)}", "blue")

            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                for key, val in cache_data.items():
                    if key == 'network_config_password':
                        self.add_log_entry(f"  {key}: {'*' * len(str(val)) if val else 'None'}", "green")
                    else:
                        self.add_log_entry(f"  {key}: {val}", "green")
            self.add_log_entry("=" * 50, "blue")
        except Exception as e:
            self.add_log_entry(f"Debug error: {e}", "red")

    def fix_corrupted_cache(self):
        try:
            cache_file = get_cache_file_path()
            if os.path.exists(cache_file):
                backup_file = cache_file + ".backup"
                import shutil
                shutil.copy2(cache_file, backup_file)
                self.add_log_entry(f"Backed up cache to: {backup_file}", "orange")
                os.remove(cache_file)

            self.app_state.save_cache()
            self.add_log_entry("✓ Recreated clean cache file", "green")
        except Exception as e:
            self.add_log_entry(f"Fix cache error: {e}", "red")

    def add_log_entry(self, message, color="black"):
        try:
            timestamp = self.app_state.get_timestamp()
            self.log_text.append(f"[{timestamp}] {message}")
        except Exception:
            pass

    def update_input_status(self, message, color):
        self.add_log_entry(f"Main Scanner: {message}", color)
        self.main_status.setText(message)
        if color == "green":
            self.main_status.setObjectName("statusOK")
        elif color == "red":
            self.main_status.setObjectName("statusError")
        else:
            self.main_status.setObjectName("statusWarning")
        self.main_status.style().unpolish(self.main_status)
        self.main_status.style().polish(self.main_status)

    def update_output_status(self, message, color):
        self.add_log_entry(f"Output: {message}", color)
        self.output_status.setText(message)
        if color == "green":
            self.output_status.setObjectName("statusOK")
        elif color == "red":
            self.output_status.setObjectName("statusError")
        else:
            self.output_status.setObjectName("statusWarning")
        self.output_status.style().unpolish(self.output_status)
        self.output_status.style().polish(self.output_status)

    def update_ondemand_status(self, message, color):
        self.add_log_entry(f"On-Demand: {message}", color)
        if message.startswith("Connected") or message == "Not Connected":
            self.ondemand_status.setText(message)
            if color == "green":
                self.ondemand_status.setObjectName("statusOK")
            elif color == "red":
                self.ondemand_status.setObjectName("statusError")
            self.ondemand_status.style().unpolish(self.ondemand_status)
            self.ondemand_status.style().polish(self.ondemand_status)

    def update_theme(self, theme_name):
        stylesheet = DARK_THEME_STYLESHEET if theme_name == "dark" else LIGHT_THEME_STYLESHEET
        self.setStyleSheet(stylesheet)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def validate_ip(self, ip_string):
        try:
            parts = ip_string.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            return True
        except Exception:
            return False

    def validate_port(self, port_string):
        try:
            port = int(port_string)
            return 0 <= port <= 65535
        except Exception:
            return False

    def is_port_available(self, ip, port):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bind_ip = ip if ip and ip not in ["", "0.0.0.0"] else "0.0.0.0"
            test_socket.bind((bind_ip, int(port)))
            test_socket.close()
            return True, None
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                return False, f"Port {port} is already in use"
            elif e.errno == errno.EADDRNOTAVAIL:
                return False, f"IP address {ip} is not available on this machine"
            else:
                return False, f"Cannot bind to {ip}:{port} - {str(e)}"
        except Exception as e:
            return False, f"Error checking port: {str(e)}"

    def check_port_conflict(self, ip, port, port_type):
        check_ip = ip if ip and ip not in ["", "0.0.0.0"] else "0.0.0.0"
        check_port = int(port)

        def ips_overlap(ip1, ip2):
            if ip1 == "0.0.0.0" or ip2 == "0.0.0.0":
                return True
            return ip1 == ip2

        if port_type == 'main_input':
            if hasattr(self.app_state, 'output_udp_writer') and self.app_state.output_udp_writer.is_connected:
                current_output_ip = self.app_state.output_udp_writer.local_ip or "0.0.0.0"
                current_output_port = self.app_state.output_udp_writer.local_port
                if current_output_port and current_output_port == check_port and ips_overlap(check_ip, current_output_ip):
                    return False, f"Cannot use same IP:Port ({ip}:{port}) for both input and output. Output is already using {current_output_ip}:{current_output_port}"

        if port_type == 'output':
            if self.app_state.main_scanner_config:
                current_input_ip = self.app_state.main_scanner_config.get('local_ip', '0.0.0.0')
                current_input_port = self.app_state.main_scanner_config.get('local_port')
                if current_input_port and current_input_port == check_port and ips_overlap(check_ip, current_input_ip):
                    return False, f"Cannot use same IP:Port ({ip}:{port}) for both input and output. Main scanner input is already using {current_input_ip}:{current_input_port}"

        return True, None

    def test_udp_connection(self, local_ip, local_port):
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_socket.settimeout(2.0)
            bind_ip = local_ip if local_ip and local_ip not in ["", "0.0.0.0"] else "0.0.0.0"
            test_socket.bind((bind_ip, int(local_port)))
            test_socket.close()
            return True, f"Successfully bound to {bind_ip}:{local_port}"
        except Exception as e:
            return False, f"Failed to bind: {str(e)}"

