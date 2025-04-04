from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from .models import Topic, Subtopic
from tests.models import TestSession, SubtopicPerformance
from django.urls import reverse
from django.urls import reverse_lazy
from django.urls import reverse
from django.urls import reverse_lazy

# Create your views here.

class TopicListView(ListView):
    model = Topic
    template_name = 'topics/list.html'
    context_object_name = 'topics'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get user's progress for each topic
            for topic in context['topics']:
                subtopics = topic.subtopics.all()
                completed = TestSession.objects.filter(
                    user=self.request.user,
                    subtopic__in=subtopics,
                    completed=True
                ).count()
                total = subtopics.count()
                topic.progress = (completed / total * 100) if total > 0 else 0
        return context

class SubtopicDetailView(DetailView):
    model = Subtopic
    template_name = 'topics/subtopic.html'
    context_object_name = 'subtopic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get user's performance for this subtopic
            performance = SubtopicPerformance.objects.filter(
                user=self.request.user,
                subtopic=self.object
            ).first()
            context['performance'] = performance

            # Get recent test sessions
            recent_tests = TestSession.objects.filter(
                user=self.request.user,
                subtopic=self.object,
                completed=True
            ).order_by('-started_at')[:5]
            context['recent_tests'] = recent_tests
        return context

@login_required
def start_test(request, subtopic_id):
    subtopic = get_object_or_404(Subtopic, id=subtopic_id)
    
    # Check if there's an incomplete test session
    existing_session = TestSession.objects.filter(
        user=request.user,
        subtopic=subtopic,
        completed=False
    ).first()
    
    if existing_session:
        # Continue the existing test
        return redirect('tests:take', test_session_id=existing_session.id)
    
    # Create a new test session
    test_session = TestSession.objects.create(
        user=request.user,
        subtopic=subtopic,
        total_questions=10  # Default number of questions
    )
    
    # Redirect to the test view
    return redirect('tests:take', test_session_id=test_session.id)
