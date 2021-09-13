# This Python file uses the following encoding: utf-8

# Imports
import ffmpeg

# Parameters
video_path = '/Users/Ryan/Downloads/reindex_demo_video.mp4'
video_output_path = '/Users/Ryan/Downloads/temp_reindex_demo_video.mp4'
frame_rate = 100
dummy_frame_index = [1, 100, 1000]  # TODO test array, remove

# Filter command
filter_command = 'PTS+1/' + str(frame_rate) + '/TB*('   #TODO add in non-int frame rate rounding
for n_frame, frame_id in enumerate(dummy_frame_index):
    if n_frame == 0:
        filter_command = filter_command + 'gte(N,' + str(frame_id - n_frame) + ')'
    else:
        filter_command = filter_command + '+gte(N,' + str(frame_id - n_frame) + ')'

filter_command = filter_command + ')'

# Align video
(
    ffmpeg
    .input(video_path)
    .filter_('setpts', filter_command)
    .output(video_output_path, **{'r': frame_rate})
    .run()
)
