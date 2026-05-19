from django.urls import path
from . import views

app_name = 'automation'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('trigger/', views.trigger_generation, name='trigger'),
    path('drafts/<int:pk>/', views.preview_draft, name='preview_draft'),
    path('drafts/<int:pk>/publish/', views.publish_post, name='publish_post'),
    path('drafts/<int:pk>/delete/', views.delete_draft, name='delete_draft'),
    path('submissions/<int:pk>/', views.preview_submission, name='preview_submission'),
    path('submissions/<int:pk>/approve/', views.approve_submission, name='approve_submission'),
    path('submissions/<int:pk>/reject/', views.reject_submission, name='reject_submission'),
]
