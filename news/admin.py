from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment

from modeltranslation.admin import TranslationAdmin


def nullfy_post_rating(modeladmin, request, queryset):
    queryset.update(rating=0)
nullfy_post_rating.short_description = 'Обнулить рейтинг публикации'


def nullfy_comment_rating(modeladmin, request, queryset):
    queryset.update(rating=0)
nullfy_comment_rating.short_description = 'Обнулить рейтинг комментария'


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    model = Post
    list_display = ('title', 'post_type', 'author')
    list_filter = ('post_type', 'author')
    search_fields = ('title', 'category__name')
    actions = [nullfy_post_rating]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post_preview', 'text_preview', 'rating')
    actions = [nullfy_comment_rating]


class CategoryAdmin(TranslationAdmin):
    model = Category


class PostsAdmin(TranslationAdmin):
    model = Post


# Register your models here.
# admin.site.register(Author, AuthorAdmin)
admin.site.register(Category)
# admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
# admin.site.register(Comment, CommentAdmin)