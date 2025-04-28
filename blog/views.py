from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'hsohsh@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
            

def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, 
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             published__year=year,
                             published__month=month,
                             published__day=day)
    comments = post.comments.filter(active=True)
    form = None

    return render(request, 
                  'blog/post/detail.html', 
                  {'post': post,
                   'comments': comments,
                   'form': form})


def post_list(request):
    post_list = Post.published_objects.all()
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page')
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # 페이지 번호가 범위를 벗어난 경우 결과의 마지막 페이지를 반환
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # 페이지 번호가 정수가 아닌 경우 첫 번째 페이지를 반환
        posts = paginator.page(1)
    return render(request, 
                  'blog/post/list.html', 
                  {'posts': posts})

class PostListView(ListView):
    """
    Alternative post list view
    """
    queryset = Post.published_objects.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})

