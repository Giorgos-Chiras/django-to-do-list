import os
import smtplib
from email.mime.text import MIMEText


def send_email(message, subject="No Subject", to_email=None):
    from_email = "chiras.to.do.list@gmail.com"
    email_password = os.getenv('EMAIL_HOST_PASSWORD')

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



