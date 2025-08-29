from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Page, Paginator
from django.urls import reverse, reverse_lazy
from django.db.models import Count, QuerySet
from django.http import (Http404, HttpRequest, HttpResponse,)
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.decorators import login_required
from .models import Category, Comment, Post
from .forms import CommentForm, PostForm
from django.contrib.auth.models import AbstractBaseUser

User = get_user_model()

# Максимальное количество постов на странице
INDEX_POST_LIMIT = 10


class ProfileView(DetailView):
    """Страница профиля пользователя с его публикациями."""

    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object
        current_user = self.request.user
        if current_user == profile_user:
            posts = profile_user.posts.annotate(
                comment_count=Count('comments')).order_by('-pub_date')
        else:
            posts = profile_user.posts.published().annotate(
                comment_count=Count('comments'))
        context['page_obj'] = get_paginator(posts, self.request)
        return context


def get_paginator(posts: QuerySet, request: HttpRequest) -> Page:
    """Разбивает посты на страницы"""
    paginator = Paginator(posts, INDEX_POST_LIMIT)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница"""
    posts = Post.objects.published().annotate(comment_count=Count('comments'))
    page_obj = get_paginator(posts, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'blog/index.html', context)


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """Страница поста по идентификатору."""
    post = get_object_or_404(Post, pk=pk)

    if ((not post.is_published or post.pub_date > timezone.now()
         or not post.category.is_published)
            and post.author != request.user):
        raise Http404
    form = CommentForm()
    comments = post.comments.select_related('author')
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """Список постов выбранной категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.published().filter(category=category)
    page_obj = get_paginator(posts, request)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Страница редактирования профиля пользователя."""

    model = User
    fields = ('username', 'first_name', 'last_name', 'email')
    template_name = 'blog/user.html'

    def get_object(self) -> AbstractBaseUser:
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


@login_required
def create_post(request):
    """Страница создания нового поста."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(
                reverse(
                    'blog:profile',
                    kwargs={'username': request.user.username}
                )
            )
    else:
        form = PostForm()

    context = {
        'form': form,
    }
    return render(request, 'blog/create.html', context)


@login_required
def edit_post(request, pk):
    """Редактирование существующего поста (доступно только автору)."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('blog:post_detail', pk=pk)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    context = {
        'form': form,
        'post': post,
        'is_edit': True
    }
    return render(request, 'blog/create.html', context)


@login_required
def delete_post(request, pk):
    """Удаление поста (доступно только автору)."""
    post = get_object_or_404(Post, pk=pk, author=request.user)
    if request.method == 'GET':
        form = PostForm(instance=post)
        return render(request, 'blog/create.html', {
            'form': form,
            'post': post,
            'is_delete': True
        })
    elif request.method == 'POST':
        post.delete()
        return redirect(
            reverse(
                'blog:profile',
                kwargs={'username': request.user.username}
            )
        )


@login_required
def add_comment(request, post_pk, comment_pk=None):
    post = get_object_or_404(Post, pk=post_pk)
    if comment_pk is not None:
        instance = get_object_or_404(
            Comment, pk=comment_pk, post=post, author=request.user)
    else:
        instance = None
    form = CommentForm(request.POST or None, instance=instance)
    context = {
        'form': form,
        'post': post,
        'editing': comment_pk is not None
    }
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        if comment_pk is None:
            comment.author = request.user
            comment.post = post
        comment.save()
        return redirect('blog:post_detail', pk=post.pk)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_pk, comment_pk):
    comment = get_object_or_404(
        Comment,
        pk=comment_pk,
        post_id=post_pk,
        author=request.user
    )
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=post_pk)
    return render(request, 'blog/comment_confirm_delete.html', {
        'comment': comment
    })


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'blog/password_change.html'

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})
