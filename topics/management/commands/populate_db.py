from django.core.management.base import BaseCommand
from topics.models import Topic, Subtopic
from django.contrib.auth import get_user_model
from tests.models import TestSession, Question, SubtopicPerformance
import random
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        # Create sample topics
        topics = [
            ('Python Programming', 'Learn Python programming language'),
            ('Web Development', 'Learn web development technologies'),
            ('Data Science', 'Learn data science and machine learning'),
            ('System Design', 'Learn system design and architecture'),
        ]

        for name, description in topics:
            Topic.objects.get_or_create(
                name=name,
                defaults={'description': description}
            )

        # Create sample subtopics
        subtopics_data = {
            'Python Programming': [
                ('Variables and Data Types', 'Understanding Python variables and data types'),
                ('Control Flow', 'If statements, loops, and control structures'),
                ('Functions', 'Creating and using functions in Python'),
                ('Object-Oriented Programming', 'Classes, objects, and inheritance'),
            ],
            'Web Development': [
                ('HTML & CSS', 'Building web pages with HTML and CSS'),
                ('JavaScript Basics', 'Introduction to JavaScript programming'),
                ('Django Framework', 'Building web applications with Django'),
                ('REST APIs', 'Designing and implementing RESTful APIs'),
            ],
            'Data Science': [
                ('Data Analysis', 'Analyzing data with Python'),
                ('Machine Learning', 'Introduction to machine learning'),
                ('Data Visualization', 'Creating visualizations with Python'),
                ('Statistical Analysis', 'Statistical methods for data science'),
            ],
            'System Design': [
                ('System Architecture', 'Designing scalable systems'),
                ('Database Design', 'Database modeling and optimization'),
                ('Cloud Computing', 'Cloud services and deployment'),
                ('Security', 'System security and best practices'),
            ],
        }

        for topic_name, subtopics in subtopics_data.items():
            topic = Topic.objects.get(name=topic_name)
            for name, description in subtopics:
                Subtopic.objects.get_or_create(
                    topic=topic,
                    name=name,
                    defaults={'description': description}
                )

        # Create a test user if not exists
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()

        # Create sample test sessions and questions
        subtopics = Subtopic.objects.all()
        for subtopic in subtopics:
            # Create test session
            started_at = timezone.now() - timedelta(days=random.randint(1, 30))
            completed_at = started_at + timedelta(minutes=random.randint(10, 60))
            
            test_session = TestSession.objects.create(
                user=user,
                subtopic=subtopic,
                total_questions=5,
                score=random.randint(60, 100),
                completed=True,
                started_at=started_at,
                completed_at=completed_at
            )

            # Create questions
            for i in range(5):
                Question.objects.create(
                    test_session=test_session,
                    text=f'Sample question {i+1} for {subtopic.name}',
                    option_a='Option A',
                    option_b='Option B',
                    option_c='Option C',
                    option_d='Option D',
                    correct_answer=random.choice(['A', 'B', 'C', 'D']),
                    user_answer=random.choice(['A', 'B', 'C', 'D']),
                    explanation='This is a sample explanation for the question.'
                )

            # Create subtopic performance
            SubtopicPerformance.objects.create(
                user=user,
                subtopic=subtopic,
                score_avg=random.randint(60, 100),
                test_count=random.randint(1, 5)
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with sample data')) 