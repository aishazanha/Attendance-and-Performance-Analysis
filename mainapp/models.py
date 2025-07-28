from django.db import models
from django.contrib.auth.models import AbstractUser

class head(AbstractUser):
    user_type = models.CharField(max_length=10, default='0')
    activation = models.PositiveIntegerField(default=0)
    assigned_subjects = models.ManyToManyField('adminapp.Subject', blank=True, related_name='teachers')

    def __str__(self):
        return self.username
