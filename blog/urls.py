from django.urls import path
from django.views.generic.base import TemplateView

app_name = 'blog'
urlpatterns = [
    path('', TemplateView.as_view(template_name='blog/index.html'), name='index'),
]
