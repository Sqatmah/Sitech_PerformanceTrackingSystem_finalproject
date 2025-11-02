from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

from .models import Assignment, Submission, Grade, Comment
from dashboard.models import Notification

User = get_user_model()


@receiver(post_save, sender=Assignment)
def assignment_created_notification(sender, instance, created, **kwargs):
    """Send notification when a new assignment is created"""
    if created:
        # Create notifications for all students
        students = User.objects.filter(role='student')
        
        for student in students:
            # Create in-app notification
            Notification.objects.create(
                recipient=student,
                title=f'New Assignment: {instance.title}',
                message=f'A new assignment "{instance.title}" has been created. Due date: {instance.due_date.strftime("%B %d, %Y at %I:%M %p")}',
                notification_type='assignment_created'
            )
            
            # Send email notification
            try:
                subject = f'New Assignment: {instance.title}'
                html_message = render_to_string('emails/assignment_created.html', {
                    'student': student,
                    'assignment': instance,
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[student.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Failed to send email to {student.email}: {e}")


@receiver(post_save, sender=Submission)
def submission_created_notification(sender, instance, created, **kwargs):
    """Send notification when a submission is created"""
    if created:
        # Notify assignment creator (manager/admin)
        assignment_creator = instance.assignment.created_by
        
        # Create in-app notification
        Notification.objects.create(
            recipient=assignment_creator,
            title=f'New Submission: {instance.assignment.title}',
            message=f'{instance.student.get_full_name() or instance.student.username} has submitted "{instance.assignment.title}"',
            notification_type='assignment'
        )
        
        # Send email notification
        try:
            subject = f'New Submission: {instance.assignment.title}'
            html_message = render_to_string('emails/submission_created.html', {
                'manager': assignment_creator,
                'submission': instance,
                'assignment': instance.assignment,
                'student': instance.student,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[assignment_creator.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {assignment_creator.email}: {e}")


@receiver(post_save, sender=Grade)
def grade_created_notification(sender, instance, created, **kwargs):
    """Send notification when a grade is created or updated"""
    if created or kwargs.get('update_fields'):
        student = instance.submission.student
        
        # Create in-app notification
        Notification.objects.create(
            recipient=student,
            title=f'Grade Posted: {instance.submission.assignment.title}',
            message=f'Your submission for "{instance.submission.assignment.title}" has been graded. Score: {instance.score}/{instance.submission.assignment.max_score} ({instance.letter_grade})',
            notification_type='grade'
        )
        
        # Send email notification
        try:
            subject = f'Grade Posted: {instance.submission.assignment.title}'
            html_message = render_to_string('emails/grade_posted.html', {
                'student': student,
                'grade': instance,
                'submission': instance.submission,
                'assignment': instance.submission.assignment,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {student.email}: {e}")


@receiver(post_save, sender=Comment)
def comment_created_notification(sender, instance, created, **kwargs):
    """Send notification when a comment is created"""
    if created:
        # Determine who to notify based on who made the comment
        if instance.author.role == 'student':
            # Student commented, notify the assignment creator
            recipient = instance.submission.assignment.created_by
            title = f'New Comment: {instance.submission.assignment.title}'
            message = f'{instance.author.get_full_name() or instance.author.username} commented on their submission for "{instance.submission.assignment.title}"'
        else:
            # Manager/Admin commented, notify the student
            recipient = instance.submission.student
            title = f'New Feedback: {instance.submission.assignment.title}'
            message = f'{instance.author.get_full_name() or instance.author.username} left feedback on your submission for "{instance.submission.assignment.title}"'
        
        # Create in-app notification
        Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type='comment'
        )
        
        # Send email notification
        try:
            subject = title
            html_message = render_to_string('emails/comment_added.html', {
                'recipient': recipient,
                'comment': instance,
                'submission': instance.submission,
                'assignment': instance.submission.assignment,
                'author': instance.author,
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                html_message=html_message,
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {recipient.email}: {e}")