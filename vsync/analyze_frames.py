# This Python file uses the following encoding: utf-8
# TODO remove hard-coded path after testing

# Imports
import numpy as np
from decord import VideoReader
from decord import cpu
from tqdm import tqdm

def analyze_frames(file_path):
    roi = np.array([0, 0, 100, 100])  # vsync, y, width, height
    batch_size = 10

    # load the VideoReader
    vr = VideoReader(file_path, ctx=cpu(0))  # can set to cpu or gpu .. ctx=gpu(0)
    video_length = len(vr)

    frame_index = np.reshape(np.arange(0, video_length, 1), (-1, batch_size))
    roi_values = np.zeros(np.shape(frame_index))

    for n_batch, n_index in enumerate(  tqdm(frame_index)   ):
        frames = vr.get_batch(n_index).asnumpy()
        frames_roi = frames[:, roi[1]:roi[3], roi[0]:roi[2], 0]
        batch_mean = np.mean(frames_roi, axis=(1, 2))

        roi_values[n_batch, :] = batch_mean

    print(roi_values[0])
