# Card-Sequence-Validator-Single-Station

The Card Sequence Validator (Single Station) is a desktop application designed to validate sequences of cards in real-time. It provides a user-friendly interface for managing card sequence files (CPD), configuring UDP network endpoints and serial communication ports for scanner input and PLC output, and monitoring validation processes with automated mismatch detection and skip approvals.

## Features

*   **Intuitive User Interface:** Built with PyQt6, featuring a clean and responsive design with theme toggling (Dark/Light).
*   **Job Sequence File Management:** Supports loading and parsing card sequence data from `.cpd` file formats with customizable re-batching and Top-to-Bottom or Bottom-to-Top scan directions.
*   **Checksum Handling:** Strip customizable checksum digits (0–5 digits) from scanned codes.
*   **Network & COM Port Configuration:** Configure UDP scanner listener, UDP PLC trigger output, and on-demand serial COM ports with live ping latency and connectivity tests.
*   **Real-time Scanning & Logging:** Monitor live scanner input, previous validated ID, and next expected ID.
*   **Mismatch Approval:** Interactive skip approval dialog allows operators to advance the sequence if a card was skipped.
*   **Secure Administration:** Password-protected hardware and network settings with automatic timeout/lock on focus loss.

## Installation

1.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    ```

2.  **Activate the virtual environment:**
    *   **Windows:**
        ```bash
        .venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To start the application, run `main.py`:

```bash
python main.py
```

## Project Structure

```
Card-Sequence-Validator-Single-Station/
├───main.py                 # Main application entry point
├───requirements.txt        # Project dependencies
├───constants.py            # Application-wide constants
├───output_formats.json     # Defines output data formats
├───assets/                 # Application assets (icons, images)
│   ├───favicon.ico
│   ├───gear_loader.gif
│   ├───Icon.png
│   └───logo.png
└───src/
    ├───app_state.py        # Single-station application state and caching
    ├───card_types.py       # Single, Half, and Quarter card configurations
    ├───logic/
    │   └───file_parser.py  # CPD file parsing and re-batching
    ├───services/
    │   ├───licensing.py    # Windows CIM/Registry machine fingerprinting
    │   ├───udp_reader.py   # Async UDP listener
    │   ├───udp_writer.py   # Async UDP sender
    │   ├───com_reader.py   # Serial COM reader
    │   └───utilities.py    # Network and ping utilities
    └───ui/
        ├───main_application.py # Main dashboard window
        ├───file_management.py  # Job file management and sequence tools
        ├───network_setup.py    # Network and COM configuration
        ├───scanner_logging.py  # Live scanner inspection and validation logs
        ├───styles.py           # Application stylesheets
        └───widgets.py          # Custom UI widgets
```
