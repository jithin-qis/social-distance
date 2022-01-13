from utils import *
import imutils
import cv2
import numpy as np
from scipy.spatial import distance as dist
import pyttsx3
import os
from tkinter import *
from tkinter.filedialog import askopenfilename
root = Tk()

text_box = ''
ws = ''


def email_config():
    global ws
    ws = Tk()
    ws.title('Email configuration')
    ws.geometry('400x300')
    ws.config(bg='#84BF04')

    fp = open('emails.txt')
    emails = fp.read()

    message = emails

    global text_box

    text_box = Text(
        ws,
        height=12,
        width=40
    )
    text_box.pack(expand=True)
    text_box.insert('end', message)

    b = Button(text='Save Email-IDs', width=45, height=2, command=save_email, bg='#0052cc',
               fg='#ffffff', activebackground='#0052cc', activeforeground='#aaffaa').pack(expand=True)

    ws.mainloop()


def save_email():
    d = text_box.get("1.0", END)
    fp = open('emails.txt', 'w')
    fp.write(d)
    fp.close()
    ws.destroy()


def converttext(message):
    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()


MIN_CONF = 0.3
NMS_THRESH = 0.3

labelsPath = os.path.join(os.getcwd(), 'coco.names')
LABELS = open(labelsPath).read().strip().split("\n")

weightsPath = os.path.join(os.getcwd(), 'yolov3_test.weights')
configPath = os.path.join(os.getcwd(), 'yolov3.cfg')
try:
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
except Exception as e:
    print('''
    Files missing
    ''')
    quit()

ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

path = askopenfilename()
print(path)
# vs = cv2.VideoCapture('pedestrians1.mp4')
vs = cv2.VideoCapture(path)
writer = None
root.destroy()
while True:
    (grabbed, frame) = vs.read()
    if not grabbed:
        break
    frame = imutils.resize(frame, width=1000)
    personIdx = LABELS.index("person")
    (H, W) = frame.shape[:2]
    results = []
    blob = cv2.dnn.blobFromImage(
        frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)
    boxes = []
    centroids = []
    confidences = []
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if classID == personIdx and confidence > MIN_CONF:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                centroids.append((centerX, centerY))
                confidences.append(float(confidence))
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONF, NMS_THRESH)
    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            r = (confidences[i], (x, y, x + w, y + h), centroids[i])
            results.append(r)

    violate = set()
    if len(results) >= 2:
        centroids = np.array([r[2] for r in results])
        D = dist.cdist(centroids, centroids, metric="euclidean")

        for i in range(0, D.shape[0]):
            for j in range(i + 1, D.shape[1]):
                if D[i, j] < 50:
                    violate.add(i)
                    violate.add(j)

    alert = list(violate)

    for (i, (prob, bbox, centroid)) in enumerate(results):
        (startX, startY, endX, endY) = bbox
        (cX, cY) = centroid
        color = (0, 255, 0)
        if i in violate:
            color = (0, 0, 255)
        cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
        cv2.circle(frame, (cX, cY), 5, color, 1)
    text = "Social Distancing Violations: {}".format(len(violate))
    csv_edit(violations=len(violate) if violate else 'No Violations')
    cv2.putText(frame, text, (10, frame.shape[0] - 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 3)
    print(text)

    d = 1
    if d > 0:
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            os.remove('report.csv')
            break
        if key == ord("e"):
            email_config()
        if key == ord("s"):
            print('Sending email.... please wait...')
            data = open('emails.txt').read().split('\n')
            send_email(fromaddr='socialdistancemonitor@gmail.com',
                       pword='quest@123',
                       toaddr=data,
                       file_path='report.csv')
            print('File sent')
            os.remove('report.csv')

    if alert != []:
        converttext('maintain social distance')
