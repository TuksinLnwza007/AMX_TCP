from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QPushButton, 
    QApplication, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon
import sys


class SerialInputDialog(QDialog):

    def __init__(self, parent=None, title: str = "Scan / Enter Serial Number"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.serial = None
        self.timeout_ms = 60000
        self.elapsed = 0

        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header with icon/emoji
        header = QLabel("🔍 Serial Number")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Description
        label = QLabel("Please scan the barcode with your scanner or type the serial number below:")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Input field with frame
        input_frame = QFrame()
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(0, 10, 0, 10)
        
        self.line = QLineEdit(self)
        self.line.setPlaceholderText("Enter or scan serial number...")
        self.line.returnPressed.connect(self._on_ok)
        self.line.setMinimumHeight(45)
        input_layout.addWidget(self.line)
        
        layout.addWidget(input_frame)

        # Progress bar for timeout
        self.progress = QProgressBar(self)
        self.progress.setMaximum(100)
        self.progress.setValue(100)
        self.progress.setTextVisible(False)
        self.progress.setMaximumHeight(4)
        layout.addWidget(self.progress)

        # Timeout label
        self.timeout_label = QLabel("Time remaining: 60s")
        self.timeout_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timeout_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.timeout_label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._on_ok)
        self.ok_btn.setMinimumHeight(40)
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.setDefault(True)
        btn_layout.addWidget(self.ok_btn)

        layout.addLayout(btn_layout)

        self.setMinimumWidth(480)
        self.setMinimumHeight(320)

    def _apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            
            QLabel {
                color: #333;
            }
            
            QLineEdit {
                padding: 12px 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                font-size: 14px;
                color: #333;
            }
            
            QLineEdit:focus {
                border: 2px solid #0066cc;
                background-color: #fff;
            }
            
            QLineEdit:hover {
                border: 2px solid #999;
            }
            
            QPushButton {
                padding: 10px 30px;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            
            QPushButton#ok_btn, QPushButton:default {
                background-color: #0066cc;
                color: white;
            }
            
            QPushButton#ok_btn:hover, QPushButton:default:hover {
                background-color: #0052a3;
            }
            
            QPushButton#ok_btn:pressed, QPushButton:default:pressed {
                background-color: #003d7a;
            }
            
            QPushButton#cancel_btn {
                background-color: #e0e0e0;
                color: #333;
            }
            
            QPushButton#cancel_btn:hover {
                background-color: #d0d0d0;
            }
            
            QPushButton#cancel_btn:pressed {
                background-color: #c0c0c0;
            }
            
            QProgressBar {
                border: none;
                border-radius: 2px;
                background-color: #e0e0e0;
            }
            
            QProgressBar::chunk {
                background-color: #0066cc;
                border-radius: 2px;
            }
        """)
        
        self.ok_btn.setObjectName("ok_btn")
        self.cancel_btn.setObjectName("cancel_btn")

    def showEvent(self, event):
        super().showEvent(event)

        # Focus and select all
        QTimer.singleShot(0, lambda: (self.line.setFocus(), self.line.selectAll()))

        # Start timeout countdown
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(100)  # Update every 100ms

    def _update_progress(self):
        self.elapsed += 100
        remaining_ms = self.timeout_ms - self.elapsed
        
        if remaining_ms <= 0:
            self.timer.stop()
            self._on_timeout()
            return
        
        # Update progress bar
        progress = int((remaining_ms / self.timeout_ms) * 100)
        self.progress.setValue(progress)
        
        # Update label
        remaining_sec = remaining_ms / 1000
        self.timeout_label.setText(f"Time remaining: {remaining_sec:.1f}s")
        
        # Change color when time is running out
        if remaining_sec <= 10:
            self.progress.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #cc0000;
                }
            """)
            self.timeout_label.setStyleSheet("color: #cc0000; font-size: 11px; font-weight: bold;")

    def _on_ok(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        text = self.line.text().strip()
        if text == "":
            self.serial = 0
        else:
            self.serial = text
        self.accept()

    def _on_cancel(self):
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        self.serial = 0
        self.reject()

    def _on_timeout(self):
        if self.isVisible():
            self.serial = 0
            self.reject()

    def exec_and_get(self):
        dlg_code = self.exec()
        if self.serial is None:
            return 0
        return self.serial


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
    
#     # Set application-wide font
#     app.setFont(QFont("Segoe UI", 10))
    
#     dlg = SerialInputDialog()
#     result = dlg.exec_and_get()

#     if result == 0:
#         print('Timeout / Cancel / Dialog closed -> returned 0')
#     else:
#         print('Serial received:', repr(result))

#     sys.exit(0)