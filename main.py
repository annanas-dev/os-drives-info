import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer, Qt


def get_drives_info():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if bitmask & 1:
            drive_letter = f'{letter}:\\'
            try:
                free_bytes_available = ctypes.c_ulonglong(0)
                total_number_of_bytes = ctypes.c_ulonglong(0)
                total_number_of_free_bytes = ctypes.c_ulonglong(0)

                ctypes.windll.kernel32.GetDiskFreeSpaceExW(drive_letter, ctypes.byref(free_bytes_available),
                                                           ctypes.byref(total_number_of_bytes),
                                                           ctypes.byref(total_number_of_free_bytes))

                type_name = ctypes.create_unicode_buffer(1024)
                ctypes.windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(drive_letter), None, 0, None, None,
                                                             None, ctypes.byref(type_name), 1024)

                drives.append({
                    'letter': drive_letter,
                    'type': type_name.value if type_name.value else 'Unknown',
                    'total': total_number_of_bytes.value,
                    'free': total_number_of_free_bytes.value,
                })
            except Exception as e:
                print(e)
        bitmask >>= 1
    return drives


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Drive Info')
        self.setGeometry(100, 100, 450, 200)

        self.table_widget = QTableWidget()
        self.setCentralWidget(self.table_widget)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(['Drive', 'Type', 'Total Space', 'Free Space'])

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_drive_info)
        self._update_period_ms = 120_000  # 2 минуты
        self.timer.start(self._update_period_ms)

        self.update_drive_info()

    def update_drive_info(self):
        drives = get_drives_info()
        self.table_widget.setRowCount(len(drives))
        for i, drive in enumerate(drives):
            self.table_widget.setItem(i, 0, self.make_read_only(QTableWidgetItem(drive['letter'])))
            self.table_widget.setItem(i, 1, self.make_read_only(QTableWidgetItem(drive['type'])))

            self.table_widget.setItem(i, 2,
                                      self.make_read_only(QTableWidgetItem(f'{drive["total"] // (1024 ** 3)} GB')))
            self.table_widget.setItem(i, 3, self.make_read_only(QTableWidgetItem(f'{drive["free"] // (1024 ** 3)} GB')))

    def make_read_only(self, item):
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
