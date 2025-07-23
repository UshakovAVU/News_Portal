from django import forms
from django_filters import FilterSet, ModelChoiceFilter, DateFilter, CharFilter
from django.utils.translation import gettext_lazy as _
from .models import Post, Author, Category


class PostFilter(FilterSet):
    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label=_('Название заголовка')
    )
    author = ModelChoiceFilter(
        queryset=Author.objects.all(),
        lookup_expr='exact',
        label=_('Автор'),
        empty_label=_('Все авторы'),
    )
    category = ModelChoiceFilter(
        queryset=Category.objects.all(),
        lookup_expr='exact',
        label=_('Категория'),
        empty_label=_('Все категории'),
    )
    datetime_post = DateFilter(
        field_name='datetime_post',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form'}),
        lookup_expr='date__gte',
        label=_('Дата')
    )

    class Meta:
        model = Post
        fields = [
            'title',
            'author',
            'category',
            'datetime_post'
        ]
