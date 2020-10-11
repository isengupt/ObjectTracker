import cv2
import numpy as np
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import time
import math
import optparse

def select_point(event, x, y, flags, params):
    global point, point_selected, old_points

    if event == cv2.EVENT_LBUTTONDOWN:

        point = (x,y)
        point_selected = True
        old_points = np.array([[x,y]], dtype=np.float32)


def measure_velocity(p1, p2, time):

    x1, y1 = p1
    x2, y2 = p2
    
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1)**2)
    print(distance/time)

    return distance / time

class CutMotion:

    def __init__(self, url):

        self.url = url
        self.count = 0
        self.clipped = False
        self.cut_frames = []

    def addFrames(self, p1, p2, time):
        if (measure_velocity(p1, p2, time) > 0):
            if (self.clipped == False):
                self.cut_frames.append([])
                self.cut_frames[len(self.cut_frames) -1].append(cap.get(cv2.CAP_PROP_POS_MSEC))
                self.clipped = True
            else:
                self.cut_frames[len(self.cut_frames) -1].append(cap.get(cv2.CAP_PROP_POS_MSEC))
        else:  
            if(self.clipped == True):
                print('Flipped')
                self.clipped = False

    def saveVideos(self):

        for clip in self.cut_frames:
            print((clip[0], clip[len(clip) - 1]))
            ffmpeg_extract_subclip(self.url, clip[0]/1000, clip[len(clip) -1]/1000, targetname="cut" + str(self.count) + ".mp4")
            self.count = self.count + 1
        self.count = 0






if __name__=="__main__":

    parser = optparse.OptionParser()

    parser.add_option("-f", "--file",  dest="filename", help="Read video from file", metavar="FILE")
    parser.add_option("-c", "--camera", dest="camera", help="Camera number", metavar="CAMERA")

    (options, _) = parser.parse_args()



    camno = int(options.camera) if options.camera else 0

    cap = cv2.VideoCapture(camno if not options.filename else options.filename)
   
    ret, frame2 = cap.read()
    old_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    cutmot = CutMotion(camno if not options.filename else options.filename)

    cv2.namedWindow("frame2")
    cv2.setMouseCallback("frame2", select_point)


    point_selected = False
    secs = cap.get(cv2.CAP_PROP_FPS) 
    lk_params = dict(winSize = (15,15),
maxLevel = 4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
    point = ()
    old_points = np.array([[]])
    

    while(1):
        ret, frame2 = cap.read()

        gray_frame = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

        if point_selected is True:
            cv2.circle(frame2, point, 5, (0.0, 255), 2)

            new_points, status,error = cv2.calcOpticalFlowPyrLK(old_gray, gray_frame, old_points, None, **lk_params )
            old_gray = gray_frame.copy()
            x2, y2 = old_points.ravel()
            frame_time = 1.0 / secs
            old_points = new_points
            x , y = new_points.ravel()
        
            cutmot.addFrames((x2,y2), (x,y), frame_time)
            cv2.circle(frame2, (x,y), 5, (0,255,0), -1)
        
        cv2.imshow('frame2',frame2)


        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break
        elif k == ord('s'):
            cv2.imwrite('opticalfb.png',frame2)
        
        prvs = next

    cap.release()
    cv2.destroyAllWindows()
    cutmot.saveVideos()
    
    

  

    
