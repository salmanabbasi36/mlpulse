from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, F
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Post, Category, Comment, Newsletter
from .forms import CommentForm, NewsletterForm


def home(request):
    featured = Post.objects.filter(status='published').first()
    posts = Post.objects.filter(status='published').exclude(pk=featured.pk if featured else 0)[:9]
    categories = Category.objects.all()
    form = NewsletterForm()
    return render(request, 'blog/home.html', {
        'featured': featured,
        'posts': posts,
        'categories': categories,
        'newsletter_form': form,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    Post.objects.filter(pk=post.pk).update(views=F('views') + 1)
    post.refresh_from_db(fields=['views'])

    comments = post.comments.filter(is_approved=True, parent=None).prefetch_related('replies')
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            if request.user.is_authenticated:
                comment.author = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    comment.parent = Comment.objects.get(pk=parent_id)
                except Comment.DoesNotExist:
                    pass
            comment.save()
            messages.success(request, 'Comment posted!')
            return redirect(post.get_absolute_url() + '#comments')

    related = Post.objects.filter(
        status='published', category=post.category
    ).exclude(pk=post.pk)[:3]

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': form,
        'related': related,
    })


def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(status='published', category=category)
    paginator = Paginator(posts, 12)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/category.html', {'category': category, 'page_obj': page})


def tag_list(request, slug):
    from taggit.models import Tag
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(status='published', tags__slug=slug)
    paginator = Paginator(posts, 12)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/tag.html', {'tag': tag, 'page_obj': page})


def search(request):
    q = request.GET.get('q', '').strip()
    posts = Post.objects.none()
    if q:
        posts = Post.objects.filter(
            status='published'
        ).filter(
            Q(title__icontains=q) | Q(body__icontains=q) | Q(excerpt__icontains=q)
        )
    paginator = Paginator(posts, 12)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/search.html', {'page_obj': page, 'query': q})


def archive(request):
    posts = Post.objects.filter(status='published')
    paginator = Paginator(posts, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/archive.html', {'page_obj': page})


@require_POST
def newsletter_subscribe(request):
    form = NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        Newsletter.objects.get_or_create(email=email)
        messages.success(request, 'You are subscribed! Welcome to MLPulse.')
    else:
        messages.error(request, 'Please enter a valid email.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
