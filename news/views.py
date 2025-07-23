import pytz
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.core.cache import cache
from django.utils.translation import gettext as _
from django.utils import timezone
from .models import Post, Author, Category
from .filters import PostFilter
from .forms import PostForm


# Create your views here.
class PostsList(ListView):
    # model = Post
    # ordering = '-datetime_post'
    queryset = Post.objects.order_by('-datetime_post')
    template_name = 'news/posts.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_time'] = timezone.localtime(timezone.now())
        context['timezones'] = pytz.common_timezones
        return context

    def post(self, request):
        request.session['django_timezone'] = request.POST.get('timezone')
        return redirect('/news/')


class PostDetail(DetailView):
    model = Post
    template_name = 'news/post.html'
    context_object_name = 'news'
    pk_url_kwarg = 'id'

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            # return custom template
            return render(request, 'news/no_post.html', status=404)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'news-{self.kwargs["id"]}', None)

        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'news-{self.kwargs["id"]}', obj)

        return obj


class PostsSearchList(ListView):
    model = Post
    ordering = '-datetime_post'
    template_name = 'news/search.html'
    context_object_name = 'news'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/post_create_or_edit.html'
    # success_url = '/news/'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == '/article/create/':
            post.post_type = 'AR'
        post.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_title'] = self.get_type()['title']
        context['get_type'] = self.get_type()['content']
        return context

    def get_type(self):
        if self.request.path == '/article/create/':
            return {'title': _('Добавить статью'), 'content': _('Добавление новой статьи')}
        else:
            return {'title': _('Добавить новость'), 'content': _('Добавление новости')}


class PostUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'news/post_create_or_edit.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_title'] = self.get_type()['title']
        context['get_type'] = self.get_type()['content']
        return context

    def get_type(self):
        if 'article' in self.request.path:
            return {'title': _('Изменить статью'), 'content': _('Редактировать статью')}
        else:
            return {'title': _('Изменить новость'), 'content': _('Редактировать новость')}


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news/post_delete.html'
    success_url = reverse_lazy('post_list')
    pk_url_kwarg = 'id'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'account/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
        Author.objects.create(user_id=request.user.pk)
    return redirect('/news/profile/')


class CategoryListView(PostsList):
    model = Post
    template_name = 'news/category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset = Post.objects.filter(category=self.category).order_by('-datetime_post')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)

    message = _('Вы успешно подписались на рассылку новых публикаций в категории: ')
    return render(request, 'account/subscribe.html', {'category': category, 'message': message})


@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.remove(user)

    message = _('Вы успешно отписаны от рассылки по категории: ')
    return render(request, 'account/unsubscribe.html', {'category': category, 'message': message})