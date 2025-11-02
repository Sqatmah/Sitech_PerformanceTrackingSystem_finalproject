from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Assignment, Submission, Grade, Comment
from accounts.models import User


class AssignmentForm(forms.ModelForm):
    """Form for creating and updating assignments"""
    
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'priority', 'max_score', 
                 'instructions', 'assigned_to', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'instructions': forms.Textarea(attrs={'rows': 6}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'assigned_to': forms.CheckboxSelectMultiple(),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.is_admin:
                # Admin can assign to any student
                self.fields['assigned_to'].queryset = User.objects.filter(role='student')
            elif user.is_manager:
                # Manager can only assign to their students
                self.fields['assigned_to'].queryset = User.objects.filter(
                    role='student',
                    student_profile__manager=user
                )
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date <= timezone.now():
            raise ValidationError("Due date must be in the future.")
        return due_date
    
    def clean_max_score(self):
        max_score = self.cleaned_data.get('max_score')
        if max_score and max_score <= 0:
            raise ValidationError("Maximum score must be greater than 0.")
        return max_score


class SubmissionForm(forms.ModelForm):
    """Form for student submissions"""
    
    class Meta:
        model = Submission
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Enter your submission content here...'
            }),
        }
    
    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Check file size (10MB limit)
            if attachment.size > 10 * 1024 * 1024:
                raise ValidationError("File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.rar']
            file_extension = attachment.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise ValidationError(
                    f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
                )
        
        return attachment


class GradeForm(forms.ModelForm):
    """Form for grading submissions"""
    
    class Meta:
        model = Grade
        fields = ['score', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Provide feedback for the student...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop('submission', None)
        super().__init__(*args, **kwargs)
        
        if self.submission and self.submission.assignment.max_score:
            self.fields['score'].widget.attrs['max'] = self.submission.assignment.max_score
            self.fields['score'].help_text = f"Maximum score: {self.submission.assignment.max_score}"
    
    def clean_score(self):
        score = self.cleaned_data.get('score')
        if self.submission and self.submission.assignment.max_score:
            if score > self.submission.assignment.max_score:
                raise ValidationError(
                    f"Score cannot exceed maximum score of {self.submission.assignment.max_score}."
                )
        if score < 0:
            raise ValidationError("Score cannot be negative.")
        return score


class CommentForm(forms.ModelForm):
    """Form for adding comments to submissions"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add a comment...',
                'class': 'w-full'
            }),
        }


class AssignmentFilterForm(forms.Form):
    """Form for filtering assignments"""
    
    STATUS_CHOICES = [
        ('', 'All'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    
    PRIORITY_CHOICES = [
        ('', 'All Priorities'),
    ] + Assignment.PRIORITY_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search assignments...',
            'class': 'form-input'
        })
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    created_by = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=['admin', 'manager']),
        required=False,
        empty_label="All Creators",
        widget=forms.Select(attrs={'class': 'form-select'})
    )