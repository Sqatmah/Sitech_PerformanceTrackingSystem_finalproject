from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Assignment, Submission, Grade, Comment
from .forms import AssignmentForm, SubmissionForm, GradeForm, CommentForm, AssignmentFilterForm
from dashboard.models import Notification


@login_required
def assignment_list(request):
    """List assignments based on user role"""
    user = request.user
    form = AssignmentFilterForm(request.GET)
    
    # Base queryset based on user role
    if user.is_admin:
        assignments = Assignment.objects.all()
    elif user.is_manager:
        assignments = Assignment.objects.filter(created_by=user)
    elif user.is_student:
        assignments = Assignment.objects.filter(assigned_to=user)
    else:
        assignments = Assignment.objects.none()
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        priority = form.cleaned_data.get('priority')
        created_by = form.cleaned_data.get('created_by')
        
        if search:
            assignments = assignments.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        if status == 'active':
            assignments = assignments.filter(is_active=True)
        elif status == 'inactive':
            assignments = assignments.filter(is_active=False)
        
        if priority:
            assignments = assignments.filter(priority=priority)
        
        if created_by:
            assignments = assignments.filter(created_by=created_by)
    
    assignments = assignments.select_related('created_by').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(assignments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'assignments/list.html', {
        'page_obj': page_obj,
        'form': form,
        'user': user,
    })


class AssignmentCreateView(LoginRequiredMixin, CreateView):
    """Create new assignment (admin/manager only)"""
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/create.html'
    success_url = reverse_lazy('assignments:list')
    
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_manager):
            messages.error(request, 'You do not have permission to create assignments.')
            return redirect('assignments:list')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Create notifications for assigned students
        for student in form.instance.assigned_to.all():
            Notification.objects.create(
                recipient=student,
                title=f"New Assignment: {form.instance.title}",
                message=f"You have been assigned a new assignment '{form.instance.title}' due on {form.instance.due_date}.",
                notification_type='assignment_created'
            )
        
        messages.success(self.request, 'Assignment created successfully!')
        return response


class AssignmentUpdateView(LoginRequiredMixin, UpdateView):
    """Update assignment (creator only)"""
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/update.html'
    
    def dispatch(self, request, *args, **kwargs):
        assignment = self.get_object()
        if not (request.user == assignment.created_by or request.user.is_admin):
            messages.error(request, 'You do not have permission to edit this assignment.')
            return redirect('assignments:detail', pk=assignment.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        return reverse_lazy('assignments:detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Assignment updated successfully!')
        return super().form_valid(form)


class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    """Delete assignment (creator only)"""
    model = Assignment
    template_name = 'assignments/delete.html'
    success_url = reverse_lazy('assignments:list')
    
    def dispatch(self, request, *args, **kwargs):
        assignment = self.get_object()
        if not (request.user == assignment.created_by or request.user.is_admin):
            messages.error(request, 'You do not have permission to delete this assignment.')
            return redirect('assignments:detail', pk=assignment.pk)
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Assignment deleted successfully!')
        return super().delete(request, *args, **kwargs)


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    """View assignment details"""
    model = Assignment
    template_name = 'assignments/detail.html'
    context_object_name = 'assignment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.object
        user = self.request.user
        
        # Check if user has submitted
        user_submission = None
        if user.is_student:
            try:
                user_submission = assignment.submissions.get(student=user)
            except Submission.DoesNotExist:
                pass
        
        context.update({
            'user_submission': user_submission,
            'can_submit': user.is_student and assignment.is_active and not user_submission,
            'can_edit': user == assignment.created_by or user.is_admin,
            'submissions': assignment.submissions.select_related('student').order_by('-submitted_at') if user.is_admin or user == assignment.created_by else None,
        })
        
        return context


@login_required
def submit_assignment(request, assignment_id):
    """Submit assignment (students only)"""
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if not request.user.is_student:
        messages.error(request, 'Only students can submit assignments.')
        return redirect('assignments:detail', pk=assignment_id)
    
    if not assignment.is_active:
        messages.error(request, 'This assignment is no longer active.')
        return redirect('assignments:detail', pk=assignment_id)
    
    # Check if already submitted
    if assignment.submissions.filter(student=request.user).exists():
        messages.error(request, 'You have already submitted this assignment.')
        return redirect('assignments:detail', pk=assignment_id)
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.submitted_at = timezone.now()
            
            # Check if late
            if assignment.due_date and submission.submitted_at > assignment.due_date:
                submission.is_late = True
            
            submission.save()
            
            # Create notification for assignment creator
            Notification.objects.create(
                recipient=assignment.created_by,
                title=f"New Submission: {assignment.title}",
                message=f"{request.user.get_full_name()} has submitted '{assignment.title}'.",
                notification_type='general'
            )
            
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignments:detail', pk=assignment_id)
    else:
        form = SubmissionForm()
    
    return render(request, 'assignments/submit.html', {
        'assignment': assignment,
        'form': form,
    })


class SubmissionDetailView(LoginRequiredMixin, DetailView):
    """View submission details"""
    model = Submission
    template_name = 'assignments/submission_detail.html'
    context_object_name = 'submission'
    
    def dispatch(self, request, *args, **kwargs):
        submission = self.get_object()
        user = request.user
        
        # Check permissions
        if not (user == submission.student or 
                user == submission.assignment.created_by or 
                user.is_admin):
            messages.error(request, 'You do not have permission to view this submission.')
            return redirect('assignments:list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.object
        user = self.request.user
        
        context.update({
            'can_grade': (user == submission.assignment.created_by or user.is_admin) and not hasattr(submission, 'grade'),
            'comments': submission.comments.select_related('author').order_by('created_at'),
            'comment_form': CommentForm(),
        })
        
        return context


@login_required
def grade_submission(request, pk):
    """Grade a submission (manager/admin only)"""
    submission = get_object_or_404(Submission, pk=pk)
    
    if not (request.user == submission.assignment.created_by or request.user.is_admin):
        messages.error(request, 'You do not have permission to grade this submission.')
        return redirect('assignments:submission_detail', pk=pk)
    
    if hasattr(submission, 'grade'):
        messages.error(request, 'This submission has already been graded.')
        return redirect('assignments:submission_detail', pk=pk)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, submission=submission)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.submission = submission
            grade.graded_by = request.user
            grade.graded_at = timezone.now()
            grade.save()
            
            # Update submission status
            submission.status = 'graded'
            submission.save()
            
            # Create notification for student
            Notification.objects.create(
                recipient=submission.student,
                title=f"Assignment Graded: {submission.assignment.title}",
                message=f"Your submission for '{submission.assignment.title}' has been graded. Score: {grade.score}/{submission.assignment.max_score}",
                notification_type='submission_graded'
            )
            
            messages.success(request, 'Submission graded successfully!')
            return redirect('assignments:submission_detail', pk=pk)
    else:
        form = GradeForm(submission=submission)
    
    return render(request, 'assignments/grade.html', {
        'submission': submission,
        'form': form,
    })


@login_required
def add_comment(request, pk):
    """Add comment to submission"""
    submission = get_object_or_404(Submission, pk=pk)
    
    # Check permissions
    if not (request.user == submission.student or 
            request.user == submission.assignment.created_by or 
            request.user.is_admin):
        messages.error(request, 'You do not have permission to comment on this submission.')
        return redirect('assignments:list')
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.submission = submission
            comment.author = request.user
            comment.save()
            
            # Create notification for relevant users
            recipients = []
            if request.user != submission.student:
                recipients.append(submission.student)
            if request.user != submission.assignment.created_by:
                recipients.append(submission.assignment.created_by)
            
            for recipient in recipients:
                Notification.objects.create(
                    recipient=recipient,
                    title=f"New Comment: {submission.assignment.title}",
                    message=f"{request.user.get_full_name()} added a comment to the submission.",
                    notification_type='comment_added'
                )
            
            messages.success(request, 'Comment added successfully!')
    
    return redirect('assignments:submission_detail', pk=pk)


@login_required
def my_submissions(request):
    """View student's own submissions"""
    if not request.user.is_student:
        messages.error(request, 'This page is only for students.')
        return redirect('dashboard:home')
    
    submissions = Submission.objects.filter(
        student=request.user
    ).select_related('assignment').order_by('-submitted_at')
    
    # Pagination
    paginator = Paginator(submissions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'assignments/my_submissions.html', {
        'page_obj': page_obj,
    })
