from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

news = "NE"
articles = "AR"

POST_TYPES = [
    (news, 'Новость'),
    (articles, 'Статья')
]


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Автор'))
    rating = models.IntegerField(default=0, verbose_name=_('Рейтинг'))

    def update_rating(self):
        posts_rating = self.posts.aggregate(pr=Coalesce(Sum('rating'), 0))['pr']
        comments_rating = self.user.comments.aggregate(cr=Coalesce(Sum('rating'), 0))['cr']
        posts_comments_rating = self.posts.aggregate(pcr=Coalesce(Sum('comment__rating'), 0))['pcr']

        self.rating = posts_rating * 3 + comments_rating + posts_comments_rating
        self.save()

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Название'))
    subscribers = models.ManyToManyField(User, blank=True, related_name='categories', verbose_name=_('Подписчики'))

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts', verbose_name=_('Автор'))
    post_type = models.CharField(max_length=2,
                                 choices=POST_TYPES,
                                 default=news,
                                 verbose_name=_('Тип публикации'))
    datetime_post = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory', related_name='posts_categories')
    title = models.CharField(max_length=255, verbose_name=_('Заголовок'))
    text = models.TextField(verbose_name=_('Текст'))
    rating = models.IntegerField(default=0, verbose_name=_('Рейтинг публикации'))

    def __str__(self):
        return f'{self.title.title()}: {self.text[:20]}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f"{self.text[:124]}..."

    def get_categories(self):
        cat_qs = self.category.all()
        return cat_qs

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'news-{self.id}')


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name=_('Публикация'))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('Категория'))


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name=_('Публикация'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Автор'))
    text = models.TextField(verbose_name=_('Комментарий'))
    datetime_comment = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0, verbose_name=_('Рейтинг комментария'))

    @property
    @admin.display(
        description=_('Публикация')
    )
    def post_preview(self):
        return f"{self.post.title[:40]}..."

    @property
    @admin.display(
        description=_('Комментарий')
    )
    def text_preview(self):
        return f"{self.text[:40]}..."

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()