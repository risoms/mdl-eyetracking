
.. raw:: html

   <h5 style="padding-top: 0px;padding-bottom: 0px;">

Example setup for Eyelink 1000 Plus, using PsychoPy 3.0.

.. raw:: html

   </h5>

.. code:: ipython3

    # Created on Wed Feb 13 15:37:43 2019
    # @author: Semeon Risom
    # @email: semeon.risom@gmail.com.
    # Sample code to run SR Research Eyelink eyetracking system. Code is optimized for the Eyelink 1000 
    # Plus (5.0), but should be compatiable with earlier systems.

.. code:: ipython3

    # To Do:
    # Finish eyetracking.drift_correction()
    # Finish eyetracking.roi()

.. raw:: html

   <p>

The sequence of operations for implementing the trial is:

.. raw:: html

   </p>

.. raw:: html

   <ol>

.. raw:: html

   <li>

Perform a DRIFT CORRECTION, which also serves as the pre-trial fixation
target.

.. raw:: html

   </li>

.. raw:: html

   <li>

Start recording, allowing 100 milliseconds of data to accumulate before
the trial display starts.

.. raw:: html

   </li>

.. raw:: html

   <li>

Draw the subject display, recording the time that the display appeared
by placing a message in the EDF file.

.. raw:: html

   </li>

.. raw:: html

   <li>

Loop until one of these events occurs RECORDING halts, due to the
tracker ABORT menu or an error, the maximum trial duration expires
‘ESCAPE’ is pressed, the program is interrupted, or abutton on the
EyeLink button box is pressed.

.. raw:: html

   </li>

.. raw:: html

   <li>

Add special code to handle gaze-contingent display updates.

.. raw:: html

   </li>

.. raw:: html

   <li>

Blank the display, stop recording after an additional 100 milliseconds
of data has been collected.

.. raw:: html

   </li>

.. raw:: html

   <li>

Report the trial result, and return an appropriate error code.

.. raw:: html

   </li>

.. raw:: html

   </ol>

[see Pylink.chm]

.. code:: ipython3

    # import
    import os
    from psychopy import visual, monitors
    import mdl

.. code:: ipython3

    # Initialize the Eyelink.
    # Before initializing, ensure psychopy window instance has been created in the experiment file. 
    # This window will be used in the calibration function.
    #
    # ```psychopy.visual.window.Window``` instance (for demonstration purposes only)
    subject = 1
    screensize = [1920, 1080]
    monitor = monitors.Monitor('Monitor', width=53.0, distance=65.0)
    monitor.setSizePix(screensize)
    window = visual.Window(size=screensize, fullscr=False, allowGUI=True, units='pix', monitor=monitor, 
                           winType='pyglet', color=[110,110,110], colorSpace='rgb255')
    #start
    eyetracking = mdl.eyetracking(libraries=False, window=window, subject=subject)

.. code:: ipython3

    # Connect to Eyelink. This allow controlls the parameters to be used when running the eyetracker.
    param = eyetracking.connect(calibration_type=13)

.. code:: ipython3

    # Setting the dominant eye. This step is especially critical for transmitting gaze coordinates from Eyelink->Psychopy.
    dominant_eye = 'left'
    eye_used = eyetracking.set_eye_used(eye=dominant_eye)

.. code:: ipython3

    # Start calibration.
    # Before running the calibration, ensure psychopy window instance has been created in the experiment file. 
    # This window will be used in the calibration function.
    eyetracking.calibration()

.. code:: ipython3

    # Enter the key "o" on the ```psychopy.visual.window.Window``` instance. This will begin the task. 
    # The Calibration, Validation, 'task-start' events are controlled by the keyboard.
    # Calibration ("c"), Validation ("v"), task-start ("o") respectively.

.. code:: ipython3

    # (Optional) Print message to console/terminal. This may be useful for debugging issues.
    eyetracking.console(c="blue", msg="eyetracking.calibration() started")

.. code:: ipython3

    # (Optional) Drift correction. This can be done at any point after calibration, including before and after 
    # eyetracking.start_recording has started.
    eyetracking.drift_correction()

.. code:: ipython3

    # Start recording. This should be run at the start of the trial.
    #
    # Create stimulus (demonstration purposes only). Note: There is an intentional delay of 150 msec to 
    # allow the Eyelink to buffer gaze samples.
    filename = "8380.bmp" #filename
    path = os.getcwd() + "/data/stimulus/" + filename #filepath
    size = (1024, 768) #image size
    pos = (screensize[0]/2, screensize[1]/2) #positioning image at center of screen
    stimulus = visual.ImageStim(win=window, image=path, size=size, pos=(0,0), units='pix')
    
    #start
    eyetracking.start_recording(trial=1, block=1)

.. code:: ipython3

    # (Optional) Gaze contigent event. This is used for realtime data collection from eyelink->psychopy.
    # For example, this can be used to require participant to look at the fixation cross for a duration
    # of 500 msec before continuing the task.
    # 
    # Collect samples with the center of the screen, for 2000 msec, with a maxinum duration of 10000 msec
    # before drift correction will start.
    region = dict(left=860, top=440, right=1060, bottom=640)
    t_min = 3000
    t_max = 10000
    
    # start
    eyetracking.gc(region=region, t_min=t_min, t_max=t_max)

.. code:: ipython3

    # (Optional) Collect current gaze coordinates from Eyelink. This command should be 
    # looped at an interval of sample/2.01 msec to prevent oversampling (500Hz).
    #
    # get time
    import time
    s1 = 0 # set current time to 0
    lgxy = [] # create list of gaze coordinates (demonstration purposes only)
    s0 = time.clock() # initial timestamp
    # repeat
    while True:
        # if difference between starting and current time is greater than > 2.01 msec, collect new sample
        diff = (s1 - s0)
        if diff >= .00201:
            print(s1)
            gxy, ps, s = eyetracking.sample(eye_used=eye_used) # get gaze coordinates, pupil size, and sample
            lgxy.append(gxy) # store in list (not required; demonstration purposes only)
            s0 = time.clock() # update starting time
        #else set current time
        else: 
            s1 = time.clock()
    
        #break `while` statement if list of gaze coordiantes >= 20 (not required; demonstration purposes only)
        if len(lgxy) >= 200: break

.. code:: ipython3

    # (Optional) Send messages to Eyelink. This allows post-hoc processing of timing related events (i.e. "stimulus onset").
    # Sending message "stimulus onset".
    #
    msg = "stimulus onset"
    eyetracking.send_message(msg=msg)

.. code:: ipython3

    # Stop Eyelink recording. Also allows transmission of trial-level variables (optional) to Eyelink.
    # Note: Variables sent are optional. If they being included, they must be in ```python dict``` format.
    
    # set variables
    variables = dict(stimulus=filename, trial_type='encoding', race="black")
    # stop recording
    eyetracking.stop_recording(trial=1, block=1, variables=variables)

.. code:: ipython3

    # Finish Eyelink recording.
    eyetracking.finish_recording()
