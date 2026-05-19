"""
Run this once after deploying:
  python manage.py setup_site
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.models import Category

User = get_user_model()

CATEGORIES = [
    {'name': 'Machine Learning', 'slug': 'machine-learning', 'color': '#6366f1'},
    {'name': 'Deep Learning', 'slug': 'deep-learning', 'color': '#8b5cf6'},
    {'name': 'Data Science', 'slug': 'data-science', 'color': '#06b6d4'},
    {'name': 'AI Research', 'slug': 'ai-research', 'color': '#f59e0b'},
    {'name': 'Tools & Libraries', 'slug': 'tools-libraries', 'color': '#10b981'},
    {'name': 'Industry News', 'slug': 'industry-news', 'color': '#ef4444'},
]


class Command(BaseCommand):
    help = 'Set up initial categories and AI author user'

    def handle(self, *args, **options):
        # Create categories
        for cat_data in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'color': cat_data['color']}
            )
            self.stdout.write(f'{"Created" if created else "Exists"}: {cat.name}')

        # Create AI author
        ai_user, created = User.objects.get_or_create(
            username='mlpulse-ai',
            defaults={
                'email': 'ai@mlpulse.app',
                'first_name': 'MLPulse',
                'last_name': 'AI',
                'bio': 'Auto-generated articles by the MLPulse AI, synthesizing the latest research and community discussions.',
                'is_author': True,
            }
        )
        if created:
            ai_user.set_unusable_password()
            ai_user.save()
            self.stdout.write('Created AI author user: mlpulse-ai')
        else:
            self.stdout.write('AI author already exists')

        self.stdout.write(self.style.SUCCESS('Setup complete!'))
