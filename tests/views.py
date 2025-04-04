from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Avg, Count, F, ExpressionWrapper, FloatField
from .models import TestSession, Question, SubtopicPerformance
from .utils import generate_questions, calculate_difficulty_level
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

class TestSessionListView(ListView):
    model = TestSession
    template_name = 'tests/list.html'
    context_object_name = 'test_sessions'

    def get_queryset(self):
        return TestSession.objects.filter(user=self.request.user).order_by('-started_at')

@login_required
def take_test(request, test_session_id):
    test_session = get_object_or_404(TestSession, id=test_session_id, user=request.user)
    
    if test_session.completed:
        return redirect('tests:results', test_session_id=test_session.id)
    
    # Get current question or generate new ones if needed
    current_question = Question.objects.filter(
        test_session=test_session,
        user_answer__isnull=True
    ).first()
    
    if not current_question:
        # Get user's performance for this subtopic
        performance = SubtopicPerformance.objects.filter(
            user=request.user,
            subtopic=test_session.subtopic
        ).first()
        
        # Calculate difficulty level based on performance
        difficulty_level = 1
        if performance:
            difficulty_level = calculate_difficulty_level(performance.score_avg)
        
        # Generate new questions
        questions = generate_questions(
            test_session.subtopic.name,
            difficulty_level=difficulty_level,
            num_questions=test_session.total_questions
        )
        
        if not questions:
            return render(request, 'tests/error.html', {
                'message': 'Failed to generate questions. Please try again later.'
            })
        
        with transaction.atomic():
            for q in questions:
                Question.objects.create(
                    test_session=test_session,
                    text=q['question'],
                    option_a=q['options']['A'],
                    option_b=q['options']['B'],
                    option_c=q['options']['C'],
                    option_d=q['options']['D'],
                    correct_answer=q['correct_answer'],
                    explanation=q['explanation']
                )
            
            current_question = Question.objects.filter(
                test_session=test_session,
                user_answer__isnull=True
            ).first()
    
    # Get progress information
    total_questions = test_session.total_questions
    answered_questions = Question.objects.filter(
        test_session=test_session,
        user_answer__isnull=False
    ).count()
    
    # Create options dictionary
    options = {
        'A': current_question.option_a,
        'B': current_question.option_b,
        'C': current_question.option_c,
        'D': current_question.option_d,
    }
    
    context = {
        'test_session': test_session,
        'question': current_question,
        'question_number': answered_questions + 1,
        'total_questions': total_questions,
        'progress': (answered_questions / total_questions) * 100,
        'options': options
    }
    return render(request, 'tests/take_test.html', context)

@login_required
def submit_answer(request, test_id):
    if request.method == 'POST':
        test_session = get_object_or_404(TestSession, id=test_id, user=request.user)
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer')
        
        if not question_id or not answer:
            return JsonResponse({'status': 'error', 'message': 'Missing question ID or answer'}, status=400)
        
        question = get_object_or_404(Question, id=question_id, test_session=test_session)
        question.user_answer = answer
        question.save()
        
        # Check if test is complete
        unanswered_questions = Question.objects.filter(
            test_session=test_session,
            user_answer__isnull=True
        ).count()
        
        if unanswered_questions == 0:
            # Calculate score
            correct_answers = Question.objects.filter(
                test_session=test_session,
                user_answer=F('correct_answer')
            ).count()
            
            score = (correct_answers / test_session.total_questions) * 100
            test_session.score = score
            test_session.completed = True
            test_session.completed_at = timezone.now()
            test_session.save()
            
            # Update subtopic performance
            performance, created = SubtopicPerformance.objects.get_or_create(
                user=request.user,
                subtopic=test_session.subtopic,
                defaults={
                    'score_avg': score,
                    'test_count': 1
                }
            )
            
            if not created:
                performance.score_avg = (
                    (performance.score_avg * performance.test_count) + score
                ) / (performance.test_count + 1)
                performance.test_count += 1
                performance.save()
            
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse('tests:results', args=[test_session.id])
            })
        
        return JsonResponse({'status': 'success', 'completed': False})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def test_results(request, test_session_id):
    test_session = get_object_or_404(TestSession, id=test_session_id, user=request.user)
    questions = Question.objects.filter(test_session=test_session)
    
    context = {
        'test_session': test_session,
        'questions': questions,
    }
    return render(request, 'tests/results.html', context)

@login_required
def test_analytics(request):
    user = request.user
    
    # Get performance data
    performance_data = SubtopicPerformance.objects.filter(user=user).select_related('subtopic', 'subtopic__topic')
    
    # Calculate overall statistics
    total_tests = TestSession.objects.filter(user=user, completed=True).count()
    average_score = TestSession.objects.filter(user=user, completed=True).aggregate(
        avg_score=Avg('score')
    )['avg_score'] or 0
    
    # Get recent test history
    recent_tests = TestSession.objects.filter(
        user=user,
        completed=True
    ).order_by('-completed_at')[:5]
    
    # Get topic-wise performance
    topic_performance = performance_data.values(
        'subtopic__topic__name'
    ).annotate(
        avg_score=Avg('score_avg'),
        test_count=Count('subtopic')
    ).order_by('-avg_score')
    
    # Get areas for improvement
    weak_areas = performance_data.filter(
        score_avg__lt=70
    ).order_by('score_avg')[:3]
    
    # Get progress over time
    last_month = timezone.now() - timedelta(days=30)
    monthly_progress = TestSession.objects.filter(
        user=user,
        completed=True,
        completed_at__gte=last_month
    ).values('completed_at__date').annotate(
        daily_score=Avg('score')
    ).order_by('completed_at__date')
    
    context = {
        'total_tests': total_tests,
        'average_score': average_score,
        'recent_tests': recent_tests,
        'topic_performance': topic_performance,
        'weak_areas': weak_areas,
        'monthly_progress': monthly_progress,
    }
    
    return render(request, 'tests/analytics.html', context)

@login_required
def get_recommendations(request):
    user = request.user
    
    # Get weak areas
    weak_areas = SubtopicPerformance.objects.filter(
        user=user,
        score_avg__lt=70
    ).select_related('subtopic', 'subtopic__topic').order_by('score_avg')[:3]
    
    # Get topics with few tests
    less_practiced = SubtopicPerformance.objects.filter(
        user=user
    ).annotate(
        days_since_last_test=ExpressionWrapper(
            timezone.now() - F('last_attempt'),
            output_field=FloatField()
        )
    ).order_by('-days_since_last_test')[:3]
    
    recommendations = []
    
    # Add weak areas as recommendations
    for area in weak_areas:
        recommendations.append({
            'type': 'weak_area',
            'subtopic': area.subtopic.name,
            'topic': area.subtopic.topic.name,
            'score': area.score_avg,
            'message': f"Focus on {area.subtopic.name} to improve your understanding"
        })
    
    # Add less practiced topics as recommendations
    for topic in less_practiced:
        recommendations.append({
            'type': 'less_practiced',
            'subtopic': topic.subtopic.name,
            'topic': topic.subtopic.topic.name,
            'days_since_last_test': int(topic.days_since_last_test.days),
            'message': f"Review {topic.subtopic.name} to maintain your knowledge"
        })
    
    return JsonResponse({'recommendations': recommendations})
