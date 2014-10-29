from __future__ import absolute_import
from celery import Celery
from seating_chart import settings

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seating_chart.settings')

app = Celery('seating_chart',
             broker=settings.BROKER_URL,
             backend=settings.BROKER_URL,
             include=['tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()