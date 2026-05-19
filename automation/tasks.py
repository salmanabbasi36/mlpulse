from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from .scraper import gather_all_content
from .writer import generate_post

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def auto_generate_post(self):
    """
    Main task: scrape → write → save as draft.
    Runs every 4 hours via Celery Beat.
    Posts are saved as DRAFT so admin can review before publishing.
    Set AUTO_PUBLISH=True in settings to skip review.
    """
    from django.conf import settings
    from blog.models import Post, Category
    from accounts.models import User

    logger.info('Starting auto post generation...')

    # 1. Gather content
    try:
        content_digest, source_urls = gather_all_content()
    except Exception as exc:
        logger.error(f'Scraping failed: {exc}')
        raise self.retry(exc=exc)

    if not content_digest.strip():
        logger.warning('No content gathered, skipping.')
        return

    # 2. Generate post via Claude
    try:
        post_data = generate_post(content_digest, source_urls)
    except Exception as exc:
        logger.error(f'Claude generation failed: {exc}')
        raise self.retry(exc=exc)

    if not post_data:
        logger.error('No post data returned from Claude.')
        return

    # 3. Get or create category
    category_slug = post_data.get('category_slug', 'machine-learning')
    category = Category.objects.filter(slug=category_slug).first()
    if not category:
        category = Category.objects.first()  # fallback

    # 4. Get AI author user
    ai_user = User.objects.filter(username='mlpulse-ai').first()

    # 5. Determine status
    auto_publish = getattr(settings, 'AUTO_PUBLISH', False)
    status = 'published' if auto_publish else 'draft'

    # 6. Create post
    post = Post.objects.create(
        title=post_data.get('title', 'Untitled'),
        excerpt=post_data.get('excerpt', ''),
        body=post_data.get('body', ''),
        meta_description=post_data.get('meta_description', ''),
        category=category,
        status=status,
        source='auto',
        source_urls=source_urls,
        ai_model=post_data.get('ai_model', ''),
        author=ai_user,
    )

    # 7. Add tags
    tags = post_data.get('tags', [])
    if tags:
        post.tags.add(*tags)

    logger.info(f'Post created: "{post.title}" (status={status}, id={post.pk})')
    return {'post_id': post.pk, 'title': post.title, 'status': status}
