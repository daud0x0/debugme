from django.db import models
from django.conf import settings
from topics.models import Subtopic

# Create your models here.

class TestSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='test_sessions')
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE, related_name='test_sessions')
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.subtopic.name} - {self.started_at}"

class Question(models.Model):
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ])
    user_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ], null=True, blank=True)
    explanation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_correct(self):
        return self.user_answer == self.correct_answer
    
    def __str__(self):
        return f"Question {self.id} - {self.test_session}"

class SubtopicPerformance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subtopic_performances')
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE, related_name='performances')
    score_avg = models.FloatField(default=0)
    test_count = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'subtopic']
        ordering = ['-last_attempt']
    
    def __str__(self):
        return f"{self.user.username} - {self.subtopic.name} - {self.score_avg}%"
