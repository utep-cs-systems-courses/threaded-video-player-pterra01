#!/usr/bin/env python3

import threading, cv2, os, queue

class QueueThread:
    def __init__(self):
        self.queue = []
        self.full = threading.Semaphore(0)
        self.empty = threading.Semaphore(10)
        self.lock = threading.Lock()

    def enqueue(self, item):
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        self.full.release()

    def dequeue(self):
        self.full.acquire()
        self.lock.acquire()
        frame = self.queue.pop(0)
        self.lock.release()
        self.empty.release()
        return frame

def extractFrames(filename, readframes):
    count =  0 #frame count

    vidcap = cv2.VideoCapture(filename) #this will open the video file

    success, image = vidcap.read() #read first image
    
    print(f'Reading frame {count} {success}')
    while success:
        
        readframes.enqueue(image) #add frames to queue

        success, image = vidcap.read()
        print(f'Reading frame {count}')
        count += 1
        
    print('Finished extracting frames :)')
    readframes.enqueue('stop') # to know where to stop

def convertToGrayScale(readframes, grayframes):
    count = 0 #frame count

    while True: #going through the color frames
        print(f'Converting Frame {count}')

        getFrame = readframes.dequeue() #load the frames
        if getFrame == 'stop': 
            break
        
        #convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(getFrame, cv2.COLOR_BGR2GRAY)

        grayframes.enqueue(grayscaleFrame) #add gray frames to queue
        
        count += 1

    print('Finished converting to gray :)')
    grayframes.enqueue('stop') # to know where to  

def displayFrames(grayframes):
    count = 0 #frame count

    while True: #going through gray frames
        print(f'Displaying Frame {count}')

        frame = grayframes.dequeue() #load the frame
        if frame == 'stop': # to know where to stop
            break
        
        cv2.imshow('Video', frame) #display image called Video
        
        if(cv2.waitKey(42) and 0xFF == ord("q")): #wait for 42ms & check if user quits
           break

        count += 1

    print('Finished display :)')
    
    cv2.destroyAllWindows() # make sure we cleanup the windows

filename = '../clip.mp4' #load clip.mp4

#queues
readframes = QueueThread()
grayframes = QueueThread()
           
#make each thread target each def with their parameters as the args 
extractThread = threading.Thread(target = extractFrames, args = (filename, readframes))
convertThread = threading.Thread(target = convertToGrayScale, args = (readframes, grayframes))
displayThread = threading.Thread(target = displayFrames, args = (grayframes,))

#start threads
extractThread.start()
convertThread.start()
displayThread.start()
