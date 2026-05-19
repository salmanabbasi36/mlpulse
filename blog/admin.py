from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Post, Category, Comment, Newsletter

@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ('body',)
    list_display = ['title', 'author', 'category', 'status', 'source', 'views', 'published_at']
    list_filter = ['status', 'source', 'category']
    search_fields = ['title', 'body']
    prepopulated_fields = {'slug': ('title',)}
    actions = ['publish_posts']

    def publish_posts(self, request, queryset):
        for post in queryset:
            post.publish()
        self.message_user(request, f'{queryset.count()} post(s) published.')
    publish_posts.short_description = 'Publish selected posts'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'name', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
