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
sys.path.insert(0, '.\lib')
import mdl

#----to initiate
#subject=subject number (int only)
#libraries = should python required libraries be checked for availability (default=False)
eyetracking = mdl.eyetracking(subject=subject, libraries=True, sample_rate=500, c_num=13, paval=1000, 
                              svt=35, sat=9500, p_size="area", ip="127.0.0.1", s_port=4444, r_port=5555)

#----start recording session
#dominant_eye=eye used #eye_used will either be 1 (left eye) or 0 (right eye)
eye_used = eyetracking.set_eye_used(eye=dominant_eye)

#----calibration
#win=psychopy win instant
eyetracking.calibration(window=win)

#------------------------within trial
#----start recording
#block=block number(from psychopy) #trial=trial number(from psychopy)
eyetracking.start_recording(block=block, trial=trial)

#----get gaze samples from eyetracker to psychopy (only if needed in experiment)
#eye_used will either be 1 (left eye) or 0 (right eye)
eyetracking.sample(eye_used=eye_used)

#----send messages to eyelink during the trial
msg = "stimulus onset"
eyetracking.send_message(msg=msg)

#----stop recording
#block=block number(from psychopy) #trial=trial number(from psychopy)
#variables (optional) = dictionary of trial-event data to be saved to eyelink
variables = dict(stimulus=imageFile, event='fixationCross')
eyetracking.stop_recording(trial=trial, block=block, variables=variables)

#----end recording session
eyetracking.finish_recording()

##############################
###### other
#----print to console, terminal for debugging
# c = blue, red, green, orange, purple, grey
eyetracking.console(c="blue", msg="eyetracking.start_recording()")
    