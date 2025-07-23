# import datetime
# import logging
#
# from django.conf import settings
#
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
# from django.core.mail import EmailMultiAlternatives
# from django.core.management.base import BaseCommand
# from django.db.models import QuerySet
# from django.template.loader import render_to_string
# from django_apscheduler.jobstores import DjangoJobStore
# from django_apscheduler.models import DjangoJobExecution
#
# from ...models import User, Post
#
# logger = logging.getLogger(__name__)
#
#
# def get_subscribers_with_posts() -> dict[User.email: QuerySet]:
#     today = datetime.datetime.now()
#     last_week = today - datetime.timedelta(days=7)
#     subs_posts_dict = dict()
#     for user in User.objects.all():
#         posts = QuerySet(model=Post).none()
#         if user.categories.all():
#             for cat in user.categories.all():
#                 posts = posts.union(cat.posts_categories.filter(datetime_post__gte=last_week))
#             subs_posts_dict[user.email] = posts.iterator()
#     return subs_posts_dict
#
#
# def send_weekly_mailing():
#     dict_for_mailing = get_subscribers_with_posts()
#     # print('send', dict_for_mailing)
#
#     for user, posts in dict_for_mailing.items():
#         html_content = render_to_string(
#             'account/email/weekly_mailing.html',
#             {
#                 'link': settings.SITE_URL,
#                 'posts': posts,
#                 'user': user.split('@')[0],
#             }
#         )
#
#         msg = EmailMultiAlternatives(
#             subject='Статьи за неделю',
#             body='',
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             to=[user],
#         )
#
#         msg.attach_alternative(html_content, 'text/html')
#         msg.send()
#
#
# # функция, которая будет удалять неактуальные задачи
# def delete_old_job_executions(max_age=604_800):
#     """This job deletes all apscheduler job executions older than `max_age` from the database."""
#     DjangoJobExecution.objects.delete_old_job_executions(max_age)
#
#
# class Command(BaseCommand):
#     help = "Runs apscheduler."
#
#     def handle(self, *args, **options):
#         scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
#         scheduler.add_jobstore(DjangoJobStore(), "default")
#
#         # добавляем работу нашему задачнику
#         scheduler.add_job(
#             send_weekly_mailing,
#             trigger=CronTrigger(day_of_week='wed', hour='23', minute='29'),
#             # То же, что и интервал, но задача тригера таким образом более понятна django
#             id="send_weekly_mailing",  # уникальный айди
#             max_instances=1,
#             replace_existing=True,
#         )
#         logger.info("Added job 'send_weekly_mailing'.")
#
#         scheduler.add_job(
#             delete_old_job_executions,
#             trigger=CronTrigger(
#                 day_of_week="mon", hour="00", minute="00"
#             ),
#             # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
#             id="delete_old_job_executions",
#             max_instances=1,
#             replace_existing=True,
#         )
#         logger.info(
#             "Added weekly job: 'delete_old_job_executions'."
#         )
#
#         try:
#             logger.info("Starting scheduler...")
#             scheduler.start()
#         except KeyboardInterrupt:
#             logger.info("Stopping scheduler...")
#             scheduler.shutdown()
#             logger.info("Scheduler shut down successfully!")
