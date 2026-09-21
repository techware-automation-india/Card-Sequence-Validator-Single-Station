# src/ui/file_management.py
"""
Single Station Job Management Window
Provides file loading (CPD), sequence configuration, checksum controls,
on-demand card inspection/counting, and validation triggering.
"""

import sys
import os
import csv
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QHBoxLayout,
    QVBoxLayout, QFrame, QFileDialog, QLineEdit, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QGridLayout,
    QScrollArea, QComboBox, QAbstractItemView
)
from PyQt6.QtCore import Qt
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget
from .card_type_selector import CardTypeSelector
import constants
from ..card_types import CardType


class PreviewWindow(QDialog):
    """Preview window for sequence data"""
    def __init__(self, expected_cards, card_type, scan_direction="top_to_bottom", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Sequence Data")
        if parent and hasattr(parent, 'styleSheet'):
            try:
                self.setStyleSheet(parent.styleSheet())
            except Exception:
                pass

        layout = QVBoxLayout(self)
        if not expected_cards:
            layout.addWidget(QLabel("No expected cards loaded."))
        else:
            direction_label = QLabel()
            if scan_direction == "bottom_to_top":
                direction_label.setText("📋 Scan Direction: Bottom → Top (Reversed Order)")
                direction_label.setStyleSheet("color: #2196F3; font-weight: bold; padding: 5px;")
            else:
                direction_label.setText("📋 Scan Direction: Top → Bottom (Normal Order)")
                direction_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
            layout.addWidget(direction_label)

            qr_labels = CardType.get_qr_labels(card_type)
            num_columns = 1 + len(qr_labels)

            display_cards = list(reversed(expected_cards)) if scan_direction == "bottom_to_top" else expected_cards

            table = QTableWidget(len(display_cards), num_columns)
            headers = ["Card Number"] + qr_labels
            table.setHorizontalHeaderLabels(headers)
            table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
            table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            for i in range(1, num_columns):
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

            for row, card in enumerate(display_cards):
                numcard = card[0]
                qr_codes = card[1:]
                table.setItem(row, 0, QTableWidgetItem(str(numcard)))
                for col, qr_code in enumerate(qr_codes, start=1):
                    table.setItem(row, col, QTableWidgetItem(str(qr_code)))

            layout.addWidget(table)
        self.setMinimumSize(600, 400)


class FileManagementWindow(QMainWindow):
    """Single-station job management window"""
    def __init__(self, app_state, open_scanner_callback=None):
        super().__init__()
        self.app_state = app_state
        self.open_scanner_callback = open_scanner_callback
        self.setWindowTitle("Job Management - Single Station")
        self.setMinimumSize(1100, 800)

        # Track preview window
        self.preview_window = None

        self.update_theme(self.app_state.current_theme)
        self.app_state.theme_changed.connect(self.update_theme)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)

        self.create_header(main_layout)
        self.create_main_panel(main_layout)
        self.create_start_validation_section(main_layout)

        main_layout.addStretch()

        # Connect signals
        self.app_state.state_changed.connect(self.update_ui)
        self.app_state.start_card_scan_complete.connect(self.handle_start_card_scan_complete)
        self.app_state.card_count_update.connect(self.handle_card_count_update)
        self.app_state.ondemand_scan_status_update.connect(self.handle_ondemand_scan_status)
        self.app_state.card_type_changed.connect(self.rebuild_card_details_fields)

        self.update_ui()

    def create_header(self, parent_layout):
        title = QLabel("Job Management")
        title.setObjectName("h1")
        subtitle = QLabel("Manage job files, sequence verification parameters, and on-demand tools")
        subtitle.setObjectName("subtitle")

        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout = QHBoxLayout()
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(ClockWidget())
        parent_layout.addLayout(header_layout)

    def create_main_panel(self, parent_layout):
        container = QFrame()
        container.setObjectName("panel")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(20)

        # File Operations Section
        file_ops = self.create_file_operations_section()
        layout.addWidget(file_ops)

        # Checksum Configuration Section
        checksum_section = self.create_checksum_section()
        layout.addWidget(checksum_section)

        # Sequence Control Tools Section
        seq_tools = self.create_sequence_tools_section()
        layout.addWidget(seq_tools)

        # Log Management Section
        log_mgmt = self.create_log_management_section()
        layout.addWidget(log_mgmt)

        parent_layout.addWidget(container)

    def create_file_operations_section(self):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title = QLabel("Job File Operations")
        title.setObjectName("h2")
        layout.addWidget(title)

        # Load file button
        load_btn = QPushButton("📁 Load Job File")
        load_btn.setObjectName("primary")
        load_btn.clicked.connect(self.select_file)
        layout.addWidget(load_btn)

        # File status
        self.file_status = QLabel("No job file loaded.")
        self.file_status.setObjectName("subtitle")
        layout.addWidget(self.file_status)

        # Scan direction toggle
        direction_layout = QHBoxLayout()
        direction_label = QLabel("Scan Direction:")
        direction_label.setObjectName("subtitle")

        self.scan_direction_toggle = QPushButton("🔄 Top → Bottom")
        self.scan_direction_toggle.setObjectName("secondary")
        self.scan_direction_toggle.setCheckable(True)
        self.scan_direction_toggle.clicked.connect(self.toggle_scan_direction)

        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(self.scan_direction_toggle)
        direction_layout.addStretch()
        layout.addLayout(direction_layout)

        # Preview and Clear buttons
        button_layout = QHBoxLayout()
        self.preview_btn = QPushButton("👁 Preview")
        self.preview_btn.setObjectName("secondary")
        self.preview_btn.clicked.connect(self.preview_file)

        self.clear_btn = QPushButton("🗑 Clear")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self.clear_file)

        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        return frame

    def create_checksum_section(self):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title = QLabel("Checksum Configuration")
        title.setObjectName("h2")
        layout.addWidget(title)

        description = QLabel("Configure additional checksum digits to strip from scanned codes.")
        description.setObjectName("subtitle")
        description.setWordWrap(True)
        layout.addWidget(description)

        # Checksum digits selector
        checksum_layout = QHBoxLayout()
        checksum_label = QLabel("Checksum Digits:")
        checksum_label.setObjectName("subtitle")

        self.checksum_combo = QComboBox()
        self.checksum_combo.addItems([
            "0 (None)",
            "1 (Last digit)",
            "2 (Last 2 digits)",
            "3 (Last 3 digits)",
            "4 (Last 4 digits)",
            "5 (Last 5 digits)"
        ])
        self.checksum_combo.setObjectName("secondary")
        self.checksum_combo.currentIndexChanged.connect(self.update_checksum_digits)
        self.checksum_combo.wheelEvent = lambda event: None

        checksum_layout.addWidget(checksum_label)
        checksum_layout.addWidget(self.checksum_combo)
        checksum_layout.addStretch()
        layout.addLayout(checksum_layout)

        # Example display
        example_frame = QFrame()
        example_frame.setObjectName("accentPanel")
        example_layout = QVBoxLayout(example_frame)
        example_layout.setSpacing(5)

        example_title = QLabel("Example:")
        example_title.setStyleSheet("font-weight: bold;")
        example_layout.addWidget(example_title)

        self.checksum_example = QLabel("Scanned: 123456789\nValidated: 123456789")
        self.checksum_example.setObjectName("subtitle")
        example_layout.addWidget(self.checksum_example)

        layout.addWidget(example_frame)
        return frame

    def create_sequence_tools_section(self):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title = QLabel("Sequence Control Tools")
        title.setObjectName("h2")
        layout.addWidget(title)

        # Card Details Subsection
        details_frame = QFrame()
        details_frame.setObjectName("accentPanel")
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(10)

        details_title = QLabel("Scan Card Details")
        details_title.setStyleSheet("font-weight: bold;")
        details_layout.addWidget(details_title)

        # Manual input row
        manual_input_layout = QHBoxLayout()
        manual_input_label = QLabel("Card ICCID:")
        self.manual_iccid_input = QLineEdit()
        self.manual_iccid_input.setPlaceholderText("Enter ICCID and press Enter or click Find")
        self.manual_iccid_input.returnPressed.connect(self.find_card_by_iccid)

        self.find_card_btn = QPushButton("Find Card")
        self.find_card_btn.setObjectName("secondary")
        self.find_card_btn.clicked.connect(self.find_card_by_iccid)

        manual_input_layout.addWidget(manual_input_label)
        manual_input_layout.addWidget(self.manual_iccid_input, 1)
        manual_input_layout.addWidget(self.find_card_btn)
        details_layout.addLayout(manual_input_layout)

        # Action buttons
        actions_layout = QHBoxLayout()
        self.scan_card_details_btn = QPushButton("Scan Card")
        self.scan_card_details_btn.setObjectName("primary")
        self.scan_card_details_btn.clicked.connect(self.scan_card_details)

        self.cancel_card_details_btn = QPushButton("Cancel")
        self.cancel_card_details_btn.setObjectName("secondary")
        self.cancel_card_details_btn.clicked.connect(self.cancel_card_details)
        self.cancel_card_details_btn.setVisible(False)

        actions_layout.addWidget(self.scan_card_details_btn)
        actions_layout.addWidget(self.cancel_card_details_btn)
        actions_layout.addStretch()
        details_layout.addLayout(actions_layout)

        # Status label
        self.card_details_status = QLabel("Click 'Scan Card' to view card information.")
        self.card_details_status.setObjectName("subtitle")
        details_layout.addWidget(self.card_details_status)

        # Fields grid
        self.details_fields_grid = QGridLayout()
        self.details_fields_grid.setSpacing(8)

        self.details_fields_grid.addWidget(QLabel("Card Number:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.card_number_field = QLineEdit()
        self.card_number_field.setReadOnly(False)
        self.card_number_field.setEnabled(False)
        self.details_fields_grid.addWidget(self.card_number_field, 0, 1)

        qr_labels = CardType.get_qr_labels(self.app_state.card_type)
        self.qr_fields = []
        for i, label in enumerate(qr_labels, start=1):
            self.details_fields_grid.addWidget(QLabel(f"{label}:"), i, 0, Qt.AlignmentFlag.AlignLeft)
            qr_field = QLineEdit()
            qr_field.setReadOnly(False)
            qr_field.setEnabled(False)
            self.details_fields_grid.addWidget(qr_field, i, 1)
            self.qr_fields.append(qr_field)

        position_row = len(qr_labels) + 1
        self.details_fields_grid.addWidget(QLabel("Position:"), position_row, 0, Qt.AlignmentFlag.AlignLeft)
        self.position_field = QLineEdit()
        self.position_field.setReadOnly(False)
        self.position_field.setEnabled(False)
        self.details_fields_grid.addWidget(self.position_field, position_row, 1)

        details_layout.addLayout(self.details_fields_grid)
        layout.addWidget(details_frame)

        # Card Count Subsection
        count_frame = QFrame()
        count_frame.setObjectName("accentPanel")
        count_layout = QVBoxLayout(count_frame)
        count_layout.setSpacing(10)

        count_title = QLabel("Count Card Range")
        count_title.setStyleSheet("font-weight: bold;")
        count_layout.addWidget(count_title)

        instruction_label = QLabel("Enter ICCIDs manually or scan cards:")
        instruction_label.setObjectName("subtitle")
        count_layout.addWidget(instruction_label)

        # Action buttons
        count_actions_layout = QHBoxLayout()
        self.count_cards_btn = QPushButton("Scan Range")
        self.count_cards_btn.setObjectName("primary")
        self.count_cards_btn.clicked.connect(self.start_card_counting)

        self.calculate_range_btn = QPushButton("Calculate Range")
        self.calculate_range_btn.setObjectName("secondary")
        self.calculate_range_btn.clicked.connect(self.calculate_card_range)

        self.cancel_count_cards_btn = QPushButton("Cancel")
        self.cancel_count_cards_btn.setObjectName("secondary")
        self.cancel_count_cards_btn.clicked.connect(self.cancel_count_cards)
        self.cancel_count_cards_btn.setVisible(False)

        count_actions_layout.addWidget(self.count_cards_btn)
        count_actions_layout.addWidget(self.calculate_range_btn)
        count_actions_layout.addWidget(self.cancel_count_cards_btn)
        count_actions_layout.addStretch()
        count_layout.addLayout(count_actions_layout)

        # Status label
        self.card_count_status = QLabel("Click 'Count Range' to begin.")
        self.card_count_status.setObjectName("subtitle")
        count_layout.addWidget(self.card_count_status)

        # Count fields
        count_fields = QGridLayout()
        count_fields.setSpacing(8)

        count_fields.addWidget(QLabel("First Card ICCID:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.first_card_field = QLineEdit()
        self.first_card_field.setPlaceholderText("Enter ICCID or scan")
        self.first_card_field.returnPressed.connect(self.calculate_card_range)
        count_fields.addWidget(self.first_card_field, 0, 1)

        count_fields.addWidget(QLabel("Last Card ICCID:"), 1, 0, Qt.AlignmentFlag.AlignLeft)
        self.last_card_field = QLineEdit()
        self.last_card_field.setPlaceholderText("Enter ICCID or scan")
        self.last_card_field.returnPressed.connect(self.calculate_card_range)
        count_fields.addWidget(self.last_card_field, 1, 1)

        count_fields.addWidget(QLabel("Total:"), 2, 0, Qt.AlignmentFlag.AlignLeft)
        self.total_count_field = QLineEdit()
        self.total_count_field.setReadOnly(True)
        count_fields.addWidget(self.total_count_field, 2, 1)

        count_layout.addLayout(count_fields)
        layout.addWidget(count_frame)

        return frame

    def create_log_management_section(self):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title = QLabel("Validation Log Management")
        title.setObjectName("h2")
        layout.addWidget(title)

        button_layout = QHBoxLayout()
        self.clear_logs_btn = QPushButton("💾 Download and Clear Logs")
        self.clear_logs_btn.setObjectName("primary")
        self.clear_logs_btn.clicked.connect(self.clear_logs)

        button_layout.addWidget(self.clear_logs_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Statistics
        stats_frame = QFrame()
        stats_frame.setObjectName("accentPanel")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setContentsMargins(15, 15, 15, 15)

        self.total_scanned_label = QLabel("0")
        self.total_scanned_label.setObjectName("accent")

        self.scanned_ok_label = QLabel("0")
        self.scanned_ok_label.setObjectName("accent")

        self.error_not_ok_label = QLabel("0")
        self.error_not_ok_label.setObjectName("accent")

        self.skipped_label = QLabel("0")
        self.skipped_label.setObjectName("accent")

        stats_layout.addWidget(self.create_stat("Total Scans:", self.total_scanned_label), 0, 0)
        stats_layout.addWidget(self.create_stat("Successful:", self.scanned_ok_label), 0, 1)
        stats_layout.addWidget(self.create_stat("Failed:", self.error_not_ok_label), 1, 0)
        stats_layout.addWidget(self.create_stat("Skipped:", self.skipped_label), 1, 1)

        layout.addWidget(stats_frame)
        return frame

    def create_stat(self, text, value_label):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(text)
        label.setObjectName("subtitle")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(value_label)
        return widget

    def create_start_validation_section(self, parent_layout):
        button_container = QFrame()
        button_container.setObjectName("accentPanel")
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(20, 15, 20, 15)

        info_label = QLabel("Ready to start validation? Click below to begin scanning.")
        info_label.setObjectName("subtitle")
        button_layout.addWidget(info_label)
        button_layout.addStretch()

        self.start_validation_btn = QPushButton("▶ Start Validation")
        self.start_validation_btn.setObjectName("primary")
        self.start_validation_btn.setMinimumWidth(220)
        self.start_validation_btn.clicked.connect(self.start_validation_and_switch)
        button_layout.addWidget(self.start_validation_btn)

        self.validation_status = QLabel("⚠ Requirements not met")
        self.validation_status.setObjectName("subtitle")
        self.validation_status.setStyleSheet("color: orange; font-size: 11px;")
        button_layout.addWidget(self.validation_status)

        parent_layout.addWidget(button_container)

    def update_checksum_digits(self, index):
        self.app_state.checksum_digits = index + 1
        self.app_state.save_cache()

        if index == 0:
            self.checksum_example.setText("Scanned: 123456789\nValidated: 123456789")
        elif index == 1:
            self.checksum_example.setText("Scanned: 123456789\nValidated: 12345678")
        elif index == 2:
            self.checksum_example.setText("Scanned: 123456789\nValidated: 1234567")
        elif index == 3:
            self.checksum_example.setText("Scanned: 123456789\nValidated: 123456")
        elif index == 4:
            self.checksum_example.setText("Scanned: 123456789\nValidated: 12345")
        elif index == 5:
            self.checksum_example.setText("Scanned: 123456789\nValidated: 1234")

        self.app_state.state_changed.emit()

    def select_file(self):
        self.app_state.stop_scanning()

        has_unloaded_file = self.app_state.selected_file_path and not self.app_state.expected_cards
        is_reloading_previous = False
        use_cached_settings = False

        if has_unloaded_file:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Load Previous File")
            msg_box.setText(f"Previous file detected:\n{os.path.basename(self.app_state.selected_file_path)}\n\nDo you want to load this file or select a different one?")
            load_prev_btn = msg_box.addButton("Load Previous", QMessageBox.ButtonRole.AcceptRole)
            select_new_btn = msg_box.addButton("Select New File", QMessageBox.ButtonRole.ActionRole)
            cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            clicked_button = msg_box.clickedButton()
            if clicked_button == cancel_btn:
                return
            elif clicked_button == load_prev_btn:
                file_path = self.app_state.selected_file_path
                is_reloading_previous = True
                use_cached_settings = True
                selected_card_type = self.app_state.card_type
                rebatch_size = self.app_state.rebatch_size
            else:
                file_path, _ = QFileDialog.getOpenFileName(self, "Select Job File", "", constants.FILE_FILTER)
                if not file_path:
                    return
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Job File", "", constants.FILE_FILTER)
            if not file_path:
                return

        if not use_cached_settings:
            total_cards = self.count_cards_in_file(file_path)
            card_type_dialog = CardTypeSelector(self, total_cards)
            if hasattr(self, 'current_theme'):
                stylesheet = DARK_THEME_STYLESHEET if self.current_theme == "dark" else LIGHT_THEME_STYLESHEET
                card_type_dialog.setStyleSheet(stylesheet)

            if card_type_dialog.exec() == QDialog.DialogCode.Accepted:
                selected_type_str = card_type_dialog.get_selected_card_type()
                rebatch_size = card_type_dialog.get_rebatch_size()

                if selected_type_str:
                    card_type_map = {
                        "single": CardType.SINGLE,
                        "half": CardType.HALF,
                        "quarter": CardType.QUARTER
                    }
                    selected_card_type = card_type_map.get(selected_type_str, CardType.HALF)
                else:
                    return
            else:
                return

        should_restore_state = False
        if self.app_state.log_data:
            if is_reloading_previous:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Resume Session")
                msg_box.setText(f"Previous session logs found ({len(self.app_state.log_data)} entries).\n\nDo you want to continue from where you left off or start fresh?")
                continue_btn = msg_box.addButton("Continue from Last Use", QMessageBox.ButtonRole.AcceptRole)
                fresh_btn = msg_box.addButton("Fresh Start (Download & Clear)", QMessageBox.ButtonRole.DestructiveRole)
                cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                msg_box.exec()

                clicked_button = msg_box.clickedButton()
                if clicked_button == fresh_btn:
                    if self.download_logs():
                        self.app_state.clear_logs()
                    else:
                        return
                elif clicked_button == cancel_btn:
                    return
                elif clicked_button == continue_btn:
                    should_restore_state = True
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Unsaved Log Data")
                msg_box.setText("Unsaved log data detected. Export before proceeding?")
                export_btn = msg_box.addButton("Export and Clear", QMessageBox.ButtonRole.AcceptRole)
                cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
                msg_box.exec()

                clicked_button = msg_box.clickedButton()
                if clicked_button == export_btn:
                    if not self.download_logs():
                        return
                    self.app_state.clear_logs()
                else:
                    return

        success, message = self.app_state.load_file(file_path, selected_card_type, rebatch_size)
        if success:
            if should_restore_state:
                self.app_state.restore_scan_state_from_logs()
                QMessageBox.information(self, "Success", f"{message}\n\nResumed from card index {self.app_state.current_card_index + 1}.")
            else:
                QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

    def clear_file(self):
        self.app_state.stop_scanning()
        self.app_state.clear_file()
        QMessageBox.information(self, "Cleared", "Job file cleared.")

    def preview_file(self):
        if not self.app_state.expected_cards:
            QMessageBox.warning(self, "Warning", "No file loaded to preview.")
            return

        if self.preview_window:
            try:
                self.preview_window.close()
            except Exception:
                pass

        dialog = PreviewWindow(self.app_state.expected_cards, self.app_state.card_type, self.app_state.scan_direction, self)
        dialog.setWindowTitle("Preview Sequence Data")
        dialog.setWindowModality(Qt.WindowModality.NonModal)
        self.preview_window = dialog
        dialog.finished.connect(lambda: setattr(self, 'preview_window', None))
        dialog.show()

    def toggle_scan_direction(self):
        if self.app_state.start_card_has_been_scanned and self.app_state.current_card_index > 0:
            QMessageBox.warning(
                self, "Cannot Toggle",
                "Direction cannot be changed after scanning has started."
            )
            return

        if self.app_state.scan_direction == "top_to_bottom":
            self.app_state.scan_direction = "bottom_to_top"
            self.scan_direction_toggle.setText("🔄 Bottom → Top")
            self.scan_direction_toggle.setChecked(True)
        else:
            self.app_state.scan_direction = "top_to_bottom"
            self.scan_direction_toggle.setText("🔄 Top → Bottom")
            self.scan_direction_toggle.setChecked(False)

        self.app_state.current_card_index = 0
        self.app_state.start_card_has_been_scanned = False
        self.app_state.first_scan_received = True
        self.app_state.save_cache()
        self.app_state.state_changed.emit()

        direction_desc = self.app_state.get_scan_direction_description()
        QMessageBox.information(self, "Direction Changed", f"Scan direction changed to {direction_desc}")

    def scan_card_details(self):
        self.app_state.scan_and_get_card_details()

    def cancel_card_details(self):
        self.app_state.cancel_card_details_scan()

    def start_card_counting(self):
        self.app_state.start_card_counting()

    def cancel_count_cards(self):
        self.app_state.cancel_count_card_range_scan()

    def find_card_by_iccid(self):
        try:
            if not self.app_state.expected_cards:
                QMessageBox.warning(self, "File Error", "A job file must be loaded before searching for cards.")
                return

            manual_input = self.manual_iccid_input.text().strip()
            if not manual_input:
                QMessageBox.warning(self, "Input Error", "Please enter a card ICCID.")
                return

            search_iccid = self.app_state.strip_checksum(manual_input, use_ui_value=True)

            found_card = None
            found_index = None

            for idx, card in enumerate(self.app_state.expected_cards):
                qr_codes = card[1:]
                if search_iccid in qr_codes:
                    found_card = card
                    found_index = idx
                    break

            if found_card:
                card_number = found_card[0]
                qr_codes = found_card[1:]

                self.card_number_field.setText(str(card_number))
                self.position_field.setText(f"{found_index + 1} of {len(self.app_state.expected_cards)}")

                for i, qr_field in enumerate(self.qr_fields):
                    if i < len(qr_codes):
                        qr_field.setText(qr_codes[i] if qr_codes[i] else '')
                    else:
                        qr_field.setText('')

                self.card_details_status.setText(f"✓ Card found at position {found_index + 1}")
                self.card_details_status.setStyleSheet("color: green;")
            else:
                QMessageBox.warning(self, "Card Not Found", f"No card found with ICCID: {search_iccid}\n\nMake sure you entered the correct ICCID.")
                self.card_details_status.setText("✗ Card not found")
                self.card_details_status.setStyleSheet("color: red;")
        except Exception as e:
            print(f"Error in find_card_by_iccid: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while searching for the card:\n{str(e)}")
            self.card_details_status.setText("✗ Error occurred")
            self.card_details_status.setStyleSheet("color: red;")

    def calculate_card_range(self):
        try:
            if not self.app_state.expected_cards:
                QMessageBox.warning(self, "File Error", "A job file must be loaded before calculating card range.")
                return

            first_iccid = self.first_card_field.text().strip()
            last_iccid = self.last_card_field.text().strip()

            if not first_iccid or not last_iccid:
                QMessageBox.warning(self, "Input Error", "Please enter both First Card and Last Card ICCIDs.")
                return

            first_iccid = self.app_state.strip_checksum(first_iccid, use_ui_value=True)
            last_iccid = self.app_state.strip_checksum(last_iccid, use_ui_value=True)

            first_index = None
            last_index = None

            for idx, card in enumerate(self.app_state.expected_cards):
                qr_codes = card[1:]
                if first_iccid in qr_codes and first_index is None:
                    first_index = idx
                if last_iccid in qr_codes and last_index is None:
                    last_index = idx

                if first_index is not None and last_index is not None:
                    break

            if first_index is None:
                QMessageBox.warning(self, "Card Not Found", f"First card ICCID not found: {first_iccid}")
                self.card_count_status.setText("✗ First card not found")
                self.card_count_status.setStyleSheet("color: red;")
                return

            if last_index is None:
                QMessageBox.warning(self, "Card Not Found", f"Last card ICCID not found: {last_iccid}")
                self.card_count_status.setText("✗ Last card not found")
                self.card_count_status.setStyleSheet("color: red;")
                return

            if first_index <= last_index:
                total_cards = last_index - first_index + 1
                self.total_count_field.setText(str(total_cards))
                self.card_count_status.setText(f"✓ Range calculated: {total_cards} cards (positions {first_index + 1} to {last_index + 1})")
                self.card_count_status.setStyleSheet("color: green;")
            else:
                QMessageBox.warning(self, "Invalid Range", f"First card (position {first_index + 1}) comes after Last card (position {last_index + 1}).\n\nPlease enter the cards in the correct order.")
                self.card_count_status.setText("✗ Invalid range order")
                self.card_count_status.setStyleSheet("color: red;")
        except Exception as e:
            print(f"Error in calculate_card_range: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while calculating the range:\n{str(e)}")
            self.card_count_status.setText("✗ Error occurred")
            self.card_count_status.setStyleSheet("color: red;")

    def download_logs(self):
        if not self.app_state.log_data:
            QMessageBox.information(self, "Info", "No log data to export.")
            return False

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        log_dir = os.path.join(desktop_path, "csv_logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        default_filename = f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        default_path = os.path.join(log_dir, default_filename)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Logs",
            default_path,
            "CSV Files (*.csv)"
        )
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    if self.app_state.card_type == CardType.SINGLE:
                        fieldnames = ['index', 'timestamp', 'scanned_code', 'expected_code', 'status']
                    else:
                        fieldnames = ['index', 'timestamp', 'scanned_code', 'expected_code', 'status', 'scanned_side']

                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for log_entry in self.app_state.log_data:
                        indexed_entry = {}
                        expected_code = log_entry.get("expected_code", "N/A")
                        display_numcard = "---"

                        for numcard, qr_codes in self.app_state.numcard_to_qrs.items():
                            if expected_code in qr_codes:
                                display_numcard = str(numcard)
                                break

                        if display_numcard == "---":
                            if expected_code == "N/A":
                                display_numcard = "N/A"
                            elif expected_code == "End of Sequence":
                                display_numcard = "End"

                        indexed_entry['index'] = display_numcard
                        indexed_entry['timestamp'] = "'" + str(log_entry.get('timestamp', ''))
                        indexed_entry['scanned_code'] = "'" + str(log_entry.get('scanned_code', ''))
                        indexed_entry['expected_code'] = "'" + str(log_entry.get('expected_code', ''))
                        indexed_entry['status'] = log_entry.get('status', '')

                        if self.app_state.card_type != CardType.SINGLE:
                            indexed_entry['scanned_side'] = log_entry.get('scanned_side', 'N/A')

                        writer.writerow(indexed_entry)

                QMessageBox.information(self, "Success", f"Logs saved to {file_path}")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving file: {e}")
                return False
        return False

    def clear_logs(self):
        if not self.app_state.log_data:
            QMessageBox.information(self, "No Logs", "No logs to clear.")
            return

        reply = QMessageBox.question(
            self,
            "Download and Clear Logs",
            "This will download the logs and then clear them.\n\nDo you want to continue?"
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.download_logs():
                self.app_state.clear_logs()
                QMessageBox.information(self, "Success", "Logs downloaded and cleared.")
            else:
                QMessageBox.warning(self, "Cancelled", "Logs were not cleared because download was cancelled.")

    def start_validation_and_switch(self):
        if not self.app_state.expected_cards:
            QMessageBox.warning(self, "No File Loaded", "Please load a job file before starting validation.")
            return

        if self.app_state.is_scanning:
            QMessageBox.information(self, "Already Scanning", "Validation is already in progress.")
            if self.open_scanner_callback:
                self.open_scanner_callback()
            return

        if self.app_state.log_data:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Existing Logs Found")
            msg_box.setText("There are existing logs in the table.")
            msg_box.setInformativeText("Do you want to download and clear the logs before starting a new scan?")
            clear_button = msg_box.addButton("Download, Clear & Start", QMessageBox.ButtonRole.AcceptRole)
            continue_button = msg_box.addButton("Continue with Existing Logs", QMessageBox.ButtonRole.DestructiveRole)
            cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            clicked_button = msg_box.clickedButton()

            if clicked_button == clear_button:
                if self.download_logs():
                    self.app_state.clear_logs()
                    self.app_state.start_scanning()
                else:
                    return
            elif clicked_button == continue_button:
                self.app_state.start_scanning()
            else:
                return
        else:
            self.app_state.start_scanning()

        if self.open_scanner_callback:
            self.open_scanner_callback()

    def handle_start_card_scan_complete(self, message, success):
        try:
            if success:
                lines = message.split('\n')
                qr_labels = CardType.get_qr_labels(self.app_state.card_type)
                qr_field_index = 0

                for line in lines:
                    if line.startswith("Card Number:"):
                        self.card_number_field.setText(line.split(":", 1)[1].strip())
                    elif line.startswith("Position:"):
                        self.position_field.setText(line.split(":", 1)[1].strip())
                    else:
                        for label in qr_labels:
                            if line.startswith(f"{label}:"):
                                if qr_field_index < len(self.qr_fields):
                                    self.qr_fields[qr_field_index].setText(line.split(":", 1)[1].strip())
                                    qr_field_index += 1
                                break

                self.card_details_status.setText("Card details loaded successfully.")
            else:
                self.card_number_field.clear()
                for qr_field in self.qr_fields:
                    qr_field.clear()
                self.position_field.clear()
                self.card_details_status.setText(message)
        except Exception as e:
            print(f"Error in handle_start_card_scan_complete: {e}")
            self.card_details_status.setText(f"Error displaying card details: {str(e)}")
        finally:
            self.update_ui()

    def handle_card_count_update(self, update_type, message):
        if update_type == 'first_card':
            self.first_card_field.setText(message)
        elif update_type == 'last_card':
            self.last_card_field.setText(message)
        elif update_type == 'total':
            self.total_count_field.setText(message)
        elif update_type == 'error':
            QMessageBox.warning(self, "Error", message)
        elif update_type == 'clear':
            self.first_card_field.clear()
            self.last_card_field.clear()
            self.total_count_field.clear()
            self.card_count_status.setText("Click 'Count Range' to begin.")

    def handle_ondemand_scan_status(self, status, message):
        if status == 'active':
            if self.app_state.is_waiting_for_start_card:
                self.card_details_status.setText(message)
                self.scan_card_details_btn.setEnabled(False)
                self.count_cards_btn.setEnabled(False)
                self.cancel_card_details_btn.setVisible(True)
                self.cancel_count_cards_btn.setVisible(False)
            elif self.app_state.is_waiting_for_count_card_1 or self.app_state.is_waiting_for_count_card_2:
                self.card_count_status.setText(message)
                self.scan_card_details_btn.setEnabled(False)
                self.count_cards_btn.setEnabled(False)
                self.cancel_card_details_btn.setVisible(False)
                self.cancel_count_cards_btn.setVisible(True)
        else:
            self.card_details_status.setText("Click 'Scan Card' to view card information.")
            self.card_count_status.setText("Click 'Count Range' to begin.")
            self.cancel_card_details_btn.setVisible(False)
            self.cancel_count_cards_btn.setVisible(False)
            self.update_ui()

    def rebuild_card_details_fields(self, card_type):
        while self.details_fields_grid.count():
            item = self.details_fields_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.details_fields_grid.addWidget(QLabel("Card Number:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.card_number_field = QLineEdit()
        self.card_number_field.setReadOnly(False)
        self.card_number_field.setEnabled(False)
        self.details_fields_grid.addWidget(self.card_number_field, 0, 1)

        qr_labels = CardType.get_qr_labels(card_type)
        self.qr_fields = []
        for i, label in enumerate(qr_labels, start=1):
            self.details_fields_grid.addWidget(QLabel(f"{label}:"), i, 0, Qt.AlignmentFlag.AlignLeft)
            qr_field = QLineEdit()
            qr_field.setReadOnly(False)
            qr_field.setEnabled(False)
            self.details_fields_grid.addWidget(qr_field, i, 1)
            self.qr_fields.append(qr_field)

        position_row = len(qr_labels) + 1
        self.details_fields_grid.addWidget(QLabel("Position:"), position_row, 0, Qt.AlignmentFlag.AlignLeft)
        self.position_field = QLineEdit()
        self.position_field.setReadOnly(False)
        self.position_field.setEnabled(False)
        self.details_fields_grid.addWidget(self.position_field, position_row, 1)

    def count_cards_in_file(self, file_path):
        try:
            total_cards = 0
            start_reading = False

            with open(file_path, mode='r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("NUMCARD"):
                        start_reading = True
                        continue

                    if start_reading and line and not line.startswith("NUMCARD"):
                        total_cards += 1

            return total_cards
        except Exception as e:
            print(f"Error counting cards in file: {e}")
            return None

    def update_ui(self):
        has_file = bool(self.app_state.expected_cards)
        has_file_path = bool(self.app_state.selected_file_path)
        has_logs = bool(self.app_state.log_data)
        has_ondemand = bool(self.app_state.ondemand_port_reader) or bool(self.app_state.ondemand_scanner_config)
        is_waiting = (
            self.app_state.is_waiting_for_start_card or
            self.app_state.is_waiting_for_count_card_1 or
            self.app_state.is_waiting_for_count_card_2
        )
        is_scanning = self.app_state.is_scanning

        has_main_scanner = bool(self.app_state.main_scanner_config)
        has_output = bool(self.app_state.output_config)
        can_start_validation = has_file and has_main_scanner and has_output

        self.preview_btn.setEnabled(has_file)
        self.clear_btn.setEnabled(has_file)
        self.scan_card_details_btn.setEnabled(has_file and has_ondemand and not is_waiting and not is_scanning)
        self.count_cards_btn.setEnabled(has_file and has_ondemand and not is_waiting)
        self.calculate_range_btn.setEnabled(has_file and not is_scanning)
        self.find_card_btn.setEnabled(has_file)
        self.clear_logs_btn.setEnabled(has_logs)

        fields_enabled = has_file and has_ondemand and not is_scanning
        self.card_number_field.setEnabled(fields_enabled)
        self.position_field.setEnabled(fields_enabled)
        for qr_field in self.qr_fields:
            qr_field.setEnabled(fields_enabled)

        self.first_card_field.setEnabled(has_file)
        self.last_card_field.setEnabled(has_file)
        self.total_count_field.setEnabled(has_file)
        self.manual_iccid_input.setEnabled(has_file)

        # Update start validation button
        self.start_validation_btn.setEnabled(can_start_validation and not is_scanning)
        if is_scanning:
            self.start_validation_btn.setText("▶ Validation Running")
            self.start_validation_btn.setToolTip("Validation is currently running")
        else:
            if not has_file:
                self.start_validation_btn.setText("▶ Start Validation")
                self.start_validation_btn.setToolTip("⚠ Cannot start: No job file loaded\n\nPlease load a CPD file first")
            elif not has_main_scanner:
                self.start_validation_btn.setText("▶ Start Validation")
                self.start_validation_btn.setToolTip("⚠ Cannot start: Main Scanner (Input) not configured\n\nPlease configure and apply Main Scanner in Network Setup")
            elif not has_output:
                self.start_validation_btn.setText("▶ Start Validation")
                self.start_validation_btn.setToolTip("⚠ Cannot start: Output not configured\n\nPlease configure and apply Output in Network Setup")
            else:
                self.start_validation_btn.setText("▶ Start Validation")
                self.start_validation_btn.setToolTip("Start QR code validation\n\nRequirements:\n✓ Job file loaded\n✓ Main Scanner configured\n✓ Output configured")

        if can_start_validation:
            self.validation_status.setText("✓ Ready to validate")
            self.validation_status.setStyleSheet("color: #4CAF50; font-size: 11px; font-weight: bold;")
        else:
            missing = []
            if not has_file:
                missing.append("File")
            if not has_main_scanner:
                missing.append("Input Config")
            if not has_output:
                missing.append("Output Config")

            if len(missing) == 1:
                self.validation_status.setText(f"⚠ Missing: {missing[0]}")
            elif len(missing) > 1:
                self.validation_status.setText(f"⚠ Missing: {', '.join(missing)}")
            else:
                self.validation_status.setText("⚠ Configuration incomplete")

            self.validation_status.setStyleSheet("color: #FF9800; font-size: 11px;")

        # Update checksum combo box
        self.checksum_combo.setCurrentIndex(max(0, self.app_state.checksum_digits - 1))

        # Update file status
        if has_file:
            self.file_status.setText(f"Active: {os.path.basename(self.app_state.selected_file_path)} ({len(self.app_state.expected_cards)} cards)")
            self.file_status.setObjectName("subtitle")
            self.file_status.setStyleSheet("")
        elif has_file_path:
            self.file_status.setText(f"⚠ File not loaded: {os.path.basename(self.app_state.selected_file_path)}\nClick 'Load Job File' to continue")
            self.file_status.setObjectName("statusWarning")
            self.file_status.setStyleSheet("font-size: 14px;")
        else:
            self.file_status.setText("No job file loaded.")
            self.file_status.setObjectName("subtitle")
            self.file_status.setStyleSheet("")

        # Update statistics
        total = len(self.app_state.log_data)
        ok = len([log for log in self.app_state.log_data if log["status"] in ("OK", "OK (JUMPED)", "LAST OK", "LAST OK (JUMPED)")])
        skipped = len([log for log in self.app_state.log_data if log["status"] == "SKIPPED"])
        error = len([log for log in self.app_state.log_data if log["status"] in ("NOT OK", "NO FILE", "EXTRA SCAN", "NOT IN SEQUENCE")])

        self.total_scanned_label.setText(str(total))
        self.scanned_ok_label.setText(str(ok))
        self.error_not_ok_label.setText(str(error))
        self.skipped_label.setText(str(skipped))

        # Update scan direction toggle
        if self.app_state.scan_direction == "bottom_to_top":
            self.scan_direction_toggle.setText("🔄 Bottom → Top")
            self.scan_direction_toggle.setChecked(True)
        else:
            self.scan_direction_toggle.setText("🔄 Top → Bottom")
            self.scan_direction_toggle.setChecked(False)

    def update_theme(self, theme_name):
        self.current_theme = theme_name
        stylesheet = DARK_THEME_STYLESHEET if theme_name == "dark" else LIGHT_THEME_STYLESHEET
        self.setStyleSheet(stylesheet)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

