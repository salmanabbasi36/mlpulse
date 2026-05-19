from django.contrib import admin
from django.utils import timezone
from .models import Submission
from blog.models import Post


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'author_name', 'status', 'submitted_at']
    list_filter = ['status']
    actions = ['approve_and_publish', 'reject']

    def approve_and_publish(self, request, queryset):
        for sub in queryset:
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
        self.message_user(request, f'{queryset.count()} article(s) published.')
    approve_and_publish.short_description = 'Approve and publish'

    def reject(self, request, queryset):
        queryset.update(status='rejected', reviewed_at=timezone.now())
    reject.short_description = 'Reject selected'
