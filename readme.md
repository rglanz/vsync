# vsync

**The problem:** High-speed video acquisition often results in dropped frames.
Moreover, recording video on one computer and collecting another type of data on
a separate computer produces desynchronization between the video and the data streams.

**The solution:** If the data acquisition hardware/software can produce a time-locking
stimulus visible to the camera, the video can be synchronized to the data stream. This
program analyzes the video frame-by-frame, compares the observed onset of the
time-locking stimulus to the predicted onset, and adjusts the video's frame
time-stamps accordingly. All video operations are performed using ffmpeg
(https://www.ffmpeg.org/), a video-processing command-line tool written in C/Assembly.

**Example:** To study the relationship between behavior and the brain, neurophysiological
recordings of brain activity are performed in rats while recording video of the rat's behavior.
In order to relate behavior to the millsecond/sub-millisecond time-scales in the brain, the neurophysiological and video
data must be exquisitely synchronized. A Lab Rat LR10 (neurophysiological signal amplifier)
running Synapse (data collection software) can be used to briefly illuminate an LED
(time-locking stimulus) every 3 seconds. The LED can be placed in view of the high-speed
video camera, and this toolbox will synchronize the video and data streams, even if the camera
occasionally drops frames.

![alt text](/assets/vsync_icon.png?raw=true)

[*readme in progress*]

### Installation

1. Clone the repository
    > git clone https://github.com/rglanz/vsync.git
   
2. Change directory to vsync folder
    > cd [path/to/folder]/vsync

3. Create the virtual environment
    > conda env create -f environment.yaml

### Startup
1. Activate *vsync* virtual environment
    > conda activate vsync   

2. Change directory to vsync folder
    > cd [path/to/folder]/vsync

3. Activate ipython
    > ipython

4. Import vsync package
    > import vsync

### Usage
1. Define the video's path as a variable
    > video_path = 'path/to/video.avi'      #macOS/Linux
    > 
    > video_path = r'path/to/video.avi'     #Windows
   
2. Read the video (saves data to a .pkl file)
    > vsync.read_video(video_path)

3. Analyze the video for dropped frames (interval is time between time-locking
   stimuli; set to 3 seconds by default)
    > vsync.find_dropped_frames(video_path, interval=3)

4. Plot the results for quality control
    > vsync.plot_results(video_path)

5. If the results are acceptable [*more detail coming soon*], align the video
    > vsync.align_video(video_path)

[*readme in progress*]
