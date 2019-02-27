#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom

References:
    https://www.psychopy.org/api/hardware/pylink.html
"""
#---main
import os
import re
import platform

#---debug
from pdb import set_trace as breakpoint

#---bridging
from . import pylink
from .calibration import calibration
 
#---------------------------------------------start
class eyetracking():
    def __init__(self, libraries=False, subject=None, c_num=13, paval=1000, sat=35, p_size="area", 
                 ip="127.0.0.1", s_port=4444, r_port=5555):
        """
        Start eyetracker.
        
        Parameters
        ----------
        libraries : :class:`bool`
            Should the code check if required libraries are available.
        c_num : :class:`int`
            Calibration type. Default is 13-point.
        paval : :class:`int`
            Subject Number.
        sat : :class:`int`
            Saccade Acceleration Threshold. Default is .9500.
        p_size : :class:`int`
            Pupil Size (area, perimeter).
        ip : :class:`int`
            IP Address to connect to Eyelink computer.
        s_port : :class:`int`
            Port address to send data.
        r_port : :class:`int`
            Port address to recieve data.
        """
        
        # check if subject number has been entered
        if subject==None:
            self.console(c='red', msg='Subject number not entered. Please enter the subject number.')
        else:
            self.subject = subject
        # check if required libraries are available
        if libraries==True:
            self.libraries()
        
        #----edf filename
        self.subject = os.path.splitext(subject)[0]  # strip away extension if present
        assert re.match(r'\w+$', self.subject), 'Name must only include A-Z, 0-9, or _'
        assert len(self.subject) <= 8, 'Name must be <= 8 characters.'
        self.fname = str(self.subject) + '.edf'
        
        #----initiate connection with eyetracker
        try:
            self.tracker = pylink.EyeLink()
            self.realconnect = True
        except RuntimeError:
            self.tracker = pylink.EyeLink(None)
            self.realconnect = False
        
        #----screen size
        if platform.system() == "Windows":
            from win32api import GetSystemMetrics
            self.w = GetSystemMetrics(0)
            self.h = GetSystemMetrics(1)
        elif platform.system() =='Darwin':
            from AppKit import NSScreen
            self.w = NSScreen.mainScreen().frame().size.width
            self.h = NSScreen.mainScreen().frame().size.height
           
        #find out which eye
        self.eye_used = None
        self.left_eye = 0
        self.right_eye = 1
        
        #----real-time settings
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
        #pupil ROI
        self.red = 'red'
        self.green = 'green'
        self.blue = 'blue'
        
        #----preset
        self.version = self.tracker.getTrackerVersion()
        #edf filters
        self.fef = "LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT"
        if self.version >= 3:
            self.fsd = 'LEFT,RIGHT,GAZE,HREF,AREA,GAZERES,STATUS,INPUT,HTARGET'
        else:
            self.fsd = "LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,INPUT"
        
        #----set link data (used for gaze cursor) 
        if self.version >= 3:
        	self.lsd = "LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT"
        else:
        	self.lsd = "LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT"
        
        #Open EDF
        pylink.getEYELINK().openDataFile(self.fname)
        pylink.flushGetkeyQueue()

        #----send settings to eyelink
        #calibration
        self.cnum = c_num #13 pt calibration
        self.paval = paval #Pacing of calibration, in milliseconds
        #tracker
        self.tracker.sendCommand("enable_search_limits=YES")
        self.tracker.sendCommand("track_search_limits=YES")
        self.tracker.sendCommand("autothreshold_click=YES")
        self.tracker.sendCommand("autothreshold_repeat=YES")
        self.tracker.sendCommand("enable_camera_position_detect=YES")
        #notify eyelink of display resolution        
        pylink.getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(self.w - 1, self.h - 1))
        pylink.getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" %(self.w - 1, self.h - 1))
        #set content of edf file
        ##edf filters
        pylink.getEYELINK().sendCommand('file_event_filter = %s')%(self.fef)
        pylink.getEYELINK().sendCommand('file_sample_data = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT')
        ##link data (used for gaze cursor)
        pylink.getEYELINK().sendCommand('link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON')
        pylink.getEYELINK().sendCommand('link_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET')
        
        #select sound for calibration and drift correct
        pylink.setCalibrationSounds("off", "off", "off")
        pylink.setDriftCorrectSounds("off", "off", "off")
        #place EyeLink tracker in offline (idle) mode        
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
    
        print(color['green'] + msg + color['ENDC'])
    
    def libraries(self):
        """
        Check if libraries are available.
        
        Parameters
        ----------
        win : :class:`object`
            PsychoPy win object.
        drift : :obj:`int`
            Counter of drift correct runs.
        """
        self.console(msg="eyetracking.libraries()")
        #check libraries for missing
        from distutils.version import StrictVersion
        import importlib
        import pkg_resources
        import pip
        
        #list of possibly missing packages to install
        required = ['psychopy','importlib']
        
        #for geting os variables
        if platform.system() == "Windows":
            required.append('win32api')
        elif platform.system() =='Darwin':
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
        self.console(msg="eyetracking.set_eye_used()")
        eye_entered = str(eye)
        if eye_entered in ('Left','LEFT','left','l','L'):
            self.eye_used = self.left_eye
        else:
            self.eye_used = self.right_eye
        return self.eye_used
        
    def calibration(self, window):
        """
        Calibrates eyetracker using psychopy stimuli.
        
        Parameters
        ----------
        win : :class:`object`
            PsychoPy win object.
        drift : :obj:`int`
            Counter of drift correct runs.
        """     
        if self.realconnect:
            self.console(msg="eyetracking.calibration()")
            # Generate custom calibration stimuli
            self.genv = calibration(w=self.w, h=self.h, tracker=self.tracker, window=window)
            pylink.getEYELINK().setCalibrationType('HV%d'%(self.c_num)) # Set calibration type
            pylink.getEYELINK().setAutoCalibrationPacing(self.paval) # Set calibraiton pacing
            pylink.openGraphicsEx(self.genv) # execute custom calibration display
            pylink.getEYELINK().doTrackerSetup(self.w, self.h) # caslibrate
    
    def drift_correction(self, window, drift, limit=999):
        """
        Starts drift correction, and calibrates eyetracker using psychopy stimuli..
        
        Parameters
        ----------
        win : :class:`object`
            PsychoPy win object.
        drift : :obj:`int`
            Counter of drift correction runs.
        limit : :obj:`int`
            Maxinum drift corrections.
        """
        self.console(msg="eyetracking.drift_correction()")
        if (drift >= limit): #if drift correct failed more than limit
            pylink.getEYELINK().sendMessage("drift correction failed") #send failure message
            self.stop_recording()
        
        if self.realconnect:
            # Generate custom calibration stimuli
            self.genv = calibration(w=self.w, h=self.h, tracker=self.tracker, window=window)
            pylink.getEYELINK().setCalibrationType('HV%d'%(self.c_num)) # Set calibration type
            pylink.getEYELINK().setAutoCalibrationPacing(self.paval) # Set calibraiton pacing
            pylink.openGraphicsEx(self.genv) # execute custom calibration display
            pylink.getEYELINK().doTrackerSetup(self.w, self.h) # calibrate
            
    def sample(self, eye_used):
        """
        Collects new gaze coordinates from Eyelink.
        
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
        
    def start_recording(self, trial=None, block=None):
        """
        Starts recording of eyelink.
        
        Parameters
        ----------
        trial : :obj:`str`
            Trial Number.
        block : :obj:`str`
            Block Number.
        
        """
        self.console(msg="eyetracking.start_recording()")
        pylink.getEYELINK().sendCommand("record_status_message 'Trial %s Block %s'" %(trial, block))
        pylink.getEYELINK().sendCommand("clear_screen 0")
        pylink.beginRealTimeMode(100) #start realtime mode
        pylink.getEYELINK().startRecording(1, 1, 1, 1) # Begin recording

    def stop_recording(self, image=None, trial=None, block=None):
        """
        Stops recording of eyelink.
        
        Parameters
        ----------
        image : :obj:`str`
            Image to be displayed in Eyelink software.
        trial : :obj:`str`
            Trial Number.
        block : :obj:`str`
            Block Number.
            
        Notes
        -----
        pylink.endRealTimeMode():
            Returns the application to a priority slightly above normal, to end realtime mode. 
            This function should execute rapidly, but there is the possibility that Windows will 
            allow other tasks to run after this call, causing delays of 1-20 milliseconds. 
            This function is equivalent to the C API void end_realtime_mode(void);
        """
        self.console(msg="eyetracking.stop_recording()")
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
        pylink.getEYELINK().sendMessage("!V TRIAL_VAR trial %s" %(trial))
        pylink.getEYELINK().sendMessage("!V TRIAL_VAR block %s" %(block))
        
    def finish_recording(self):
        """
        Finish recording of eyelink.
        
        Parameters
        ----------
        subject : :obj:`int`
            subject number.
        
        """
        self.console(msg="eyetracking.finish_recording()")
        # Generate file path
        self.path = "%s/data/edf/"%(os.getcwd())
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        # Close the file and transfer it to Display PC
        pylink.endRealTimeMode()
        pylink.getEYELINK().closeDataFile()
        pylink.msecDelay(50)
        #copy EDF file to Display PC
        #pylink.getEYELINK().receiveDataFile(self.edfname, self.fpath) 
        pylink.getEYELINK().receiveDataFile(self.fname, self.path)
        #Close connection to tracker
        pylink.getEYELINK().close()
