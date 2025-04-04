from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('', views.TestSessionListView.as_view(), name='list'),
    path('take/<int:test_session_id>/', views.take_test, name='take'),
    path('submit/<int:test_session_id>/', views.submit_answer, name='submit'),
    path('results/<int:test_session_id>/', views.test_results, name='results'),
    path('analytics/', views.test_analytics, name='analytics'),
    path('recommendations/', views.get_recommendations, name='recommendations'),
] 