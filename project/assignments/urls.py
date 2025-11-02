from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('', views.assignment_list, name='list'),
    path('create/', views.AssignmentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AssignmentDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.AssignmentUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.AssignmentDeleteView.as_view(), name='delete'),
    path('<int:assignment_id>/submit/', views.submit_assignment, name='submit'),
    path('submission/<int:pk>/', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('submission/<int:pk>/grade/', views.grade_submission, name='grade_submission'),
    path('submission/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('my-submissions/', views.my_submissions, name='my_submissions'),
]