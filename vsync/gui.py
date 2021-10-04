import subprocess
import sys
import time
import re
import cv2

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pathlib import Path
import align_video
import main_analysis
import read_video


class VideoSyncher(QWidget):

    def __init__(self, app):
        super().__init__()
        self.app = App
        # calling initUI method
        self.initUI()

    # method for creating widgets
    def initUI(self):
        self.w = 380
        self.h = 420

        # creating SelectVideo button
        self.btn_selectVid = QPushButton('Select Video', self)
        # changing its position
        self.btn_selectVid.setGeometry(5, 5, 120, 60)
        # adding action to push button
        self.btn_selectVid.clicked.connect(self.pick_vid)

        # creating ReadVideo button
        self.btn_readVid = QPushButton('Read Video', self)
        # changing its position
        self.btn_readVid.setGeometry(5, 90, 120, 60)
        # adding action to push button
        self.btn_readVid.clicked.connect(self.read_vid)
        self.btn_readVid.setEnabled(False)

        # creating Diagnostics button
        self.btn_diag = QPushButton('Diagnostics', self)
        # changing its position
        self.btn_diag.setGeometry(5, 215, 120, 60)
        # adding action to push button
        self.btn_diag.clicked.connect(self.diagnostics_vid)
        self.btn_diag.setEnabled(False)

        # creating AlignVideo button
        self.btn_alignVid = QPushButton('Align Video', self)
        # changing its position
        self.btn_alignVid.setGeometry(5, 280, 120, 60)
        # adding action to push button
        self.btn_alignVid.clicked.connect(self.align_vid)
        self.btn_alignVid.setEnabled(False)

        # Create directory label
        self.label_dir = QLabel('Video Directory:', self)
        self.label_dir.move(7, 70)

        # Create read_eta label
        self.label_read_eta = QLabel('', self)
        self.label_read_eta.move(7, 193)

        # Create align_eta label
        self.label_align_eta = QLabel('', self)
        self.label_align_eta.move(7, 380)

        # Create led_interval label
        self.label_led_interval = QLabel('LED Interval (seconds):', self)
        self.label_led_interval.move(160, 9)

        # Create textbox for LED interval
        self.textbox_led = QLineEdit(self)
        self.textbox_led.move(195, 25)
        self.textbox_led.resize(30, 30)
        self.textbox_led.setText('3.0')
        self.textbox_led.setAlignment(Qt.AlignCenter)

        # creating progress bar
        self.pbar_read = QProgressBar(self)
        self.pbar_align = QProgressBar(self)

        # setting its geometry
        self.pbar_read.setGeometry(5, 155, 250, 30)
        self.pbar_align.setGeometry(5, 345, 250, 30)

        # setting window geometry
        self.setGeometry(300, 300, self.w, self.h)
        # setting window action
        self.setWindowTitle("VideoSyncher")

        # showing all the widgets
        self.show()

    # Function to select video directory
    def pick_vid(self):
        dialog = QFileDialog()
        file_path = dialog.getOpenFileName(None, "Select Folder")
        self.file_path = file_path[0]
        self.label_dir.setText('Video Directory: ' + file_path[0])
        self.label_dir.adjustSize()
        self.label_dir.repaint()
        self.btn_readVid.setEnabled(True)
        self.btn_diag.setEnabled(True)
        self.btn_alignVid.setEnabled(True)

    # Function to read video
    def read_vid(self):
        read_video.read_video(self.file_path, self.pbar_read, self.label_read_eta, self.app)
        main_analysis.find_dropped_frames(self.file_path, float(self.textbox_led.text()))
        # self.btn_diag.setEnabled(True)

    # Function to view dropped frame diagnostics
    def diagnostics_vid(self):
        main_analysis.plot_results(self.file_path)

    # Function to view dropped frame diagnostics
    def align_vid(self):
        align_video.align_video(self.file_path, self.pbar_align, self.label_align_eta, self.app)


# main method
if __name__ == '__main__':
    # create pyqt5 app
    App = QApplication(sys.argv)

    # create the instance of our Window
    window = VideoSyncher(App)

    # start the app
    sys.exit(App.exec())