from django.urls import path
from .views import PostListView, PostDetailView, post_share, post_detail
app_name = 'blog'
urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', post_detail, name='post_detail'),
    path('<int:post_id>/share/', post_share, name='post_share')
]
