from django.db import models


class Submission(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    # Author info (can be anonymous)
    author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_bio = models.TextField(max_length=500, blank=True)

    # Article
    title = models.CharField(max_length=300)
    excerpt = models.TextField(max_length=500)
    body = models.TextField()
    category = models.ForeignKey('blog.Category', on_delete=models.SET_NULL, null=True)
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')
    cover_image = models.ImageField(upload_to='submissions/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    admin_notes = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.title} — {self.author_name}'
