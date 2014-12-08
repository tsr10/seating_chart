from seating_chart.models import PersonToDinner

from random import shuffle

def create_possible_neighbor_dict(diners, past_dinners):
    """
    This function creates the dictionary that lists the possible neighbors for each diner. Possible neighbors are 
    excluded when one of the past dinners we're looking up has the diner sitting next to that person.
    """
    possible_neighbors = {}
    past_person_to_dinners = PersonToDinner.objects.filter(dinner__in=past_dinners)
    for diner in diners:
        diner_person_to_dinners = past_person_to_dinners.filter(person=diner)
        past_neighbors = [diner]
        for person_to_dinner in diner_person_to_dinners:
            past_neighbors += person_to_dinner.get_neighbors()
        cannot_sit_next_to_list = list(set(past_neighbors))
        possible_neighbors[str(diner.pk)] = [str(potential_neighbor.pk) for potential_neighbor in diners if (potential_neighbor not in cannot_sit_next_to_list)]
    return possible_neighbors
        
def make_new_seating_chart(diners, manually_placed_diners, randomly_placed_diners, past_dinners=[]):
    """
    This is the function we call when we want to generate a seating chart for a dinner. It doesn't do any saving.
    It first creates a dictionary that contains the possible diners for each neighbor based on the old PersonToDinner
    objects fetched by the past_dinners value. If a valid dinner isn't possible given these constraints, we drop
    the oldest dinner in the list and try again.
    """
    possible_neighbors = create_possible_neighbor_dict(diners=diners, past_dinners=past_dinners)
    i = 0
    while i < 100000:
        diner_list = randomly_arrange_diners(diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=list(randomly_placed_diners))
        return_value, chart = add_one_more_diner(current_chart=[], possible_neighbors=possible_neighbors, diner_list=diner_list, manually_placed_diners=manually_placed_diners)
        if return_value == True:
            break
        i += 1
    if return_value == False:
        del past_dinners[-1]
        chart = make_new_seating_chart(diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=randomly_placed_diners, past_dinners=past_dinners)
    return chart

def add_one_more_diner(current_chart, possible_neighbors, diner_list, manually_placed_diners):
    """
    We try adding one more diner to the table here. This is a recursive function. I tried out a 'smarter' solution,
    one that didn't just randomly arrange, but it ended up running in n! time, which was far too slow. This implementation
    will miss out on possible solutions, but that's okay - there isn't a huge dollar cost associated with
    dropping an extra dinner or two.
    """
    if len(current_chart) == len(diner_list):
        if (manually_placed_diners.has_key(len(current_chart)) and manually_placed_diners.has_key(0)) or (diner_list[len(current_chart) - 1] in possible_neighbors[diner_list[0]]):
            return True, current_chart
        else:
            return False, current_chart
    next_choice = None
    if manually_placed_diners.has_key(len(current_chart)):
        if (manually_placed_diners[len(current_chart)] in possible_neighbors[diner_list[len(current_chart) - 1]]) or (manually_placed_diners.has_key(len(current_chart)-1)):
            next_choice = manually_placed_diners[len(current_chart)]
    else:
        if diner_list[len(current_chart)] in possible_neighbors[diner_list[len(current_chart) - 1]]:
            next_choice = diner_list[len(current_chart)]
    if next_choice:
        current_chart.append(next_choice)
        return_value, chart = add_one_more_diner(current_chart=current_chart, possible_neighbors=possible_neighbors, manually_placed_diners=manually_placed_diners, diner_list=diner_list)
        if return_value == True:
            return True, chart
    return False, current_chart

def configure_person_to_dinner_flags(person_to_dinner_list, dinner):
    """
    Loads each diner's neighbors and sets the is_head and is_foot flags.
    """
    for i, person_to_dinner in enumerate(person_to_dinner_list):
        person_to_dinner_list[i].left_neighbor = person_to_dinner_list[i-1]
        person_to_dinner_list[i].right_neighbor = person_to_dinner_list[(i+1)%(len(person_to_dinner_list))]
        person_to_dinner_list[i].seat_number = str(i)
        if i == 0:
            person_to_dinner_list[i].is_head = True
        if dinner.attendees()/2 == i:
            person_to_dinner_list[i].is_foot = True
    return person_to_dinner_list

def randomly_arrange_diners(randomly_placed_diners, manually_placed_diners, diners):
    """
    Creates a new diner list with manually placed diners in their proper location and the other diners placed 
    in a random order. Used to create the new list we're testing against.
    """
    new_diner_list = []
    shuffle(randomly_placed_diners)
    for i in xrange(0, len(diners)):
        if manually_placed_diners.has_key(i):
            new_diner_list.append(manually_placed_diners[i])
        else:
            new_diner_list.append(randomly_placed_diners[0])
            randomly_placed_diners.pop(0)
    return new_diner_list

