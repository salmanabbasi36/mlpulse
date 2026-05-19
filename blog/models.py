from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from taggit.managers import TaggableManager
import readtime


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6366f1')  # hex

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category', args=[self.slug])


class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    SOURCE_AUTO = 'auto'
    SOURCE_USER = 'user'
    SOURCE_CHOICES = [
        (SOURCE_AUTO, 'Auto-generated'),
        (SOURCE_USER, 'User submitted'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=350)
    author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = TaggableManager(blank=True)

    excerpt = models.TextField(max_length=500, help_text='Short summary shown in listings')
    body = models.TextField()
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    cover_image_url = models.URLField(blank=True)  # For auto-generated posts using web images

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_AUTO)

    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)

    # Automation metadata
    source_urls = models.JSONField(default=list, blank=True, help_text='URLs scraped to generate this post')
    ai_model = models.CharField(max_length=100, blank=True)

    # Stats
    views = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=0, help_text='Minutes')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        if self.body:
            try:
                result = readtime.of_html(self.body)
                self.reading_time = result.minutes
            except Exception:
                self.reading_time = max(1, len(self.body.split()) // 200)
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])

    def publish(self):
        self.status = self.STATUS_PUBLISHED
        self.published_at = timezone.now()
        self.save()

    @property
    def cover(self):
        if self.cover_image:
            return self.cover_image.url
        return self.cover_image_url or '/static/img/default-cover.jpg'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    body = models.TextField(max_length=2000)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author or self.name} on {self.post}'


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
