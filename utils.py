import csv
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from utils import *
import imutils
import cv2
import numpy as np
from scipy.spatial import distance as dist
import pyttsx3
import os
from tkinter import *
from tkinter.filedialog import askopenfilename

def csv_edit(violations='No violations'):
    FILE_PATH = 'report.csv'
    up_dt = []
    try:
        f = open(FILE_PATH, "r")
        dt = csv.DictReader(f)
        up_dt = []
        for r in dt:
            row = {
                'No.': r['No.'],
                'Violations': r['Violations'],
                'Time': r['Time'],
            }
            up_dt.append(row)
        f.close()
    except:pass
    op = open(FILE_PATH, "w", newline='')
    headers = ['No.', 'Violations', 'Time']
    data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
    data.writerow(dict((heads, heads) for heads in headers))
    new = {}
    new['Violations']=str(violations)
    current_time = time.localtime()
    time.strftime('%Y-%m-%d %A', current_time)
    time.strftime('%Y Week %U Day %w', current_time)
    time.strftime('%a, %d %b %Y %H:%M:%S GMT', current_time)
    new['Time']=time.strftime('%a, %d %b %Y %H:%M:%S GMT', current_time)
    try:
        new['No.']=str(int(up_dt[-1]['Sno'])+1) 
    except:
        new['No.']=1
        
    up_dt.append(new)
    data.writerows(up_dt)
    
    op.close()


def send_email(fromaddr, pword, toaddr, file_path,subject=None, body=None):
    '''
    file_path : File name with extension
    fromaddr  : EMAIL address of the sender
    toaddr    : EMAIL address of the receiver
    body      : Body of the mail
    subject   : Subject of the mail
    '''

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = 'Social Distance Monitoring Project'
    # msg['From'] = fromaddr

    # storing the receivers email address
    # msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = 'Social Distance Violations Report' if subject == None else subject

    # string to store the body of the mail
    body = '''
Greetings from SDV-System,
    This email is automatically generated by SDVM-System (Social Distance Violations Monitoring System). The csv file attached to this email is a report generated by the analysis through AI algorithms''' if body==None else body 

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    attachment = open(file_path, "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % attachment.name)
    # with open(PATH_TO_CSV_FILE,'rb') as file:
    # # Attach the file with filename to the email
    #     msg.attach(MIMEApplication(file.read(), Name=FILE_NAME))

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, pword)

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    for emails in toaddr:
        if len(emails)>4:s.sendmail(fromaddr, emails, text)
    # s.sendmail(fromaddr, emails, text)
    # terminating the session
    s.quit()

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

    b = Button(ws,text='Save Email-IDs', width=45, height=2, command=save_email, bg='#0052cc',
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
