import os
import smtplib


def send_email(message, subject, to_email=None):
    from_email = "chiras.to.do.list@gmail.com"
    email_password = os.getenv('EMAIL_HOST_PASSWORD')

    # Create the SMTP connection
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Encrypt connection
        server.login(from_email, email_password)

        if to_email is None:
            server.sendmail(from_email, from_email, message.as_string())
        else:
            server.sendmail(from_email, to_email, message.as_string())
