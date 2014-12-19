from celery import Celery

from seating_chart.models import Seating
from seating_chart.utils import make_new_seating_chart, configure_seating_flags
from django.conf import settings

app = Celery('tasks', backend=settings.BACKEND_URL, broker=settings.BROKER_URL)


@app.task
def call_make_seating_chart_process(dinner, diners, manually_placed_diners, randomly_placed_diners, past_dinners, past_seatings):
    """Generates a new seating chart. This task is performed asynchronously. We make the seating chart, then save the seatings
    that correspond to that chart.
    """
    chart = make_new_seating_chart(diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=randomly_placed_diners, past_dinners=past_dinners, past_seatings=past_seatings)

    seatings = Seating.objects.select_related('person').filter(dinner=dinner)
    seating_list = [seatings.filter(person__id=int(x))[0] for x in chart]

    seating_list = configure_seating_flags(seating_list=seating_list)
    [seating.save() for seating in seating_list]

    dinner.is_processing = False
    dinner.is_saved = True
    dinner.save()
