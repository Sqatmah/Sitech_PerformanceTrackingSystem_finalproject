from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from .models import User, StudentProfile, ManagerProfile
from .forms import (
    CustomUserCreationForm, LoginForm, ProfileUpdateForm, 
    StudentProfileForm, ManagerProfileForm
)


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            from django.contrib.auth import authenticate
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard:home')
                return redirect(next_url)
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


class RegisterView(CreateView):
    """User registration view"""
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registration successful! Please log in.')
        return response


class ProfileView(LoginRequiredMixin, DetailView):
    """User profile view"""
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    
    def get_object(self):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Update user profile"""
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


@login_required
def setup_profile(request):
    """Setup additional profile information based on user role"""
    user = request.user
    
    if user.role == 'student':
        try:
            profile = user.student_profile
            form = StudentProfileForm(instance=profile)
        except StudentProfile.DoesNotExist:
            form = StudentProfileForm()
        
        if request.method == 'POST':
            if hasattr(user, 'student_profile'):
                form = StudentProfileForm(request.POST, instance=user.student_profile)
            else:
                form = StudentProfileForm(request.POST)
            
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                messages.success(request, 'Student profile updated successfully!')
                return redirect('accounts:profile')
    
    elif user.role == 'manager':
        try:
            profile = user.manager_profile
            form = ManagerProfileForm(instance=profile)
        except ManagerProfile.DoesNotExist:
            form = ManagerProfileForm()
        
        if request.method == 'POST':
            if hasattr(user, 'manager_profile'):
                form = ManagerProfileForm(request.POST, instance=user.manager_profile)
            else:
                form = ManagerProfileForm(request.POST)
            
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
                messages.success(request, 'Manager profile updated successfully!')
                return redirect('accounts:profile')
    
    else:
        messages.info(request, 'No additional profile setup required for your role.')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/setup_profile.html', {
        'form': form,
        'user_role': user.role
    })


@login_required
def user_list_view(request):
    """View for listing users (admin/manager only)"""
    if not (request.user.is_admin or request.user.is_manager):
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard:home')
    
    user = request.user
    
    if user.is_admin:
        users = User.objects.all().order_by('username')
    elif user.is_manager:
        # Managers can only see their assigned students
        users = User.objects.filter(
            student_profile__manager=user
        ).order_by('username')
    
    return render(request, 'accounts/user_list.html', {'users': users})
