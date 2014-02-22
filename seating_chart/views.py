from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from seating_chart.forms import add_person_form_factory, add_dinner_form_factory
from seating_chart.models import Person, Dinner, PersonToDinner, Account
from seating_chart.utils import get_placed_seats, all_seats_filled, create_new_working_seating_chart, generate_random_seat_list, check_to_see_if_list_works, create_new_working_seating_chart, get_all_dinners

def home(request):
	return redirect('seating_chart.views.add_person')

def generate_seating_chart(request):
	"""
	Generates the seating chart. You can only use these commands if you've assigned enough people to this
	dinner already.
	"""

	error = False

	dinners = Dinner.objects.filter(is_saved=False)
	if not dinners:
		return redirect('seating_chart.views.add_dinner')
	else:
		dinner = dinners[0]
	people_at_dinner = PersonToDinner.objects.filter(dinner=dinner)

	if people_at_dinner.count() < dinner.attendees:
		messages.add_message(request, messages.ERROR, 'Add more people to this dinner!')
		error = True
	elif people_at_dinner.count() > dinner.attendees:
		error = True
		messages.add_message(request, messages.ERROR, 'Too many people in this dinner!')

	seat_numbers = dinner.get_seat_numbers()
	seat_dictionary = {}
	placed_seats = {}

	if request.method == 'POST' and error == False:
		placed_seats = get_placed_seats(request_dict=request.POST)
		generate = request.POST.get('generate')
		save = request.POST.get('save')
		reset = request.POST.get('reset')
		if generate:
			previous_dinners = Dinner.objects.filter(is_saved=True)
			if not error:
				does_list_work = False
				seat_list = generate_random_seat_list(placed_seats=placed_seats, dinner=dinner, diners=people_at_dinner)
				does_list_work = check_to_see_if_list_works(seat_list=seat_list, placed_diners=placed_seats)
				if does_list_work:
					i = 0
					for person in seat_list:
						person_to_dinner = PersonToDinner.objects.get(dinner=dinner, person=person, account=account)
						person_to_dinner.seat_number = i
						i += 1
						person_to_dinner.save()
		if save:
			if not all_seats_filled(placed_seats=placed_seats, dinner=dinner):
				messages.add_message(request, messages.ERROR, "Check to make sure all seats are placed.")
				error = True
			else:
				dinner.is_saved = True
				dinner.save()
				return redirect('seating_chart.views.add_dinner')
		if reset:
			for person_to_dinner in PersonToDinner.objects.filter(dinner=dinner):
				person_to_dinner.seat_number = None
				person_to_dinner.save()
			return redirect('seating_chart.views.generate_seating_chart')

	post_dict = {'people_at_dinner' : people_at_dinner,
	'seat_numbers' : seat_numbers,}
	post_dict.update(placed_seats)

	return render_to_response('generate_seating_chart.html',
		post_dict,
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
	else:
		form = Form()

	people = Person.objects.filter(account=account)

	return render_to_response('add_person.html',
		{'people' : people,
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
			dinner = Dinner(date=form.cleaned_data['date'], attendees=form.cleaned_data['attendees'], account=account)
			dinner.save()
		messages.add_message(request, messages.SUCCESS, "Dinner for " + str(dinner.date) + " was added to database.")
	else:
		form = Form()

	dinners = get_all_dinners()

	return render_to_response('add_dinner.html',
		{'dinners' : dinners,
		'form' : form,},
		context_instance=RequestContext(request))

def add_person_to_dinner(request):
	"""
	Allows the host to add a person to a dinner.
	"""
	account = Account.objects.filter()[0]

	dinner = Dinner.objects.filter(is_saved=False)
	if dinner.exists():
		dinner = dinner[0]
	else:
		messages.add_message(request, messages.WARNING, "You need to add a new dinner first!")
		return redirect('seating_chart.views.add_dinner')
	people = set([person for person in Person.objects.filter()])
	people_already_at_dinner = set([person_to_dinner.person for person_to_dinner in PersonToDinner.objects.filter(dinner=dinner)])

	people_not_at_dinner = list(people - people_already_at_dinner)

	people_at_dinner = PersonToDinner.objects.filter(dinner=dinner)

	if request.method == 'POST':
		add = request.POST.get('add')
		delete = request.POST.get('delete')
		change_attendees = request.POST.get('change_attendees')
		if add:
			if dinner.attendees <= people_at_dinner.count():
				messages.add_message(request, messages.ERROR, "Dinner is full!")
			else:
				person = request.POST.get('select_person')
				person_to_dinner = PersonToDinner(person=Person.objects.get(pk=person), dinner=dinner, account=account)
				person_to_dinner.save()
				messages.add_message(request, messages.SUCCESS, person_to_dinner.person.name + " added to dinner on " + str(person_to_dinner.dinner.date))
				return redirect('seating_chart.views.add_person_to_dinner')
		elif delete:
			person_to_dinner_to_delete = request.POST.get('delete')
			person_to_dinner = PersonToDinner.objects.get(pk=person_to_dinner_to_delete, account=account)
			name = person_to_dinner.person.name
			person_to_dinner.delete()
			messages.add_message(request, messages.SUCCESS, name + " deleted from dinner.")
			return redirect('seating_chart.views.add_person_to_dinner')
		elif change_attendees:
			attendees = request.POST.get('attendees')
			dinner.attendees = int(attendees)
			dinner.save()
			messages.add_message(request, messages.SUCCESS, "Number of attendees changed to " + str(dinner.attendees) + ".")
			return redirect('seating_chart.views.add_person_to_dinner')

	attendees = range(3, 100)

	return render_to_response('add_person_to_dinner.html',
		{'people_not_at_dinner' : people_not_at_dinner,
		'dinner' : dinner,
		'people_at_dinner' : people_at_dinner,
		'attendees' : attendees},
		context_instance=RequestContext(request))
