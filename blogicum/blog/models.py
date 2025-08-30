from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

SLUG_MAX_LENGTH = 64
NAME_MAX_LENGTH = 256
TITLE_MAX_LENGTH = 256
COMMENT_PREVIEW_LENGTH = 20


class PublishedModel(models.Model):
    """Абстрактная базовая модель с общими полями для публикуемого контента.
    Служит основой для других моделей, требующих функционал публикации
    и отслеживания времени создания. Не создает отдельную таблицу в БД.
    """

    is_published = models.BooleanField(
        verbose_name='Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию от пользователей.'
    )
    created_at = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True)

    class Meta:
        abstract = True
    """Нужны ли class Meta методы str для обстракной модели? """


class Location(PublishedModel):
    """Модель географического местоположения для привязки контента.
    Позволяет ассоциировать публикации с конкретными местами.
    """

    name = models.CharField(
        verbose_name='Название места',
        max_length=NAME_MAX_LENGTH)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name


class Category(PublishedModel):
    """Модель Категории"""

    title = models.CharField(
        verbose_name='Заголовок',
        max_length=TITLE_MAX_LENGTH)
    description = models.TextField(
        verbose_name='Описание')
    slug = models.SlugField(
        max_length=SLUG_MAX_LENGTH,
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'допускаются только латинские буквы,'
            'цифры, дефис и подчёркивание.')
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self) -> str:
        return self.title


class PostQuerySet(models.QuerySet):
    """Возвращает опубликованные посты с опубликованными категориями"""

    def published(self) -> models.QuerySet:
        return self.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).order_by('-pub_date')
    """Нужны ли class Meta методы str для  менеджерa запросов (QuerySet)? """


class Post(PublishedModel):
    """Модель Публикации"""

    title = models.CharField(
        verbose_name='Заголовок публикации',
        max_length=TITLE_MAX_LENGTH)
    text = models.TextField(
        verbose_name='Текст публикации')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Установите будущую дату для отложенной публикации - '
            'пост автоматически станет доступен в указанное время.')
    )
    image = models.ImageField(
        verbose_name='Изображение',
        blank=True)

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации')
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория')

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """Модель комментария пользователей к публикациям."""

    text = models.TextField(
        verbose_name='Текст комментария')
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments'
    )
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        verbose_name='Публикация',
        related_name='comments'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return self.text[:COMMENT_PREVIEW_LENGTH]
