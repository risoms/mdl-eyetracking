#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# %% [markdown]
# <h5 style="padding-top: 0px;padding-bottom: 0px;">Example setup for Eyelink 1000 Plus, using PsychoPy 3.0.</h5>
# %%
# Created on Wed Feb 13 15:37:43 2019
# @author: Semeon Risom
# @email: semeon.risom@gmail.com.
# Sample code to run SR Research Eyelink eyetracking system. Code is optimized for the Eyelink 1000 
# Plus (5.0), but should be compatiable with earlier systems.
# %%
# To Do:
# Finish eyetracking.drift_correction()
# Finish eyetracking.roi()
# %% [markdown]
# <p>The sequence of operations for implementing the trial is:</p>
# <ol><li>Perform a DRIFT CORRECTION, which also serves as the pre-trial fixation target.</li>
# <li>Start recording, allowing 100 milliseconds of data to accumulate before the trial display starts.</li>
# <li>Draw the subject display, recording the time that the display appeared by placing a message in
# the EDF file.</li>
# <li>Loop until one of these events occurs RECORDING halts, due to the tracker ABORT menu or an error,
# the maximum trial duration expires 'ESCAPE' is pressed, the program is interrupted, or abutton on the
# EyeLink button box is pressed.</li>
# <li>Add special code to handle gaze-contingent display updates.</li>
# <li>Blank the display, stop recording after an additional 100 milliseconds of data has been collected.</li>
# <li>Report the trial result, and return an appropriate error code.</li></ol>
# <a>[see Pylink.chm]</a>
# %%
# import
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(os.getcwd())))
from psychopy import visual
import mdl
# %%
# Initialize the Eyelink.
# Before initializing, ensure psychopy window instance has been created in the experiment file. 
# This window will be used in the calibration function.
#
# ```psychopy.visual.window.Window``` instance (for demonstration purposes only)
window = visual.Window(size=[1920, 1080], fullscr=False, screen=0, allowGUI=True, units='pix',
                       monitor='Monitor', winType='pyglet', color=[110,110,110], colorSpace='rgb255')
subject = 1
eyetracking = mdl.eyetracking(libraries=False, window=window, subject=subject)
# %%
# Connect to Eyelink. This allow controlls the parameters to be used when running the eyetracker.
param = eyetracking.connect(calibration_type=13)
# %%
# Setting the dominant eye. This step is especially critical for transmitting gaze coordinates from Eyelink->Psychopy.
dominant_eye = 'left'
eye_used = eyetracking.set_eye_used(eye=dominant_eye)
# %%
# Start calibration.
# Before running the calibration, ensure psychopy window instance has been created in the experiment file. 
# This window will be used in the calibration function.
eyetracking.calibration(event='calibration')
# %%
# Enter the key "o" on the ```psychopy.visual.window.Window``` instance. This will begin the task. 
# The Calibration, Validation, 'task-start' events are controlled by the keyboard.
# Calibration ("c"), Validation ("v"), task-start ("o") respectively.
# %%
# (Optional) Print message to console/terminal. This may be useful for debugging issues.
eyetracking.console(c="blue", msg="eyetracking.calibration() started")
# %%
# Drift correction. This can be done at any point after calibration, including before and after 
# eyetracking.start_recording has started. #!! To do. Finish.
eyetracking.drift_correction()
print('finished')
# %%
# Gaze contigent. This is used for realtime data collection from eyelink->psychopy.
# For example, this can be used to require participant to look at the fixation cross for a duration
# of 500 msec before continuing the task.
# 
# Using the eyetracking.roi function to collect samples with the center of the screen.
roi = dict(center=[860,1060,640,440])
# start
eyetracking.roi(window=window, region=roi)
# %%
# Region of interest. This is used for sending regions of interest for each trial from PsychoPy>Eyelink.
# 
# Using the eyetracking.roi function to collect samples with the center of the screen.
roi = dict(center=[860,1060,640,440])
# start
eyetracking.gc(window=window, region=roi)
# %%
# Start recording. This should be run at the start of the trial. 
# Note: There is an intentional delay of 150 msec to allow the Eyelink to buffer gaze samples.
eyetracking.start_recording(trial=1, block=1)
# %%
# Collect current gaze coordinates from Eyelink (only if needed in experiment). This command should be 
# looped at an interval of sample/2.01 msec to prevent oversampling (500Hz).
#
# get time
import time
s1 = 0 # set current time to 0
lgxy = [] # create list of gaze coordinates (demonstration purposes only)
s0 = time.clock() # initial timestamp
# repeat
while True:
    # if difference between starting and current time is greater than > 2.01 msec, collect new sample
    if (s1 - s0) >= .00201:
        gxy, ps, s = eyetracking.sample(eye_used=eye_used) # get gaze coordinates, pupil size, and sample
        lgxy.append(gxy) # store in list (not required; demonstration purposes only)
        s0 = time.clock() # update starting time
    #else set current time
    else: 
        s1 = time.clock()

    #break `while` statement if list of gaze coordiantes >= 20 (not required; demonstration purposes only)
    if len(lgxy) >= 200: print(lgxy); break
# %%
# Send messages to Eyelink. This allows post-hoc processing of timing related events (i.e. "stimulus onset").
# Sending message "stimulus onset".
msg = "stimulus onset"
eyetracking.send_message(msg=msg)
# %%
# Stops Eyelink recording. Also allows transmission of trial-level variables (optional) to Eyelink.
# Note: Variables sent are optional. If they being included, they must be in ```python dict``` format.
#
# set variables
variables = dict(stimulus='001B_F.jpg', trial_type='encoding', race="black")
# stop recording
eyetracking.stop_recording(trial=1, block=1, variables=variables)
# %%
# Finish Eyelink recording.
eyetracking.finish_recording()