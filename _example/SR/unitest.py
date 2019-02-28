#
# Copyright (c) 1996-2012, SR Research Ltd., All Rights Reserved
#
#
# For use by SR Research licencees only. Redistribution and use in source
# and binary forms, with or without modification, are NOT permitted.
#
#
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the distribution.
#
# Neither name of SR Research Ltd nor the name of contributors may be used
# to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# $Date: 2012/11/14
# 
#
# DESCRIPTION:
# unitest.py demonstrates Pylink code required to connect, setup,
# control and use an EyeLink eyetracker to record and access eyemovement.
# In order to eliminate dependency on third party display software like Pygame,
# this example does not demonstrate use of any visual stimuli during trials.
# The experiment is made up of three trials that start with a drift correction
# screen followed by a five-second blank screen. During this time, the tracker
# screen shows fixation update events (cross), fixation end events (number) 
# and saccade start and end events (line).
#
# This Pylink code demonstrates the following steps:
# 1-initializing connection to the tracker
# 2-initializing display-side graphics
# 3-initializing data file
# 4-setting up tracking, recording and calibration options
# 5-launching experiment display (run_trials)
# 6-initial tracker calibration (run_trials)
# 7-running individual trial (do_trial)
# 8-verify connection to tracker and do drift correction
#   while checking if recalibration is needed (do_trial)
# 9-start actual recording of samples and events to the data file
#   and send both over the link (do_trial)
# 10-enter realtime mode and mark trial start time (do_trial)
# 11-stub to insert code that loads the initial visual stimulus (do_trial)
# 12-mark the time initial visual stimulus came on relative
#   to the trial start time in the data file (do_trial)
# 13-wait and make sure we get the start signal for link samples
#   then mark which eye is being tracked (do_trial)
# 14-flush outstanding input from response box (do_trial)
# 15-pole for newest sample over the link while verifying that tracker
#   is still recording, that termination or setup have not been requested
#   and that the trial time has not yet exceeded the predefined trial duration (do_trial)
# 16-consume all outstanding data in the link buffer (do_trial).
#   send tracker command to draw the following on the gaze cursor of the tracker screen:
#     draw cross when a fixation update event is encountered (drawFixation)
#     draw line when saccade end event is encountered (drawSaccade)
#     print fixation number when fixation end event is encountered (printFixation)
# 17-end realtime mode, stop recording and consume pending key presses (end_trial)
# 18-record various event counts and mock trial result to data file (do_trial)
# 19-set offline,close and transfer data file from host to display pc
# 20-close eyelink connection and quit display-side graphics

from pylink import *
import time
import gc
import sys
import os

RIGHT_EYE = 1
LEFT_EYE = 0
BINOCULAR = 2
NTRIALS = 3
TRIALDUR = 5000
TARGETSIZEFIX = 6
TARGETSIZEFIXUPDATE = 3
TARGETSIZESACC = 12
COLOURWHITE = 15
COLOURRED = 4
SCREENWIDTH = 800 
SCREENHEIGHT = 600
trial_condition=['condition1', 'condition2', 'condition3']

def end_trial():
	'''Ends recording: adds 100 msec of data to catch final events'''
	pylink.endRealTimeMode()  
	pumpDelay(100)	   
	getEYELINK().stopRecording()
	while getEYELINK().getkey() : 
		pass
	
# printFixation. print text representing the location, order, or type of fixation event on the tracker display
# Parameters:
# fix: a three element tuplet to be interpreted as follows:
# as fix[0]=text,fix[1]=x,fix[2]=y
def printFixation(fix):
	# send the command to print text on the tracker screen
	# use asterisk (*) to log the command in the edf file
	# use exclamation (!) to prioritize the command
	# sendCommand will wait for acknowledgement from the tracker side
	# but the draw command may not have completed by the time sendCommand returns
	if len(fix) == 3:
		#getEYELINK().drawText(fix[0], (int(fix[1]/SCREENWIDTH*80), int(fix[2]/SCREENHEIGHT*30)))
		getEYELINK().sendCommand("print_position %d %d" % \
			(max(int(fix[1]/SCREENWIDTH*80),1), max(int(fix[2]/SCREENHEIGHT*30),1)))
		getEYELINK().sendCommand("echo %s" %(fix[0]))
	# if coordinates tuplet has other number of elements, give a warning message and keep going
	else:
		print("printFixation expects a three-element tuplet for its first argument\n")

# drawFixation. draw a cross or a filled box representing a fixation or fixation update on the tracker display
# Parameters:
# fix: a two to four-element tuplet to be interpreted as follows:
# if tuplet fix contains two elements a cross is requested. 
#	Interpret as fix[0]=x,fix[1]=y
# if tuplet fix contains three elements a box is requested. 
# 	Interpret as fix[0]=right,fix[1]=top,fix[2]=width,fix[2]=height
# if tuplet fix contains four elements a box is requested. 
#	Interpret as fix[0]=right,fix[1]=top,fix[2]=width,fix[3]=height
# colour: numerical value from 0 to 15 to represent the colour of the target 
def drawFixation(fix, colour):
	# send the command to draw a cross or filled box on the tracker screen
	# all draw functions call on sendCommand, which waits for acknowledgement 
	# from the tracker side before returning. However, drawing may  
	# not have completed by the time sendCommand returns
	if len(fix) == 2:
		getEYELINK().drawCross(fix[0],fix[1],colour)
	elif len(fix) == 3:
		getEYELINK().drawBox(fix[0],fix[1],fix[2],fix[2], colour)
	elif len(fix) == 4:
		getEYELINK().drawFilledBox(fix[0], fix[1],fix[2], fix[3], colour)
		# or alternatively use equivalent sendCommand where you can:
		# use asterisk (*) to log the command in the edf file
		# use exclamation (!) to prioritize the command
		#getEYELINK().sendCommand("*draw_filled_box %d %d %d %d %d" % \
		#	(int(fix[0] - fix[2]), int(fix[1] - fix[3]), \
		#	int(fix[0] + fix[2]), int(fix[1] + fix[3]), int(colour)))
	# if coordinates tuplet has other number of elements, give a warning message and keep going
	else:
		print("drawFixation expects a three-element tuplet for its first argument\n")

# updateSaccade. draw a line representing a saccade on the tracker display
# Parameters:
# sacc: a four-element tuplet to be interpreted as:
#	sacc[0]=x1,sacc[1]=y1,sacc[2]=x2,sacc[3]=y2
# colour: numerical value from 0 to 15 to represent the colour of the target 
def drawSaccade(sacc, colour):
	if len(sacc) == 4:
		# send the command to draw a line on the tracker screen
		# use asterisk (*) to log the command in the edf file
		# use exclamation (!) to prioritize the command
		# sendCommand will wait for acknowledgement from the tracker side
		# but the draw command may not have completed by the time sendCommand returns
		getEYELINK().sendCommand("*draw_line %d %d %d %d %d" % \
			(int(sacc[0]), int(sacc[1]),int(sacc[2]), int(sacc[3]), int(colour)))
	else:
		print("drawSaccade expects a four-element tuplet for its first argument\n")

# updateTarget is a stub. You can use it to implement your own display-side graphics. 
# Note that you will need to import your own 3rd party module like pygame for that purpose.
# Parameters:
# ntarget: a variable-size tuplet to represent the coordinates and size of the target to be drawn 
# colour: numerical value from 0 to 15 to represent the colour of the target 
def updateTarget(ntarget, colour):
	# since we're operating in double buffer mode, there is no need to erase 
	# the last target since it was drawn on a different buffer.   
	if len(ntarget) < 2:
		pass
		#ADAPT CODE HERE
		#updateRect = draw.circle(surface, colour, 
		#	(surface.get_rect().w // 2 + ntarget[0], surface.get_rect().h // 2), TARGETSIZESAMPLE)
		#getEYELINK().drawCross(int(ntarget[0]), int(ntarget[0]), int(colour))
		#getEYELINK().sendCommand("*draw_cross %d %d %d" % (ntarget[0], ntarget[0], colour))
	elif len(ntarget) == 2:
		pass
		#ADAPT CODE HERE
		#updateRect = draw.circle(surface, colour, (int(ntarget[0]), int(ntarget[1])), TARGETSIZESAMPLE)
		#getEYELINK().drawCross(int(ntarget[0]), int(ntarget[1]),int(colour))
		#getEYELINK().sendCommand("*draw_cross %d %d %d" % (ntarget[0], ntarget[1],colour))
	elif len(ntarget) == 3:
		pass
		#ADAPT CODE HERE
		#updateRect = draw.circle(surface, colour, (int(ntarget[0]), int(ntarget[1])), int(ntarget[2]))
		#getEYELINK().drawFilledBox(int(ntarget[0]), int(ntarget[1]), int(ntarget[2]), int(ntarget[2]), int(colour))
		#getEYELINK().sendCommand("*draw_filled_box %d %d %d %d %d" % \
		#	(int(ntarget[0] - ntarget[2]), int(ntarget[1] - ntarget[2]), \
		#	int(ntarget[0] + ntarget[2]), int(ntarget[1] + ntarget[2]), int(colour)))
	elif len(ntarget) == 4:
		pass
		#ADAPT CODE HERE
		#getEYELINK().sendCommand("*draw_line %d %d %d %d %d" % \
		#	(int(ntarget[0]), int(ntarget[1]), int(ntarget[2]), int(ntarget[3]), int(colour)))
	# to accurately measure the time the target was drawn, read the current time right before refreshing display graphics
	preDrawingTime = currentTime()
	# Since this function is intended to be called on often, 
	# we avoid flipping the whole display to avoid flickering
	# Instead, we just update the new rect. This has the added 
	# advantage of preserving a saccade and gaze trace as opposed to simply
	# showing the current gaze position
	#display.update(updateRect) 
	#display.flip() 
	return preDrawingTime
	
def do_trial(trial):
	#initialize link events count
	fixUpdateCnt = 0
	saccStartCnt = 0
	saccEndCnt = 0
	fixStartCnt = 0
	fixEndCnt = 0
	#initialize sample data, saccade data and button input variables
	nSData = None
	sData = None
	sacc=(0,0,0,0)
	button = 0
	#This supplies the title of the current trial at the bottom of the eyetracker display
	message = "record_status_message 'CROSS-PLATFORM TEST, %s, Trial %d/%d '" % (trial_condition[trial], trial + 1, NTRIALS)
	getEYELINK().sendCommand(message)	
	#Always send a TRIALID message before starting to record.
	#EyeLink Data Viewer defines the start of a trial by the TRIALID message.  
	#This message is different than the start of recording message START that is logged when the trial recording begins. 
	#The Data viewer will not parse any messages, events, or samples, that exist in the data file prior to this message.
	msg = "TRIALID %d" % trial
	getEYELINK().sendMessage(msg)
	msg = "!V TRIAL_VAR_DATA %d" % trial
	getEYELINK().sendMessage(msg)
	#The following loop does drift correction at the start of each trial
	while True:
		# Checks whether we are still connected to the tracker
		if not getEYELINK().isConnected():
			return ABORT_EXPT			
		# Does drift correction and handles the re-do camera setup situations
		try:
			error = getEYELINK().doDriftCorrect(SCREENWIDTH // 2, SCREENHEIGHT // 2, 1, 1)
			if error != 27: 
				break
			else:
				getEYELINK().doTrackerSetup()
		except:
			getEYELINK().doTrackerSetup()
			
	#switch tracker to ide and give it time to complete mode switch
	getEYELINK().setOfflineMode()
	msecDelay(50) 
	#start recording samples and events to edf file and over the link. 
	error = getEYELINK().startRecording(1, 1, 1, 1)
	if error:	return error
	#disable python garbage collection to avoid delays
	gc.disable()
	#begin the realtime mode
	pylink.beginRealTimeMode(100)
	#clear tracker display to black
	getEYELINK().sendCommand("clear_screen 0")
	#determine trial start time	
	startTime = currentTime()
	#INSERT CODE TO DRAW INITIAL DISPLAY HERE
	#determine trial time at which initial display came on
	drawTime = (currentTime() - startTime)
	getEYELINK().sendMessage("%d DISPLAY ON" %drawTime)
	getEYELINK().sendMessage("SYNCTIME %d" %drawTime)
	try: 
		getEYELINK().waitForBlockStart(100,1,0) 
	except RuntimeError: 
		if getLastError()[0] == 0: # wait time expired without link data 
			end_trial()
			print ("ERROR: No link samples received!") 
			return TRIAL_ERROR 
		else: # for any other status simply re-raise the exception 
			raise
	#determine which eye is-are available
	eye_used = getEYELINK().eyeAvailable() #determine which eye(s) are available 
	if eye_used == RIGHT_EYE:
		getEYELINK().sendMessage("EYE_USED 1 RIGHT")
	elif eye_used == LEFT_EYE or eye_used == BINOCULAR:
		getEYELINK().sendMessage("EYE_USED 0 LEFT")
		eye_used = LEFT_EYE
	else:
		print ("Error in getting the eye information!")
		return TRIAL_ERROR
	#reset keys and buttons on tracker
	getEYELINK().flushKeybuttons(0)
	# pole for link events and samples
	while True:
		#check recording status
		error = getEYELINK().isRecording()  # First check if recording is aborted 
		if error != 0:
			end_trial()
			return error
		#check if trial duration exceeded
		if currentTime() > startTime + TRIALDUR:
			getEYELINK().sendMessage("TIMEOUT")
			end_trial()
			button = 0
			break
		#check if break pressed
		if(getEYELINK().breakPressed()):	# Checks for program termination or ALT-F4 or CTRL-C keys
			end_trial()
			return ABORT_EXPT
		#check if escape pressed
		elif(getEYELINK().escapePressed()): # Checks for local ESC key to abort trial (useful in debugging)
			end_trial()
			return SKIP_TRIAL
		# see if there are any new samples
		#get next link data	
		nSData = getEYELINK().getNewestSample() # check for new sample update
		# Do we have a sample in the sample buffer? 
		# and does it differ from the one we've seen before?
		if(nSData != None and (sData == None or nSData.getTime() != sData.getTime())):
			# it is a new sample, let's mark it for future comparisons.
			sData = nSData 
			# Detect if the new sample has data for the eye currently being tracked, 
			if eye_used == RIGHT_EYE and sData.isRightSample():
				sample = sData.getRightEye().getGaze()
				#INSERT OWN CODE (EX: GAZE-CONTINGENT GRAPHICS NEED TO BE UPDATED)
			elif eye_used != RIGHT_EYE and sData.isLeftSample():
				sample = sData.getLeftEye().getGaze()
				#INSERT OWN CODE (EX: GAZE-CONTINGENT GRAPHICS NEED TO BE UPDATED)
		# Now we consume and process the events and samples that are in the link data queue 
		# until there are no more left.
		while True:
			ltype = getEYELINK().getNextData()
			# If there are no more link data items, 
			# we have nothing more to consume and we can do other things until we get it.
			if not ltype: break 
			# There is link data to be processed, 
			# Let's see if it's something we need to look at before we decide what to do with it.
			if ltype == FIXUPDATE:
				# record to EDF the arrival of a fixation update event over the data link.
				getEYELINK().sendMessage("fixUpdate")
				# we fetch fixation update event then update the target position 
				# according to the retrieved gaze coordinates but only if the data 
				# corresponds to the eye being tracked   
				ldata = getEYELINK().getFloatData()
				if ldata.getEye() == eye_used:
					gaze = ldata.getAverageGaze()
					#drawFixation((gaze[0],gaze[1],TARGETSIZEFIXUPDATE), COLOURWHITE)
					drawFixation((gaze[0],gaze[1]), COLOURWHITE)
					fixUpdateCnt = fixUpdateCnt + 1
			elif ltype == STARTFIX:
				# record to EDF the arrival of a fixation start event over the data link.
				getEYELINK().sendMessage("fixStart")
				# we fetch fixation start event then increment count of similar events 
				# but only if the data	corresponds to the eye being tracked
				ldata = getEYELINK().getFloatData()
				if ldata.getEye() == eye_used:
					fixStartCnt = fixStartCnt + 1
			elif ltype == ENDFIX:
				# record to EDF the arrival of a fixation end event over the data link.
				getEYELINK().sendMessage("fixEnd")
				# we fetch fixation end event then update the target position 
				# according to the retrieved gaze coordinates but only if the data 
				# corresponds to the eye being tracked 
				ldata = getEYELINK().getFloatData()
				if ldata.getEye() == eye_used:
					gaze = ldata.getAverageGaze()
					#updateTarget((gaze[0],gaze[1],TARGETSIZEFIX), COLOURWHITE)
					fixEndCnt = fixEndCnt + 1
					printFixation((str(fixEndCnt),gaze[0],gaze[1]))
			elif ltype == STARTSACC:
				# record to EDF the arrival of a saccade start event over the data link.
				getEYELINK().sendMessage("saccStart")
				# we fetch saccade start event then update the target position 
				# accordingly but only if the data corresponds to the eye being tracked
				ldata = getEYELINK().getFloatData()
				if ldata.getEye() == eye_used:
					if sample:
						# update target position to match the coordinates of the 
						# last sample we've encountered if available. 
						# Use large hollow circle to mark the start of saccade. 
						# Like fixation start events, Saccade start events do not store
						# gaze coordinates unless link_event_data is used without NOSTART
						sacc=(sample[0],sample[1],0,0)
						#updateTarget((sample[0],sample[1],TARGETSIZESACC, 1), COLOURWHITE)
						saccStartCnt = saccStartCnt + 1
			elif ltype == ENDSACC:
				# record to EDF the arrival of a saccade end event over the data link.
				getEYELINK().sendMessage("saccEnd")
				# we fetch saccade end event then update the target position 
				# according to the retrieved gaze coordinates but only if the data 
				# corresponds to the eye being tracked
				ldata = getEYELINK().getFloatData()
				if ldata.getEye() == eye_used:
					gaze = ldata.getEndGaze()
					sacc = (sacc[0], sacc[1],gaze[0], gaze[1])
					# Use large filled circle to mark the end of saccade. 
					drawSaccade(sacc, COLOURWHITE)
					saccEndCnt = saccEndCnt + 1
	#after loop send message with link data event stats 
	getEYELINK().sendMessage("fixUpdate Count: %d" %fixUpdateCnt)
	getEYELINK().sendMessage("fixStart Count: %d" %fixStartCnt)
	getEYELINK().sendMessage("fixEnd Count: %d" %fixEndCnt)
	getEYELINK().sendMessage("saccStart Count: %d" %saccStartCnt)
	getEYELINK().sendMessage("saccEnd Count: %d" %saccEndCnt)
	getEYELINK().sendMessage("TRIAL_RESULT %d" % button)
	#return exit record status
	ret_value = getEYELINK().getRecordingStatus()
	#end realtime mode
	pylink.endRealTimeMode()
	#re-enable python garbage collection to do memory cleanup at the end of trial
	gc.enable()
	return ret_value
	
def run_trials():
	''' This function is used to run individual trials and handles the trial return values. '''
	''' Returns a successful trial with 0, aborting experiment with ABORT_EXPT (3); It also handles
	the case of re-running a trial. '''
	#Do the tracker setup at the beginning of the experiment.
	getEYELINK().doTrackerSetup()
	for trial in range(NTRIALS):
		if(not getEYELINK().isConnected() or getEYELINK().breakPressed()): break
		while True:
			ret_value = do_trial(trial)
			endRealTimeMode()
			if (ret_value == TRIAL_OK):
				getEYELINK().sendMessage("TRIAL OK")
				break
			elif (ret_value == SKIP_TRIAL):
				getEYELINK().sendMessage("TRIAL ABORTED")
				break			
			elif (ret_value == ABORT_EXPT):
				getEYELINK().sendMessage("EXPERIMENT ABORTED")
				return ABORT_EXPT
			elif (ret_value == REPEAT_TRIAL):
				getEYELINK().sendMessage("TRIAL REPEATED")
			else: 
				getEYELINK().sendMessage("TRIAL ERROR")
				break
	return 0
		
# change current directory to the one where this code is located 
# this way resource stimuli like images and sounds can be located using relative paths
spath = os.path.dirname(sys.argv[0])
if len(spath) !=0: os.chdir(spath)

#initialize tracker object with default IP address.
#created objected can now be accessed through getEYELINK()
eyelinktracker = EyeLink()
#Here is the starting point of the experiment
#Initializes the graphics
#INSERT THIRD PARTY GRAPHICS INITIALIZATION HERE IF APPLICABLE 
pylink.openGraphics((SCREENWIDTH, SCREENHEIGHT),32)

#Opens the EDF file.
edfFileName = "TEST.EDF"
getEYELINK().openDataFile(edfFileName)		
	
#flush all key presses and set tracker mode to offline.
pylink.flushGetkeyQueue() 
getEYELINK().setOfflineMode()						  

#Sets the display coordinate system and sends mesage to that effect to EDF file;
getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d" %(SCREENWIDTH - 1, SCREENHEIGHT - 1))
getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d" %(SCREENWIDTH - 1, SCREENHEIGHT - 1))

tracker_software_ver = 0
eyelink_ver = getEYELINK().getTrackerVersion()
if eyelink_ver == 3:
	tvstr = getEYELINK().getTrackerVersionString()
	vindex = tvstr.find("EYELINK CL")
	tracker_software_ver = int(float(tvstr[(vindex + len("EYELINK CL")):].strip()))
	
if eyelink_ver>=2:
	getEYELINK().sendCommand("select_parser_configuration 0")
	if eyelink_ver == 2: #turn off scenelink camera stuff
		getEYELINK().sendCommand("scene_camera_gazemap = NO")
else:
	getEYELINK().sendCommand("saccade_velocity_threshold = 35")
	getEYELINK().sendCommand("saccade_acceleration_threshold = 9500")
	
# set EDF file contents 
getEYELINK().sendCommand("file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT")
if tracker_software_ver>=4:
	getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,HTARGET,INPUT")
else:
	getEYELINK().sendCommand("file_sample_data  = LEFT,RIGHT,GAZE,AREA,GAZERES,STATUS,INPUT")

# set link data (used for gaze cursor) 
getEYELINK().sendCommand("link_event_filter = LEFT,RIGHT,FIXATION,FIXUPDATE,SACCADE,BLINK,BUTTON,INPUT")
if tracker_software_ver>=4:
	getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,HTARGET,INPUT")
else:
	getEYELINK().sendCommand("link_sample_data  = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT")

pylink.setCalibrationColors( (0, 0, 0),(255, 255, 255))  	#Sets the calibration target and background color
pylink.setTargetSize(SCREENWIDTH//70, SCREENWIDTH//300)     #select best size for calibration target
pylink.setCalibrationSounds("", "", "")
pylink.setDriftCorrectSounds("", "off", "off")

# make sure display-tracker connection is established and no program termination or ALT-F4 or CTRL-C pressed
if(getEYELINK().isConnected() and not getEYELINK().breakPressed()):
	#start the actual experiment
	run_trials()

if getEYELINK() != None:
	# File transfer and cleanup!
	getEYELINK().setOfflineMode()						  
	msecDelay(500)				 

	#Close the file and transfer it to Display PC
	getEYELINK().closeDataFile()
	getEYELINK().receiveDataFile(edfFileName, edfFileName)
	getEYELINK().close()

#Close the experiment graphics	
pylink.closeGraphics()
