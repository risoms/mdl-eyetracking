#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:47:20 2019

@author: mdl-admin
"""

import sys
import os
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path + '.')
#import eyetracking
import pylink
import eyetracking
from psychopy import visual

#---------start eyetracker
# Prepare eyetracker
eyelink = eyetracking.run('555')

#start view
window = visual.Window(
    size=[eyelink.w, eyelink.h], fullscr=False, screen=0,
    allowGUI=True, allowStencil=False,
    monitor=u'testMonitor', color=u'white', colorSpace='rgb',
    blendMode='avg')

##---------start calibration
## Calibrate eyetracker
drift = 0
eyelink.calibrate(window=window, drift=drift)

#eye used
#eye_used = eyelink.set_eye_used()
#
#
##---------start of every trial
##eyelink-start recording
#eyelink.start_recording()
##eyelink-send message for edf
#pylink.getEYELINK().sendMessage('Start Recording')
#
##---------within every trial (loop every .002)
##eyelink-gaze coordinates
#gxy = eyelink.sample()
#
##---------end of every trial
##end of trial message to edf
#pylink.getEYELINK().sendMessage('End Recording')
##eyelink-stop recording
#eyelink.stop_recording()
##send messages to edf
#msg = "!V TRIAL_VAR BlockVar %s" %(trialNum) #trialNum
#pylink.getEYELINK().sendMessage(msg)
#msg = "!V TRIAL_VAR BlockVar %s" %(blockNum) #blocknum
#pylink.getEYELINK().sendMessage(msg)
###trial results
#pylink.getEYELINK().sendMessage("TRIAL_RESULT 1")
#
##---------end of task
##set offline mode so we can transfer file
#edfpath = _thisDir + os.sep + '_data/edf'
#eyelink.close(edfpath)