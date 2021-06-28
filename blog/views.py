from django.shortcuts import render, redirect, get_object_or_404
from .models import Post
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import EmailPostForm, CommentPostForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


class PostListView(ListView):
    queryset = Post.published.all()
    paginate_by = 3  # 3 posts in each page
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag, ])

    paginator = Paginator(object_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post/list.html', {'page_obj': page_obj, 'tag': tag})


class PostDetailView(DetailView):
    template_name = 'blog/post/detail.html'

    def get_queryset(self):
        queryset = Post.published.filter(
            publish__year=self.kwargs['year'],
            publish__month=self.kwargs['month'],
            publish__day=self.kwargs['day'],
            slug=self.kwargs['slug']
        )
        return queryset


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(
        Post, slug=slug,
        status='published',
        publish__year=year,
        publish__month=month,
        publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    new_comment = None # new_comment will be None because views always redirect
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentPostForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            return redirect(post)
    else:
        comment_form = CommentPostForm()

    # list of similar posts

    # retrieve q.s. with list of tag ids from current post. flat = True - get single value for each id
    post_tags_ids = post.tags.values_list('id', flat=True)

    # retrieve all occurrence post (with post repeat) with tags_ids, excluding current post
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(pk=post.id)

    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts,
                                                     })


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(Post, pk=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form fields passed validation
            cd = form.cleaned_data
            # send mail
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n\n{cd['name']}'s comments: {cd['comments']}"
            from_email = cd['email']
            to = cd['to']
            send_mail(subject=subject, message=message, from_email=from_email, recipient_list=[to, ])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'form': form, 'post': post, 'sent': sent})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)
                                              ).filter(rank__gte=0.3).order_by('-rank')

    return render(request, 'blog/post/search.html', {'form': form, 'results': results, 'query': query})