import cv2
import numpy as np
import math
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

cap = cv2.VideoCapture("traffic.mp4")
ret, frame2 = cap.read()
old_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)


secs = cap.get(cv2.CAP_PROP_FPS) 

lk_params = dict(winSize = (15,15),
maxLevel = 4, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))




global clipped 

clipped = False
cut_frames = []

def measure_velocity(p1, p2, time):

    x1, y1 = p1
    x2, y2 = p2
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1)**2)

    #if (distance / time > 0 ):
    #    print(cap.get(cv2.CAP_PROP_POS_MSEC))
     #   cut_frames.append(cap.get(cv2.CAP_PROP_POS_MSEC))
    #print(distance/ time)
    return distance / time



def select_point(event, x, y, flags, params):
    global point, point_selected, old_points

    if event == cv2.EVENT_LBUTTONDOWN:

        point = (x,y)
        point_selected = True
        old_points = np.array([[x,y]], dtype=np.float32)

cv2.namedWindow("frame2")
cv2.setMouseCallback("frame2", select_point)


point_selected = False
point = ()
old_points = np.array([[]])

while(1):
    ret, frame2 = cap.read()

    gray_frame = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    


   # next = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)

    if point_selected is True:
  
        

        cv2.circle(frame2, point, 5, (0.0, 255), 2)

        new_points, status,error = cv2.calcOpticalFlowPyrLK(old_gray, gray_frame, old_points, None, **lk_params )
        old_gray = gray_frame.copy()
        #print(old_points)
        x2, y2 = old_points.ravel()
        frame_time = 1.0 / secs
        old_points = new_points

       

        x , y = new_points.ravel()

        if (measure_velocity((x2,y2), (x,y), frame_time) > 0):
       
            if (clipped == False):
                
                print('Added array')
                cut_frames.append([])
                cut_frames[len(cut_frames) -1].append(cap.get(cv2.CAP_PROP_POS_MSEC))
                clipped = True

            else:
                cut_frames[len(cut_frames) -1].append(cap.get(cv2.CAP_PROP_POS_MSEC))
        else:  
            if(clipped == True):
                print('Flipped')
                clipped = False
            
                

        #print(x, y)

    
        cv2.circle(frame2, (x,y), 5, (0,255,0), -1)
       

   # flow = cv2.calcOpticalFlowFarneback(prvs,next, None, 0.5, 3, 15, 3, 5, 1.2, 0)

   # mag, ang = cv2.cartToPolar(flow[...,0], flow[...,1])
   # hsv[...,0] = ang*180/np.pi/2
   # hsv[...,2] = cv2.normalize(mag,None,0,255,cv2.NORM_MINMAX)
   # rgb = cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)
    
    cv2.imshow('frame2',frame2)


    k = cv2.waitKey(1) & 0xFF
    if k == ord("q"):
        break
    elif k == ord('s'):
        cv2.imwrite('opticalfb.png',frame2)

    prvs = next

cap.release()
cv2.destroyAllWindows()
print(cut_frames)
count = 0
for clip in cut_frames:
    print((clip[0], clip[len(clip) - 1]))
    ffmpeg_extract_subclip( "traffic.mp4", clip[0]/1000, clip[len(clip) -1]/1000, targetname="cut" + str(count) + ".mp4")
    count = count + 1
#print(cut_frames[0]/1000, cut_frames[len(cut_frames) -1]/1000)
#ffmpeg_extract_subclip("traffic.mp4", cut_frames[0]/1000, cut_frames[len(cut_frames) -1]/1000, targetname="test.mp4")




