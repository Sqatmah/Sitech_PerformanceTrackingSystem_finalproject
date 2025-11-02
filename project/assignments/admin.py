from django.contrib import admin
from .models import Assignment, Submission, Grade, Comment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'due_date', 'priority', 'is_active', 'submission_count')
    list_filter = ('priority', 'is_active', 'due_date', 'created_by')
    search_fields = ('title', 'description')
    filter_horizontal = ('assigned_to',)
    raw_id_fields = ('created_by',)
    date_hierarchy = 'due_date'


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'status', 'submitted_at', 'is_late')
    list_filter = ('status', 'submitted_at', 'assignment')
    search_fields = ('assignment__title', 'student__username', 'student__first_name', 'student__last_name')
    raw_id_fields = ('assignment', 'student')
    date_hierarchy = 'submitted_at'


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('submission', 'score', 'percentage', 'letter_grade', 'graded_by', 'graded_at')
    list_filter = ('graded_at', 'graded_by')
    search_fields = ('submission__assignment__title', 'submission__student__username')
    raw_id_fields = ('submission', 'graded_by')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('submission', 'author', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('submission__assignment__title', 'author__username', 'content')
    raw_id_fields = ('submission', 'author')
