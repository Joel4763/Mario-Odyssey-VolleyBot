import numpy as np
import cv2
import pygame
import serial
import time
import sys
import threading
def mean(numbers):
	return float(sum(numbers)) / max(len(numbers), 1)
frame = None
xp = 0
yp = 0
bI = 0
scale_percent = 67
isitover = False
def caploop():
	global frame
	global isitover
	cap = cv2.VideoCapture(0)
	#cap.set(3,1280)
	#cap.set(4,720)
	ret, frame = cap.read()
	#print (ret)
	try:
		while(True):
			# Capture frame-by-frame
			cap.get(2)
			cap.get(2)
			cap.get(2)
			cap.get(2)
			cap.get(2)
			ret, frame = cap.read()
			if isitover:
				isitover = True
				break
	finally:
		print("no more caps")
		cap.release()
		return

def doLoop():
	global ser
	global xp
	global yp
	global mrb
	global bI
	global frame
	global isitover
	global scale_percent
	
	going = False
	bXs = [0,0,0,0,0]
	cXs = [0,0,0,0,0]
	bYs = [0,0,0,0,0]
	cYs = [0,0,0,0,0]
	ssums = [0]*20
	sI = 0
	prim = None
	centering = False
	actuallycentering = False
	now = time.time()
	#ftime = time.time()
	
	while True:
		if (frame is not None):
			frame2=frame.copy()
			
			width = int(frame2.shape[1] * scale_percent / 100)
			height = int(frame2.shape[0] * scale_percent / 100)
			dim = (width, height)
			# resize image
			frame2 = cv2.resize(frame2, dim, interpolation = cv2.INTER_AREA)
			
			bI = (bI + 1) % 5
			
			pressed = []
			s = frame2[507:587, 1051:1235]
			s = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
			ret, s = cv2.threshold(s, 200, 255, cv2.THRESH_BINARY)
			sI = sI + 1
			ssum = np.mean(s)
			if (sI < 20):
				ssums[sI] = ssum
			else:
				ssums.append(ssum)
				ssums.pop(0)

			prim = s.copy()
			if time.time() - now > 1.3:
				centering = False
			
			blue,g,r = cv2.split(frame2)
			cv2.rectangle(frame2, (453, 117), (817, 609), (0,0,0), 5)
			
			cv2.rectangle(frame2, (453, 7), (897, 720), (0,255,0), 1)
			r = cv2.GaussianBlur(r[17:720, 453:897], (31, 31), 0)
			cv2.rectangle(r, (0,0), (5,55), 255, 20)
			cv2.rectangle(r, (260,0), (330,40), 255, -1)
			(minVal, maxVal, cLoc, maxLoc) = cv2.minMaxLoc(r)
			cX, cY = cLoc
			#cXs[bI], cYs[bI] = cLoc
			#cX = int(mean(cXs))
			#cY = int(mean(cYs))
			cY = cY - 110
			cv2.circle(frame2, (cX + 453, cY + 117), 30, (0, 255, 0), 4)
			
			g = cv2.GaussianBlur(g[117:609, 453:817], (31, 31), 0)
			(minVal, maxVal, bLoc, maxLoc) = cv2.minMaxLoc(g)
			if centering:# and (cX - bLoc[0])**2 + (cY - bLoc[1])**2 < 35*35:#time.time() - now > 0.5:
				bLoc = (40, (609-117)/2)
				actuallycentering = True	
			else:
				actuallycentering = False
			bXs[bI], bYs[bI] = bLoc
			bX = int(mean(bXs))
			bY = int(mean(bYs))
			if bX < 40:
				bX = 40
			cv2.circle(frame2, (bX + 453, bY + 117), 30, (0, 0, 255) if not actuallycentering else (255,0,0), 4)
			if (going):
				xp = max(min(bX - cX, 100), -100)
				yp = max(min(bY - cY, 100), -100)
				
				#put my hat back in the ring
				if cX < 100 and xp < 0:
					xp = 0
				if cX > (817-453-10) and xp > 0:
					xp = 0
				if cY < 100 and yp < 0:
					yp = 0
				if cY > (609-117-90) and yp > 0:
					yp = 0
					
				#but for real
				if cX > (817-453):
					xp = -127
				if cY < 0:
					yp = 127
				if cY > (609-117):
					yp = -127
			if (not isitover):
				if (pygame.key.get_focused()):
					press=pygame.key.get_pressed()
					for i in range(len(press)):
						if press[i]:
							pressed.append(pygame.key.name(i))
			else:
				return
			if "g" in pressed:
				going = not going
			if "q" in pressed:
				isitover = not isitover
			if "w"  in pressed:
				yp = -127
			elif not going:
				yp = 0
			if "s"  in pressed:
				yp = 127
			if "a"  in pressed:
				xp = -127
			elif not going:
				xp = 0			
			if "d"  in pressed:
				xp = 127

			#print(pressed, mrb, xp, yp, bX, bY, cX, cY)
			cv2.arrowedLine(frame2, (cX+ 453, cY+ 117), (cX + (xp // 2) + 453, cY + (yp//2) + 117), (0,0,255), 5)
			cv2.imshow("Window",frame2)
			#ftime = time.time()
	return
def serialLoop():
	global xp
	global yp
	global mrb
	global isitover
# 						macOS: /dev/cu.usbserial  Windows: COM1-COM10
	ser = serial.Serial("/dev/cu.usbserial", 115200, writeTimeout = 0)
	while not isitover:
			if isitover:
				print("done")
#			print(xp, yp, mrb)
			ser.write(bytearray([xp + 127, yp + 127]))
			ser.read()
	print("the end")
	ser.close()

cthread = threading.Thread(target=caploop)
cthread.daemon = False
cthread.start()

sthread = threading.Thread(target=serialLoop)
sthread.daemon = False
sthread.start()

cv2.namedWindow("Window", cv2.WINDOW_NORMAL)


pygame.init()
pygame.display.set_mode((640,64),0,0)

dthread = threading.Thread(target=doLoop)
dthread.daemon = False
dthread.start()

while not isitover:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			isitover = True
			cv2.destroyAllWindows()
			pygame.display.quit()
sys.exit(0)
