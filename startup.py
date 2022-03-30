#!/usr/bin/env python3

from PyQt5.Qt import QApplication, Qt, QMainWindow, QFileDialog, QPixmap
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QProgressBar, \
                            QDesktopWidget, QGridLayout, QMessageBox
from PyQt5.QtGui import QImage
import numpy as np
import cv2
import sys
from pathlib import Path
import pickle

from src.read_video import VideoReader
from src.diagnostics import Diagnostics
from src.align_video import VideoAligner


class VideoSync(QMainWindow):
    def __init__(self, app):
        super().__init__()
        _, _, self.screen_w, self.screen_h = QDesktopWidget().screenGeometry(-1).getRect()
        self.screen_geometry = np.array([0.25 * self.screen_w, 0.125 * self.screen_h,
                                0.50 * self.screen_w, 0.75 * self.screen_h], dtype=int)
        self.setGeometry(*self.screen_geometry)
        self.app = app

        self.create_gui_elements()
        self.arrange_gui_elements()


    def create_gui_elements(self):
        ### Video Frame ###
        self.plot_window = QLabel('Load Video')
        self.plot_window.setStyleSheet('color : gray')
        self.video_isLoaded = False     # Event filter for label function
        self.plot_window.mousePressEvent = self.file_dialog

        ### Buttons ###
        # Read Video
        self.lbl_readVid = QLabel('1.')
        self.btn_readVid = QPushButton('Read Video', self)
        self.btn_readVid.setEnabled(False)
        self.btn_readVid.clicked.connect(lambda: VideoReader.read_video(self))

        # Diagnostics
        self.lbl_diag = QLabel('2.')
        self.btn_diag = QPushButton('Diagnostics', self)
        self.btn_diag.setEnabled(False)
        self.btn_diag.clicked.connect(lambda: Diagnostics.__init__(self))

        # Align Video
        self.lbl_alignVid = QLabel('3.')
        self.btn_alignVid = QPushButton('Align Video', self)
        self.btn_alignVid.setEnabled(False)
        self.btn_alignVid.clicked.connect(lambda: VideoAligner.__init__(self))

        # Read pkl
        self.btn_readPkl = QPushButton('Read .pkl', self)
        self.btn_readPkl.setEnabled(False)
        self.btn_readPkl.clicked.connect(self.load_data)

        ### Progress Bars ###
        self.pbar_readVid = QProgressBar(self)
        self.pbar_diag = QProgressBar(self)
        self.pbar_alignVid = QProgressBar(self)

        ### Labels ###
        self.lbl_left = QLabel()
        self.lbl_center = QLabel()
        self.lbl_right = QLabel()
        self.lbl_ledInterval = QLabel('LED Interval (s)')

        ### Textboxes ###
        self.textbox_led = QLineEdit(self)
        self.textbox_led.setText('3.0')
        self.textbox_led.setAlignment(Qt.AlignCenter)
        self.textbox_led.setFocusPolicy(Qt.ClickFocus)


    def arrange_gui_elements(self):
        # Controls Layout
        self.control_layout = QGridLayout()
        self.control_layout.addWidget(self.lbl_readVid, 0, 0, 1, 1)
        self.control_layout.addWidget(self.btn_readVid, 0, 1, 1, 1)
        self.control_layout.addWidget(self.pbar_readVid, 0, 3, 1, 3)
        self.control_layout.addWidget(self.lbl_diag, 1, 0, 1, 1)
        self.control_layout.addWidget(self.btn_diag, 1, 1, 1, 1)
        self.control_layout.addWidget(self.pbar_diag, 1, 3, 1, 3)
        self.control_layout.addWidget(self.lbl_alignVid, 2, 0, 1, 1)
        self.control_layout.addWidget(self.btn_alignVid, 2, 1, 1, 1)
        self.control_layout.addWidget(self.pbar_alignVid, 2, 3, 1, 3)
        self.control_layout.addWidget(self.lbl_ledInterval, 3, 1, 1, 2, alignment=Qt.AlignCenter)
        self.control_layout.addWidget(self.textbox_led, 3, 3, 1, 1, alignment=Qt.AlignLeft)
        self.control_layout.addWidget(self.btn_readPkl, 3, 8, 1, 2, alignment=Qt.AlignRight)
        self.control_layout.setColumnStretch(1, 1)
        self.control_layout.setColumnStretch(2, 0)
        self.control_layout.setColumnStretch(3, 3)

        # Media Layout
        self.media_layout = QGridLayout()
        self.media_layout.addWidget(self.plot_window, 0, 0, 8, 10, alignment=Qt.AlignCenter)
        self.media_layout.addWidget(self.lbl_left, 9, 2, 1, 2, alignment=Qt.AlignCenter)
        self.media_layout.addWidget(self.lbl_center, 9, 4, 1, 2, alignment=Qt.AlignCenter)
        self.media_layout.addWidget(self.lbl_right, 9, 6, 1, 2, alignment=Qt.AlignCenter)
        self.media_layout.addLayout(self.control_layout, 11, 0, 1, 9)
        self.media_layout.setRowStretch(9, 0)

        # Show GUI
        self.media_widget = QWidget()
        self.media_widget.setLayout(self.media_layout)
        self.media_widget.setFocusPolicy(Qt.ClickFocus)
        self.setCentralWidget(self.media_widget)
        self.setWindowTitle("vsync")


    def file_dialog(self, event):
        if self.video_isLoaded:
            pass
        else:
            dialog = QFileDialog()
            file_path = dialog.getOpenFileName(None, "Select Folder")
            self.video_path = file_path[0]

            self.setWindowTitle(self.video_path)
            video_object = cv2.VideoCapture(self.video_path)
            first_frame = video_object.read(1)[1].astype(np.int8)
            frame_data = QImage(first_frame, first_frame.shape[1], first_frame.shape[0], QImage.Format_RGB888)

            pix_map = QPixmap(frame_data)
            self.plot_window.setPixmap(pix_map)
            self.btn_readVid.setEnabled(True)
            self.btn_readPkl.setEnabled(True)
            self.video_isLoaded = True


    def load_data(self):
        self.pkl_path = Path(self.video_path).parent / (Path(self.video_path).stem + '.pkl')
        if self.pkl_path.is_file():
            # Load data
            self.data_dict = pickle.load(open(str(self.pkl_path), 'rb'))    #this code is not portable
            self.btn_diag.setEnabled(True)
        else:
            message = QMessageBox()
            message.setWindowTitle('vsync')
            message.setText("No .pkl found.")
            message.exec_()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_0:
            self.file_dialog(event)
        if event.key() == Qt.Key_1:
            VideoReader.read_video(self)
        if event.key() == Qt.Key_2:
            Diagnostics.__init__(self)
        if event.key() == Qt.Key_3:
            VideoAligner.__init__(self)
        if event.key() == Qt.Key_R:
            self.load_data(event)


# Execute
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoSync(app)
    window.show()
    sys.exit(app.exec())
