#!usr/bin/env python3

import cv2
import subprocess
import numpy as np
from pathlib import Path
import ffmpeg
import os
import pickle
import re
from datetime import datetime

class VideoReader:
    def read_video(self):
        # Select ROI
        VideoReader.get_roi(self)

        # Convert video to xvid (for faster analysis)
        VideoReader.convert_video(self)

        # Frame-by-frame analysis
        video_object = cv2.VideoCapture(self.temp_video_path)
        n_frames = video_object.get(cv2.CAP_PROP_FRAME_COUNT)

        video_object.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.raw_values = []
        while video_object.isOpened():
            ret, frame = video_object.read()
            if ret:
                frame_mean = np.mean(frame, axis=(0, 1, 2))
                self.raw_values.append(frame_mean)
            else:
                break

        # Save data to pickle file
        VideoReader.save_read_video(self)

        # Delete temp video
        video_object.release()
        try:
            os.remove(self.temp_video_path)
        except OSError:
            pass

        # Update btn_diag
        self.btn_diag.setEnabled(True)

    def get_roi(self):
        video_object = cv2.VideoCapture(self.video_path)
        self.frame_rate = int(ffmpeg.probe(self.video_path)['streams'][0]['avg_frame_rate'][0:-2])

        first_frame = video_object.read(1)[1]
        self.roi = cv2.selectROI(first_frame)
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        # Round to even (ffmpeg will only crop to even-pixel-number width/height)
        self.roi = np.array(self.roi)
        if self.roi[2] % 2:
            self.roi[2] = self.roi[2] + 1

        if self.roi[3] % 2:
            self.roi[3] = self.roi[3] + 1

        roi = np.roll(self.roi, 2)  # ffmpeg-python docs say [x, y, w, h], but must be wrong (i.e., [w, h, x, y])


    def convert_video(self):
        path_obj = Path(self.video_path)
        self.temp_video_path = str(path_obj.parent / ('temp_' + path_obj.stem +'.mp4'))
        cmd = ['ffmpeg -y -i "', self.video_path, '" -filter:v crop=', str(self.roi[0]), ':', str(self.roi[1]), \
               ':', str(self.roi[2]), ':', str(self.roi[3]), ' -c:v libxvid "', self.temp_video_path, '"']

        process = subprocess.Popen(''.join(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, \
                               shell=True, universal_newlines=True)

        cap = cv2.VideoCapture(self.video_path)
        length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for line in process.stdout:
            m = re.search('frame=.*?fps', line)
            if m:
                frame = int(m.group(0)[6:-3])
                progress = round(100 * frame / length)
                self.pbar_readVid.setValue(progress)
                cur_speed_regex = re.search('speed=.*?x', line)
                cur_speed = float(cur_speed_regex.group(0)[6:-1])
                t_left = round((length - frame) / self.frame_rate / cur_speed)
                if t_left >= 0:  # Catch a weird edge case where things go negative
                    s_left = t_left % 60
                    t_left = (t_left - s_left) / 60
                    m_left = int(t_left % 60)
                    h_left = int((t_left - m_left) / 60)
                    """label.setText(f"Time left: {h_left}h,{m_left}m,{s_left}s")"""    # TODO re-insert label into GUI
                else:
                    """label.setText(f"Time left: 0h,0m,0s")
                    label.adjustSize()"""
                self.app.processEvents()
        process.terminate()


    def save_read_video(self):
        self.data_dict = {}
        self.data_dict['video_path'] = self.video_path
        self.data_dict['temp_video_path'] = self.temp_video_path
        self.data_dict['roi'] = self.roi
        self.data_dict['raw_values'] = self.raw_values

        self.pkl_path = str(Path(self.video_path).parent / (Path(self.video_path).stem + '.pkl'))
        pickle.dump(self.data_dict, open(self.pkl_path, 'wb'))
