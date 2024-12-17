from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class AddItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    text=models.CharField(max_length=100)
    due_date=models.DateField(default=timezone.now,)
    completed=models.BooleanField(default=False)
    picture=models.ImageField(default='default.jpg',blank=True)

    def __str__(self):
        return f"{self.text} due: {self.due_date}"

