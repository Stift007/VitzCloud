import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

def _get_server(provider,port=25):
    print(provider)
    try:
        server = smtplib.SMTP(f'smtp.{provider}',port)
        server.ehlo()
    except:
        ...
    return server

def login_user(server,username,password):
    server.login(username,password)
    return server

def post_mail(server,sender,to,subject,message,attachments=None):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(message,'plain'))

    text = msg.as_string()
    server.sendmail(sender,to, text)