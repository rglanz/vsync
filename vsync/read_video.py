# This Python file uses the following encoding: utf-8

# Imports
import cv2
import ffmpeg
import numpy as np
from pathlib import Path
from tqdm import tqdm
import os
import pickle

def get_roi(video_path):
    # Gets the ROI for the stimulus (e.g., LED)
    video_object = cv2.VideoCapture(video_path)
    first_frame = video_object.read(1)[1]
    roi = cv2.selectROI(first_frame)    # TODO suppress output
    cv2.waitKey(1)
    cv2.destroyAllWindows()
    cv2.waitKey(1)

    # Round to even (ffmpeg will only crop to even-pixel-number width/height)
    roi = np.array(roi)
    if roi[2]%2:
        roi[2] = roi[2] + 1

    if roi[3]%2:
        roi[3] = roi[3] + 1

    roi = np.roll(roi, 2)   # ffmpeg-python docs say [x, y, w, h], but must be wrong (i.e., [w, h, x, y])
    return roi


def convert_video(video_path, roi):
    # Convert original video to LED only, low quality. Saves on analysis time.
    path_obj = Path(video_path)
    temp_video_path = str(path_obj.parent / ('temp_' + path_obj.stem +'.mp4'))

    print('Converting video...', flush=True)
    (
        ffmpeg
        .input(video_path)
        .filter('crop', *roi)
        .output(temp_video_path, **{'c:v': 'libxvid'})
        .run(overwrite_output=True)
    )
    return temp_video_path


def read_video(video_path):
    # Analyze frames (after getting roi and converting video)
    roi = get_roi(video_path)
    temp_video_path = convert_video(video_path, roi)

    print('Reading frames...', flush=True)
    video_object = cv2.VideoCapture(temp_video_path)
    n_frames = video_object.get(cv2.CAP_PROP_FRAME_COUNT)

    video_object.set(cv2.CAP_PROP_POS_FRAMES, 0)
    raw_values = []
    p_bar = tqdm(total=int(n_frames))
    while video_object.isOpened():
        ret, frame = video_object.read()
        if ret:
            frame_mean = np.mean(frame, axis=(0, 1, 2))
            raw_values.append(frame_mean)
            p_bar.update()
        else:
            break

    # Save pickle
    save_video(video_path, temp_video_path, roi, raw_values)

    # Delete temp video
    video_object.release()
    try:
        os.remove(temp_video_path)
    except OSError:
        pass


def save_video(video_path, temp_video_path, roi, raw_values):
    # Save relevant data in pickle file
    data_dict = {}
    data_dict['video_path'] = video_path
    data_dict['temp_video_path'] = temp_video_path
    data_dict['roi'] = roi
    data_dict['raw_values'] = raw_values

    pkl_path = str(Path(video_path).parent / (Path(video_path).stem + '.pkl'))
    pickle.dump(data_dict, open(pkl_path, 'wb'))
