from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext

from seating_chart.forms import add_person_form_factory, add_dinner_form_factory, add_seating_form_factory, arrange_seating_chart_form_factory
from seating_chart.models import Person, Dinner, Seating, Account
from tasks import call_make_seating_chart_process


def home(request):
    return redirect('seating_chart.views.add_person')


@login_required
def arrange_seating_chart(request, pk):
    """
    Generates the seating chart. You can only use these commands if you've assigned enough people to this
    dinner already.
    """
    account = Account.objects.filter()[0]

    dinner = Dinner.objects.get(pk=pk)

    dinner = dinner.reset_dinner()

    Form = arrange_seating_chart_form_factory(dinner=dinner)

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            return redirect('seating_chart.views.generate_seating_chart', pk=dinner.pk)
    else:
        form = Form()

    return render_to_response('arrange_seating_chart.html', {'form': form,
                                                             'account': account,
                                                             'dinner': dinner, },
                              context_instance=RequestContext(request))


@login_required
def generate_seating_chart(request, pk):
    """
    Generates the seating chart and outputs it to a form.
    """

    account = Account.objects.filter()[0]

    dinner = Dinner.objects.get(pk=pk)

    manually_placed_diners = {}

    for seating in Seating.objects.select_related('person').filter(manually_placed_diner=True, dinner=dinner):
        manually_placed_diners[seating.seat_number] = str(seating.person.pk)
        manually_placed_diners[str(seating.person.pk)] = seating.seat_number

    diners = [seating.person for seating in Seating.objects.filter(dinner=dinner).order_by('-is_head', 'manually_placed_diner')]
    randomly_placed_diners = [str(seating.person.pk) for seating in Seating.objects.select_related('person').filter(manually_placed_diner=False, dinner=dinner)]

    if not dinner.is_processing and not dinner.is_saved:
        past_dinners = list(Dinner.objects.filter(account=account, is_saved=True).order_by('-date'))
        call_make_seating_chart_process.delay(dinner=dinner, diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=randomly_placed_diners, past_dinners=past_dinners, past_seatings=Seating.objects.filter(dinner__in=past_dinners))
        dinner.is_processing = True
        dinner.save()

    head, sides, foot = dinner.render_chart()

    return render_to_response('generate_seating_chart.html', {'head': head,
                                                              'sides': sides,
                                                              'foot': foot,
                                                              'account': account,
                                                              'dinner': dinner, },
                              context_instance=RequestContext(request))


@login_required
def add_person(request):
    """
    Allows the host to add a new person to the database.
    """
    account = Account.objects.get(user=request.user)

    Form = add_person_form_factory(account=account)

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            person = Person(first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'], account=account)
            person.save()
            messages.add_message(request, messages.SUCCESS, person.get_name() + " was added to database.")
            return redirect('seating_chart.views.add_person')
    else:
        form = Form()

    people = Person.objects.filter(account=account)

    return render_to_response('add_person.html', {'people': people,
                                                  'account': account,
                                                  'form': form},
                              context_instance=RequestContext(request))


@login_required
def add_dinner(request):
    """
    Allows the host to add a new dinner.
    """
    account = Account.objects.filter()[0]

    Form = add_dinner_form_factory(account=account)

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            dinner = Dinner(date=form.cleaned_data['date'], account=account)
            dinner.save()
        messages.add_message(request, messages.SUCCESS, "Dinner for " + str(dinner.date) + " was added to database.")
    else:
        form = Form()

    dinners = Dinner.objects.filter(account=account).order_by('-date')

    return render_to_response('add_dinner.html', {'dinners': dinners,
                                                  'account': account,
                                                  'form': form, },
                              context_instance=RequestContext(request))


@login_required
def add_seating(request, pk):
    """
    Allows the host to add a person to a dinner.
    """
    account = Account.objects.filter()[0]

    dinner = Dinner.objects.get(pk=pk)

    people_at_dinner = Seating.objects.filter(dinner=dinner)

    Form = add_seating_form_factory(dinner=dinner, account=account)

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            seating = Seating(person=form.cleaned_data['person'], dinner=dinner)
            seating.save()
            messages.add_message(request, messages.SUCCESS, seating.person.get_name() + " added to dinner on " + str(seating.dinner.date))
            return redirect('seating_chart.views.add_seating', pk=dinner.pk)
    else:
        form = Form()

    return render_to_response('add_seating.html', {'dinner': dinner,
                                                   'account': account,
                                                   'form': form,
                                                   'people_at_dinner': people_at_dinner, },
                              context_instance=RequestContext(request))


@login_required
def delete_dinner(request, pk):
    """
    Allows the host to add a person to a dinner.
    """
    dinner = get_object_or_404(Dinner, pk=pk)

    dinner.delete()
    messages.add_message(request, messages.SUCCESS, "Dinner was deleted.")

    return redirect('seating_chart.views.add_dinner')


@login_required
def about(request):
    """
    Shows the about page.
    """
    return render_to_response('about.html', {}, context_instance=RequestContext(request))
