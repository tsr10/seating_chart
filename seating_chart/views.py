from django.contrib import messages
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from seating_chart.models import Person, Dinner, PersonToDinner
from seating_chart.utils import get_placed_seats, all_seats_filled, create_new_working_seating_chart, generate_random_seat_list, check_to_see_if_list_works, create_new_working_seating_chart

def home(request):
	return redirect('seating_chart.views.add_person')

def generate_seating_chart(request):

	dinners = Dinner.objects.filter(is_saved=False)
	if not dinners:
		return redirect('seating_chart.views.add_dinner')
	else:
		dinner = dinners[0]
	people_at_dinner = PersonToDinner.objects.filter(dinner=dinner)

	if people_at_dinner.count() < dinner.attendees:
		messages.add_message(request, messages.ERROR, 'Add more people to this dinner!')
	elif people_at_dinner.count() > dinner.attendees:
		messages.add_message(request, messages.ERROR, 'Too many people in this dinner!')

	seat_numbers = range(0, dinner.attendees)
	seat_dictionary = {}
	placed_seats = {}
	error = False

	if request.method == 'POST':
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
					for person in seat_list:
						person_to_dinner = PersonToDinner.objects.get(dinner=dinner, person=person)
						person_to_dinner.seat_number = i
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

	if request.method == 'POST':
		name = request.POST.get('name')
		person = Person(name=name)
		person.save()
		messages.add_message(request, messages.SUCCESS, person.name + " was added to database.")

	people = Person.objects.filter()

	return render_to_response('add_person.html',
		{'people' : people},
		context_instance=RequestContext(request))

def add_dinner(request):
	"""
	Allows the host to add a new dinner.
	"""
	if request.method == 'POST':
		date = request.POST.get('date')
		attendees = request.POST.get('attendees')
		dinner = Dinner(date=date, attendees=attendees)
		dinner.save()
		messages.add_message(request, messages.SUCCESS, "Dinner for " + dinner.date + " was added to database.")

	dinners = Dinner.objects.filter()

	return render_to_response('add_dinner.html',
		{'dinners' : dinners,},
		context_instance=RequestContext(request))

def add_person_to_dinner(request):
	"""
	Allows the host to add a person to a dinner.
	"""
	people = Person.objects.filter()
	dinner = Dinner.objects.get(is_saved=False)
	people_at_dinner = PersonToDinner.objects.filter(dinner=dinner)

	if request.method == 'POST':
		add = request.POST.get('add')
		delete = request.POST.get('delete')
		if add:
			if dinner.attendees <= people_at_dinner.count():
				messages.add_message(request, messages.ERROR, "Dinner is full!")
			else:
				person = request.POST.get('select_person')
				person_to_dinner = PersonToDinner(person=Person.objects.get(pk=person), dinner=dinner)
				person_to_dinner.save()
				messages.add_message(request, messages.SUCCESS, person_to_dinner.person.name + " added to dinner on " + str(person_to_dinner.dinner.date))
		elif delete:
			person_to_dinner_to_delete = request.POST.get('delete')
			person_to_dinner = PersonToDinner.objects.get(pk=person_to_dinner_to_delete)
			name = person_to_dinner.person.name
			person_to_dinner.delete()
			messages.add_message(request, messages.SUCCESS, name + " deleted from dinner.")

	return render_to_response('add_person_to_dinner.html',
		{'people' : people,
		'dinner' : dinner,
		'people_at_dinner' : people_at_dinner},
		context_instance=RequestContext(request))

def view_dinner(request, dinner_pk):
	"""
	Displays the layout of a particular dinner.
	"""
	dinner = Dinner.objects.get(pk=dinner_pk)