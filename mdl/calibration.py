#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
| Created on Wed Feb 13 15:37:43 2019
| @author: Semeon Risom
| @email: semeon.risom@gmail.com.
| Sample code to run SR Research Eyelink eyetracking system. Code is optimized for the Eyelink 1000 Plus (5.0),
| but should be compatiable with earlier systems.
"""

#---main
from pdb import set_trace as breakpoint
import string, scipy, os, tempfile, array
from PIL import Image
import numpy as np

#---psychopy
from psychopy import visual, event, sound

#---eyetracking
from . import pylink

class calibration(pylink.EyeLinkCustomDisplay):
    """This alows eye mdl.eyetracking package to initiate a calibration/validation/drift correction screen."""
    def __init__(self, w, h, tracker, window):
        """
        Allow colored printing to console.

        Parameters
        ----------
        w,h : :class:`int`
            Screen width, height.
        tracker : :class:`object`
            Eyelink tracker instance.
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
        self.__target_beep__ = sound.Sound("dist/type.wav",secs=-1,loops=0)
        self.__target_beep__done__ = sound.Sound("dist/qbeep.wav",secs=-1,loops=0)
        self.__target_beep__error__ = sound.Sound("dist/error.wav",secs=-1,loops=0)        
        #color, image
        self.rgb_index_array = None
        self.backcolor = window.color
        self.txtcol = -1
        self.imgBuffInitType = 'I'
        self.img_scaling_factor = 3
        self.imagebuffer = array.array(self.imgBuffInitType)
        self.resizeImagebuffer = array.array(self.imgBuffInitType)
        #title
        self.msgHeight = self.size[1]/20.0
        self.title = visual.TextStim(win=self.window, text='', pos = (0,-self.size[1]/2-self.msgHeight), color=[1,1,1], 
                                        units='pix', height=self.msgHeight, alignVert='center', wrapWidth=self.w)
        ##menu
        menu = '\n'.join(['Enter: Show/Hide camera image','Left/Right: Switch camera view','C: Calibration','V: Validation','O: Start Recording',
        '+=/-: CR threshold','Up/Down: Pupil threshold','Alt+arrows: Search limit'])
        self.menu = visual.TextStim(self.window, alignHoriz='left',alignVert ='top', height=self.msgHeight, color=[1,1,1],
                                    pos = (-self.w/2.0, self.h/2.0), units='pix', text = menu)
        #fixation
        self.line = visual.Line(self.window, start=(0, 0), end=(0,0), lineWidth=2.0, lineColor=[0,0,0], units='pix')

        #set circles
        self.out = visual.Circle(self.window, pos=(0, 0), radius=10, fillColor=[1,1,1], lineColor=[1,1,1], units='pix')
        self.on = visual.Circle(self.window, pos=(0,0), radius=3, fillColor=[-1,-1,-1], lineColor=[-1,-1,-1], units='pix')

        # lines for drawing cross hair etc.
        self.line = visual.Line(self.window, start=(0, 0), end=(0,0), lineWidth=2.0, lineColor=[0,0,0], units='pix')

    def setup_cal_display(self):
        """Sets up the initial calibration display, which contains a menu with instructions."""
        self.menu.draw()
        self.window.flip()

    def exit_cal_display(self):
        """Exits calibration display."""       
        self.setup_cal_display()

    def record_abort_hide(self):
        pass    

    def clear_cal_display(self):
        """Clear the calibration display."""
        self.setup_cal_display()

    def erase_cal_target(self):
        """Erase the calibration/validation target."""
        self.window.flip()
        
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

    def play_beep(self, beepid):
        """ Play a sound during calibration/drift correction."""
        if beepid == pylink.CAL_TARG_BEEP or beepid == pylink.DC_TARG_BEEP:
            self.__target_beep__.play()
        if beepid == pylink.CAL_ERR_BEEP or beepid == pylink.DC_ERR_BEEP:
            self.__target_beep__error__.play()
        if beepid in [pylink.CAL_GOOD_BEEP, pylink.DC_GOOD_BEEP]:
            self.__target_beep__done__.play()
        
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
        """
        This function will be constantly pools, update the stimuli here is you need
        dynamic calibration target.
        """
        
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

        self.last_mouse_state = -1
        self.size = (width, height)
        self.title.autoDraw = True
        self.menu.autoDraw = True

    def image_title(self, text):
        """Display or update Pupil/CR info on image screen."""
        self.title.text = text

    def draw_image_line(self, width, line, totlines, buff):
        """Display image pixel by pixel, line by line."""
        self.size = (width, totlines)

        for i in range(width):
            try: self.imagebuffer.append(self.pal[buff[i]])
            except: pass
            
        if line == totlines:
            bufferv = self.imagebuffer.tostring()
            img = Image.frombytes("RGBX", (width, totlines), bufferv)
            imgResize = img.resize((width*self.img_scaling_factor, totlines*self.img_scaling_factor))
            imgResizeVisual = visual.ImageStim(self.window, image=imgResize, units='pix')
            imgResizeVisual.draw()
            self.draw_cross_hair()
            self.window.flip()
            self.imagebuffer = array.array(self.imgBuffInitType)

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