from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationManager(models.Manager):
    def unread(self):
        return self.filter(is_read=False)
    
    def read(self):
        return self.filter(is_read=True)


class Notification(models.Model):
    """Notification system for users"""
    
    TYPE_CHOICES = [
        ('assignment_created', 'Assignment Created'),
        ('assignment_due', 'Assignment Due Soon'),
        ('submission_graded', 'Submission Graded'),
        ('comment_added', 'Comment Added'),
        ('general', 'General'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = NotificationManager()
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    class Meta:
        ordering = ['-created_at']


class SystemSettings(models.Model):
    """System-wide settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.key
    
    class Meta:
        verbose_name_plural = "System Settings"
