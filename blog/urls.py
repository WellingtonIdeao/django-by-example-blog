from django.urls import path
from .views import PostListView, PostDetailView, post_share, post_detail, post_list, post_search
from .feeds import LatestPostsFeed

app_name = 'blog'
urlpatterns = [
    # path('', PostListView.as_view(), name='post_list'),
    path('', post_list, name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', post_detail, name='post_detail'),
    path('<int:post_id>/share/', post_share, name='post_share'),
    path('tag/<slug:tag_slug>/', post_list, name='post_list_by_tag'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', post_search, name='post_search'),
]
