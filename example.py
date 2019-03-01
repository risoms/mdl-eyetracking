#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom
@email: semeon.risom@gmail.com

References:
    https://www.psychopy.org/api/hardware/pylink.html
"""

#----------------imports
#%%import
from psychopy import visual, core
import sys
sys.path.insert(0, '.\lib')
import mdl

#----------------pre-task
# init
## is_libraries - should python required libraries be checked for availability (default=False)
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

subject = 1
eyetracking = mdl.eyetracking(libraries=False, subject=subject, sample_rate=500, c_num=13, paval=1000,
                              pupil_size="area", ip="127.0.0.1", s_port=4444, r_port=5555, 
                              saccade_velocity_threshold=35, saccade_acceleration_threshold=9500, 
                              recording_parse_type="GAZE", enable_search_limits=True, 
                              track_search_limits=True, autothreshold_click=True, autothreshold_repeat=True, 
                              enable_camera_position_detect=True)
# create psychopy window
window = visual.Window(
    size=[1336, 768], fullscr=False, screen=0,
    allowGUI=True, allowStencil=False,
    monitor=u'testMonitor', color=u'white', colorSpace='rgb',
    blendMode='avg')

# set dominant eye
## eye_used will either be should either be 'left' or 'right'
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

dominant_eye = 'left'
eye_used = eyetracking.set_eye_used(eye=dominant_eye)

#%%
#----------------calibration
# calibration
##window - psychopy window object instant
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

eyetracking.calibration(window=window)

# print to console, terminal (for debugging)
## c - blue, red, green, orange, purple, grey
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

eyetracking.console(c="green", msg="eyetracking.calibration() started")

#%%
#----------------within trial
# start recording
## block=block number(from psychopy) #trial=trial number(from psychopy)
eyetracking.start_recording(trial=1, block=1)

#%%
# get gaze samples from eyetracker to psychopy (only if needed in experiment)
## loop every .002 msec #eye_used will either be 1 (left eye) or 0 (right eye)
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

eyetracking.sample(eye_used=eye_used)

#%%
# send messages to eyelink during the trial
msg = "stimulus onset"
eyetracking.send_message(msg=msg)

#%%
# stop recording
## block=block number(from psychopy), trial=trial number(from psychopy)
## variables (optional) = dictionary of trial-event data to be saved to eyelink
variables = dict(stimulus='img.jpg', 
                 trial_type='fixation', 
                 race="white")
eyetracking.stop_recording(trial=trial, block=block, variables=variables)

#%%
# end recording session
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

eyetracking.finish_recording()