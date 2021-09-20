# This Python file uses the following encoding: utf-8

# Imports
import ffmpeg
from pathlib import Path
import pickle


def align_video(video_path):
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
    filter_command = 'PTS+1/' + str(frame_rate) + '/TB*('   #TODO add in non-int frame rate rounding
    for n_frame, frame_id in enumerate(dummy_frame_index):
        if n_frame == 0:
            filter_command = filter_command + 'gte(N,' + str(frame_id - n_frame - 1) + ')'
        else:
            filter_command = filter_command + '+gte(N,' + str(frame_id - n_frame - 1) + ')'

    filter_command = filter_command + ')'

    # Align video
    (
        ffmpeg
        .input(video_path)
        .filter_('setpts', filter_command)
        .trim(start_frame=first_stimulus)
        .trim(end_frame=corrected_video_length-len(dummy_frame_index))
        .output(output_video_path, **{'r': frame_rate}, **{'vcodec': 'libx264'}, **{'crf': 17})
        .run(overwrite_output=True)
    )
