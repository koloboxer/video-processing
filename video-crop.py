#!/usr/bin/python

# original source: https://www.life2coding.com/crop-image-using-mouse-click-movement-python/
# rewritten for our needs.

# The program allows to crop areas from input images or videos and save these either as an
# image or as a video. The actions depend on how many input arguments are provided.
# :: Single input argument:
#    argument #1: path to an input image.
#    The input image file is being opened and the user can draw a region of interest.
#    If the user is not satisfied with the result,
#    he can redraw the region as many times as needed. When the user is satisfied he should
#    press 'Esc' key, then the cropped region will be saved by adding a number to the original
#    image name.
# :: Two arguments:
#    argument #1: path to a video file
#    argument #2: time in the input video in the form "hh:mm:ss"
#    The program will open a screenshot from this video taken at the time "hh:mm:ss". Again, the
#    user should draw a region of interest.
# :: Three arguments
#    argument #1: path to a video file
#    argument #2: time in the input video in the form "hh:mm:ss"
#    argument #3: duration to cut in seconds

screenWidth = 1920
screenHeight = 1080

import cv2
import sys
import os
import subprocess

try:
    import colors
except:
    print("Local module 'colors.py' cannot be found. Exiting.")
    exit()

###########
#def insertStringIntoFileName(fName, sName):

###########################################################################
def checkCommandExists(command):
    result = subprocess.run(["which", command], capture_output=True, text=True)
    if result.returncode == True:
        print("'{}' command is not present. Please, install, the corresponding package.".format(command))
    return result.returncode
###########################################################################

###########################################################################
def getFrameFromVideo(pathToVideo, positionSeconds) :
    cap = cv2.VideoCapture(pathToVideo)

    # get total number of frames
    totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frameNumber = round(fps * float(positionSeconds))
    #print("frameNumber = {}".format(frameNumber))
    # check for valid frame number
    if frameNumber < 0 or frameNumber >= totalFrames:
        print("Frame position {} seconds is outside the video length. Exiting.".format(positionSeconds))
        sys.exit(1)
    # set frame position
    cap.set(cv2.CAP_PROP_POS_FRAMES, frameNumber)
    ret, image = cap.read()
    return image
###########################################################################

###########################################################################
def set_yend(xStart, yStart, xEnd, yEnd) :
    deltaY = round(abs(xEnd - xStart + 1) * 1.77777777777)
    if yEnd >= yStart:
        res = yStart + deltaY
    else:
        res = yStart - deltaY
    return res - 1
###########################################################################

###########################################################################
def mouse_crop(event, x, y, flags, param):
    # grab references to the global variables
    global x_start, y_start, x_end, y_end, cropping

    # if the left mouse button was DOWN, start RECORDING
    # (x, y) coordinates and indicate that cropping is being done
    if event == cv2.EVENT_LBUTTONDOWN:
        x_start, y_start, x_end, y_end = x, y, x, y
        #print("left button pressed")
        cropping = True

    # Mouse is moving
    elif event == cv2.EVENT_MOUSEMOVE:
        #print("mouse moving")
        if cropping == True:
            x_end, y_end = x, y
            #temporary remove fixed ratio
            #y_end = set_yend(x_start, y_start, x, y)

    # if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        #print("left button released")

        # record the ending (x, y) coordinates
        x_end, y_end = x, y
        #y_end = set_yend(x_start, y_start, x, y)
        cropping = False # cropping is finished

        # exchange start and end if we moved mouse up or left
        if x_start > x_end:
            x_start, x_end = x_end, x_start
        if y_start > y_end:
            y_start, y_end = y_end, y_start

        # when two points were found such that height and width is not zero
        if x_start != x_end and y_start != y_end:
            roi = scaled_image[y_start : y_end, x_start : x_end]
            #roi = originalImage[y_start : y_end, x_start : x_end]
            cv2.imshow("Cropped", roi)
###########################################################################

numArgs = len(sys.argv)

if numArgs < 2 or numArgs > 4:
    baseName = os.path.basename(sys.argv[0])
    print("{}Usage: {}{}{} /path/to/image".format(colors.warning, colors.green, baseName, colors.reset))
    print("       {}{}{} /path/to/video hour:minute:seconds [cut_time_in_seconds]".format(colors.green, baseName, colors.reset))
    exit(1)

file_name = sys.argv[1]
inputFileSplit = os.path.splitext(file_name)

ext = inputFileSplit[1][1:]
inputIsVideo = (ext == 'mp4' or ext == 'mpeg' or ext == 'avi' or ext == 'mkv')

if numArgs == 2:
    if inputIsVideo:
        print("{}Error:{} '{}' has been recognized as a video, so you must provide start time (h:m:s) and optionally the output file length (s)".format(colors.fail, colors.reset, file_name))
        exit(1)
    elif ext != 'jpg' and ext != 'png':
        print("{}Warning:{} if '{}' is a video file, you must provide start time (h:m:s) and optionally the output file length (s)".format(colors.warning, colors.reset, file_name))

cropping = False
x_start, y_start, x_end, y_end = 0, 0, 0, 0

if len(sys.argv) == 2:
    image = cv2.imread(file_name)
elif len(sys.argv) == 3 or len(sys.argv) == 4:
    hms = sys.argv[2].split(':')
    startTime = 3600. * float(hms[0]) + 60. * float(hms[1]) + float(hms[2])
    image = getFrameFromVideo(file_name, startTime)
    if len(sys.argv) == 4:
        videoLength = float(sys.argv[3])

originalHeight, originalWidth, channels = image.shape
print("originalHeight = {}, originalWidth = {}".format(originalHeight, originalWidth))
print("Input frame size = {} x {}, number of color channels = {}".format(originalHeight, originalWidth, channels))

if originalWidth > 0.7 * screenWidth or originalHeight > 0.7 * screenHeight:
    scaleWidth = 0.7 * screenWidth / originalWidth
    scaleHeight = 0.7 * screenHeight / originalHeight
    scale_down = min(scaleWidth, scaleHeight)
    print("scaling ON ({})".format(scale_down))
else:
    scale_down = 1.
    print("scaling OFF ({})".format(scale_down))

#scale_down = 0.2
scale_up = 1. / scale_down

#print("Display size = {} x {}".format(scale_down * width, scale_down * height))

scaled_image = cv2.resize(image, None, fx = scale_down, fy = scale_down, interpolation = cv2.INTER_LINEAR)

cv2.namedWindow("image")
cv2.setMouseCallback("image", mouse_crop)

while True:
    i = scaled_image.copy()

    cv2.rectangle(i, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2) # 2 is the width of cropping lines
    cv2.imshow("image", i)

    k = cv2.waitKey(30) # how long to wait for a keypress (milliseconds); also time period between
                        # redrawing source image and therefore affects the speed of response to mouse
                        # motions when cropping is being done (lesser is faster)

    if k == 27: # Esc key to stop

        x_start, x_end, y_start, y_end = int(scale_up * x_start), int(scale_up * x_end), int(scale_up * y_start), int(scale_up * y_end)

        sizeX = x_end - x_start + 1
        sizeY = y_end - y_start + 1
        
        if sizeX == 1 or sizeY == 1:
            cropped = False
            print("{}Warning:{} crop area has not been chosen, the whole screen will be used.".format(colors.warning, colors.reset))
        else:
            cropped = True

        if len(sys.argv) == 4: # crop video from video
            checkCommandExists("ffmpeg")
            print("x_start = {}, x_end = {}, y_start = {}, y_end = {}".format(x_start, x_end, y_start, y_end))
            outputFile = "{}_start_{}s_cut_{}s{}".format(inputFileSplit[0], startTime, videoLength, inputFileSplit[1])
            if cropped == True:
                # todo: the problem of different video orientations should be solved
                print("HERE")
                # opencv shows picture not the same way as ffmpeg and video viewers. in opencv the frame is rotated CCW.
                # this means that
                #command = "ffmpeg -y -i {} -ss {} -t {} -filter:v \"crop={}:{}:{}:{}\" -an {}".format(file_name, startTime, videoLength, sizeY, sizeX, originalHeight - y_end - 1, x_start, outputFile)
                #command = "ffmpeg -y -i {} -ss {} -t {} -filter:v \"crop={}:{}:{}:{}\" {}".format(file_name, startTime, videoLength, sizeY, sizeX, y_start, x_start, outputFile)
                command = "ffmpeg -y -i {} -ss {} -t {} -filter:v \"crop={}:{}:{}:{}\" {}".format(file_name, startTime, videoLength, sizeX, sizeY, x_start, y_start, outputFile)
            else:
                #command = "ffmpeg -y -i {} -ss {} -t {} -c:v libx264 -crf 0 -c:a copy {}".format(file_name, startTime, videoLength, outputFile)
                command = "ffmpeg -y -i {} -ss {} -t {} -c:v copy -c:a copy {}".format(file_name, startTime, videoLength, outputFile)
        else: # crop image (from video or from image)
            command = ""
            if len(sys.argv) == 3: # crop image from video
                startTimeText = "_{}sec".format(startTime)
            else:
                startTimeText = ""

            if cropped == True:
                cropped_image = image[y_start : y_end, x_start : x_end]
                outputFile = "{}{}_cut_{}x{}.png".format(inputFileSplit[0], startTimeText, sizeX, sizeY)
                cv2.imwrite(outputFile, cropped_image)
            else:
                if len(sys.argv) == 3: # if area was not chosen we create new image only from video
                                       # because otherwise it will create a copy of the original image
                                       # or overwrite the original image if it was png-image
                    outputFile = "{}{}.png".format(inputFileSplit[0], startTimeText)
                    cv2.imwrite(outputFile, image)
        break

print("output file = {}".format(outputFile))
print("command = {}".format(command))
subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)

# close all open windows
cv2.destroyAllWindows()

exit(0)
