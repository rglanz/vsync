# This Python file uses the following encoding: utf-8
# TODO add Windows path support
# TODO remove hard-coded path after testing

# Imports
import ffmpeg
from pathlib import Path

video_path = Path('/Users/Ryan/Downloads/demo_video.mp4')
video_output_path = str(video_path.parent / ('reindex_' + video_path.name))

(
    ffmpeg
    .input(video_path)
    .output(video_output_path,**{'map': 0}, **{'c': 'copy'})
    .run()
)
