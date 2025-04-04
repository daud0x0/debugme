from django.urls import path
from . import views

app_name = 'topics'

urlpatterns = [
    path('', views.TopicListView.as_view(), name='list'),
    path('subtopic/<int:pk>/', views.SubtopicDetailView.as_view(), name='subtopic'),
    path('subtopic/<int:subtopic_id>/start-test/', views.start_test, name='start_test'),
] 