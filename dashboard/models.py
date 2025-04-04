from django.db import models
from django.conf import settings
from topics.models import Topic, Subtopic

# Create your models here.

class UserProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='user_progress')
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE, related_name='user_progress')
    score = models.FloatField(default=0)
    attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'subtopic']
        ordering = ['-last_attempt']
    
    def __str__(self):
        return f"{self.user.username} - {self.subtopic.name} - {self.score}%"
