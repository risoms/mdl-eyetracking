#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom
@email: semeon.risom@gmail.com.

Sample code to run SR Research Eyelink eyetracking system. Code is optimized for the Eyelink 1000 Plus (5.0),
but should be compatiable with earlier systems.
"""

#---main
from pdb import set_trace as breakpoint
import string, scipy, os, tempfile
import numpy as np

#---psychopy
from psychopy import visual, event, sound

#---eyetracking
import pylink

class calibration(pylink.EyeLinkCustomDisplay):
    """This inherits a default class from pylink then adds psychopy stim."""
    def __init__(self, w, h, tracker, window):
        """
        Allow color print to console.
        
        Parameters
        ----------
        w,h : :class:`int`
            Screen width, height.
        tracker : :class:`psychopy.visual.window.Window`
            PsychoPy window instance.
        window : :class:`psychopy.visual.window.Window`
            PsychoPy window instance.
        """
        pylink.EyeLinkCustomDisplay.__init__(self)
        #---setup
        #window
        self.window = window
        self.window.flip(clearBuffer=True)
        self.w = w
        self.h = h
        #mouse
        self.window.mouseVisible = False
        self.mouse = event.Mouse(visible=False)
        self.last_mouse_state = -1
        #sound
        self.__target_beep__ = sound.Sound('A', octave=4, secs=0.1)
        self.__target_beep__done__ = sound.Sound('E', octave=4, secs=0.1)
        self.__target_beep__error__ = sound.Sound('E', octave=6, secs=0.1)
        
        #display
        self.backcolor = window.color
        tcolout = -1
        self.txtcol = tcolout
        
        #set circles
        self.out = visual.Circle(self.window, pos=(0, 0), radius=10, fillColor=[1,1,1], lineColor=[1,1,1], units='pix')
        self.on = visual.Circle(self.window, pos=(0,0), radius=3, fillColor=[-1,-1,-1], lineColor=[-1,-1,-1], units='pix')
        
        # lines for drawing cross hair etc.
        self.line = visual.Line(self.window, start=(0, 0), end=(0,0), lineWidth=2.0, lineColor=[0,0,0], units='pix')

    def setup_cal_display(self):
        """Sets up the initial calibration display, which contains a menu with instructions."""
        menu_screen = visual.ImageStim(self.window, name='menu_screen', image="instructions/menu.png", mask=None, 
        ori=0, pos=[0, 0], size=None, color=[1,1,1], colorSpace='rgb', opacity=1, flipHoriz=False, flipVert=False, texRes=128, 
        interpolate=True, depth=-1.0)
        menu_screen.draw()
        self.window.flip()

    def setup_drift_display(self):
        """Sets up the initial drift display"""
        drift_screen = visual.ImageStim(self.window, name='drift_screen', image="instructions/fixation.png", mask=None,
        ori=0, pos=[0, 0], size=None, color=[1,1,1], colorSpace='rgb',opacity=1,flipHoriz=False,flipVert=False,texRes=128,
        interpolate=True, depth=-1.0)
        drift_screen.draw()
        self.window.flip()

    def exit_cal_display(self):
        """Exits calibration display."""       
        self.setup_cal_display()
    
    def exit_drift_display(self):
        """Exits drift display."""
        self.setup_drift_display()
    
    def record_abort_hide(self):
        pass    
    
    def clear_cal_display(self):
        """Clear the calibration display."""
        self.setup_cal_display()
        
    def clear_drift_display(self):
        """Clear the drift-check display."""
        self.setup_drift_display()
    
    def erase_cal_target(self):
        """Erase the calibration/validation target."""
        self.window.flip()

    def erase_drift_target(self):
        """Erase the drift-check target."""
        self.window.flip()   

    def play_beep(self, beepid):
        """ Play a sound during calibration/drift correct."""
        print('beepid: %s'%(beepid))
        if beepid == pylink.CAL_TARG_BEEP or beepid == pylink.DC_TARG_BEEP:
            self.__target_beep__.play()
        if beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
            self.__target_beep__error__.play()
        if beepid in [pylink.CAL_GOOD_BEEP, pylink.DC_GOOD_BEEP]:
            self.__target_beep__done__.play()
        
    def draw_cal_target(self, x, y):
        """Draw the calibration/validation target."""
        # convert to psychopy coordinates
        x = x - (self.w / 2)
        y = -(y - (self.h / 2))

        # set calibration target position
        self.out.pos = (x, y)
        self.on.pos = (x, y)

        # display
        self.play_beep(pylink.CAL_TARG_BEEP)
        self.out.draw()
        self.on.draw()
        self.window.flip()
        
    def draw_drift_target(self, x, y):
        """Draw the drift-check target."""
        # convert to psychopy coordinates
        x = x - (self.w / 2)
        y = -(y - (self.h / 2))

        # set calibration target position
        self.out.pos = (x, y)
        self.on.pos = (x, y)

        # display
        self.play_beep(pylink.CAL_TARG_BEEP)
        self.out.draw()
        self.on.draw()
        self.window.flip()
        
    def getColorFromIndex(self, colorindex):
        if colorindex == pylink.CR_HAIR_COLOR:
            return (1, 1, 1)
        elif colorindex == pylink.PUPIL_HAIR_COLOR:
            return (1, 1, 1)
        elif colorindex == pylink.PUPIL_BOX_COLOR:
            return (-1, 1, -1)
        elif colorindex == pylink.SEARCH_LIMIT_BOX_COLOR:
            return (1, -1, -1)
        elif colorindex == pylink.MOUSE_CURSOR_COLOR:
            return (1, -1, -1)
        else:
            return (-1, -1, -1)

    def get_input_key(self):
        """This function will be constantly pools, update the stimuli here is you need
        dynamic calibration target."""
        
        ky=[]
        for keycode, modifier in event.getKeys(modifiers=True):
            k= pylink.JUNK_KEY
            if keycode   == 'f1': k = pylink.F1_KEY
            elif keycode == 'f2': k = pylink.F2_KEY
            elif keycode == 'f3': k = pylink.F3_KEY
            elif keycode == 'f4': k = pylink.F4_KEY
            elif keycode == 'f5': k = pylink.F5_KEY
            elif keycode == 'f6': k = pylink.F6_KEY
            elif keycode == 'f7': k = pylink.F7_KEY
            elif keycode == 'f8': k = pylink.F8_KEY
            elif keycode == 'f9': k = pylink.F9_KEY
            elif keycode == 'f10': k = pylink.F10_KEY
            elif keycode == 'pageup': k = pylink.PAGE_UP
            elif keycode == 'pagedown': k = pylink.PAGE_DOWN
            elif keycode == 'up': k = pylink.CURS_UP
            elif keycode == 'down': k = pylink.CURS_DOWN
            elif keycode == 'left': k = pylink.CURS_LEFT
            elif keycode == 'right': k = pylink.CURS_RIGHT
            elif keycode == 'backspace': k = ord('\b')
            elif keycode == 'return': k = pylink.ENTER_KEY
            elif keycode == 'space': k = ord(' ')
            elif keycode == 'escape': k = pylink.ESC_KEY
            elif keycode == 'tab': k = ord('\t')
            elif keycode in string.ascii_letters: k = ord(keycode)
            elif k== pylink.JUNK_KEY: k = 0

            # plus/equal & minux signs for CR adjustment
            if keycode in ['num_add', 'equal']: k = ord('+')
            if keycode in ['num_subtract', 'minus']: k = ord('-')

            if modifier['alt']==True: mod = 256
            else: mod = 0
            
            ky.append(pylink.KeyInput(k, mod))

        return ky

    def exit_image_display(self):
        """Clear the camera image."""
        self.clear_cal_display()

    def alert_printf(self, msg):
        """Print error messages."""
        print ("alert_printf %s")%(msg)

    def setup_image_display(self, width, height):
        """Set up the camera image, for newer APIs, the size is 384 x 320 pixels."""

        self.size = (width / 2, height / 2)
        self.clear_cal_display()
        self.last_mouse_state = -1

        # Create array to hold image data later
        if self.rgb_index_array is None:
            self.rgb_index_array = np.zeros((self.size[1], self.size[0]),
                                            dtype=np.uint8)

    def image_title(self, text):
        """Display or update Pupil/CR info on image screen."""
        if self.imagetitlestim is None:
            self.imagetitlestim = visual.TextStim(self.window,
                                                  text=text,
                                                  pos=(0, self.window.size[1] / 2 - 15), height=28,
                                                  color=self.txtcol,
                                                  alignHoriz='center', alignVert='top',
                                                  wrapWidth=self.window.size[0] * .8,
                                                  units='pix')
        else:
            self.imagetitlestim.setText(text)

    def draw_image_line(self, width, line, totlines, buff):
        """Display image pixel by pixel, line by line."""
        for i in range(width):
            self.rgb_index_array[line - 1, i] = buff[i]

        # Once all lines are collected turn into an image to display
        if line == totlines:
            # Make image
            image = scipy.misc.toimage(self.rgb_index_array,
                                       pal=self.rgb_pallete,
                                       mode='P')
            # Resize Image
            if self.imgstim_size is None:
                maxsz = self.w / 2
                mx = 1.0
                while (mx + 1) * self.size[0] <= maxsz:
                    mx += 1.0
                self.imgstim_size = int(self.size[0] * mx), int(
                    self.size[1] * mx)
            image = image.resize(self.imgstim_size)

            # Save image as a temporary file
            tfile = os.path.join(tempfile.gettempdir(), '_eleye.png')
            image.save(tfile, 'PNG')

            # Need this for target distance to show up
            self.__img__ = image
            self.draw_cross_hair()
            self.__img__ = None

            # Create eye image
            if self.eye_image is None:
                self.eye_image = visual.ImageStim(self.window, tfile,
                                                  size=self.imgstim_size,
                                                  units='pix')
            else:
                self.eye_image.setImage(tfile)

            # Redraw the Camera Setup Mode graphics
            self.eye_image.draw()
            if self.imagetitlestim:
                self.imagetitlestim.draw()

            # Display
            self.window.flip()

    def set_image_palette(self, r, g, b):
        """
        Given a set of RGB colors, create a list of 24bit numbers representing the pallet. 
        Example: RGB of (1,64,127) would be saved as 82047, or the number 00000001 01000000 011111111.
        """
        self.clear_cal_display()
        sz = len(r)
        self.rgb_pallete = np.zeros((sz, 3), dtype=np.uint8)
        i = 0
        while i < sz:
            self.rgb_pallete[i:] = int(r[i]), int(g[i]), int(b[i])
            i += 1
