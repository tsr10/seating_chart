from seating_chart.models import Person, PersonToDinner, Dinner

from random import shuffle


def get_random_list_of_unplaced_diners(dinner, all_person_to_dinners_at_dinner):
    """
    Creates the random list of diners that have not been assigned seats.
    """
    unplaced_diners = all_person_to_dinners_at_dinner.filter(manually_placed_diner=False).order_by('?')
    return unplaced_diners

def make_new_seating_chart(dinner):
    '''
    The seating chart generating function.
    '''
    old_dinner_list = [old_dinner.pk for old_dinner in Dinner.objects.filter(account=dinner.account).exclude(pk=dinner.pk).order_by('-date')]
    old_dinners_dict = {}
    for old_dinner_pk in old_dinner_list:
        old_dinner_dict = {}
        for person_to_dinner in PersonToDinner.objects.filter(dinner__pk=old_dinner_pk):
            old_dinner_dict[str(person_to_dinner.person.pk)] = person_to_dinner
        old_dinners_dict[str(old_dinner_pk)] = old_dinner_dict
    all_person_to_dinners_at_dinner = PersonToDinner.objects.filter(dinner=dinner)
    available_seats = dinner.get_available_seats()
    validated = False
    i = 0
    while not validated:
        while i < 100:
            seated_diners = get_random_seating_arrangement(dinner=dinner, available_seats=available_seats, all_person_to_dinners_at_dinner=all_person_to_dinners_at_dinner)
            if not validate_against_dinners(current_dinner=dinner, old_dinner_list=old_dinner_list, old_dinners_dict=old_dinners_dict, seated_diners=seated_diners):
                i += 1
            else:
                validated = True
                break
        i = 0
        old_dinner_list.pop()
    for person_to_dinner in seated_diners:
        person_to_dinner.save()
    dinner.is_saved = True
    dinner.save()
    return dinner

def get_random_seating_arrangement(dinner, available_seats, all_person_to_dinners_at_dinner):
    unplaced_diners = get_random_list_of_unplaced_diners(dinner=dinner, all_person_to_dinners_at_dinner=all_person_to_dinners_at_dinner)
    placed_diners = all_person_to_dinners_at_dinner.filter(manually_placed_diner=True)
    i = 0
    diner_dict = {}
    for unplaced_diner in unplaced_diners:
        unplaced_diner.seat_number = available_seats[i]
        unplaced_diner.is_head = False
        unplaced_diner.is_foot = False
        if available_seats[i] == 'head':
            unplaced_diner.is_head = True
        elif available_seats[i] == 'foot':
            unplaced_diner.is_foot = True
        diner_dict[str(unplaced_diner.seat_number)] = unplaced_diner
        i += 1
    for placed_diner in placed_diners:
        diner_dict[str(placed_diner.seat_number)] = placed_diner
    person_to_dinner_list = get_neighbors(diner_dict=diner_dict)
    return person_to_dinner_list

def validate_against_dinners(current_dinner, old_dinner_list, old_dinners_dict, seated_diners):
    '''
    Checks to see if our current arrangement is valid against all of the dinners we're currently checking against.
    '''
    for person_to_dinner in seated_diners:
        for old_dinner_pk in old_dinner_list:
            if str(old_dinner_pk) in old_dinners_dict:
                if str(person_to_dinner.person.pk) in old_dinners_dict[str(old_dinner_pk)]:
                    old_person_to_dinner = old_dinners_dict[str(old_dinner_pk)][str(person_to_dinner.person.pk)]
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

def get_neighbors(diner_dict):
    head = diner_dict.get('head')
    head.left_neighbor = None
    head.right_neighbor = None
    foot = diner_dict.get('foot')
    foot.left_neighbor = None
    foot.right_neighbor = None
    pairs_list = []
    for i in range(0, number_of_pairs(diner_dict=diner_dict)):
        try:
            left = diner_dict.get(str(i) + '__left')
            left.left_neighbor = None
            left.right_neighbor = None
        except:
            left = None
        try:
            right = diner_dict.get(str(i) + '__right')
            right.left_neighbor = None
            right.right_neighbor = None
        except:
            right = None
        pairs_list.append((left, right))
    filled_list = fill_neighbors(head=head, foot=foot, pairs_list=pairs_list)
    return filled_list

def fill_neighbors(head, foot, pairs_list):
    diner_list = []
    left_side_left_neighbor = head
    right_side_right_neighbor = head
    for left, right in pairs_list:
        if left:
            left_side_left_neighbor.right_neighbor = left
            left.left_neighbor = left_side_left_neighbor
            if left_side_left_neighbor.left_neighbor and left_side_left_neighbor.right_neighbor:
                diner_list.append(left_side_left_neighbor)
            left_side_left_neighbor = left
        if right:
            right_side_right_neighbor.left_neighbor = right
            right.right_neighbor = right_side_right_neighbor
            if right_side_right_neighbor.left_neighbor and right_side_right_neighbor.right_neighbor:
                diner_list.append(right_side_right_neighbor)
            right_side_right_neighbor = right
    foot.left_neighbor = left_side_left_neighbor
    left_side_left_neighbor.right_neighbor = foot
    if left_side_left_neighbor.left_neighbor and left_side_left_neighbor.right_neighbor:
        diner_list.append(left_side_left_neighbor)
    foot.right_neighbor = right_side_right_neighbor
    right_side_right_neighbor.left_neighbor = foot
    if right_side_right_neighbor.left_neighbor and right_side_right_neighbor.right_neighbor:
                diner_list.append(right_side_right_neighbor)
    diner_list.append(foot)
    return diner_list

def number_of_pairs(diner_dict):
    attendees = len(diner_dict.items())
    if attendees <= 2:
        return 0
    elif attendees % 2 == 0:
        return attendees/2 - 1
    else:
        return attendees/2