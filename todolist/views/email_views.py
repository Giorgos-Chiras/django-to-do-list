import os
import smtplib
from email.mime.text import MIMEText
from decouple import config


def send_email(message, subject="No Subject", to_email=None):
    from_email = config('EMAIL_HOST_USER')
    email_password = config('EMAIL_HOST_PASSWORD')

    #Make the message into a MIMEText
    if not isinstance(message, MIMEText):
        msg= MIMEText(message)
        msg["Subject"] = subject or "No Subject"

        message=msg.as_string()
    else:
        message = message.as_string()


    # Create the SMTP connection
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Encrypt connection
        server.login(from_email, email_password)

        if to_email is None:
            server.sendmail(from_email, from_email, message)
        else:
            server.sendmail(from_email, to_email, message)



