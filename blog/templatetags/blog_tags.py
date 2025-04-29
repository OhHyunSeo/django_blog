from django import template
from django.db.models import Count
from ..models import Post
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

@register.simple_tag
def total_posts():
    return Post.published_objects.count()

@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published_objects.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published_objects.order_by('-published')[:count]
    return {'latest_posts': latest_posts}
