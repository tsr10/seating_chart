from seating_chart.models import Person, PersonToDinner, Dinner

from random import shuffle

def get_placed_seats(request_dict):
	"""
	Gets all of the seats that have been pre-placed by the event planner.
	"""
	placed_seats = {}
	for i in range(0, 1000):
		seat = request_dict.get('seat__' + str(i))
		if seat and seat != 'blank':
			placed_seats[str(i)] = Person.objects.get(pk=seat)
	return placed_seats

def all_seats_filled(placed_seats, dinner):
	"""
	Checks to make sure that all of the seats are populated before saving.
	"""
	i = 0
	for placed_seat, person in placed_seats.items():
		i += 1
	if i == dinner.attendees:
		return True
	return False

def check_to_see_if_list_works(seat_list, placed_diners):
	"""
	We check against previous dinners to make sure that all randomly placed diners are not next to someone
	that they have not already sat next to.
	"""
	error = False
	i = 0
	for person in seat_list:
		if not is_a_placed_diner:
			for previous_dinner in Dinner.objects.filter(is_saved=True).order_by('-date'):
				if PersonToDinner.objects.filter(person=person, dinner=previous_dinner).exists():
					seat_number_at_previous_dinner = PersonToDinner.objects.filter(person=person, dinner=previous_dinner)[0].seat_number
					previous_left_neighbor = get_left_neighbor(dinner=previous_dinner, diner=person)
					previous_right_neighbor = get_right_neighbor(dinner=previous_dinner, diner=person)
					if i == 0:
						proposed_left_neighbor = seat_list[seat_list.length() - 1]
					else:
						proposed_left_neighbor = seat_list[i - 1]
					if i == seat_list[seat_list.length() - 1]:
						proposed_right_neighbor = seat_list[0]
					else:
						proposed_right_neighbor = seat_list[i + 1]
					if proposed_left_neighbor == current_left_neighbor or proposed_right_neighbor == current_right_neighbor:
						error = True
		i += 1
	if not error:
		return True
	else:
		return False

def generate_random_seat_list(placed_seats, dinner, diners):
	"""
	Makes our random list of diners, placing the already-placed diners where they belong.
	"""
	seat_list = []
	random_list_of_unplaced_diners = get_random_list_of_unplaced_diners(dinner=dinner, placed_seats=placed_seats)
	for i in range(0, dinner.attendees):
		if str(i) in placed_seats:
			seat_list.append(placed_seats[str(i)])
		else:
			seat_list.append(random_list_of_unplaced_diners.pop())
	return seat_list

def get_unplaced_diners(dinner, placed_seats):
	"""
	Gets only those diners for a particular dinner who have not yet been placed.
	"""
	person_to_dinners = PersonToDinner.objects.filter(dinner=dinner)
	people = []
	for person_to_dinner in person_to_dinners:
		people.append(person_to_dinner.person)
	placed_diners = []
	for placed_seat, person in placed_seats.items():
		placed_diners.append(person)
	unplaced_diners = list(set(people) - set(placed_diners))
	return list(set(people) - set(placed_diners))

def get_random_list_of_unplaced_diners(dinner, placed_seats):
	"""
	Creates the random list of diners that have not been assigned seats.
	"""
	unplaced_diners = get_unplaced_diners(dinner=dinner, placed_seats=placed_seats)
	shuffle(unplaced_diners)
	return unplaced_diners

def is_a_placed_diner(placed_seats, diner):
	"""
	Checks to see if a particular diner is one of those who has already been assigned a seat by the host.
	"""
	for placed_seat, person in placed_seats.items():
		if person == diner:
			return True
	return False

def get_left_neighbor(dinner, person):
	"""
	Gets a diner's left neighbor at a particular dinner.
	"""
	seat_number = PersonToDinner.objects.filter(person=person, dinner=dinner).seat_number
	if seat_number == 0:
		left_neighbor = PersonToDinner.objects.filter(person=person, dinner=dinner, seat_number=2)[0]
	elif seat_number == dinner.attendees - 1:
		left_neighbor = PersonToDinner.objects.filter(person=person, dinner=dinner, seat_number=dinner.attendees-3)[0]
	elif seat_number == 1:
		left_neighbor = PersonToDinner.objects.filter(person=person, dinner=dinner, seat_number=0)[0]
	else: 
		left_neighbor = PersonToDinner.objects.filter(person=person, dinner=dinner, seat_number=seat_number-2)[0]
	return left_neighbor

def get_right_neighbor(dinner, person):
	"""
	Gets a diner's right neighbor at a particular dinner.
	"""
	seat_number = PersonToDinner.objects.filter(person=person, dinner=dinner).seat_number
	if seat_number == 0:
		right_neighbor = PersonToDinner.objects.filter(person=person, dinner=dinner, seat_number=1)[0]
	elif seat_number == 1000:
		right_neighbor = PersonToDinner.objects.filter(person=person, dinner=dinner, seat_number=dinner.attendees - 3)[0]
	elif seat_number == dinner.attendees-2:
		right_neighbor = PersonToDinner.objects.filter(person=person, dinner=dinner, seat_number=dinner.attendees - 1)[0]
	else: 
		right_neighbor = PersonToDinner.objects.filter(person=person, dinner=dinner, seat_number=seat_number+2)[0]
	return right_neighbor

def create_new_working_seating_chart(seat_list):
	"""
	Generates the new seating chart by creating the proper dictionary that can be rendered to the template.
	"""
	i = 0
	placed_seats = {}
	for seat in seat_list:
		placed_seats[str(i)] = seat
		i += 1
	return placed_seats


