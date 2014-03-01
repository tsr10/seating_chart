from seating_chart.models import Person, PersonToDinner, Dinner

from random import shuffle


def get_random_list_of_unplaced_diners(dinner):
	"""
	Creates the random list of diners that have not been assigned seats.
	"""
	unplaced_diners = list(set(PersonToDinner.objects.filter(manually_placed_diner=False, dinner=dinner)))
	shuffle(unplaced_diners)
	return unplaced_diners

def make_new_seating_chart(dinner):
	'''
	The seating chart generating function.
	'''
	old_dinner_list = [old_dinner for old_dinner in Dinner.objects.filter(account=dinner.account).exclude(pk=dinner.pk).order_by('-date')]
	available_seats = dinner.get_available_seats()
	validated = False
	i = 0
	while not validated:
		while i < 100:
			dinner = get_random_seating_arrangement(dinner=dinner, available_seats=available_seats)
			if not validate_against_dinners(current_dinner=dinner, old_dinner_list=old_dinner_list):
				i += 1
			else:
				validated = True
				break
		i = 0
		old_dinner_list.pop()
		print old_dinner_list
	dinner.is_saved = True
	dinner.save()
	return dinner

def get_random_seating_arrangement(dinner, available_seats):
	unplaced_diners = get_random_list_of_unplaced_diners(dinner=dinner)
	for i in range(0, len(unplaced_diners)):
		unplaced_diners[i].seat_number = available_seats[i]
		unplaced_diners[i].is_head = False
		unplaced_diners[i].is_foot = False
		if available_seats[i] == 'head':
			unplaced_diners[i].is_head = True
		elif available_seats[i] == 'foot':
			unplaced_diners[i].is_foot = True
		unplaced_diners[i].save()
	dinner = dinner.save_neighbors()
	return dinner

def validate_against_dinners(current_dinner, old_dinner_list):
	'''
	Checks to see if our current arrangement is valid against all of the dinners we're currently checking against.
	'''
	for person_to_dinner in PersonToDinner.objects.filter(dinner=current_dinner):
		for old_dinner in old_dinner_list:
			if PersonToDinner.objects.filter(dinner=old_dinner, person=person_to_dinner.person).exists():
				old_person_to_dinner = PersonToDinner.objects.get(dinner=old_dinner, person=person_to_dinner.person)
				if is_overlap(person_to_dinner=person_to_dinner, old_person_to_dinner=old_person_to_dinner):
					return False
	return True

def is_overlap(person_to_dinner, old_person_to_dinner):
	'''
	Sees if two people are excluded from sitting next to each other because of an old dinner. This does not apply to manually placed
	diners, as if two people must sit together it does not matter if they sat next to one another before.
	'''
	if not person_to_dinner.manually_placed_diner or not person_to_dinner.left_neighbor.manually_placed_diner:
		if person_to_dinner.left_neighbor.person == old_person_to_dinner.left_neighbor.person or person_to_dinner.left_neighbor.person == old_person_to_dinner.right_neighbor.person:
			return True
	if not person_to_dinner.manually_placed_diner or not person_to_dinner.right_neighbor.manually_placed_diner:
		if person_to_dinner.right_neighbor.person == old_person_to_dinner.left_neighbor.person or person_to_dinner.right_neighbor.person == old_person_to_dinner.right_neighbor.person:
			return True
	return False