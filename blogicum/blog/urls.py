from django.urls import path

from . import views
from .views import (ProfileView, ProfileUpdateView, CustomPasswordChangeView)

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/create/',
         views.create_post,
         name='create_post'),
    path('posts/<int:pk>/edit/',
         views.edit_post,
         name='edit_post'),
    path('posts/<int:pk>/delete/',
         views.delete_post,
         name='delete_post'),
    path('posts/<int:post_pk>/comment/',
         views.add_comment,
         name='add_comment'),
    path('posts/<int:post_pk>/comment/<int:comment_pk>/',
         views.add_comment,
         name='edit_comment'),
    path('posts/<int:post_pk>/comment/<int:comment_pk>/delete/',
         views.delete_comment,
         name='delete_comment'),
    path(
        'posts/<int:pk>/',
        views.post_detail,
        name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'),
    path(
        'profile/edit/',
        ProfileUpdateView.as_view(),
        name='edit_profile'),
    path('password/change/',
         CustomPasswordChangeView.as_view(),
         name='password_change'),
    path(
        'profile/<str:username>/',
        ProfileView.as_view(),
        name='profile'),
]
