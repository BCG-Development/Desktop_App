# System Information App

This application displays real-time system information and allows you to run internet speed tests. It is built using Python and the PySide6 library for the graphical user interface.

## Features

- Display CPU usage, memory usage, disk usage, network activity, processes count, and process uptime.
- Run internet speed tests and display the result.

## Prerequisites

- Python 3
- Pip (Python package installer)

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/system-information-app.git
    ```

2. **Navigate to the project directory:**

    ```bash
    cd system-information-app
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the application:**

    ```bash
    python main.py
    ```

2. The main window will open, displaying real-time system information.

3. **Click the "Run Speed Test" button to perform an internet speed test. The result will be displayed, including the time of the last test.**

4. **Click the "Refresh" button to manually refresh the system information.**

5. **Click the "Quit" button to close the application.**

## Notes

- The application uses PySide6 for the GUI, psutil for system information retrieval, and speedtest for internet speed testing.

- The system information is updated every second, and the speed test can be manually triggered.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
