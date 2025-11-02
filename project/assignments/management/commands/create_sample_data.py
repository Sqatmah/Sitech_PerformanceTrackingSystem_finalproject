from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from assignments.models import Assignment, Submission, Grade, Comment

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for testing the student dashboard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of sample users to create (default: 10)'
        )
        parser.add_argument(
            '--assignments',
            type=int,
            default=5,
            help='Number of sample assignments to create (default: 5)'
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample users if they don't exist
        self.create_sample_users(options['users'])
        
        # Create sample assignments
        self.create_sample_assignments(options['assignments'])
        
        # Create sample submissions and grades
        self.create_sample_submissions()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def create_sample_users(self, count):
        """Create sample users with different roles"""
        
        # Create managers if they don't exist
        managers_data = [
            {'username': 'manager1', 'email': 'manager1@example.com', 'first_name': 'John', 'last_name': 'Smith'},
            {'username': 'manager2', 'email': 'manager2@example.com', 'first_name': 'Sarah', 'last_name': 'Johnson'},
        ]
        
        for manager_data in managers_data:
            if not User.objects.filter(username=manager_data['username']).exists():
                user = User.objects.create_user(
                    username=manager_data['username'],
                    email=manager_data['email'],
                    password='password123',
                    first_name=manager_data['first_name'],
                    last_name=manager_data['last_name'],
                    role='manager'
                )
                self.stdout.write(f'Created manager: {user.username}')
        
        # Create students
        existing_students = User.objects.filter(role='student').count()
        students_to_create = max(0, count - existing_students)
        
        for i in range(students_to_create):
            student_num = existing_students + i + 1
            username = f'student{student_num}'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123',
                    first_name=f'Student',
                    last_name=f'{student_num}',
                    role='student'
                )
                self.stdout.write(f'Created student: {user.username}')

    def create_sample_assignments(self, count):
        """Create sample assignments"""
        managers = User.objects.filter(role='manager')
        if not managers.exists():
            self.stdout.write(self.style.WARNING('No managers found. Creating assignments with admin user.'))
            managers = User.objects.filter(role='admin')
        
        if not managers.exists():
            self.stdout.write(self.style.ERROR('No managers or admin users found. Cannot create assignments.'))
            return
        
        assignment_templates = [
            {
                'title': 'Python Basics Assignment',
                'description': 'Complete the Python programming exercises covering variables, loops, and functions.',
                'instructions': 'Write Python code to solve the given problems. Submit your .py files.',
                'priority': 'medium',
                'max_score': 100,
            },
            {
                'title': 'Database Design Project',
                'description': 'Design and implement a database schema for a library management system.',
                'instructions': 'Create an ERD and implement the database using SQL. Submit your SQL scripts.',
                'priority': 'high',
                'max_score': 150,
            },
            {
                'title': 'Web Development Portfolio',
                'description': 'Create a personal portfolio website using HTML, CSS, and JavaScript.',
                'instructions': 'Build a responsive website showcasing your projects. Include at least 3 pages.',
                'priority': 'medium',
                'max_score': 120,
            },
            {
                'title': 'Data Analysis Report',
                'description': 'Analyze the provided dataset and create a comprehensive report.',
                'instructions': 'Use Python/R for analysis. Submit your code and a written report.',
                'priority': 'high',
                'max_score': 100,
            },
            {
                'title': 'Algorithm Implementation',
                'description': 'Implement sorting and searching algorithms in your preferred language.',
                'instructions': 'Code must be well-documented with time complexity analysis.',
                'priority': 'low',
                'max_score': 80,
            },
        ]
        
        existing_assignments = Assignment.objects.count()
        assignments_to_create = min(count, len(assignment_templates))
        
        for i in range(assignments_to_create):
            if existing_assignments + i >= len(assignment_templates):
                break
                
            template = assignment_templates[i]
            manager = random.choice(managers)
            
            # Create due date 1-4 weeks from now
            due_date = timezone.now() + timedelta(days=random.randint(7, 28))
            
            assignment = Assignment.objects.create(
                title=template['title'],
                description=template['description'],
                instructions=template['instructions'],
                due_date=due_date,
                max_score=template['max_score'],
                priority=template['priority'],
                created_by=manager,
                is_active=True
            )
            
            self.stdout.write(f'Created assignment: {assignment.title}')

    def create_sample_submissions(self):
        """Create sample submissions and grades"""
        assignments = Assignment.objects.all()
        students = User.objects.filter(role='student')
        
        if not assignments.exists() or not students.exists():
            self.stdout.write(self.style.WARNING('No assignments or students found. Skipping submissions.'))
            return
        
        submission_contents = [
            "I have completed the assignment as requested. Please find my solution attached.",
            "This was a challenging assignment but I learned a lot. Here's my approach to solving the problem...",
            "I've implemented all the required features. The code is well-documented and tested.",
            "Please review my submission. I've included additional features beyond the requirements.",
            "I encountered some difficulties but managed to complete most of the assignment.",
        ]
        
        for assignment in assignments:
            # Random number of submissions (50-80% of students)
            num_submissions = random.randint(
                int(len(students) * 0.5), 
                int(len(students) * 0.8)
            )
            
            selected_students = random.sample(list(students), num_submissions)
            
            for student in selected_students:
                # Check if submission already exists
                if Submission.objects.filter(assignment=assignment, student=student).exists():
                    continue
                
                # Random submission date (between assignment creation and due date)
                days_diff = (assignment.due_date - assignment.created_at).days
                if days_diff > 0:
                    submission_date = assignment.created_at + timedelta(
                        days=random.randint(0, max(1, days_diff))
                    )
                else:
                    submission_date = assignment.created_at
                
                submission = Submission.objects.create(
                    assignment=assignment,
                    student=student,
                    content=random.choice(submission_contents),
                    status=random.choice(['submitted', 'late', 'reviewed']),
                    submitted_at=submission_date
                )
                
                # Create grade for some submissions (70% chance)
                if random.random() < 0.7:
                    score = random.randint(
                        int(assignment.max_score * 0.6), 
                        assignment.max_score
                    )
                    
                    feedback_options = [
                        "Good work! Well-structured solution.",
                        "Excellent implementation. Great attention to detail.",
                        "Good effort. Consider improving the documentation.",
                        "Well done! Creative approach to the problem.",
                        "Solid work. Minor improvements needed in error handling.",
                    ]
                    
                    grade = Grade.objects.create(
                        submission=submission,
                        score=score,
                        feedback=random.choice(feedback_options),
                        graded_by=assignment.created_by,
                        graded_at=submission_date + timedelta(days=random.randint(1, 7))
                    )
                    
                    # Create some comments (30% chance)
                    if random.random() < 0.3:
                        comment_contents = [
                            "Great job on this assignment!",
                            "I have a question about the implementation approach.",
                            "Could you explain this part in more detail?",
                            "Thanks for the feedback, I'll improve this in future assignments.",
                            "This was a challenging problem but I enjoyed solving it.",
                        ]
                        
                        # Random author (student or instructor)
                        author = random.choice([student, assignment.created_by])
                        
                        Comment.objects.create(
                            submission=submission,
                            author=author,
                            content=random.choice(comment_contents)
                        )
                
                self.stdout.write(f'Created submission for {student.username} -> {assignment.title}')