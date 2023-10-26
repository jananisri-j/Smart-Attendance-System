import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, date
import time
import pygsheets
import json
import zmq

context = zmq.Context()


 
path = 'ImageAttendance'
images = []
classNames = []
myList = os.listdir(path)

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)
 
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
 
'''
def markAttendance(name):
    with open('Attendance.csv','r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')
            return(True)
        else:
        	return(False)
'''


def markAttendance(name):
	Today = date.today()
	dateString = str(Today.day) + "-" + str(Today.month) + "-" + str(Today.year)
	#dateString = "28-06-2021"
	SPID='1FsoyHJX1_qu1CUVbKGozjM6PEYFmafZwhubPAP_vf3E'
	client = pygsheets.authorize(client_secret='client_secret.json')
	sheet_data = client.sheet.get(SPID)
	sheet = client.open_by_key(SPID)
	wks = sheet.worksheet_by_title('Attendance')
	headers = wks.get_row(10, include_tailing_empty=False)
	enumerated_headers = list(enumerate(headers))

	cells = wks.find(dateString, searchByRegex=False, matchCase=False,
    matchEntireCell=False, includeFormulas=False,
    cols=None, rows=None, forceFetch=True)

	if cells == []:
		print("Column not present")
		wks.insert_cols(len(enumerated_headers) + 1, number=1, values=None, inherit=True)
		wks.insert_cols(len(enumerated_headers) + 2, number=1, values=None, inherit=True)
		wks.update_value((10,len(enumerated_headers) + 1), dateString)
		wks.update_value((10,len(enumerated_headers) + 2), "Attendance")
		headers = wks.get_row(10, include_tailing_empty=False)
		enumerated_headers = list(enumerate(headers))

		cells = wks.find(name, searchByRegex=False, matchCase=False,
        matchEntireCell=False, includeFormulas=False,
        cols=None, rows=None, forceFetch=True)

		for cell in cells:
			now = datetime.now()  # current date and time
			curtime = now.strftime("%H:%M:%S")
			
			if int(now.strftime("%H")) < 9:
				ATTENDANCE="✔"
				print("PRESENT")
			else:
				#print("LATE")
				ATTENDANCE="Ⓛ"
			wks.update_value((cell.row,len(enumerated_headers) - 1), curtime)
			wks.update_value((cell.row,len(enumerated_headers)), ATTENDANCE)
	else:
		for cell in cells:
			DATE_COLUMN = cell.label[0]

		cells = wks.find(name, searchByRegex=False, matchCase=False,
        matchEntireCell=False, includeFormulas=False,
        cols=None, rows=None, forceFetch=True)

		for cell in cells:
			now = datetime.now()  # current date and time
			curtime = now.strftime("%H:%M:%S")
			
			if int(now.strftime("%H")) < 9:
				ATTENDANCE="✔"
				print("PRESENT")
			else:
				print("LATE")
				ATTENDANCE="Ⓛ"
			COLTOUPDATE = DATE_COLUMN + str(cell.row)
			wks.update_value(COLTOUPDATE, curtime)
			wks.update_value((cell.row,len(enumerated_headers)), ATTENDANCE)


"""

	if enumerated_headers[len(enumerated_headers) - 1][1] == dateString:
		pass
	else:
		wks.insert_cols(len(enumerated_headers) + 1, number=1, values=None, inherit=True)
		wks.insert_cols(len(enumerated_headers) + 2, number=1, values=None, inherit=True)
		wks.update_value((10,len(enumerated_headers) + 1), dateString)
		wks.update_value((10,len(enumerated_headers) + 2), "Attendance")
		headers = wks.get_row(10, include_tailing_empty=False)
		enumerated_headers = list(enumerate(headers))

	cells = wks.find(name, searchByRegex=False, matchCase=False,
    matchEntireCell=False, includeFormulas=False,
    cols=None, rows=None, forceFetch=True)

	for cell in cells:
		now = datetime.now()  # current date and time
		curtime = now.strftime("%H:%M:%S")
		wks.update_value((cell.row,len(enumerated_headers) - 1), curtime)
"""


        

#### FOR CAPTURING SCREEN RATHER THAN WEBCAM
# def captureScreen(bbox=(300,300,690+300,530+300)):
#     capScr = np.array(ImageGrab.grab(bbox))
#     capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
#     return capScr
 
encodeListKnown = findEncodings(images)
print('Recognition on Progess !!! Please wait !!')
 
cap = cv2.VideoCapture(0)


 
while True:
    success, img = cap.read()
    #img = captureScreen()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
 
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

 
    for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        #print(faceDis)
        matchIndex = np.argmin(faceDis)
 
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            print(name)
            #face location
            y1,x2,y2,x1 = faceLoc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            markAttendance(name)
        else:
            cv2.putText(img,"Unknown Person",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)

 
    cv2.imshow('Webcam',img)
    cv2.waitKey(1)