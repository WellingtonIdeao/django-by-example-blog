from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator


def post_list(request):
    post_pub_list = Post.published.all()
    paginator = Paginator(post_pub_list, 3)  # 3 posts in each page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post/list.html', {'posts': page_obj})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post, slug=post,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    return render(request, 'blog/post/detail.html', {'post': post})
