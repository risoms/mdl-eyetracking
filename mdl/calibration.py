#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:57:56 2019

@author: mdl-admin
"""

#---main
from pdb import set_trace as breakpoint
import array, string
from PIL import Image

#---psychopy
from psychopy import visual, event, sound

#---eyetracking
from . import pylink

#---------------------------------------------start
class calibration(pylink.EyeLinkCustomDisplay):
    """This inherits a default class from pylink then adds psychopy stim."""
    def __init__(self, w, h, tracker, window):
        """
        Allow color print to console.
        
        Parameters
        ----------
        class : :class:`object`
            Eyelink tracker instance.
        msg : :class:`object`
           The Psychopy window we plan to use for stimulus presentation.
        """
        pylink.EyeLinkCustomDisplay.__init__(self)
        #---setup
        #window
        self.window = window
        self.window.flip(clearBuffer=True)
        self.w = w
        self.h = h
        #mouse
        self.display.mouseVisible = False
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
        self.targetout = visual.Circle(self.window, pos=(0, 0), radius=10, fillColor=[1,1,1], lineColor=[1,1,1], units='pix')
        self.targetin = visual.Circle(self.window, pos=(0, 0), radius=3, fillColor=[-1,-1,-1], lineColor=[-1,-1,-1], units='pix')
        
        # lines for drawing cross hair etc.
        self.line = visual.Line(self.display, start=(0, 0), end=(0,0), lineWidth=2.0, lineColor=[0,0,0], units='pix')

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
        ori=0, pos=[0, 0], size=None, color=[1,1,1], colorSpace='rgb', opacity=1, flipHoriz=False, flipVert=False,texRes=128,
        interpolate=True, depth=-1.0)
        drift_screen.draw()
        self.window.flip()

    def clear_cal_display(self):
        """Clear the calibration display."""
        
        self.calibInst.autoDraw = False
        self.title.autoDraw = False
        self.display.clearBuffer()
        self.display.color = self.bg_color
        self.display.flip()
        
    def exit_cal_display(self):
        """Exit the calibration/validation routine."""    
        self.display.setUnits(self.units)
        self.clear_cal_display()
        
    def clear_drift_display(self):
        self.setup_drift_display()
    
    def exit_drift_display(self):
        """Exits drift display."""
        self.clear_drift_display()

    def record_abort_hide(self):
        pass

    def erase_cal_target(self):
        self.window.flip()

    def erase_drift_target(self):
        self.window.flip()
        
    def draw_cal_target(self, x, y):
        # Convert to psychopy coordinates
        x = x - (self.w / 2)
        y = -(y - (self.h / 2))

        # Set calibration target position
        self.targetout.pos = (x, y)
        self.targetin.pos = (x, y)

        # Display
        #self.play_beep(pylink.CAL_TARG_BEEP)
        self.targetout.draw()
        self.targetin.draw()
        self.window.flip()

    def draw_drift_target(self, x, y):
        # Convert to psychopy coordinates
        x = x - (self.w / 2)
        y = -(y - (self.h / 2))

        # Set calibration target position
        self.targetout.pos = (x, y)
        self.targetin.pos = (x, y)

        # Display
        #self.play_beep(pylink.CAL_TARG_BEEP)
        self.targetout.draw()
        self.targetin.draw()
        self.window.flip()
        
    def play_beep(self, beepid):
        """Play a sound during calibration/drift correct."""

        if beepid == pylink.CAL_TARG_BEEP or beepid == pylink.DC_TARG_BEEP:
            self.__target_beep__.play()
        if beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
            self.__target_beep__error__.play()
        if beepid in [pylink.CAL_GOOD_BEEP, pylink.DC_GOOD_BEEP]:
            self.__target_beep__done__.play()
            
    def getColorFromIndex(self, colorindex):
         """Return psychopy colors for elements in the camera image"""
         
         if colorindex   ==  pylink.CR_HAIR_COLOR:          return (1, 1, 1)
         elif colorindex ==  pylink.PUPIL_HAIR_COLOR:       return (1, 1, 1)
         elif colorindex ==  pylink.PUPIL_BOX_COLOR:        return (-1, 1, -1)
         elif colorindex ==  pylink.SEARCH_LIMIT_BOX_COLOR: return (1, -1, -1)
         elif colorindex ==  pylink.MOUSE_CURSOR_COLOR:     return (1, -1, -1)
         else:                                              return (0,0,0)
   
    def draw_line(self, x1, y1, x2, y2, colorindex):
        """Draw a line. This is used for drawing crosshairs/squares"""
        
        if self.pylinkMinorVer== '1': # the Mac version
            x1 = x1/2; y1=y1/2; x2=x2/2;y2=y2/2;
            
        y1 = (-y1  + self.size[1]/2)* self.img_scaling_factor 
        x1 = (+x1  - self.size[0]/2)* self.img_scaling_factor 
        y2 = (-y2  + self.size[1]/2)* self.img_scaling_factor 
        x2 = (+x2  - self.size[0]/2)* self.img_scaling_factor 
        color = self.getColorFromIndex(colorindex)
        self.line.start     = (x1, y1)
        self.line.end       = (x2, y2)
        self.line.lineColor = color
        self.line.draw()
    
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
        """Clcear the camera image"""
        
        self.clear_cal_display()
        self.calibInst.autoDraw=True
        self.display.flip()

    def alert_printf(self, msg):
        """Print error messages."""
        print("Error: " + msg)

    def setup_image_display(self, width, height):
        """set up the camera image, for newer APIs, the size is 384 x 320 pixels"""
        
        self.last_mouse_state = -1
        self.size = (width, height)
        self.title.autoDraw = True
        self.calibInst.autoDraw=True

    def image_title(self, text):
        """Draw title text below the camera image"""
        
        self.title.text = text
        
    def draw_image_line(self, width, line, totlines, buff):
        """Display image pixel by pixel, line by line"""

        self.size = (width, totlines)
        i =0
        for i in range(width):
            try: self.imagebuffer.append(self.pal[buff[i]])
            except: pass
            
        if line == totlines:
            bufferv = self.imagebuffer.tostring()
            img = Image.frombytes("RGBX", (width, totlines), bufferv) # Pillow
            imgResize = img.resize((width*self.img_scaling_factor, totlines*self.img_scaling_factor))
            imgResizeVisual = visual.ImageStim(self.display, image=imgResize, units='pix')
            imgResizeVisual.draw()
            self.draw_cross_hair()
            self.display.flip()
            self.imagebuffer = array.array(self.imgBuffInitType)

    def set_image_palette(self, r, g, b):
        """Given a set of RGB colors, create a list of 24bit numbers representing the pallet.
        I.e., RGB of (1,64,127) would be saved as 82047, or the number 00000001 01000000 011111111"""
        
        self.imagebuffer = array.array(self.imgBuffInitType)
        self.resizeImagebuffer = array.array(self.imgBuffInitType)
        #self.clear_cal_display()
        sz = len(r)
        i =0
        self.pal = []
        while i < sz:
            rf = int(b[i])
            gf = int(g[i])
            bf = int(r[i])
            self.pal.append((rf<<16) | (gf<<8) | (bf))
            i = i+1