from django.shortcuts import render, get_object_or_404
from .models import Post
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .forms import EmailPostForm
from django.core.mail import send_mail


class PostListView(ListView):
    queryset = Post.published.all()
    paginate_by = 3  # 3 posts in each page
    template_name = 'blog/post/list.html'


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
