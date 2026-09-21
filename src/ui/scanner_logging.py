# src/ui/scanner_logging.py
"""
Single Station Live Status and Logs Window
Displays real-time scan verification, sequence status, and paginated validation logs.
Handles mismatch approvals and log exports.
"""

import sys
import os
import csv
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QAbstractItemView, QStackedLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QApplication, QGridLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QMovie
from .styles import DARK_THEME_STYLESHEET, LIGHT_THEME_STYLESHEET
from .widgets import ClockWidget, ApprovalDialog
from ..card_types import CardType


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ScannerLoggingWindow(QMainWindow):
    """Single-station live scanner inspection and validation logging window"""
    def __init__(self, app_state):
        super().__init__()
        self.app_state = app_state
        self.setWindowTitle("Live Status and Logs - Single Station")
        self.setMinimumSize(1000, 750)

        # Pagination
        self.current_page = 0
        self.items_per_page = 100
        self.total_log_entries = []
        self.filtered_log_entries = []

        self.update_theme(self.app_state.current_theme)
        self.app_state.theme_changed.connect(self.update_theme)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(35, 25, 35, 25)
        main_layout.setSpacing(20)

        self.create_header(main_layout)
        self.create_control_panel(main_layout)
        self.create_scanner_section(main_layout)
        self.create_validation_log(main_layout)

        # Connect signals
        self.app_state.log_updated.connect(self.on_log_updated)
        self.app_state.log_cleared.connect(self.on_log_cleared)
        self.app_state.state_changed.connect(self.update_displays)
        self.app_state.card_type_changed.connect(self.rebuild_log_table)
        self.app_state.mismatch_found_in_sequence.connect(self.show_approval_dialog)

        # Load existing logs if already in state
        if self.app_state.log_data:
            self.on_log_updated(self.app_state.log_data)

        self.update_displays()

    def create_header(self, parent_layout):
        layout = QHBoxLayout()
        title = QLabel("Live Status and Logs")
        title.setObjectName("h1")

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(ClockWidget())
        parent_layout.addLayout(layout)

    def create_control_panel(self, parent_layout):
        panel = QFrame()
        panel.setObjectName("accentPanel")
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(15)

        self.start_btn = QPushButton("▶ Start Validation")
        self.start_btn.setObjectName("primary")
        self.start_btn.clicked.connect(self.start_scanning_clicked)

        self.stop_btn = QPushButton("⏹ Stop Validation")
        self.stop_btn.setObjectName("secondary")
        self.stop_btn.clicked.connect(self.app_state.stop_scanning)

        self.clear_logs_btn = QPushButton("🗑 Clear Logs")
        self.clear_logs_btn.setObjectName("secondary")
        self.clear_logs_btn.clicked.connect(self.clear_logs_clicked)

        self.export_logs_btn = QPushButton("💾 Export Logs")
        self.export_logs_btn.setObjectName("secondary")
        self.export_logs_btn.clicked.connect(self.download_logs)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.clear_logs_btn)
        layout.addWidget(self.export_logs_btn)
        layout.addStretch()

        parent_layout.addWidget(panel)

    def create_scanner_section(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)

        columns_layout = QGridLayout()
        columns_layout.setSpacing(15)

        self.scanner_input_label = QLabel("Awaiting Scan Input...")
        self.current_card_label = QLabel("N/A")
        self.next_card_label = QLabel("No file loaded")

        columns_layout.addWidget(self.create_display_column("Last Scanned ID", self.scanner_input_label), 0, 0)
        columns_layout.addWidget(self.create_display_column("Previous Validated ID", self.current_card_label), 0, 1)
        columns_layout.addWidget(self.create_display_column("Next Expected ID", self.next_card_label), 0, 2)

        layout.addLayout(columns_layout)
        parent_layout.addWidget(frame)

    def create_display_column(self, title_text, data_label):
        column = QFrame()
        column.setObjectName("accentPanel")
        layout = QVBoxLayout(column)
        layout.setSpacing(5)
        title = QLabel(title_text)
        title.setObjectName("subtitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_label.setObjectName("accent")
        data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        data_label.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(data_label)
        return column

    def create_validation_log(self, parent_layout):
        frame = QFrame()
        frame.setObjectName("panel")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()
        title = QLabel("Scan Validation Log")
        title.setObjectName("h2")
        header_layout.addWidget(title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.log_table = QTableWidget()
        self.setup_log_table_columns()
        self.log_table.setAlternatingRowColors(True)
        self.log_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.log_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.log_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(self.log_table)

        # Optional loader
        loading_label = QLabel()
        loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gear_path = resource_path("assets/gear_loader.gif")
        if os.path.exists(gear_path):
            movie = QMovie(gear_path)
            loading_label.setMovie(movie)
            movie.start()
        else:
            loading_label.setText("Processing...")
        self.stacked_layout.addWidget(loading_label)

        layout.addLayout(self.stacked_layout, 1)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        self.first_page_button = QPushButton("<<")
        self.prev_page_button = QPushButton("<")
        self.page_status_label = QLabel("Page 0 of 0")
        self.next_page_button = QPushButton(">")
        self.last_page_button = QPushButton(">>")

        pagination_layout.addWidget(self.first_page_button)
        pagination_layout.addWidget(self.prev_page_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_status_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_page_button)
        pagination_layout.addWidget(self.last_page_button)
        layout.addLayout(pagination_layout)

        self.first_page_button.clicked.connect(self.go_to_first_page)
        self.prev_page_button.clicked.connect(self.go_to_previous_page)
        self.next_page_button.clicked.connect(self.go_to_next_page)
        self.last_page_button.clicked.connect(self.go_to_last_page)

        parent_layout.addWidget(frame, 1)

    def setup_log_table_columns(self):
        if self.app_state.card_type == CardType.SINGLE:
            self.log_table.setColumnCount(5)
            self.log_table.setHorizontalHeaderLabels(["Entry #", "Time", "Scanned ID", "Expected ID", "Result"])
            header = self.log_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        else:
            self.log_table.setColumnCount(6)
            self.log_table.setHorizontalHeaderLabels(["Entry #", "Time", "Scanned ID", "Expected ID", "Result", "Scan Side"])
            header = self.log_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

    def on_log_updated(self, new_entries):
        self.total_log_entries.extend(new_entries)
        self.filtered_log_entries.extend(new_entries)
        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        self.current_page = max(0, total_pages - 1)
        self.update_pagination_controls()
        self.display_current_page()

    def on_log_cleared(self):
        self.total_log_entries = []
        self.filtered_log_entries = []
        self.current_page = 0
        self.scanner_input_label.setText("Awaiting Scan Input...")
        self.current_card_label.setText("N/A")
        self.next_card_label.setText("Start scanning to set start card" if self.app_state.expected_cards else "No file loaded")
        self.update_pagination_controls()
        self.display_current_page()

    def show_approval_dialog(self, scanned_code, num_skipped, future_index):
        dialog = ApprovalDialog(
            "Sequence Mismatch Detected",
            f"The scanned card ({scanned_code}) was found {num_skipped} position(s) ahead of the expected sequence. Would you like to advance the sequence to this card?",
            parent=self
        )
        approved = dialog.exec()

        if approved:
            self.stacked_layout.setCurrentIndex(1)
            QApplication.processEvents()

        self.app_state.resolve_mismatch(scanned_code, approved, future_index)

    def start_scanning_clicked(self):
        if self.app_state.log_data:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Existing Logs Found")
            msg_box.setText("There are existing logs in the table.")
            msg_box.setInformativeText("Do you want to download and clear the logs before starting a new scan?")
            clear_button = msg_box.addButton("Download, Clear & Start", QMessageBox.ButtonRole.AcceptRole)
            continue_button = msg_box.addButton("Continue with Existing Logs", QMessageBox.ButtonRole.DestructiveRole)
            cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
            msg_box.exec()

            clicked = msg_box.clickedButton()
            if clicked == clear_button:
                if self.download_logs():
                    self.app_state.clear_logs()
                    self.app_state.start_scanning()
                else:
                    return
            elif clicked == continue_button:
                self.app_state.start_scanning()
        else:
            self.app_state.start_scanning()

    def clear_logs_clicked(self):
        if not self.app_state.log_data:
            QMessageBox.information(self, "No Logs", "No logs to clear.")
            return

        reply = QMessageBox.question(
            self, "Clear Logs",
            "Are you sure you want to clear all validation logs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.app_state.clear_logs()

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
                        indexed_entry['timestamp'] = log_entry.get("timestamp", "")
                        indexed_entry['scanned_code'] = log_entry.get("scanned_code", "")
                        indexed_entry['expected_code'] = expected_code
                        indexed_entry['status'] = log_entry.get("status", "")

                        if self.app_state.card_type != CardType.SINGLE:
                            indexed_entry['scanned_side'] = log_entry.get("scanned_side", "")

                        writer.writerow(indexed_entry)

                QMessageBox.information(self, "Success", f"Logs saved to {file_path}")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save logs: {e}")
                return False

        return False

    def display_current_page(self):
        self.log_table.setUpdatesEnabled(False)
        self.log_table.setRowCount(0)

        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        entries_to_display = self.filtered_log_entries[start_index:end_index]

        for log_entry in entries_to_display:
            row_position = self.log_table.rowCount()
            self.log_table.insertRow(row_position)

            expected_code = log_entry["expected_code"]
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

            self.log_table.setItem(row_position, 0, QTableWidgetItem(display_numcard))
            self.log_table.setItem(row_position, 1, QTableWidgetItem(log_entry["timestamp"]))
            self.log_table.setItem(row_position, 2, QTableWidgetItem(log_entry["scanned_code"]))
            self.log_table.setItem(row_position, 3, QTableWidgetItem(log_entry["expected_code"]))

            status_item = QTableWidgetItem(log_entry["status"])
            if "NOT OK" in log_entry["status"]:
                status_item.setForeground(QColor("#e74c3c"))
            elif "SKIPPED" in log_entry["status"]:
                status_item.setForeground(QColor("#f39c12"))
            elif "OK" in log_entry["status"]:
                status_item.setForeground(QColor("#2ecc71"))

            self.log_table.setItem(row_position, 4, status_item)

            if self.app_state.card_type != CardType.SINGLE:
                self.log_table.setItem(row_position, 5, QTableWidgetItem(log_entry.get("scanned_side", "N/A")))

        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if self.current_page == total_pages - 1:
            self.log_table.scrollToBottom()

        self.log_table.setUpdatesEnabled(True)
        self.log_table.viewport().update()
        self.stacked_layout.setCurrentIndex(0)

    def update_pagination_controls(self):
        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if total_pages == 0:
            total_pages = 1

        self.page_status_label.setText(f"Page {self.current_page + 1} of {total_pages}")
        self.first_page_button.setEnabled(self.current_page > 0)
        self.prev_page_button.setEnabled(self.current_page > 0)
        self.next_page_button.setEnabled(self.current_page < total_pages - 1)
        self.last_page_button.setEnabled(self.current_page < total_pages - 1)

    def go_to_first_page(self):
        self.current_page = 0
        self.display_current_page()
        self.update_pagination_controls()

    def go_to_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
        self.display_current_page()
        self.update_pagination_controls()

    def go_to_next_page(self):
        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
        self.display_current_page()
        self.update_pagination_controls()

    def go_to_last_page(self):
        total_items = len(self.filtered_log_entries)
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        self.current_page = max(0, total_pages - 1)
        self.display_current_page()
        self.update_pagination_controls()

    def update_displays(self):
        is_scanning = self.app_state.is_scanning
        has_port = bool(self.app_state.main_scanner_config)
        has_file = bool(self.app_state.expected_cards)

        self.start_btn.setEnabled(not is_scanning and has_port and has_file)
        self.stop_btn.setEnabled(is_scanning)

        idx = self.app_state.current_card_index
        cards = self.app_state.expected_cards

        if self.app_state.scan_direction == "bottom_to_top" and cards:
            actual_idx = len(cards) - 1 - idx
        else:
            actual_idx = idx

        if self.app_state.card_type == CardType.SINGLE:
            scan_side_index = 1
        elif self.app_state.card_type == CardType.HALF:
            scan_side_index = 1 if self.app_state.scan_side == 'left' else 2
        elif self.app_state.card_type == CardType.QUARTER:
            position_map = {"bottom_left": 1, "top_left": 2, "top_right": 3, "bottom_right": 4}
            scan_side_index = position_map.get(self.app_state.scan_side, 1)
        else:
            scan_side_index = 1

        if cards and idx > 0 and 0 <= actual_idx < len(cards):
            prev_actual_idx = len(cards) - idx if self.app_state.scan_direction == "bottom_to_top" else idx - 1
            if 0 <= prev_actual_idx < len(cards):
                self.current_card_label.setText(cards[prev_actual_idx][scan_side_index])
            else:
                self.current_card_label.setText("N/A")
        elif has_file and idx == 0:
            self.current_card_label.setText("N/A")
        else:
            self.current_card_label.setText("No file loaded")

        if cards and idx < len(cards) and 0 <= actual_idx < len(cards):
            if self.app_state.start_card_has_been_scanned:
                self.next_card_label.setText(cards[actual_idx][scan_side_index])
            else:
                self.next_card_label.setText("Start scanning to set start card")
        elif has_file and self.app_state.start_card_has_been_scanned:
            self.next_card_label.setText("End of Sequence")
        elif has_file:
            self.next_card_label.setText("Start scanning to set start card")
        else:
            self.next_card_label.setText("No file loaded")

        if self.app_state.log_data:
            last_log = self.app_state.log_data[-1]
            self.scanner_input_label.setText(last_log["scanned_code"])
        else:
            self.scanner_input_label.setText("Awaiting Scan Input...")

    def rebuild_log_table(self, card_type):
        self.setup_log_table_columns()
        self.display_current_page()

    def update_theme(self, theme_name):
        stylesheet = DARK_THEME_STYLESHEET if theme_name == "dark" else LIGHT_THEME_STYLESHEET
        self.setStyleSheet(stylesheet)
        for widget in self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

