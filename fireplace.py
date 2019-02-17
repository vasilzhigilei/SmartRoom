'''
Simple function that plays a fireplace video on loop on a monitor that stands in my dorm room fireplace.
'''

import cv2
import os

def assure_path_exists(path):
    '''
    Assures that the given path, path, exists, if not, create said path
    :param path: path towards a certain folder or file
    '''
    dir = os.path.dirname(path)
    if not os.path.exists(dir):
        os.makedirs(dir)

assure_path_exists(os.path.expanduser('~')+"/Documents/opensesame/resources")

def play_vid(vid_directory=os.path.expanduser('~')+"/Documents/opensesame/resources/fireplace.mp4"):
    '''
    Takes in video to play on loop, until user presses the Escape key
    :param vid_directory: directory for video to be played, defaults to fireplace.mp4
    '''
    cap = cv2.VideoCapture(vid_directory)
    if (cap.isOpened()== False):
        print("Error opening video stream or file")
    else:
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret == True:
                capname = "Fireplace Video"
                cv2.namedWindow(capname, cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty(capname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow(capname, frame)
                if(cv2.waitKeyEx(40) == 27):
                    break
            else:
                print("Looping video")
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

play_vid()