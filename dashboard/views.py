from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from topics.models import Topic, Subtopic
from tests.models import TestSession, SubtopicPerformance
from .models import UserProgress

class DashboardHomeView(TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Get user's recent test sessions
            recent_tests = TestSession.objects.filter(
                user=self.request.user
            ).order_by('-started_at')[:5]
            
            # Get user's progress by topic
            topics = Topic.objects.all()
            topic_progress = []
            for topic in topics:
                subtopics = topic.subtopics.all()
                completed = UserProgress.objects.filter(
                    user=self.request.user,
                    subtopic__in=subtopics,
                    completed=True
                ).count()
                total = subtopics.count()
                progress = (completed / total * 100) if total > 0 else 0
                
                topic_progress.append({
                    'topic': topic,
                    'progress': progress,
                    'completed': completed,
                    'total': total
                })
            
            # Get weak areas (subtopics with lowest scores)
            weak_areas = SubtopicPerformance.objects.filter(
                user=self.request.user
            ).order_by('score_avg')[:3]
            
            context.update({
                'recent_tests': recent_tests,
                'topic_progress': topic_progress,
                'weak_areas': weak_areas,
            })
        return context

@login_required
def profile_view(request):
    user = request.user
    test_count = TestSession.objects.filter(user=user).count()
    total_score = user.total_score
    level = user.level
    
    # Calculate progress to next level (example: 100 points per level)
    points_to_next_level = (level * 100) - total_score
    progress_percentage = (total_score % 100) if level > 1 else (total_score / 100 * 100)
    
    context = {
        'user': user,
        'test_count': test_count,
        'total_score': total_score,
        'level': level,
        'points_to_next_level': points_to_next_level,
        'progress_percentage': progress_percentage,
    }
    return render(request, 'dashboard/profile.html', context)
