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

3. Analyze the video for dropped frames and plot results (interval is time between time-locking
   stimuli; set to 3 seconds by default)
    > vsync.analyze_frames(video_path, interval=3)

5. If the results are acceptable, align the video
    > vsync.align_video(video_path)

### Interpreting the plots
![alt text](/assets/vsync_icon.png?raw=true)

**Raw ROI Intensity**: This is the intensity of the ROI as a function of time (frames). 
You should see a low, consistent level of baseline noise. The large, transitory spikes represent your
stimulus presentation. If there are periods of disruptive noise, your ROI may not be selected properly, 
or something in the video may have moved in front of your stimulus (not desirable). The red marker indicates
the first detected stimulus presentation, to which the beginning of the video will be trimmed.

**First Frame**: This is the frame representing the first stimulus presentation (e.g., an LED).
You should see the stimulus, which should line up with the red marker in the previous plot.

**Frame Interval**: This is a measure of the number of frames per interval (frame rate * interval rate). 
You should occasionally see a single down-tick (a dropped frame). Regular frame drops indicate poor write-speed
or a non-integer frame rate. Periods where multiple frames are dropped indicate major writing issues during 
video collection, and the video should be discarded entirely.

**Frame-drop Histogram**: As with the previous plot, there should only be single (or, very rarely, double),
frame drops. Multiple stimulus intervals with multiple dropped frames cause the video to be unreliable, even if
properly adjusted. Best practice is to discard the video from analysis.

### Features under development
* Interactive GUI

* Function to manually readjust the stimulus detection threshold

* Suppression of verbose ffmpeg output
