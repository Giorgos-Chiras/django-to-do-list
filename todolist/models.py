
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import os
from decouple import config


def user_upload_to(instance, filename):
    media_root = config('MEDIA_ROOT', default='/mnt/data/default_media_folder/media/')

    return os.path.join(media_root, 'task_pictures', str(instance.user.username), filename)

class AddItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    text=models.CharField(max_length=100)
    due_date=models.DateField(default=timezone.now,)
    completed=models.BooleanField(default=False)
    picture = models.ImageField(upload_to=user_upload_to, blank=True, null=True)


    def __str__(self):
        return f"{self.text} due: {self.due_date}"

