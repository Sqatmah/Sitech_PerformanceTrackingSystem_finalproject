from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class Assignment(models.Model):
    """Assignment model for tasks given to students"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_assignments',
        limit_choices_to={'role__in': ['admin', 'manager']}
    )
    assigned_to = models.ManyToManyField(
        User,
        related_name='assignments',
        limit_choices_to={'role': 'student'},
        blank=True
    )
    due_date = models.DateTimeField()
    max_score = models.PositiveIntegerField(default=100)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    instructions = models.TextField(blank=True)
    attachment = models.FileField(upload_to='assignment_files/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        return timezone.now() > self.due_date
    
    @property
    def submission_count(self):
        return self.submissions.count()
    
    @property
    def graded_count(self):
        return self.submissions.filter(grade__isnull=False).count()
    
    class Meta:
        ordering = ['-created_at']


class Submission(models.Model):
    """Student submission for assignments"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('returned', 'Returned for Revision'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='submissions',
        limit_choices_to={'role': 'student'}
    )
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='submission_files/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_late(self):
        if self.submitted_at:
            return self.submitted_at > self.assignment.due_date
        return False
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-updated_at']


class Grade(models.Model):
    """Grade model for submissions"""
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='grade')
    score = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='graded_submissions',
        limit_choices_to={'role__in': ['admin', 'manager']}
    )
    graded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.submission} - {self.score}/{self.submission.assignment.max_score}"
    
    @property
    def percentage(self):
        return (self.score / self.submission.assignment.max_score) * 100
    
    @property
    def letter_grade(self):
        percentage = self.percentage
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'


class Comment(models.Model):
    """Comments on submissions for feedback"""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.submission}"
    
    class Meta:
        ordering = ['created_at']
