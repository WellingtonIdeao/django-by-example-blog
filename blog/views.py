from django.shortcuts import render, get_object_or_404
from .models import Post
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView


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