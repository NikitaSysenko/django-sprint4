from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Post


class CustomUserCreationForm(UserCreationForm):
    """Расширенная форма регистрации пользователей с дополнительными полями."""

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class PostForm(forms.ModelForm):
    """Форма создания и редактирования постов."""

    class Meta:
        model = Post
        fields = ['title', 'text', 'pub_date', 'image',
                  'location', 'category', 'is_published']
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    """Форма добавления и редактирования комментариев."""

    class Meta:
        model = Comment
        fields = ('text',)
