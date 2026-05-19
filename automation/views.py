from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from blog.models import Post
from submissions.models import Submission
from automation.tasks import auto_generate_post


@staff_member_required
def dashboard(request):
    drafts = Post.objects.filter(status='draft').order_by('-created_at')
    pending_submissions = Submission.objects.filter(status='pending').order_by('-submitted_at')
    published_today = Post.objects.filter(
        status='published',
        published_at__date=timezone.now().date()
    ).count()
    total_posts = Post.objects.filter(status='published').count()

    return render(request, 'admin_dashboard/dashboard.html', {
        'drafts': drafts,
        'pending_submissions': pending_submissions,
        'published_today': published_today,
        'total_posts': total_posts,
    })


@staff_member_required
def preview_draft(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'admin_dashboard/preview.html', {'post': post})


@staff_member_required
@require_POST
def publish_post(request, pk):
    post = get_object_or_404(Post, pk=pk, status='draft')
    post.publish()
    messages.success(request, f'"{post.title}" published successfully!')
    return redirect('automation:dashboard')


@staff_member_required
@require_POST
def delete_draft(request, pk):
    post = get_object_or_404(Post, pk=pk, status='draft')
    post.delete()
    messages.success(request, 'Draft deleted.')
    return redirect('automation:dashboard')


@staff_member_required
def preview_submission(request, pk):
    sub = get_object_or_404(Submission, pk=pk)
    return render(request, 'admin_dashboard/preview_submission.html', {'sub': sub})


@staff_member_required
@require_POST
def approve_submission(request, pk):
    sub = get_object_or_404(Submission, pk=pk, status='pending')
    from blog.models import Post, Category

    post = Post.objects.create(
        title=sub.title,
        excerpt=sub.excerpt,
        body=sub.body,
        category=sub.category,
        cover_image=sub.cover_image,
        status='published',
        source='user',
        author=sub.author,
    )
    if sub.tags:
        post.tags.add(*[t.strip() for t in sub.tags.split(',')])

    sub.status = 'approved'
    sub.reviewed_at = timezone.now()
    sub.save()

    messages.success(request, f'"{sub.title}" approved and published!')
    return redirect('automation:dashboard')


@staff_member_required
@require_POST
def reject_submission(request, pk):
    sub = get_object_or_404(Submission, pk=pk, status='pending')
    sub.status = 'rejected'
    sub.reviewed_at = timezone.now()
    sub.admin_notes = request.POST.get('notes', '')
    sub.save()
    messages.success(request, 'Submission rejected.')
    return redirect('automation:dashboard')


@staff_member_required
@require_POST
def trigger_generation(request):
    try:
        from .scraper import gather_all_content
        from .writer import generate_post
        from blog.models import Post, Category
        from accounts.models import User

        content_digest, source_urls = gather_all_content()
        post_data = generate_post(content_digest, source_urls)

        if post_data:
            category = Category.objects.filter(slug=post_data.get('category_slug')).first()
            if not category:
                category = Category.objects.first()
            ai_user = User.objects.filter(username='mlpulse-ai').first()
            post = Post.objects.create(
                title=post_data.get('title', 'Untitled'),
                excerpt=post_data.get('excerpt', ''),
                body=post_data.get('body', ''),
                meta_description=post_data.get('meta_description', ''),
                category=category,
                status='draft',
                source='auto',
                source_urls=source_urls,
                ai_model=post_data.get('ai_model', ''),
                author=ai_user,
            )
            tags = post_data.get('tags', [])
            if tags:
                post.tags.add(*tags)
            messages.success(request, f'Post generated: "{post.title}" — ready to preview!')
        else:
            messages.error(request, 'Generation failed. Check your Gemini API key.')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('automation:dashboard')