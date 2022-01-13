import csv
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def csv_edit(violations='No violations'):
    FILE_PATH = 'sample.csv'
    up_dt = []
    try:
        f = open(FILE_PATH, "r")
        dt = csv.DictReader(f)
        up_dt = []
        for r in dt:
            row = {
                'Sno': r['Sno'],
                'violations': r['violations'],
                'time': r['time'],
            }
            up_dt.append(row)
        f.close()
    except:pass
    op = open(FILE_PATH, "w", newline='')
    headers = ['Sno', 'violations', 'time']
    data = csv.DictWriter(op, delimiter=',', fieldnames=headers)
    data.writerow(dict((heads, heads) for heads in headers))
    new = {}
    # for i in up_dt:
    #     print(i, '\n')
        # if not i['Sno'] == int(up_dt[-1]['Sno']) or len(up_dt)==1:
    new['violations']=str(violations)
    current_time = time.localtime()
    time.strftime('%Y-%m-%d %A', current_time)
    time.strftime('%Y Week %U Day %w', current_time)
    time.strftime('%a, %d %b %Y %H:%M:%S GMT', current_time)
    new['time']=time.strftime('%a, %d %b %Y %H:%M:%S GMT', current_time)
    try:
        new['Sno']=str(int(up_dt[-1]['Sno'])+1) 
    except:
        new['Sno']=1
        
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
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = 'Social distance monitoring report' if subject == None else subject

    # string to store the body of the mail
    body = "" if body==None else body 

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
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()