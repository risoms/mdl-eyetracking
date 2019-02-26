#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: mdl-admin

References:
    https://www.psychopy.org/api/hardware/pylink.html
"""
#---main
import os
import sys
import re
from win32api import GetSystemMetrics

#---debug
from pdb import set_trace as breakpoint

#---pylink
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(path)

#---eyelink
from .pylink import pylink

#---bridging
from .calibration import calibration
 
#---------------------------------------------start
class eyetracking():
    def __init__(self,edfsubject):
        # Make filename
        self.fname = os.path.splitext(edfsubject)[0]  # strip away extension if present
        assert re.match(r'\w+$', self.fname), 'Name must only include A-Z, 0-9, or _'
        assert len(self.fname) <= 8, 'Name must be <= 8 characters.'
        # Make filename 
        self.edfname = self.fname + '.edf'
    
        # Initialize connection with eyetracker
        try:
            self.tracker = pylink.EyeLink()
            self.realconnect = True
        except RuntimeError:
            self.tracker = pylink.EyeLink(None)
            self.realconnect = False
        
        #properties
        #screen
        self.w = GetSystemMetrics(0)
        self.h = GetSystemMetrics(1)       
        #find out which eye
        self.left_eye = 0
        self.right_eye = 1    
        #gaze-timing
        self.GCWINDOW = .5 #500 msec
        self.DURATION = 2 #2000 msec
        self.gbox = 200 #gaze boundary
        self.inbox = False
        self.Finished = False     
        #gaze-bounding box
        self.sc = [self.w / 2.0, self.h / 2.0] #center of screen
        self.size = 100 #Length of one side of box
        self.xbdr = [self.sc[0] - self.size, self.sc[0] + self.size]
        self.ybdr = [self.sc[1] - self.size, self.sc[1] + self.size]
        #calibration
        self.cnum = 13 # 13 pt calibration
        self.paval = 1000 #Pacing of calibration, t in milliseconds        
        #pupil
        self.red = 'red'
        self.green = 'green'
        self.blue = 'blue'

        #Open EDF
        pylink.getEYELINK().openDataFile(self.edfname)
        pylink.flushGetkeyQueue()

        #notify eyelink of display resolution        
        pylink.getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(self.w - 1, self.h - 1))
        pylink.getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" %(self.w - 1, self.h - 1))
        
        #Set content of edf file
        pylink.getEYELINK().sendCommand(
            'file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT')        
        pylink.getEYELINK().sendCommand(
            'link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON')    
        pylink.getEYELINK().sendCommand(
            'link_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET')    
        pylink.getEYELINK().sendCommand(
            'file_sample_data = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT')
        
        #select sound for calibration and drift correct
        pylink.setCalibrationSounds("off", "off", "off")
        pylink.setDriftCorrectSounds("off", "off", "off")

        #Places EyeLink tracker in offline (idle) mode        
        pylink.getEYELINK().setOfflineMode()
        
    def console(c='blue', msg=''):
        """
        Allow color print to console.
        
        Parameters
        ----------
        color : :class:`str`
            Color to use (black, red, green, orange, purple, blue, grey).
        msg : :class:`str`
            Message to be color printed.
        """
    
        color = dict(
            black = '\33[40m',
            red =  '\33[41m',
            green =  '\33[42m',
            orange = '\33[43m',
            purple = '\33[45m',
            blue =  '\33[46m',
            grey =  '\33[47m',
            ENDC = '\033[0m')
    
        print(_data = color['green'] + msg + color['ENDC'])
    
    def libraries():
        """
        Check if libraries are available.
        
        Parameters
        ----------
        win : :class:`object`
            PsychoPy win object.
        drift : :obj:`int`
            Counter of drift correct runs.
        """
        #check libraries for missing
        from distutils.version import StrictVersion
        import importlib
        import pkg_resources
        import platform
        import pip
        
        #list of possibly missing packages to install
        required = ['psychopy','importlib']
        
        #for geting os variables
        os_ = platform.system()
        if os_ == "Windows":
            required.append('win32api')
        elif os_ =='Darwin':
            required.append('pyobjc')
        
        #try installing and/or importing packages
        try:
            #if pip >= 10.01
            pip_ = pkg_resources.get_distribution("pip").version
            if StrictVersion(pip_) > StrictVersion('10.0.0'):
                from pip._internal import main as _main
                #for required packages check if package exists on device
                for package in required:
                    #if missing, install
                    if importlib.util.find_spec(package) is None:
                        _main(['install',package])
                    #else import
                    else:
                        __import__(package)
                        
            #else pip < 10.01          
            else:
                #for required packages check if package exists on device
                for package in required:
                    #if missing
                    if importlib.util.find_spec(package) is None:
                        pip.main(['install',package])
                    #else import
                    else:
                        __import__(package)
                
        except Exception as e:
            return e
        
    def set_eye_used(self, eye):
        """
        Set dominant eye.
        
        Parameters
        ----------
        win : :class:`object`
            PsychoPy win object.
        drift : :obj:`int`
            Counter of drift correct runs.
        """
        eye_entered = str(eye)
        if eye_entered in ('Left','LEFT','left','l','L'):
            eye_used = self.left_eye
        else:
            eye_used = self.right_eye
        return eye_used       
    
    def calibrate(self, window, drift):
        """
        Calibrates eyetracker using psychopy stimuli.
        
        Parameters
        ----------
        win : :class:`object`
            PsychoPy win object.
        drift : :obj:`int`
            Counter of drift correct runs.
        """
        if drift >= 2: #if drift correct failed 3 times in a row
            pylink.getEYELINK().sendMessage("Drift_failed") #send failure message
            self.stop_recording()
        
        if self.realconnect:
            # Generate custom calibration stimuli
            self.genv = calibration.calibration(w=self.w, h=self.h, tracker=self.tracker, window=window)
             
            pylink.getEYELINK().setCalibrationType('HV%d'%(self.cnum)) # Set calibration type
            pylink.getEYELINK().setAutoCalibrationPacing(self.paval) # Set calibraiton pacing
            pylink.openGraphicsEx(self.genv) # Execute custom calibration display
            pylink.getEYELINK().doTrackerSetup(self.w, self.h) # Calibrate
            
    def sample(self, eye_used):
        """
        Collects new pupil sample.
        
        Parameters
        ----------
        eye_used : :obj:`str`
            Checks if eye used is available.
        """
        #check for new sample update
        s = pylink.getEYELINK().getNewestSample() # check for new sample update
        if(s != None): # Gets the gaze position of the latest sample
            #pupil area
            if eye_used == self.right_eye:
                ps = s.getRightEye().getPupilSize()
            else:
                ps = s.getLeftEye().getPupilSize()
            return ps
    
    def send_message(self, msg):
        """
       send message to eyelink.
        
        Parameters
        ----------
        msg : :obj:`str`
            Message to be recieved by eyelink.
        """
        pylink.getEYELINK().sendMessage(msg)
        
    def send_variable(self, variable, value):
        """
        send trial variable to eyelink.
        
        Parameters
        ----------
        variable : :obj:`str`
            Trial-related variable to be read by eyelink.
        value : :obj:`str`
            Variable value to be read by eyelink.
        
        """
        msg = "!V TRIAL_VAR %s %s" %(variable, value)
        pylink.getEYELINK().sendMessage(msg)
        
    def start_recording(self, trialNum, blockNum):
        """
        Starts recording of eyelink.
        
        Parameters
        ----------
        trialNum : :obj:`str`
            Trial Number.
        blockNum : :obj:`str`
            PsychoPy win object.
        
        """
        pylink.getEYELINK().sendCommand("record_status_message 'Trial %s Block %s'" %(trialNum,blockNum))
        pylink.getEYELINK().sendCommand("clear_screen 0")
        pylink.beginRealTimeMode(100) #start realtime mode
        pylink.getEYELINK().startRecording(1, 1, 1, 1)# Begin recording

    def stop_recording(self, image=None, trial=None, block=None):
        """
        Stops recording of eyelink.
        
        Parameters
        ----------
        image : :obj:`str`
            Image to be displayed in Eyelink software.
            
        Notes
        -----
        pylink.endRealTimeMode():
            Returns the application to a priority slightly above normal, to end realtime mode. This function should execute rapidly, 
            but there is the possibility that Windows will allow other tasks to run after this call, causing delays of 1-20 
            milliseconds. This function is equivalent to the C API void end_realtime_mode(void);
        
        """
        #end of trial message
        pylink.getEYELINK().sendMessage('Ending Recording')
        ##add image to display
        pylink.getEYELINK().sendMessage("!V IMGLOAD CENTER  %s" %(image))
        pylink.endRealTimeMode()
        
        #Allow Windows to clean up while we record additional 100 msec of data
        pylink.msecDelay(100)
        pylink.getEYELINK().stopRecording()
        pylink.msecDelay(50)
        
        #Places EyeLink tracker in off-line (idle) mode
        pylink.getEYELINK().setOfflineMode()
        #send trial data
        pylink.getEYELINK().sendMessage("!V TRIAL_VAR trialNum %s" %(value))
        
    def finish_recording(self, path):
        """
        Finish recording of eyelink.
        
        Parameters
        ----------
        path : :obj:`str`
            Save folder of edf file.
        
        """
        # Generate file path
        self.fpath = os.path.join(path, self.edfname)
        
        # Close the file and transfer it to Display PC
        pylink.endRealTimeMode()
        pylink.getEYELINK().closeDataFile()
        pylink.msecDelay(50)
        pylink.getEYELINK().receiveDataFile(self.edfname, self.fpath) #copy EDF file to Display PC
        pylink.getEYELINK().close() #Close connection to tracker
