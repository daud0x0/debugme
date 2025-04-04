from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    level = models.IntegerField(default=1)
    total_score = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    def __str__(self):
        return self.username
