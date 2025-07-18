# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
# from django.template.loader import render_to_string

from .models import PostCategory
from .tasks import send_email_about_new_post


# def send_notifications(preview, pk, title, subscribres):
#     html_content = render_to_string(
#         'account/email/email_post_created.html',
#         {
#             'text': preview,
#             'link': f'{settings.SITE_URL}/news/{pk}'
#         }
#     )
#
#     msg = EmailMultiAlternatives(
#         subject=title,
#         body='',
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         to=subscribres,
#     )
#
#     msg.attach_alternative(html_content, 'text/html')
#     msg.send()
#
# @receiver(m2m_changed, sender=PostCategory)
# def notify_about_new_post(sender, instance, **kwargs):
#     if kwargs['action'] == 'post_add':
#         categories = instance.category.all()
#         subscribers_emails = []
#
#         for cat in categories:
#             subscribers = cat.subscribers.all()
#             subscribers_emails += [s.email for s in subscribers]
#
#         send_notifications(instance.preview(), instance.pk, instance.title, subscribers_emails)


@receiver(m2m_changed, sender=PostCategory)
def notify_about_new_post(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        send_email_about_new_post.delay(instance.pk)
