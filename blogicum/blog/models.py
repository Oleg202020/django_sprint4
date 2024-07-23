from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db import models


User = get_user_model()
HEADER_LIMIT_STR = 256
HARACTER_LIMIT_STR = 25


class PublishedModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True,

    def __str__(self):
        return self.title[:HARACTER_LIMIT_STR]


class Category(PublishedModel):
    """Модель описывает категории в приложении"""

    title = models.CharField(
        max_length=HEADER_LIMIT_STR,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL;'
            ' разрешены символы латиницы, цифры, дефис и подчёркивание.')
    )

    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Location(PublishedModel):
    """Модель описывает поля для добавления места, где была добавлена запись"""

    name = models.CharField(
        max_length=HEADER_LIMIT_STR,
        verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:HARACTER_LIMIT_STR]


class Post(PublishedModel):
    """Модель описывает данные публикации"""

    title = models.CharField(
        max_length=HEADER_LIMIT_STR,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        unique=True,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем'
            ' — можно делать отложенные публикации.')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts',
        null=True
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        related_name='posts',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts',
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='post_images/',
        blank=True,
    )

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Comment(PublishedModel):
    text = models.TextField('Текст')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='comments'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        verbose_name='Публикация',
        related_name='comments'
    )

    class Meta:
        verbose_name = 'коментарий'
        verbose_name_plural = 'коментарии'
