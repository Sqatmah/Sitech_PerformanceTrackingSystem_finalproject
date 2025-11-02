#!/usr/bin/env python
import os
import sys
import django
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_dashboard.settings')
django.setup()

from accounts.models import User, StudentProfile, ManagerProfile
from assignments.models import Assignment, Submission, Grade, Comment
from dashboard.models import Notification

def create_sample_data():
    print("Creating sample data...")
    
    # Create manager
    manager, created = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@example.com',
            'first_name': 'John',
            'last_name': 'Manager',
            'role': 'manager'
        }
    )
    if created:
        manager.set_password('manager123')
        manager.save()
        print(f"Created manager: {manager.username}")
    
    # Create manager profile
    manager_profile, created = ManagerProfile.objects.get_or_create(
        user=manager,
        defaults={
            'department': 'Computer Science',
            'hire_date': timezone.now().date()
        }
    )
    
    # Create students
    students = []
    for i in range(1, 6):
        student, created = User.objects.get_or_create(
            username=f'student{i}',
            defaults={
                'email': f'student{i}@example.com',
                'first_name': f'Student',
                'last_name': f'{i}',
                'role': 'student'
            }
        )
        if created:
            student.set_password('student123')
            student.save()
            print(f"Created student: {student.username}")
        
        # Create student profile
        student_profile, created = StudentProfile.objects.get_or_create(
            user=student,
            defaults={
                'student_id': f'STU{2024000 + i}',
                'manager': manager,
                'enrollment_date': timezone.now().date() - timedelta(days=30*i),
                'is_active': True
            }
        )
        students.append(student)
    
    # Create assignments
    assignments = []
    assignment_data = [
        {
            'title': 'Python Basics Assignment',
            'description': 'Complete the Python fundamentals exercises',
            'priority': 'medium',
            'max_score': 100,
            'due_date': timezone.now() + timedelta(days=7)
        },
        {
            'title': 'Database Design Project',
            'description': 'Design and implement a database schema',
            'priority': 'high',
            'max_score': 150,
            'due_date': timezone.now() + timedelta(days=14)
        },
        {
            'title': 'Web Development Task',
            'description': 'Create a responsive web page using HTML/CSS',
            'priority': 'low',
            'max_score': 80,
            'due_date': timezone.now() + timedelta(days=21)
        }
    ]
    
    for data in assignment_data:
        assignment, created = Assignment.objects.get_or_create(
            title=data['title'],
            defaults={
                'description': data['description'],
                'created_by': manager,
                'priority': data['priority'],
                'max_score': data['max_score'],
                'due_date': data['due_date'],
                'instructions': f"Instructions for {data['title']}",
                'is_active': True
            }
        )
        if created:
            assignment.assigned_to.set(students)
            print(f"Created assignment: {assignment.title}")
        assignments.append(assignment)
    
    # Create some submissions and grades
    import random
    for assignment in assignments[:2]:  # Only for first 2 assignments
        for student in students[:3]:  # Only first 3 students submit
            submission, created = Submission.objects.get_or_create(
                assignment=assignment,
                student=student,
                defaults={
                    'content': f"This is {student.first_name}'s submission for {assignment.title}",
                    'submitted_at': timezone.now() - timedelta(days=random.randint(1, 5)),
                    'status': 'submitted'
                }
            )
            
            if created:
                print(f"Created submission: {student.username} -> {assignment.title}")
                
                # Grade some submissions
                if random.choice([True, False]):
                    score = random.randint(70, 100)
                    grade, grade_created = Grade.objects.get_or_create(
                        submission=submission,
                        defaults={
                            'score': score,
                            'graded_by': manager,
                            'graded_at': timezone.now() - timedelta(days=random.randint(0, 3)),
                            'feedback': f"Good work! Score: {score}/{assignment.max_score}"
                        }
                    )
                    if grade_created:
                        submission.status = 'graded'
                        submission.save()
                        print(f"Graded submission: {score}/{assignment.max_score}")
                
                # Add some comments
                if random.choice([True, False]):
                    comment, comment_created = Comment.objects.get_or_create(
                        submission=submission,
                        author=manager,
                        defaults={
                            'content': "Please review the requirements and make necessary adjustments.",
                            'created_at': timezone.now() - timedelta(days=random.randint(0, 2))
                        }
                    )
                    if comment_created:
                        print(f"Added comment to submission")
    
    # Create some notifications
    for student in students[:2]:
        notification, created = Notification.objects.get_or_create(
            recipient=student,
            title="Welcome to Student Dashboard",
            defaults={
                'message': "Welcome to the student dashboard! Check out your assignments and track your progress.",
                'notification_type': 'general',
                'is_read': False
            }
        )
        if created:
            print(f"Created notification for {student.username}")
    
    print("Sample data creation completed!")
    print("\nLogin credentials:")
    print("Admin: admin / admin123")
    print("Manager: manager / manager123")
    print("Students: student1-student5 / student123")

if __name__ == '__main__':
    create_sample_data()