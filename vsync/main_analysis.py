# This Python file uses the following encoding: utf-8

# Imports
from pathlib import Path
import ffmpeg
import cv2
from scipy import signal as sg
import numpy as np
import matplotlib.pyplot as mpl
import pickle


def find_dropped_frames(video_path, interval=3):
    # Load data
    pkl_path = str(Path(video_path).parent / (Path(video_path).stem + '.pkl'))
    data_dict = pickle.load(open(pkl_path, 'rb'))
    raw_values = np.array(data_dict['raw_values'])

    # Parameters
    frame_rate = int(ffmpeg.probe(video_path)['streams'][0]['avg_frame_rate'][0:-2])
    data_dict['frame_rate'] = frame_rate
    stimulus_interval = interval * frame_rate
    data_dict['stimulus_interval'] = stimulus_interval

    # Threshold
    f_roi = raw_values - sg.medfilt(raw_values, 101)  # 1d med filter
    threshold = max(f_roi) / 2
    data_dict['threshold'] = threshold

    stimulus_onset = np.where(f_roi > threshold)[0]
    frame_interval = np.insert(np.diff(stimulus_onset), 0, stimulus_interval)

    stimulus_onset = stimulus_onset[frame_interval > .95 * stimulus_interval]  # remove frames with signal bleed-over
    frame_interval = np.diff(stimulus_onset)
    data_dict['stimulus_onset'] = stimulus_onset
    data_dict['frame_interval'] = frame_interval

    # Dummy frame index
    dropped_frames = np.where(frame_interval < stimulus_interval)[0]
    data_dict['dropped_frames'] = dropped_frames

    next_frame = frame_interval[dropped_frames]
    sum_frames = frame_interval[dropped_frames] + next_frame
    dropped_frames = dropped_frames[sum_frames != 2 * stimulus_interval]
    dummy_frame_index = stimulus_onset[dropped_frames + 1] - 1
    data_dict['dummy_frame_index'] = dummy_frame_index

    corrected_video_length = stimulus_onset[-1] - stimulus_onset[0] + len(dummy_frame_index)
    data_dict['corrected_video_length'] = corrected_video_length
    data_dict['first_stimulus'] = stimulus_onset[0]

    # Save data
    pickle.dump(data_dict, open(pkl_path, 'wb'))


def plot_results(video_path):
    # Load data
    pkl_path = str(Path(video_path).parent / (Path(video_path).stem + '.pkl'))
    data_dict = pickle.load(open(pkl_path, 'rb'))
    raw_values = data_dict['raw_values']
    stimulus_onset = data_dict['stimulus_onset']
    frame_interval = data_dict['frame_interval']
    stimulus_interval = data_dict['stimulus_interval']

    # Intensity vs. time
    fig, ax = mpl.subplots(2, 2)
    fig.tight_layout()
    ax[0, 0].plot(raw_values)
    ax[0, 0].scatter(stimulus_onset[0], raw_values[stimulus_onset[0]]*1.02, \
                     c='r', marker='v')
    ax[0, 0].title.set_text('Intensity')

    # Frames vs. interval
    ax[1, 0].plot(frame_interval)
    ax[1, 0].set_ylim(stimulus_interval - 5, stimulus_interval*1.002)
    ax[1, 0].title.set_text('Frame Interval')

    # Frame-drop histogram
    ax[1, 1].hist(frame_interval - stimulus_interval, np.arange(-5, 0), align='right')
    ax[1, 1].set_yticks([])
    ax[1, 1].title.set_text('Frame-drop Histogram')

    # First signal onset
    video_object = cv2.VideoCapture(video_path)
    video_object.set(1, stimulus_onset[0])
    first_signal_frame = video_object.read()[1]
    ax[0, 1].imshow(first_signal_frame)
    ax[0, 1].set_xticks([])
    ax[0, 1].set_yticks([])
    ax[0, 1].title.set_text('First Frame')

    mpl.show()
