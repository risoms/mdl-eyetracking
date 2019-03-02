#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#%%
# """
# Created on Wed Feb 13 15:37:43 2019

# @author: Semeon Risom
# @email: semeon.risom@gmail.com.

# Sample code to run SR Research Eyelink eyetracking system. Code is optimized for the Eyelink 1000 Plus (5.0),
# but should be compatiable with earlier systems.
# """
# %%
# imports
from psychopy import visual
import mdl
# %%
# Initialize the Eyelink.
subject = 1
eyetracking = mdl.eyetracking(libraries=False, subject=subject)
# %%
# Setting the dominant eye. This step is especially critical for transmitting gaze coordinates from Eyelink->Psychopy. 
dominant_eye = 'left'
eye_used = eyetracking.set_eye_used(eye=dominant_eye)
# %%
# Start calibration.
# Before running the calibration, ensure psychopy window instance has been created in the experiment file. 
# This window will be used in the calibration function.
#
# ```psychopy.visual.window.Window``` instance
window = visual.Window(size=[1336, 768], fullscr=False, screen=0, allowGUI=True, 
                       allowStencil=False, monitor=u'testMonitor', 
                       color=(128,128,128), colorSpace='rgb', blendMode='avg')
# start
eyetracking.calibration(window=window)
# %%
# (Optional) Print message to console/terminal. This may be useful for debugging issues.
eyetracking.console(c="green", msg="eyetracking.calibration() started")
# %%
# Start recording. This should be run at the start of the trial. 
# Note: There is an intentional delay of 150 msec to allow the Eyelink to buffer gaze samples.
eyetracking.start_recording(trial=1, block=1)
# %%
# Collects new gaze coordinates from Eyelink (only if needed in experiment). This command should be 
# looped at an interval of sample/2.01 msec to prevent oversampling (500Hz).
import time
s1 = 0 # set current time to 0
lgxy = [] # create list of gaze coordinates (demonstration purposes only)
s0 = time.clock() # initial timestamp
while True:
    # if difference between starting and current time is greater than > 2.01 msec, collect new sample
    if (s1 - s0) >= .00201:
        gxy = eyetracking.sample(eye_used=eye_used) # get gaze coordinates
        lgxy.append(gxy) # store in list
        s0 = time.clock() # update starting time
    #else set current time
    else: 
        s1 = time.clock()

    #break `while` statement if list of gaze coordiantes >= 20 (demonstration purposes only)
    if len(lgxy) >= 20: break
# %%
# Send messages to Eyelink. This allows post-hoc processing of timing related events (i.e. "stimulus onset").
# Sending message "stimulus onset".
msg = "stimulus onset"
eyetracking.send_message(msg=msg)
# %%
# Stops Eyelink recording. Also allows transmission of trial-level variables (optional) to Eyelink.
# Note: Variables sent are optional. If they being included, they must be in ```python dict``` format.
variables = dict(stimulus='001B_F.jpg', trial_type='encoding', race="black")
eyetracking.stop_recording(trial=1, block=1, variables=variables)
# %%
# Finish Eyelink recording.
eyetracking.finish_recording()
