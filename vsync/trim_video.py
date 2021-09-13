# This Python file uses the following encoding: utf-8
# TODO remove hard-coded path after testing

# Imports
import ffmpeg
import os

# Parameters
video_path = '/Users/Ryan/Downloads/temp_reindex_demo_video.mp4'
video_output_path = '/Users/Ryan/Downloads/final_demo_video.mp4'
frame_start = 10    #TODO remove hard-coded frame

# Trim video to first LED
(
    ffmpeg
    .input(video_path)
    .trim(start_frame=frame_start)
    .output(video_output_path)
    .run()
)

# Delete temporary video
os.remove(video_path)   #TODO make sure the filepath is correct
