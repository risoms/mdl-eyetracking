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
from psychopy import visual
import mdl

```html
pre-task
initalize
Parameters
----------
libraries : :class:`bool`
    Should the code check if required libraries are available.
sample_rate : :class:`int`
    Subject Number.
```
# %%
subject = 1
eyetracking = mdl.eyetracking(libraries=False, subject=subject)
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
