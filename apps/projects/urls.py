from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('responded/', views.responded_list, name='responded_list'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/respond/', views.mark_responded, name='mark_responded'),
    path('<int:pk>/archive/', views.mark_archived, name='mark_archived'),
    path('parse-start/', views.parse_projects_start, name='parse_projects_start'),
    path('parse-status/', views.parse_projects_status, name='parse_projects_status'),
]
