# This Python file uses the following encoding: utf-8

# Imports
from pathlib import Path
import pickle
import subprocess
import re
from datetime import datetime


def align_video(video_path, pbar, label, app):
    # Load data
    pkl_path = str(Path(video_path).parent / (Path(video_path).stem + '.pkl'))
    data_dict = pickle.load(open(pkl_path, 'rb'))

    # Parameters
    output_video_path = str(Path(video_path).parent / ('corrected_' + Path(video_path).stem + '.mp4'))
    frame_rate = data_dict['frame_rate']
    first_stimulus = data_dict['first_stimulus']
    corrected_video_length = data_dict['corrected_video_length']
    dummy_frame_index = data_dict['dummy_frame_index']

    # Filter command
    cmd = 'ffmpeg -y -i "' + video_path + '"' +  " -vf setpts='PTS+1/" + str(frame_rate) + '/TB*('   #TODO add in non-int frame rate rounding
    for n_frame, frame_id in enumerate(dummy_frame_index):
        if n_frame == 0:
            cmd += 'gte(N,' + str(frame_id - n_frame - 1) + ')'
        else:
            cmd += '+gte(N,' + str(frame_id - n_frame - 1) + ')'
    cmd += ")' -ss " + str(first_stimulus/frame_rate) + ' -t ' + str((corrected_video_length + first_stimulus)/frame_rate) + ' -r ' + str(frame_rate) + ' -c:v libxvid "' + output_video_path + '"'

    print(cmd)

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        print(line)
        m = re.search('frame=.*?fps', line)
        if m:
            frame = int(m.group(0)[6:-3])
            progress = round(100 * frame / corrected_video_length)
            pbar.setValue(progress)
            cur_speed_regex = re.search('speed=.*?x', line)
            cur_speed = float(cur_speed_regex.group(0)[6:-1])
            t_left = round((corrected_video_length - frame) / 100 / cur_speed)  # TODO: 100 should be frame rate, pass into func and correct
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
