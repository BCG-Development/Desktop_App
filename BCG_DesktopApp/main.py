import sys
import os
import psutil
import platform
import speedtest
from datetime import datetime
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer, Qt, QThread, Signal
from PySide6.QtGui import QFont

class SystemInfoRetrievalThread(QThread):
    """
    A thread class for retrieving system information and running speed tests.
    """

    update_signal = Signal(str)
    speed_test_complete_signal = Signal(float, str)  # Signal for speed test completion

    def __init__(self):
        super().__init__()
        self.speed_test_requested = False
        self.last_speed_test_time = None
        self.last_speed_test_result = None

    def run(self):
        while not self.isInterruptionRequested():
            try:
                system_info = self.get_system_info()
                self.update_signal.emit(system_info)

                if self.speed_test_requested:
                    speed_info = self.get_speed_test()
                    self.last_speed_test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.last_speed_test_result = f"Internet Speed: {speed_info:.2f} Mbps"
                    self.speed_test_complete_signal.emit(speed_info, self.last_speed_test_time)
                    self.speed_test_requested = False

            except Exception as e:
                print(f"Error retrieving system info: {e}")

            self.msleep(1000)  # Sleep for 1000 milliseconds (1 second)

    def get_system_info(self):
        """
        Retrieve and format system information.
        """
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        network_info = psutil.net_io_counters()
        uptime = self.get_uptime()
        processes_count = self.get_processes_count()

        platform_info = f"Platform: {platform.system()} {platform.release()} {platform.machine()}"
        return (
            f"{platform_info}\n"
            f"CPU Usage: {cpu_percent:.2f}%\n"
            f"Memory Usage: {memory_info.percent:.2f}%\n"
            f"Disk Usage: {disk_info.percent:.2f}%\n"
            f"Network Sent: {network_info.bytes_sent / (1024 * 1024):.2f} MB\n"
            f"Network Received: {network_info.bytes_recv / (1024 * 1024):.2f} MB\n"
            f"Processes Count: {processes_count}\n"
            f"Uptime: {uptime}"
        )

    def get_uptime(self):
        """
        Get and format the process uptime.
        """
        process_create_time = psutil.Process(os.getpid()).create_time()
        uptime_seconds = psutil.time.time() - process_create_time
        minutes, _ = divmod(uptime_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return f"{days} days, {hours} hours, {minutes} minutes"

    def get_speed_test(self):
        """
        Run a speed test and return the download speed in Mbps.
        """
        st = speedtest.Speedtest()
        st.get_best_server()  # Choose the best server automatically
        download_speed = st.download() / 1024 / 1024  # Convert to Mbps
        return download_speed

    def request_speed_test(self):
        """
        Set the flag to request a speed test on the next iteration.
        """
        self.speed_test_requested = True

    def get_processes_count(self):
        """
        Get the count of running processes.
        """
        return len(list(psutil.process_iter()))

class SystemInfoApp(QWidget):
    """
    Main application window for displaying system information.
    """

    def __init__(self):
        super().__init__()

        self.init_ui()

        self.thread = SystemInfoRetrievalThread()
        self.thread.update_signal.connect(self.update_info_label)
        self.thread.speed_test_complete_signal.connect(self.update_speed_test_info)
        self.thread.start()

        self.check_thread_timer = QTimer(self)
        self.check_thread_timer.timeout.connect(self.check_thread)
        self.check_thread_timer.start(1000)  # Check every 1 second

    def init_ui(self):
        """
        Initialize the user interface.
        """
        self.setWindowTitle("System Information")
        self.setGeometry(100, 100, 500, 250)

        self.info_label = QLabel(self)
        self.info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.info_label.setFont(QFont("Helvetica", 12))

        layout = QVBoxLayout(self)
        layout.addWidget(self.info_label)

        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.refresh_info)
        layout.addWidget(self.refresh_button)

        self.speed_test_button = QPushButton("Run Speed Test", self)
        self.speed_test_button.clicked.connect(self.request_speed_test)
        layout.addWidget(self.speed_test_button)

        self.last_speed_test_label = QLabel(self)
        layout.addWidget(self.last_speed_test_label)

        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(self.close)
        layout.addWidget(self.quit_button)

    def update_info_label(self, system_info):
        """
        Update the information label with the latest system information.
        """
        self.info_label.setText(system_info)

    def update_speed_test_info(self, speed_info, last_speed_test_time):
        """
        Update the label with the result of the last speed test.
        """
        self.last_speed_test_label.setText(f"Last Speed Test ({last_speed_test_time}): {speed_info:.2f} Mbps")

    def check_thread(self):
        """
        Check if the retrieval thread is still running. If not, stop the timer.
        """
        if not self.thread.isRunning():
            self.check_thread_timer.stop()
            self.info_label.setText("Thread stopped. Check your system.")

    def refresh_info(self):
        """
        Manually trigger a refresh of system information.
        """
        self.thread.get_system_info()  # Update the information immediately

    def request_speed_test(self):
        """
        Request a speed test from the retrieval thread.
        """
        self.thread.request_speed_test()

    def closeEvent(self, event):
        """
        Handle the close event. Request thread interruption and wait for it to finish.
        """
        self.thread.requestInterruption()
        self.thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = SystemInfoApp()
    main_window.show()
    sys.exit(app.exec())
