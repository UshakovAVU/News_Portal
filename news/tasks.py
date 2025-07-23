import datetime

from django.conf import settings

from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models import QuerySet
from django.template.loader import render_to_string

from .models import Post


def send_notifications(post, subscribers):
    html_content = render_to_string(
        'account/email/email_post_created.html',
        {
            'text': post.preview(),
            'link': f'{settings.SITE_URL}/news/{post.pk}',
        }
    )

    msg = EmailMultiAlternatives(
        subject=post.title,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=subscribers
    )

    msg.attach_alternative(html_content, 'text/html')
    msg.send()


@shared_task
def send_email_about_new_post(pk):
    post = Post.objects.get(pk=pk)
    categories = post.get_categories()
    subscribers_emails = []

    for cat in categories:
        subscribers = cat.subscribers.all()
        subscribers_emails += [s.email for s in subscribers]

    send_notifications(post, subscribers_emails)


def get_subscribers_with_posts() -> dict[User.email: QuerySet]:
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    subs_posts_dict = dict()
    for user in User.objects.all():
        posts = QuerySet(model=Post).none()
        if user.categories.all():
            for cat in user.categories.all():
                posts = posts.union(cat.posts_categories.filter(datetime_post__gte=last_week))
            subs_posts_dict[user.email] = posts.iterator()
    return subs_posts_dict


@shared_task
def send_weekly_mail():
    dict_for_mailing = get_subscribers_with_posts()

    for user, posts in dict_for_mailing.items():
        html_content = render_to_string(
            'account/email/weekly_mailing.html',
            {
                'link': settings.SITE_URL,
                'posts': posts,
                'user': user.split('@')[0],
            }
        )

        msg = EmailMultiAlternatives(
            subject='Статьи за неделю',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user]
        )

        msg.attach_alternative(html_content, 'text/html')
        msg.send()
