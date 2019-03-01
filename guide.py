#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom
@email: semeon.risom@gmail.com

References:
    https://www.psychopy.org/api/hardware/pylink.html
"""

##############################
###### main
#----imports
import mdl
from psychopy import visual, core

#%%----initiate
#subject=subject number (int only)
#libraries = should python required libraries be checked for availability (default=False)
eyetracking = mdl.eyetracking(libraries=False, subject=None, sample_rate=500, c_num=13, paval=1000,
                              pupil_size="area", ip="127.0.0.1", s_port=4444, r_port=5555, 
                              saccade_velocity_threshold=35, saccade_acceleration_threshold=9500, 
                              recording_parse_type="GAZE", enable_search_limits=True, 
                              track_search_limits=True, autothreshold_click=True, autothreshold_repeat=True, 
                              enable_camera_position_detect=True)

#create psychopy window
window = visual.Window(
    size=[eyelink.w, eyelink.h], fullscr=False, screen=0,
    allowGUI=True, allowStencil=False,
    monitor=u'testMonitor', color=u'white', colorSpace='rgb',
    blendMode='avg')

#----start recording session
#eye_used will either be should either be 'left' or 'right'
dominant_eye = 'left'
eye_used = eyetracking.set_eye_used(eye=dominant_eye)

#%%----calibration
#win=psychopy win instant
eyetracking.calibration(window=win)

#----print to console, terminal (for debugging)
# c = blue, red, green, orange, purple, grey
eyetracking.console(c="blue", msg="eyetracking.calibration() started")

#------------------------within trial
#%%----start recording
#block=block number(from psychopy) #trial=trial number(from psychopy)
eyetracking.start_recording(block=block, trial=trial)

#%%----get gaze samples from eyetracker to psychopy (only if needed in experiment)
#---- (loop every .002 msec)
#eye_used will either be 1 (left eye) or 0 (right eye)
eyetracking.sample(eye_used=eye_used)

#%%----send messages to eyelink during the trial
msg = "stimulus onset"
eyetracking.send_message(msg=msg)

#%%----stop recording
#block=block number(from psychopy) #trial=trial number(from psychopy)
#variables (optional) = dictionary of trial-event data to be saved to eyelink
variables = dict(stimulus='img.jpg', 
                 trial_type='fixation', 
                 race="white")
eyetracking.stop_recording(trial=trial, block=block, variables=variables)

#%%------------------------end recording session
eyetracking.finish_recording()