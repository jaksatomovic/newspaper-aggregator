import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

smtp_port = 587
smtp_server = "smtp.gmail.com"
sender_mail = "jaksa.tomovic@gmail.com"
sender_pw = "nzgivgfudszoyayz"
recipients = ["jaksa.tomovic@icloud.com"]

def send_alert(title, message):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"{title}"
    message["From"] = sender_mail
    message["To"] = ", ".join(recipients)
    body = f"{message}"
    message.attach(MIMEText(body, "html"))
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(sender_mail, sender_pw)
        server.sendmail(sender_mail, recipients, message.as_string())