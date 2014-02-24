from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from seating_chart.forms import add_person_form_factory, add_dinner_form_factory, add_person_to_dinner_form_factory, generate_seating_chart_form_factory
from seating_chart.models import Person, Dinner, PersonToDinner, Account
from seating_chart.utils import get_placed_seats, all_seats_filled, create_new_working_seating_chart, generate_random_seat_list, check_to_see_if_list_works, create_new_working_seating_chart, get_all_dinners

def home(request):
	return redirect('seating_chart.views.add_person')

def generate_seating_chart(request, pk):
	"""
	Generates the seating chart. You can only use these commands if you've assigned enough people to this
	dinner already.
	"""
	account = Account.objects.filter()[0]

	dinner = Dinner.objects.get(pk=pk)

	people_at_dinner = PersonToDinner.objects.filter(dinner=dinner)

	Form = generate_seating_chart_form_factory(dinner=dinner)

	if request.method == 'POST':
		form = Form(request.POST)
		if form.is_valid():
			dinner.is_saved = True
			dinner.save()
			messages.add_message(request, messages.SUCCESS, "Dinner saved.")
	else:
		form = Form()

	return render_to_response('generate_seating_chart.html',
		{'form' : form,
		'account' : account,
		'dinner' : dinner,},
		context_instance=RequestContext(request))

def add_person(request):
	"""
	Allows the host to add a new person to the database.
	"""
	account = Account.objects.filter()[0]

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

	return render_to_response('add_person.html',
		{'people' : people,
		'account' : account,
		'form' : form},
		context_instance=RequestContext(request))

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

	dinners = get_all_dinners()

	return render_to_response('add_dinner.html',
		{'dinners' : dinners,
		'account' : account,
		'form' : form,},
		context_instance=RequestContext(request))

def add_person_to_dinner(request, pk):
	"""
	Allows the host to add a person to a dinner.
	"""
	account = Account.objects.filter()[0]

	dinner = Dinner.objects.get(pk=pk)

	people_at_dinner = PersonToDinner.objects.filter(dinner=dinner)

	Form = add_person_to_dinner_form_factory(dinner=dinner, account=account)

	if request.method == 'POST':
		form = Form(request.POST)
		if form.is_valid():
			person_to_dinner = PersonToDinner(person=form.cleaned_data['person'], dinner=dinner)
			person_to_dinner.save()
			messages.add_message(request, messages.SUCCESS, person_to_dinner.person.get_name() + " added to dinner on " + str(person_to_dinner.dinner.date))
			return redirect('seating_chart.views.add_person_to_dinner', pk=dinner.pk)
	else:
		form = Form()

	return render_to_response('add_person_to_dinner.html',
		{'dinner' : dinner,
		'account' : account,
		'form' : form,
		'people_at_dinner' : people_at_dinner,},
		context_instance=RequestContext(request))
