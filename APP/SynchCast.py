import sys
import numpy as np
import sounddevice as sd
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGroupBox, QSpacerItem, QSizePolicy, QScrollArea, QCheckBox, QFrame, QSlider, QGridLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import subprocess
from PyQt5.QtWidgets import QGraphicsDropShadowEffect

class AudioRouterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SynchCast – Multi-Device Audio Sharing')
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #f7f7f7;")
        self.layout = QVBoxLayout()
        self.layout.setSpacing(18)
        self.layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel('SynchCast – Multi-Device Audio Sharing')
        title.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                padding-top: 15px;
                padding-bottom: 10px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }
        """)
        self.layout.addWidget(title)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 2)
        shadow.setColor(Qt.gray)
        title.setGraphicsEffect(shadow)


        # Device List Title (standalone label)
        device_list_title = QLabel('Available Output Devices')
        device_list_title.setFont(QFont('Segoe UI', 13, QFont.Bold))
        device_list_title.setStyleSheet('color: #fff; margin-bottom: 8px; margin-top: 18px; letter-spacing: 0.5px;')
        self.layout.addWidget(device_list_title)

        # Device List Group (no title)
        device_group = QGroupBox()
        device_group.setStyleSheet('QGroupBox { border: 1.5px solid #232a36; border-radius: 12px; background: #181c24; margin-top: 0px; }')
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(0)

        # Scroll area for checkboxes
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet('background: #f0f4fa; border-radius: 10px; border: 1px solid #cfd8dc;')
        self.device_widget = QWidget()
        self.device_layout = QVBoxLayout()
        self.device_layout.setSpacing(10)
        self.device_widget.setLayout(self.device_layout)
        self.scroll_area.setWidget(self.device_widget)
        group_layout.addWidget(self.scroll_area)
        device_group.setLayout(group_layout)
        self.layout.addWidget(device_group)

        # Start/Stop Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton('Start Broadcasting')
        self.start_btn.setStyleSheet("padding: 8px 18px; font-size: 16px; background: #4caf50; color: white;")
        self.stop_btn = QPushButton('Stop Broadcasting')
        self.stop_btn.setStyleSheet("padding: 8px 18px; font-size: 16px; background: #f44336; color: white;")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        self.layout.addLayout(btn_layout)

        self.refresh_devices()
        self.setLayout(self.layout)

        self.start_btn.clicked.connect(self.start_broadcasting)
        self.stop_btn.clicked.connect(self.stop_broadcasting)

        self.broadcasting = False
        self.broadcast_thread = None
        self.output_checkboxes = []

        self.selected_order = []  # Track order of selected device indices

        self.setFixedSize(900, 600)  # Make window fixed size
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)  # Remove maximize button

    def refresh_devices(self):
        # Remove old widgets
        while self.device_layout.count():
            item = self.device_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        devices = sd.query_devices()
        exclude_keywords = [
            'Sound Mapper', 'Hands-Free', 'Intelligo', 'System', 'Mapper', 'HAP', 'Utility', '%',
            'Virtual Audio Cable', 'Line 1', 'Line Out', 'Primary Sound Driver'
        ]
        seen_names = set()
        self.device_controls = []  # List of (checkbox, slider, device_idx)
        grid = QGridLayout()
        grid.setContentsMargins(10, 10, 10, 10)
        grid.setSpacing(12)
        # Header row
        header_font = QFont('Segoe UI', 11, QFont.Bold)
        header_style = "color: #b0b0b0; background: transparent;"
        grid.addWidget(self._header_label('Use', header_font, header_style), 0, 0)
        grid.addWidget(self._header_label('Audio Device', header_font, header_style), 0, 1)
        grid.addWidget(self._header_label('Volume', header_font, header_style), 0, 2)
        row = 1
        for real_idx, dev in enumerate(devices):
            name = dev['name']
            if (
                dev['max_output_channels'] > 0 and
                not any(x in name for x in exclude_keywords) and
                name not in seen_names
            ):
                seen_names.add(name)
                # Icon selection
                icon_file = None
                lower_name = name.lower()
                if any(x in lower_name for x in ['headphone', 'headset']):
                    icon_file = 'headphone.png'
                elif any(x in lower_name for x in ['speaker', 'audio', 'output']):
                    icon_file = 'speaker.png'
                # Checkbox
                checkbox = QCheckBox()
                checkbox.setProperty('device_idx', real_idx)
                checkbox.setStyleSheet("QCheckBox { margin-left: 8px; margin-right: 8px; } QCheckBox::indicator { width: 20px; height: 20px; }")
                # Device label with icon
                dev_layout = QHBoxLayout()
                dev_layout.setContentsMargins(0, 0, 0, 0)
                dev_layout.setSpacing(8)
                dev_layout.setAlignment(Qt.AlignVCenter)
                if icon_file:
                    icon_label = QLabel()
                    icon_label.setPixmap(QPixmap(icon_file).scaled(22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    icon_label.setFixedSize(26, 26)  # Add some space for perfect vertical alignment
                    icon_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                    dev_layout.addWidget(icon_label)
                dev_name_label = QLabel(name)
                dev_name_label.setStyleSheet("color: #222; font-size: 16px; font-family: 'Segoe UI', 'Roboto', 'San Francisco', Arial, sans-serif; font-weight: bold;")
                dev_name_label.setFont(QFont('Segoe UI', 15, QFont.Bold))
                dev_name_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                dev_layout.addWidget(dev_name_label)
                dev_layout.addStretch(1)
                dev_widget = QWidget()
                dev_widget.setLayout(dev_layout)
                # Slider and percentage label
                slider_layout = QHBoxLayout()
                slider_layout.setContentsMargins(0, 0, 0, 0)
                slider_layout.setSpacing(8)
                slider = QSlider(Qt.Horizontal)
                slider.setMinimum(0)
                slider.setMaximum(100)
                slider.setValue(100)
                slider.setSingleStep(1)
                slider.setTickInterval(10)
                slider.setTickPosition(QSlider.NoTicks)
                slider_enabled_style = """
                    QSlider::groove:horizontal {
                        border: 1px solid #0d0d0d;
                        height: 8px;
                        background: #232a36;
                        border-radius: 4px;
                    }
                    QSlider::handle:horizontal {
                        background: #2196f3;
                        border: 1px solid #2196f3;
                        width: 18px;
                        margin: -5px 0;
                        border-radius: 9px;
                    }
                    QSlider::sub-page:horizontal {
                        background: #2196f3;
                        border-radius: 4px;
                    }
                    QSlider::add-page:horizontal {
                        background: #444;
                        border-radius: 4px;
                    }
                """
                slider_disabled_style = """
                    QSlider::groove:horizontal {
                        border: 1px solid #0d0d0d;
                        height: 8px;
                        background: #232a36;
                        border-radius: 4px;
                    }
                    QSlider::handle:horizontal {
                        background: #a5d0f2;
                        border: 1px solid #a5d0f2;
                        width: 18px;
                        margin: -5px 0;
                        border-radius: 9px;
                    }
                    QSlider::sub-page:horizontal {
                        background: #a5d0f2;
                        border-radius: 4px;
                    }
                    QSlider::add-page:horizontal {
                        background: #444;
                        border-radius: 4px;
                    }
                """
                slider.setStyleSheet(slider_disabled_style)
                slider.setEnabled(False)  # Start disabled
                def on_checkbox_state_changed(state, slider=slider, idx=real_idx):
                    if state == Qt.Checked:
                        slider.setEnabled(True)
                        slider.setStyleSheet(slider_enabled_style)
                        if idx not in self.selected_order:
                            self.selected_order.append(idx)
                    else:
                        slider.setEnabled(False)
                        slider.setStyleSheet(slider_disabled_style)
                        if idx in self.selected_order:
                            self.selected_order.remove(idx)
                checkbox.stateChanged.connect(on_checkbox_state_changed)
                percent_label = QLabel("100%")
                percent_label.setFixedWidth(44)
                percent_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                percent_label.setStyleSheet("color: #2196f3; font-size: 15px; font-weight: bold;")
                def update_label(val, label=percent_label):
                    label.setText(f"{val}%")
                slider.valueChanged.connect(update_label)
                slider_layout.addWidget(slider)
                slider_layout.addWidget(percent_label)
                slider_widget = QWidget()
                slider_widget.setLayout(slider_layout)
                grid.addWidget(checkbox, row, 0, alignment=Qt.AlignCenter)
                grid.addWidget(dev_widget, row, 1)
                grid.addWidget(slider_widget, row, 2)
                self.device_controls.append((checkbox, slider, real_idx))
                # If checkbox is checked on refresh, ensure order is preserved
                if checkbox.isChecked() and real_idx not in self.selected_order:
                    self.selected_order.append(real_idx)
                row += 1
        # Set the grid layout
        self.device_layout.addLayout(grid)

    def _header_label(self, text, font, style):
        label = QLabel(text)
        label.setFont(font)
        label.setStyleSheet(style)
        return label

    def get_selected_output_indices(self):
        # Only return indices that are still checked and in the current device_controls
        checked_indices = set(idx for cb, slider, idx in self.device_controls if cb.isChecked())
        return [idx for idx in self.selected_order if idx in checked_indices]

    def get_device_volumes(self):
        # Returns a dict: device_idx -> volume (0.0 to 1.0)
        return {idx: slider.value() / 100.0 for cb, slider, idx in self.device_controls if cb.isChecked()}

    def set_vac_default(self):
        from PyQt5.QtWidgets import QMessageBox
        try:
            subprocess.run(["./nircmd.exe", "setdefaultsounddevice", "Line 1"], check=True)
            QMessageBox.information(self, "Success", "Synchcast (Line 1) has been set as the default output device.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to Synchcast Line 1 as default output.\n{e}")

    def start_broadcasting(self):
        from PyQt5.QtWidgets import QMessageBox
        import time
        # Step 1: Set VAC as default output
        try:
            subprocess.run(["./nircmd.exe", "setdefaultsounddevice", "Line 1"], check=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to set 'Line 1 (Virtual Audio Cable)' as default output.\n{e}")
            return False
        # Step 2: Wait 1 second
        time.sleep(1)
        # Step 3: Start broadcasting
        selected_outputs = self.get_selected_output_indices()
        print('Selected output device indices:', selected_outputs)
        if not selected_outputs:
            QMessageBox.warning(self, "No Output Selected", "Please select at least one output device.")
            return False
        if self.broadcasting:
            return False
        self.broadcasting = True
        self.broadcast_thread = threading.Thread(target=self.broadcast_audio, daemon=True)
        self.broadcast_thread.start()
        QMessageBox.information(self, "Success", "Broadcasting started and 'Line 1 (Virtual Audio Cable)' set as default output.")
        return True

    def stop_broadcasting(self):
        from PyQt5.QtWidgets import QMessageBox
        # Step 1: Stop broadcasting
        self.broadcasting = False
        # Step 2: Set default output back to Speakers
        try:
            subprocess.run(["./nircmd.exe", "setdefaultsounddevice", "Speakers"], check=True)
            QMessageBox.information(self, "Success", "Broadcasting stopped and default output set to 'Speakers'.")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Broadcasting stopped, but failed to set default output to 'Speakers'.\n{e}")
            return False

    def broadcast_audio(self):
        devices = sd.query_devices()
        vac_idx = None
        for idx, dev in enumerate(devices):
            if dev['max_input_channels'] > 0 and 'Line 1' in dev['name']:
                vac_idx = idx
                break
        if vac_idx is None:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", "Could not find 'Line 1' (VAC) input device.")
            self.broadcasting = False
            return
        selected_outputs = self.get_selected_output_indices()
        if not selected_outputs:
            return
        # Use VAC's default sample rate and channels
        vac_info = devices[vac_idx]
        samplerate = int(vac_info['default_samplerate'])
        channels = min(2, vac_info['max_input_channels'])
        # Prepare output streams and volume controls
        output_streams = []
        output_sliders = []
        try:
            for cb, slider, out_idx in self.device_controls:
                if cb.isChecked() and out_idx in selected_outputs:
                    out_info = devices[out_idx]
                    out_channels = min(2, out_info['max_output_channels'])
                    stream = sd.OutputStream(device=out_idx, samplerate=samplerate, channels=out_channels, dtype='float32')
                    stream.start()
                    output_streams.append((stream, slider))
            # Input stream from VAC
            with sd.InputStream(device=vac_idx, channels=channels, samplerate=samplerate, dtype='float32') as in_stream:
                while self.broadcasting:
                    data, _ = in_stream.read(512)
                    for stream, slider in output_streams:
                        try:
                            volume = slider.value() / 100.0
                            stream.write(data * volume)
                        except Exception:
                            pass
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Audio routing failed:\n{e}")
        finally:
            for stream, _ in output_streams:
                try:
                    stream.stop()
                    stream.close()
                except Exception:
                    pass
            self.broadcasting = False

    def setup_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #181c24;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1.5px solid #232a36;
                border-radius: 12px;
                margin-top: 12px;
                font-size: 17px;
                font-weight: bold;
                color: #fff;
                background: #181c24;
            }
            QLabel {
                color: #e0e0e0;
            }
            QPushButton {
                background: #232a36;
                color: #e0e0e0;
                border-radius: 8px;
                border: 1.5px solid #232a36;
                font-size: 15px;
                font-family: 'Segoe UI', 'Roboto', 'San Francisco', Arial, sans-serif;
                padding: 10px 24px;
            }
            QPushButton:hover {
                background: #2196f3;
                color: #fff;
                border: 1.5px solid #2196f3;
            }
            QCheckBox::indicator {
                background: #232a36;
                border: 1.5px solid #444;
                width: 20px;
                height: 20px;
                border-radius: 6px;
            }
            QCheckBox::indicator:checked {
                background: #2196f3;
                border: 1.5px solid #2196f3;
            }
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 8px;
                background: #232a36;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2196f3;
                border: 1px solid #2196f3;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::sub-page:horizontal {
                background: #2196f3;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #444;
                border-radius: 4px;
            }
        """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AudioRouterGUI()
    window.setup_dark_theme()
    window.show()
    sys.exit(app.exec_())
