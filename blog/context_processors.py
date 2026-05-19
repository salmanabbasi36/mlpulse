from .models import Category, Post

def site_context(request):
    return {
        'categories': Category.objects.all()[:10],
        'recent_posts': Post.objects.filter(status='published')[:5],
        'site_name': 'MLPulse',
        'site_tagline': 'The pulse of machine learning, AI & data science',
    }
