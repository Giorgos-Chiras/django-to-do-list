from celery import shared_task

from todolist.views import send_email


@shared_task
def schedule_email(message, subject, to_email=None):
    print(f"Received task arguments: {message}, {subject},  {to_email}")

    # Send email immediately (Celery will handle timing via countdown)
    send_email(message, subject, to_email)