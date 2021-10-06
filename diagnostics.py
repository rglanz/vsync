#!/usr/bin/env python3

from pathlib import Path
import numpy as np
import pickle
import cv2
from scipy import signal as sg
from matplotlib import pyplot as mpl


class Diagnostics:
    def __init__(self):
        # Load data
        self.pkl_path = str(Path(self.video_path).parent / (Path(self.video_path).stem + '.pkl'))
        self.data_dict = pickle.load(open(self.pkl_path, 'rb'))
        self.raw_values = np.array(self.data_dict['raw_values'])

        Diagnostics.find_dropped_frames(self)
        Diagnostics.plot_diagnostics(self)

    def find_dropped_frames(self):
        self.led_interval = int(float(self.textbox_led.text()))
        stimulus_interval = self.led_interval * self.frame_rate

        # Threshold
        f_roi = self.raw_values - sg.medfilt(self.raw_values, 101)  # 1d med filter
        self.threshold = max(f_roi) / 2
        self.data_dict['threshold'] = self.threshold

        stimulus_onset = np.where(f_roi > self.threshold)[0]
        frame_interval = np.insert(np.diff(stimulus_onset), 0, stimulus_interval)

        stimulus_onset = stimulus_onset[
            frame_interval > .95 * stimulus_interval]  # remove frames with signal bleed-over
        frame_interval = np.diff(stimulus_onset)
        self.data_dict['stimulus_onset'] = stimulus_onset
        self.data_dict['frame_interval'] = frame_interval

        # Dummy frame index
        dropped_frames = np.where(frame_interval < stimulus_interval)[0]
        self.data_dict['dropped_frames'] = dropped_frames

        next_frame = frame_interval[dropped_frames]
        sum_frames = frame_interval[dropped_frames] + next_frame
        dropped_frames = dropped_frames[sum_frames != 2 * stimulus_interval]
        dummy_frame_index = stimulus_onset[dropped_frames + 1] - 1
        self.data_dict['dummy_frame_index'] = dummy_frame_index

        corrected_video_length = stimulus_onset[-1] - stimulus_onset[0] + len(dummy_frame_index)
        self.data_dict['corrected_video_length'] = corrected_video_length
        self.data_dict['first_stimulus'] = stimulus_onset[0]

        # Save data
        pickle.dump(self.data_dict, open(self.pkl_path, 'wb'))

    def plot_diagnostics(self):
        stimulus_onset = self.data_dict['stimulus_onset']
        frame_interval = self.data_dict['frame_interval']
        stimulus_interval = self.led_interval * self.frame_rate

        # Open plot
        mpl.switch_backend('Qt5Agg')
        fig, ax = mpl.subplots(2, 2)
        fig.tight_layout()
        fig_window = mpl.get_current_fig_manager()
        fig_window.window.showMaximized()

        # Intensity vs. time
        ax[0, 0].plot(self.raw_values)
        ax[0, 0].scatter(stimulus_onset[0], self.raw_values[stimulus_onset[0]]*1.02, c='r', marker='v')
        ax[0, 0].set_ylabel('Intensity (0–255)')
        ax[0, 0].set_xlabel('Frame #')
        ax[0, 0].title.set_text('Raw ROI Intensity')

        # Frames vs. interval
        ax[1, 0].plot(frame_interval)
        ax[1, 0].set_ylim(stimulus_interval - 5, stimulus_interval*1.002)
        ax[1, 0].set_ylabel('Frames per interval')
        ax[1, 0].set_xlabel('Interval #')
        ax[1, 0].title.set_text('Frame Interval')

        # Frame-drop histogram
        ax[1, 1].hist(frame_interval - stimulus_interval, np.arange(-5, 0), align='right')
        ax[1, 1].set_yticks([])
        ax[1, 1].set_xticks(np.arange(-5, 0))
        ax[1, 1].set_ylabel('Frequency')
        ax[1, 1].set_xlabel('# of dropped frames')
        ax[1, 1].title.set_text('Frame-drop Histogram')

        # First signal onset
        video_object = cv2.VideoCapture(self.video_path)
        video_object.set(1, stimulus_onset[0])
        first_signal_frame = video_object.read()[1]
        ax[0, 1].imshow(first_signal_frame)
        ax[0, 1].set_xticks([])
        ax[0, 1].set_yticks([])

        mpl.show()

        # Update btn_AlignVid / GUI
        self.btn_alignVid.setEnabled(True)
        self.pbar_diag.setValue(100)
