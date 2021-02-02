from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intent_model.settings')
app = Celery('intent_model', broker=settings.BROKER_URL)

# Using a string here means the worker will not have to
# pickle the object when using Windows.

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# If time zones are active (USE_TZ = True) define your local CELERY_TIMEZONE = 'Asia/Kolkata'
app.conf.enable_utc = False # so celery doesn't take utc by default
# We're going to have our tasks rolling soon, so that will be handy CELERY_BEAT_SCHEDULE = {}
