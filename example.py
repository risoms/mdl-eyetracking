#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom
@email: semeon.risom@gmail.com

References:
    https://www.psychopy.org/api/hardware/pylink.html
"""

# %%
# ----imports
from psychopy import visual, core
import sys
import mdl

# %%
#----pre-task
# initalize
"""
Parameters
----------
libraries : :class:`bool`
    Should the code check if required libraries are available.
sample_rate : :class:`int`
    Sampling rate (250, 500, 1000, or 2000).
c_num : :class:`int`
    Calibration type. Default is 13-point.
paval : :class:`int`
    Set calibraiton pacing
pupil_size : :class:`int`
    Pupil Size (area, perimeter).
ip : :class:`int`
    IP Address to connect to Eyelink computer.
s_port : :class:`int`
    Port address to send data.
r_port : :class:`int`
    Port address to recieve data.
saccade_velocity_threshold : :class:`int`
    Saccade Velocity Threshold. Default is 35.
saccade_acceleration_threshold : :class:`int`
    Saccade Acceleration Threshold. Default is 9500.
recording_parse_type : :class:`str`
    Options are either 'GAZE','HREF'.
enable_search_limits : :class:`bool`
    s
track_search_limits : :class:`bool`
    s
autothreshold_click : :class:`bool`
    s
autothreshold_repeat : :class:`bool`
    a
enable_camera_position_detect : :class:`bool`
    a
"""
subject = 1
eyetracking = mdl.eyetracking(libraries=False, subject=subject, sample_rate=500, c_num=13, paval=1000,
                              pupil_size="area", ip="127.0.0.1", s_port=4444, r_port=5555,
                              saccade_velocity_threshold=35, saccade_acceleration_threshold=9500,
                              recording_parse_type="GAZE", enable_search_limits=True,
                              track_search_limits=True, autothreshold_click=True, autothreshold_repeat=True,
                              enable_camera_position_detect=True)

# %%
# set dominant eye
"""
Parameters
----------
eye : :obj:`str`
    Dominant eye, either left or right. This will be used for outputting Eyelink gaze samples.
"""
dominant_eye = 'left'
eye_used = eyetracking.set_eye_used(eye=dominant_eye)

# %%
# ----------------calibration
"""
Parameters
----------
window : :class:`psychopy.visual.window.Window`
    PsychoPy window instance.
"""
# create psychopy window
window = visual.Window(
    size=[1336, 768], fullscr=False, screen=0,
    allowGUI=True, allowStencil=False,
    monitor=u'testMonitor', color=u'white', colorSpace='rgb',
    blendMode='avg')

# start calibration
eyetracking.calibration(window=window)
#----------------debugging (optional)
"""
Parameters
----------
color : :class:`str`
    Color to use (black, red, green, orange, purple, blue, grey).
msg : :class:`str`
    Message to be color printed.
"""
eyetracking.console(c="green", msg="eyetracking.calibration() started")

# %%
# ----------------within trial
# start recording
"""
Parameters
----------
trial : :obj:`int`
    Trial Number.
block : :obj:`int`
     Block Number.
variables : :obj:`dict`
     Dict of variables to send to eyelink (variable name, value).
"""
eyetracking.start_recording(trial=1, block=1)

# %%
# Collects new gaze coordinates from Eyelink (only if needed in experiment)
"""
Parameters
----------
eye_used : :obj:`str`
    Checks if eye used is available.
"""
gxy = eyetracking.sample(eye_used=eye_used)

# %%
# Send messages to eyelink.
"""
Parameters
----------
msg : :obj:`str`
    Message to be recieved by eyelink.
"""
msg = "stimulus onset"
eyetracking.send_message(msg=msg)

# %%
# Stops recording of eyelink. Also allows transmission of trial-level variables to Eyelink.
"""
Stops recording of eyelink. Also allows transmission of trial-level variables to Eyelink.

Parameters
----------
image : :obj:`str`
    Image to be displayed in Eyelink software.
trial : :obj:`int`
    Trial Number.
block : :obj:`int`
    Block Number.
block : :obj:`int`
    Accuracy (1=correct, 0=incorrect).
variables : :obj:`dict`
    Dictionary of variables to send to eyelink (variable name, value).
"""
variables = dict(stimulus='img.jpg',
                 trial_type='fixation',
                 race="white")
eyetracking.stop_recording(trial=1, block=1, variables=variables)

# %%
# Finish recording of eyelink.
"""
Parameters
----------
subject : :obj:`int`
    subject number.
"""
eyetracking.finish_recording()
