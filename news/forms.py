from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django.utils.translation import gettext_lazy as _
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'author']
        labels = {
            'title': _('Заголовок'),
            'text': _('Текст'),
            'category': _('Категория'),
            'author': _('Автор')
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        content = cleaned_data.get('text')
        if content == title:
            raise ValidationError(
                _('Текст не должен совпадать с заголовком.')
            )
        return cleaned_data


class CommonSignupForm(SignupForm):

    def save(self, request):
        user = super(CommonSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user
