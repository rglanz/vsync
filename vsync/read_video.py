# This Python file uses the following encoding: utf-8

# Imports
import cv2
import subprocess
import numpy as np
from pathlib import Path
from tqdm import tqdm
import os
import pickle
import re
from datetime import datetime


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


def convert_video(video_path, roi, pbar, label, app):
    # Convert original video to LED only, low quality. Saves on analysis time.
    path_obj = Path(video_path)
    temp_video_path = str(path_obj.parent / ('temp_' + path_obj.stem +'.mp4'))
    cmd = 'ffmpeg -y -i ' + video_path + ' -filter:v crop=' + str(roi[0]) + ':' + str(roi[1]) + ':' + str(roi[2]) + \
          ':' + str(roi[3]) + ' -c:v libxvid ' + temp_video_path


    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    cap = cv2.VideoCapture(video_path)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for line in process.stdout:
        print(line)
        m = re.search('frame=.*?fps', line)
        if m:
            frame = int(m.group(0)[6:-3])
            progress = round(100 * frame / length)
            pbar.setValue(progress)
            cur_speed_regex = re.search('speed=.*?x', line)
            cur_speed = float(cur_speed_regex.group(0)[6:-1])
            t_left = round((length - frame) / 100 / cur_speed)  #TODO: 100 should be frame rate, pass into func and correct
            if t_left >= 0:  # Catch a weird edge case where things go negative
                s_left = t_left % 60
                t_left = (t_left - s_left) / 60
                m_left = int(t_left % 60)
                h_left = int((t_left - m_left) / 60)
                label.setText(f"Time left: {h_left}h,{m_left}m,{s_left}s")
            else:
                label.setText(f"Time left: 0h,0m,0s")
            label.adjustSize()
            app.processEvents()
    process.terminate()
    return temp_video_path


def read_video(video_path, pbar, label, app):
    # Analyze frames (after getting roi and converting video)
    roi = get_roi(video_path)
    temp_video_path = convert_video(video_path, roi, pbar, label, app)

    print('Analyzing frames...', flush=True)
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
    save_read_video(video_path, temp_video_path, roi, raw_values)

    # Delete temp video
    video_object.release()
    try:
        os.remove(temp_video_path)
    except OSError:
        pass


def save_read_video(video_path, temp_video_path, roi, raw_values):
    # Save relevant data in pickle file
    data_dict = {}
    data_dict['video_path'] = video_path
    data_dict['temp_video_path'] = temp_video_path
    data_dict['roi'] = roi
    data_dict['raw_values'] = raw_values

    pkl_path = str(Path(video_path).parent / (Path(video_path).stem + '.pkl'))
    pickle.dump(data_dict, open(pkl_path, 'wb'))
