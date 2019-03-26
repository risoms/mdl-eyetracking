notes
- draw roi using code (mdl-roi)
- show fixation cross for drift correction
- have path of stimulus presented on Host pc (ie IMGLOAD)
- set up gaze contigent, drift correct, and eyetracking.roi (i.e. IAREA RECTANGLE)

steps
- between blocks, do drift correct 
- when start recording started
	- do gaze contigent (if gc=True)
		- if fail gaze contigent (2 seconds, no fixation)
			- start drift correct



# OPTIONAL-- set an Interest Area for data viewer integraiton
# a full list of Data Viewer integration messages and their syntax can be found in the Data Viewer Manual 
# (Help menu -> Contents -> Protocol for EyeLink Data To Viewer Integraiton).
tk.sendMessage("!V IAREA RECTANGLE 1 %d %d %d %d target" % (scnWidth/2-w/2, scnHeight/2-h/2, scnWidth/2+w/2, scnHeight/2+h/2))


# OPTIONAL-- draw the text on the Host screen and show the bounding box
tk.sendCommand('clear_screen 0') # clear the host Display first
tk.sendCommand('draw_box %d %d %d %d 6' % (scnWidth/2-w/2, scnHeight/2-h/2, scnWidth/2+w/2, scnHeight/2+h/2))
	

# This message specifies the image to be used as the background for the Spatial Overlay
View of a trial within the viewer.
# [see Data Viewer User Manual, Section 7: Protocol for EyeLink Data to Viewer Integration]
# !V IMGLOAD CENTER fixations.gif 200 200
path_ = '..' + os.sep + pic
tk.sendMessage('!V IMGLOAD FILL %s %d %d' % (path_, width, height))

!V IMGLOAD CENTER fixations.gif 200 200