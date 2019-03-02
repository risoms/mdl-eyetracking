#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom
@email: semeon.risom@gmail.com

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
    def __init__(self, libraries=False, subject=None, sample_rate=500, c_num=13, paval=1000,  
                 pupil_size="area", ip="127.0.0.1", s_port=4444, r_port=5555, 
                 saccade_velocity_threshold=35,
                 saccade_acceleration_threshold=9500, 
                 recording_parse_type="GAZE",
                 enable_search_limits=True, track_search_limits=True, autothreshold_click=True, 
                 autothreshold_repeat=True, enable_camera_position_detect=True):
        """
        Start eyetracker.
        
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
        
        # check if subject number has been entered
        if subject==None:
            self.console(c='red', msg='Subject number not entered. Please enter the subject number.')
        else:
            self.subject = subject
        # check if required libraries are available
        if libraries==True:
            self.libraries()
        
        #----edf filename
        self.subject = os.path.splitext(str(subject))[0]
        #check if interger
        if re.match(r'\w+$', self.subject):
            pass
        else:
            self.window.close()
            raise AssertionError('Name must only include A-Z, 0-9, or _')
        #check length
        if len(self.subject) <= 8:
            pass
        else:
            self.window.close()
            raise AssertionError('Name must be <= 8 characters.')
        #store name
        self.fname = str(self.subject) + '.edf'
        
        #----initiate connection with eyetracker
        try:
            self.tracker = pylink.EyeLink()
            self.connected = True
        except RuntimeError:
            self.tracker = pylink.EyeLink(None)
            self.connected = False
        
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
        
        #----tracker metadata
        # get eyelink version
        self.eyelink_version = self.tracker.getTrackerVersion()
        # get host tracking software version
        self.host_version = 0
        if self.eyelink_version == 3:
            tvstr  = self.tracker.getTrackerVersionString()
            vindex = tvstr.find("EYELINK CL")
            self.host_version = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))
        
        #----preset
        self.saccade_acceleration_threshold = saccade_acceleration_threshold
        self.saccade_velocity_threshold = saccade_velocity_threshold
        self.recording_parse_type = recording_parse_type
        self.enable_search_limits =  "YES" if enable_search_limits else "NO"
        self.track_search_limits = "YES" if track_search_limits else "NO"
        self.autothreshold_click = "YES" if autothreshold_click else "NO"
        self.autothreshold_repeat = "YES" if autothreshold_repeat else "NO"
        self.enable_camera_position_detect = "YES" if enable_camera_position_detect else "NO"
        #sampling rate
        self.sample_rate = sample_rate
        #calibration
        self.c_num = c_num #[]-point calibration
        self.paval = paval
        # specify the EVENT and SAMPLE data that are stored in EDF or retrievable from the Link
        #[see Section 4.6 Data Files of the  EyeLink 1000 Plus user manual]
        self.fef = "LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT"
        self.lef = "LEFT,RIGHT,FIXATION,FIXUPDATE,SACCADE,BLINK,BUTTON,INPUT"
        if self.host_version >= 4:
            self.fsd = "LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT"
            self.lsd = "LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT"
        else:
            self.fsd = "LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS"
            self.lsd = "LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS"
        
        #----set tracker
        self.setup()
        
    def console(self, c='green', msg=''):
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
        
        print(color[c] + msg + color['ENDC'])
    
    def libraries(self):
        """Check if required libraries are available."""
        
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
        
    def setup(self):
        """
        Set Eyelink configuration.

        Attributes
        ----------
        saccade_velocity_threshold : :class:`str`
            Sets velocity threshold of saccade detector: usually 30 for cognitive research, 22 for 
            pursuit and neurological work. [see http://download.sr-support.com/dispdoc/cmds9.html]
            
        saccade_acceleration_threshold : :class:`str`
            Sets acceleration threshold of saccade detector: usually 9500 for cognitive research, 5000 
            for pursuit and neurological work. [see http://download.sr-support.com/dispdoc/cmds9.html]
        recording_parse_type : :class:`str`
            s
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
        
        #----open edf
        self.tracker.openDataFile(self.fname)
        pylink.flushGetkeyQueue()
        
        #----send settings to eyelink
        #place EyeLink tracker in offline (idle) mode before changing settings     
        self.tracker.setOfflineMode()
        #eiter GAZE or HREF
        self.tracker.sendCommand("recording_parse_type = %s"%(self.recording_parse_type))
        
        #if using tracker version 2 or below
        if self.eyelink_version>=2: 
            self.console(c='blue', msg="select_parser_configuration")
            self.tracker.sendCommand('select_parser_configuration 0')
        else:
            self.tracker.sendCommand("saccade_velocity_threshold = %s"(self.saccade_velocity_threshold))
            self.tracker.sendCommand("saccade_acceleration_threshold = %s"(self.saccade_velocity_threshold))
                
        #if using tracker version 2 or above
        if self.eyelink_version>=3:
            self.console(c='blue', msg="autothreshold_click")
            self.tracker.sendCommand("autothreshold_click = %s"%(self.autothreshold_click))
            self.tracker.sendCommand("autothreshold_repeat = %s"%(self.autothreshold_repeat))
            self.tracker.sendCommand("enable_camera_position_detect = %s"%(self.enable_camera_position_detect))
            self.tracker.sendCommand("enable_search_limits = %s"%(self.enable_search_limits))
            self.tracker.sendCommand("track_search_limits = %s"%(self.track_search_limits))
        
        #set content of edf file
        ##edf filters #event types
        self.tracker.sendCommand('file_event_filter = %s'%(self.fef))
        self.tracker.sendCommand('file_sample_data = %s'%(self.fsd))
        self.tracker.sendCommand('link_event_filter = %s'%(self.lef))
        self.tracker.sendCommand('link_sample_data = %s'%(self.lsd))
        #select sound for calibration and drift correct
        pylink.setCalibrationSounds("off", "off", "off")
        pylink.setDriftCorrectSounds("off", "off", "off")
        
    def set_eye_used(self, eye):
        """
        Set dominant eye.
        
        Parameters
        ----------
        eye : :obj:`str`
            Dominant eye, either left or right. This will be used for outputting Eyelink gaze samples.
        """
        self.console(msg="eyetracking.set_eye_used()")
        eye_entered = str(eye)
        if eye_entered in ('Left','LEFT','left','l','L'):
            self.console(c='blue', msg="eye_entered = left (%s)"%(eye_entered))
            self.eye_used = self.left_eye
        else:
            self.console(c='blue', msg="eye_entered = right (%s)"%(eye_entered))
            self.eye_used = self.right_eye
            
        return self.eye_used
            
        
    def calibration(self, window):
        """
        Calibrates eyetracker using psychopy stimuli.
        
        Parameters
        ----------
        window : :class:`psychopy.visual.window.Window`
            PsychoPy window instance.
            
        Examples
        --------
        >>> eyetracking.calibration(window=window)
        """   
        self.console(msg="eyetracking.calibration()")
        #if connected to eyetracker
        if self.connected:
            self.console(c='blue', msg="connected")
            # put the tracker in offline mode before we change its configrations
            self.tracker.setOfflineMode()
            # Generate custom calibration stimuli
            self.genv = calibration(w=self.w, h=self.h, tracker=self.tracker, window=window)
            # execute custom calibration display
            pylink.openGraphicsEx(self.genv)
            #set sampling rate
            self.tracker.sendCommand('sample_rate %d'%(self.sample_rate))
            # inform the tracker the resolution of the subject display
            # note: [see Eyelink Installation Guide, Section 8.4: Customizing Your PHYSICAL.INI Settings ]
            self.tracker.sendCommand("screen_pixel_coords = 0 0 %d %d"%(self.w - 1, self.h - 1))
            # save display resolution in EDF data file for Data Viewer integration purposes
            # note: [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
            self.tracker.sendMessage("DISPLAY_COORDS = 0 0 %d %d"%(self.w - 1, self.h - 1))
            # set calibration type    
            self.tracker.sendCommand("calibration_type = HV%d"%(self.c_num))
            # set calibraiton pacing
            self.tracker.setAutoCalibrationPacing(self.paval)
            # calibrate
            self.tracker.doTrackerSetup(self.w, self.h)
    
    def drift_correction(self, window, drift, limit=999, core=None, thisExp=None):
        """
        Starts drift correction, and calibrates eyetracker using psychopy stimuli..
        
        Parameters
        ----------
        window : :class:`psychopy.visual.window.Window`
            PsychoPy window instance.
        drift : :obj:`int`
            Counter of drift correction runs.
        limit : :obj:`int`
            Maxinum drift corrections.
        core : :obj:`psychopy.core`
            Basic functions, including timing, rush (imported), quit.
        thisExp : :obj:`psychopy.data.experiment.ExperimentHandler`
            Experiment handler instance, used to keep track of multiple loops/handlers.
            
        Examples
        --------
        >>> eyetracking.drift_correction(window=window, drift=1, limit=999)
        """
        self.console(msg="eyetracking.drift_correction()")
        if (drift >= limit): #if drift correct failed more than limit
            self.tracker.sendMessage("drift correction failed") #send failure message
            self.stop_recording()
            #end experiment
            if self.is_psychopy:
                thisExp.abort()
                window.close()
                core.quit()
        
        #run calibration
        self.calibration(window)
            
    def sample(self, eye_used):
        """
        Collects new gaze coordinates from Eyelink.
        
        Parameters
        ----------
        eye_used : :obj:`str`
            Checks if eye used is available.
            
        Examples
        --------
        >>> eyetracking.sample(eye_used=eye_used)
        """
        #check for new sample update
        s = self.tracker.getNewestSample() # check for new sample update
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
        
        Examples
        --------
        >>> msg = "stimulus onset"
        >>> eyetracking.send_message(msg=msg)
        """
        self.tracker.sendMessage(msg)
        
    def send_variable(self, variables):
        """
        send trial variable to eyelink at the end of trial.
        
        Parameters
        ----------
        variable : :obj:`dict`
            Trial-related variables to be read by eyelink.
        """
        if variables is not None:
            for key, value in variables.items():
                msg = "!V TRIAL_VAR %s %s" %(key, value)
                self.tracker.sendMessage(msg)
                pylink.msecDelay(1)
            #finished
            self.console(msg="variables sent")
        else:
            self.console(c="red", msg="no variables entered")
            
        
    def start_recording(self, trial=None, block=None):
        """
        Starts recording of eyelink.
        
        Parameters
        ----------
        trial : :obj:`str`
            Trial Number.
        block : :obj:`str`
            Block Number.
            
        Notes
        ----- 
        tracker.beginRealTimeMode():
            To ensure that no data is missed before the important part of the trial starts. The EyeLink 
            tracker requires 10 to 30 milliseconds after the recording command to begin writing data. 
            This extra data also allows the detection of blinks or saccades just before the trial start, 
            allowing bad trials to be discarded in saccadic RT analysis. A "SYNCTIME" message later 
            in the trial marks the actual zero-time in the trial's data record for analysis.
            [see pylink.chm]
        TrialID:
            The "TRIALID" message is sent to the EDF file next. This message must be placed 
            in the EDF file before the drift correction and before recording begins, and is critical 
            for data analysis. The viewer will not parse any messages, events, or samples that exist
            in the data file prior to this message. The command identifier can be changed in the data
            loading preference settings.
            [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
        SYNCTIME:
            Marks the zero-time in a trial. A number may follow, which is interpreted as the delay of 
            the message from the actual stimulus onset. It is suggested that recording start 100 
            milliseconds before the display is drawn or unblanked at zero-time, so that no data at the 
            trial start is lost.
            [see pylink.chm]
        
        Examples
        --------
        >>> eyetracking.start_recording(block=1, trial=1)
        """
        self.console(msg="eyetracking.start_recording()")
        
        #Message to post to Eyelink Display Monitor
        self.tracker.sendCommand("record_status_message 'Trial %d Block %d'" %(trial, block))
            
        #indicates start of trial
        self.tracker.sendMessage('TRIALID %d'%(trial))
        
        # start recording, parameters specify whether events and samples are
        # stored in file, and available over the link
        self.tracker.startRecording(1, 1, 1, 1)
        
        #buffer to prevent loss of data
        pylink.beginRealTimeMode(100)
        
        #indicates zero-time of trial
        self.tracker.sendMessage('SYNCTIME')
        self.tracker.sendMessage('start recording')

    def stop_recording(self, trial=None, block=None, variables=[]):
        """
        Stops recording of eyelink. Also allows transmission of trial-level variables to Eyelink.
        
        Parameters
        ----------
        trial : :obj:`int`
            Trial Number.
        block : :obj:`int`
            Block Number.
        variables : :obj:`dict`
            Dict of variables to send to eyelink (variable name, value).
        
        Notes
        -----
        pylink.pumpDelay():
            Does a unblocked delay using currentTime(). This is the preferred delay function 
            when accurate timing is not needed.
            [see pylink.chm]
        pylink.msecDelay():
            During calls to pylink.msecDelay(), Windows is not able to handle messages. One result of 
            this is that windows may not appear. This is the preferred delay function when accurate 
            timing is needed.
            [see pylink.chm]
        tracker.endRealTimeMode():
            Returns the application to a priority slightly above normal, to end realtime mode. This 
            function should execute rapidly, but there is the possibility that Windows will allow other 
            tasks to run after this call, causing delays of 1-20 milliseconds. This function is equivalent 
            to the C API void end_realtime_mode(void).
            [see pylink.chm]
        TRIAL_VAR: 
            Lets users specify a trial variable and value for the given trial. One
            message should be sent for each trial condition variable and its corresponding value. If
            this command is used there is no need to use TRIAL_VAR_LABELS. The default command identifier 
            can be changed in the data loading preference settings. Please note that the eye tracker 
            can handle about 20 messages every 10 milliseconds. So be careful not to send too many 
            messages too quickly if you have many trial condition messages to send. Add one millisecond 
            delay between message lines if this is the case.
            [see pylink.chm]
        TRIAL_RESULT: 
            Defines the end of a trial. The viewer will not parse any messages, events, or samples that 
            exist in the data file after this message. The command identifier can be changed in the 
            data loading preference settings.
            [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
            
        Examples
        --------
        >>> variables = dict(stimulus='face.png', event='stimulus')
        >>> eyetracking.stop_recording(trial=trial, block=block, variables=variables)
        """
        self.console(msg="eyetracking.stop_recording()")
        
        #end of trial message
        self.tracker.sendMessage('end recording')
        
        #end realtime mode
        pylink.endRealTimeMode()
        pylink.msecDelay(100)
        
        #send trial-level variables
        variables['trial'] = trial
        variables['block'] = block
        self.send_variable(variables=variables)
        
        #specify end of trial
        self.tracker.sendMessage("TRIAL_RESULT 1")
        
        #stop recording eye data
        self.tracker.stopRecording()
        
    def finish_recording(self):
        """
        Finish recording of eyelink.
        
        Parameters
        ----------
        subject : :obj:`int`
            subject number.
        
        Notes
        -----
        pylink.pumpDelay():
            Does a unblocked delay using currentTime(). This is the preferred delay function 
            when accurate timing is not needed.
            [see pylink.chm]
        pylink.msecDelay():
            During calls to pylink.msecDelay(), Windows is not able to handle messages. One result of 
            this is that windows may not appear. This is the preferred delay function when accurate 
            timing is needed.
            [see pylink.chm]
        tracker.setOfflineMode():
            Places EyeLink tracker in offline (idle) mode. Wait till the tracker has finished the 
            mode transition.
            [see pylink.chm]
        tracker.endRealTimeMode():
            Returns the application to a priority slightly above normal, to end realtime mode. This 
            function should execute rapidly, but there is the possibility that Windows will allow other 
            tasks to run after this call, causing delays of 1-20 milliseconds. This function is 
            equivalent to the C API void end_realtime_mode(void).
            [see pylink.chm]
        tracker.receiveDataFile():
            This receives a data file from the EyeLink tracker PC. Source filename and destination 
            filename should be given.
            [see pylink.chm]
            
        Examples
        --------
        >>> #end recording session
        >>> eyetracking.finish_recording()
        """
        self.console(msg="eyetracking.finish_recording()")
        # generate file path
        self.path = "%s/data/edf/"%(os.getcwd())
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        #double check realtime mode has ended
        pylink.endRealTimeMode()
        pylink.pumpDelay(500)
        
        #rlaces eyeLink tracker in offline (idle) mode
        self.tracker.setOfflineMode()
        
        #allow buffer to prepare data for closing
        pylink.msecDelay(500)
        
        #closes any currently opened EDF file on the EyeLink tracker computer's hard disk
        self.tracker.closeDataFile()
        
        #This receives a data file from the eyelink tracking computer
        destination = self.path + self.fname
        self.tracker.receiveDataFile(self.fname, destination)
        
        #wends a disconnect message to the EyeLink tracker
        self.tracker.close()
