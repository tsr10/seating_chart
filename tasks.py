from celery import Celery

from seating_chart.models import Dinner, PersonToDinner
from seating_chart.utils import make_new_seating_chart, configure_person_to_dinner_flags
from django.conf import settings

app = Celery('tasks', backend=settings.BACKEND_URL, broker=settings.BROKER_URL)


@app.task
def call_make_seating_chart_process(dinner, diners, manually_placed_diners, randomly_placed_diners, past_dinners):
    """
    Generates a new seating chart. Performed asynchronously.
    """
    chart = make_new_seating_chart(diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=randomly_placed_diners, past_dinners=list(Dinner.objects.filter(account=dinner.account, is_saved=True).order_by('-date')))

    person_to_dinners = PersonToDinner.objects.select_related('person').filter(dinner=dinner)
    person_to_dinner_list = [person_to_dinners.filter(person__id=int(x))[0] for x in chart]

    person_to_dinner_list = configure_person_to_dinner_flags(person_to_dinner_list=person_to_dinner_list, dinner=dinner)
    [person_to_dinner.save() for person_to_dinner in person_to_dinner_list]

    dinner.is_processing = False
    dinner.is_saved = True
    dinner.save()
