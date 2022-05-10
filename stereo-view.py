import cv2
import depthai as dai
import numpy as np
import pyautogui
import win32gui
import os

numberPhoto = 1

def screenshot(window_title=None):
    if window_title:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
            x, y, x1, y1 = win32gui.GetClientRect(hwnd)
            x, y = win32gui.ClientToScreen(hwnd, (x, y))
            x1, y1 = win32gui.ClientToScreen(hwnd, (x1 - x, y1 - y))
            im = pyautogui.screenshot(region=(x, y, x1, y1))
            return im
        else:
            print('Window not found!')
    else:
        im = pyautogui.screenshot()
        return im

def getFrame(queue):
    # Get frame from queue
    frame = queue.get()
    # Convert frame to OpenCV format and return
    return frame.getCvFrame()

def getMonoCamera(pipeline, isLeft):
    # Configure mono camera
    mono = pipeline.createMonoCamera()

    # Set Camera Resolution
    mono.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    
    if isLeft:
        # Get left camera
        mono.setBoardSocket(dai.CameraBoardSocket.LEFT)
    else :
        # Get right camera
        mono.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    return mono

if __name__ == '__main__':

    # Define a pipeline
    pipeline = dai.Pipeline()

    # Set up left and right cameras
    monoLeft = getMonoCamera(pipeline, isLeft = True)
    monoRight = getMonoCamera(pipeline, isLeft = False)

    # Set output Xlink for left camera
    xoutLeft = pipeline.createXLinkOut()
    xoutLeft.setStreamName("left")

    # Set output Xlink for right camera
    xoutRight = pipeline.createXLinkOut()
    xoutRight.setStreamName("right")
 
    # Attach cameras to output Xlink
    monoLeft.out.link(xoutLeft.input)
    monoRight.out.link(xoutRight.input)
    
    # Pipeline is defined, now we can connect to the device
    with dai.Device(pipeline) as device:

        # Get output queues. 
        leftQueue = device.getOutputQueue(name="left", maxSize=1)
        rightQueue = device.getOutputQueue(name="right", maxSize=1)

        # Set display window name
        cv2.namedWindow("Stereo Pair")
        # Variable use to toggle between side by side view and one frame view. 
        sideBySide = True
        
        while True:
            # Get left frame
            leftFrame = getFrame(leftQueue)
            # Get right frame 
            rightFrame = getFrame(rightQueue)

            if sideBySide:
                # Show side by side view
                imOut = np.hstack((leftFrame, rightFrame))
            else : 
                # Show overlapping frames
                imOut = np.uint8(leftFrame/2 + rightFrame/2)

            # Display output image
            cv2.imshow("Stereo Pair", imOut)
            
            # Check for keyboard input
            key = cv2.waitKey(1)
            if key == ord('q'):
                # Quit when q is pressed
                break
            elif key == ord('t'):
                # Toggle display when t is pressed
                sideBySide = not sideBySide
            elif key == ord('s'):
                # Take screenshot
                im = screenshot('Stereo Pair')
                if im:
                    while os.path.exists(f"Photos\Full\PhotoFull{numberPhoto}.png"):
                        numberPhoto += 1
                    im.save(f"Photos\Full\PhotoFull{numberPhoto}.png")
                    imLeft = im.crop((0, 0, 640, 400)) #left,upper,right,lower
                    imLeft.save(f"Photos\Left\PhotoLeft{numberPhoto}.png")
                    imRight = im.crop((640, 0, 1280, 400)) #left,upper,right,lower
                    imRight.save(f"Photos\Right\PhotoRight{numberPhoto}.png")
                    print('Screenshot Taken!')
