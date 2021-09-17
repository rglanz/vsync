## vsync

**The problem:** High-speed video acquisition often results in dropped frames.
Moreover, recording video on one computer and collecting another type of data on
a separate computer produces desynchronization between the video and the data streams.

**The solution:** If the data acquisition hardware/software can produce a time-locking
stimulus visible to the camera, the video can be synchronized to the data stream. This
program analyzes the video frame-by-frame, compares the observed presentation of the
time-locking stimulus to the predicted presentation, and adjusts the video's frame
time-stamps accordingly. All video operations are performed using ffmpeg
(https://www.ffmpeg.org/), a video-processing command-line tool written in C/assembly.

**Example:** To study the relationship between behavior and the brain, neurophysiological
recordings brain activity are performed in rats while collecting video of the rat's behavior.
Due to millsecond/sub-millisecond time-scales in the brain, the neurophysiological and video
data must be exquisitely synchronized. A Lab Rat LR10 (neurophysiological signal amplifier)
running Synapse (data collection software) can be used to briefly illuminate an LED
(time-locking stimulus) every three seconds. The LED can be placed in view of the high-speed
video camera, and this toolbox will synchronize the two data streams, even if the camera
occasionally drops frames.

![alt text](/assets/vsync_icon.png?raw=true)

[readme in progress]