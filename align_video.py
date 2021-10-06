# This Python file uses the following encoding: utf-8

# Imports
from pathlib import Path
import subprocess
import re


class VideoAligner:
    def __init__(self):
        self.output_video_path = str(Path(self.video_path).parent \
                                     / ('corrected_' + Path(self.video_path).stem + '.mp4'))
        first_stimulus = self.data_dict['first_stimulus']
        corrected_video_length = self.data_dict['corrected_video_length']
        dummy_frame_index = self.data_dict['dummy_frame_index']

        # Filter command
        cmd = 'ffmpeg -y -i "' + self.video_path + '"' +  " -vf setpts='PTS+1/" + str(self.frame_rate) + '/TB*('   #TODO warn if rounding too much
        for n_frame, frame_id in enumerate(dummy_frame_index):
            if n_frame == 0:
                cmd += 'gte(N\,' + str(frame_id - n_frame - 1) + ')'
            else:
                cmd += '+gte(N\,' + str(frame_id - n_frame - 1) + ')'
        cmd += ")' -ss " + str(first_stimulus/self.frame_rate) + ' -t ' + str((corrected_video_length +
                    first_stimulus)/self.frame_rate) + ' -r ' + str(self.frame_rate) + \
                    ' -c:v libxvid "' + self.output_video_path + '"'

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True,
                                   universal_newlines=True)
        for line in process.stdout:
            m = re.search('frame=.*?fps', line)
            if m:
                frame = int(m.group(0)[6:-3])
                progress = round(100 * frame / corrected_video_length)
                self.pbar_alignVid.setValue(progress)
                cur_speed_regex = re.search('speed=.*?x', line)
                cur_speed = float(cur_speed_regex.group(0)[6:-1])
                t_left = round((corrected_video_length - frame) / self.frame_rate / cur_speed)
                if t_left >= 0:  # Catch a weird edge case where things go negative
                    s_left = t_left % 60
                    t_left = (t_left - s_left) / 60
                    m_left = int(t_left % 60)
                    h_left = int((t_left - m_left) / 60)
                    """label.setText(f"Time left: {h_left}h,{m_left}m,{s_left}s")""" #TODO Add label back into GUI
                else:
                    """label.setText(f"Time left: 0h,0m,0s")
                    label.adjustSize()"""
                self.app.processEvents()
        process.terminate()
