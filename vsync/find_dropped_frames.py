# This Python file uses the following encoding: utf-8
# TODO convert csv input to attribute of self
# TODO remove hardcoded frame rate, interval

# Imports
import numpy as np
from scipy import signal as sg

# Parameters
roi_linear = np.genfromtxt('/Users/Ryan/Downloads/LEDTimes.csv', dtype='float')
frame_rate = 100
interval = 3

# Threshold
f_roi = roi_linear - sg.medfilt(roi_linear, 101)  # 1d med filter
threshold = max(f_roi) / 2
signal_onset = np.where(f_roi > threshold)[0]
d_signal_onset = np.insert(np.diff(signal_onset), 0, frame_rate*interval)

signal_onset = signal_onset[d_signal_onset > .95*frame_rate*interval]   # remove frames with signal bleed-over
d_signal_onset = np.diff(signal_onset)

# Dummy Frames
dropped_frames = np.where(d_signal_onset < frame_rate*interval)[0]
next_frame = d_signal_onset[dropped_frames + 1]
sum_frames = d_signal_onset[dropped_frames] + next_frame
dropped_frames = dropped_frames[sum_frames != 2*frame_rate*interval]
dummy_frame_index = signal_onset[dropped_frames + 1] - 1

corrected_video_length = signal_onset[-1] - signal_onset[0] + len(dummy_frame_index)
