from seating_chart.models import Person, PersonToDinner, Dinner

def create_possible_neighbor_dict(diners, past_dinners):
    """
    This function creates the dictionary that lists the possible neighbors for each diner. Possible neighbors are 
    excluded when one of the past dinners we're looking up has the diner sitting next to that person.
    """
    possible_neighbors = {}
    past_person_to_dinners = PersonToDinner.objects.filter(dinner__in=past_dinners)
    for diner in diners:
        diner_person_to_dinners = past_person_to_dinners.filter(person=diner)
        past_neighbors = []
        for person_to_dinner in diner_person_to_dinners:
            past_neighbors += person_to_dinner.get_neighbors()
        past_neighbors.append(diner) 
        cannot_sit_next_to_list = list(set(past_neighbors))
        possible_neighbors[str(diner.pk)] = [str(potential_neighbor.pk) for potential_neighbor in diners if (potential_neighbor not in cannot_sit_next_to_list)]
    return possible_neighbors
        
def make_new_seating_chart(diners, past_dinners=[]):
    """
    This is the function we call when we want to generate a seating chart for a dinner. It doesn't do any saving.
    It first creates a dictionary that contains the possible diners for each neighbor based on the old PersonToDinner
    objects fetched by the past_dinners value. If a valid dinner isn't possible given these constraints, we drop
    the oldest dinner in the list and try again.
    """
    forbidden_configurations = {}
    possible_neighbors = create_possible_neighbor_dict(diners=diners, past_dinners=past_dinners)
    possible_neighbors = update_possible_neighbors(current_chart=[str(diners[0].pk)], possible_neighbors=possible_neighbors)
    return_value, chart, forbidden_configurations = add_one_more_diner(current_chart=[str(diners[0].pk)], possible_neighbors=possible_neighbors, forbidden_configurations={}, number_of_diners=len(diners))
    print forbidden_configurations
    if return_value == False:
        del past_dinners[-1]
        chart = make_new_seating_chart(diners=diners, past_dinners=past_dinners)
    return chart

def add_one_more_diner(current_chart, possible_neighbors, forbidden_configurations, number_of_diners):
    """
    We try adding one more diner to the table here. This is a recursive function, and when we hit the failure condition
    we want to record the configuration that failed in forbidden_configurations.
    """
    if len(current_chart) == number_of_diners:
        return True, current_chart, forbidden_configurations
    if check_forbidden(current_chart=current_chart, forbidden_configurations=forbidden_configurations):
        return False, current_chart, forbidden_configurations
    for diner, neighbors in possible_neighbors.iteritems():
        if len(neighbors) < 2:
            forbid_configuration(current_chart=current_chart, forbidden_configurations=forbidden_configurations)
            return False, current_chart, forbidden_configurations
    next_choices = []
    for diner, neighbors in possible_neighbors.iteritems():
        if current_chart[-1] in neighbors:
            next_choices.append(diner)
    for next_choice in next_choices:
        return_value, chart, forbidden_configurations = add_one_more_diner(current_chart=current_chart + [next_choice], possible_neighbors=update_possible_neighbors(current_chart=current_chart + [next_choice], possible_neighbors=possible_neighbors), forbidden_configurations=forbidden_configurations, number_of_diners=number_of_diners)
        if return_value == True:
            return True, chart, forbidden_configurations
    forbid_configuration(current_chart=current_chart, forbidden_configurations=forbidden_configurations)
    return False, current_chart, forbidden_configurations

def update_possible_neighbors(current_chart, possible_neighbors):
    """
    We eliminate the entries in the possible_neighbors dict for people who have been placed onto the list.
    Note that we need to make a copy of the dictionary, as the possible_neighbors dictionary is different
    for each branch of recursive calls.
    """
    new_possible_neighbors = possible_neighbors.copy()
    del new_possible_neighbors[current_chart[-1]]
    if len(current_chart) < 3:
        return new_possible_neighbors
    else:
        for diner, neighbors in new_possible_neighbors.iteritems():
            if current_chart[-2] in neighbors:
                neighbors.remove(current_chart[-2])
                new_possible_neighbors[diner] = neighbors
        return new_possible_neighbors

def forbid_configuration(current_chart, forbidden_configurations):
    """
    Add this configuration to the forbidden dict. Note that we sort all middle (not first or last) elements of the 
    current configuration, as it doesn't really matter how the middle elements are ordered - it won't affect
    the validity of future actions.
    """
    if len(current_chart) < 2:
        forbidden_configurations[",".join(map(lambda x: str(x), current_chart))] = True
    else:
        sorted_chart = [current_chart[0]] + sorted(current_chart[1:(len(current_chart)-2)]) + [current_chart[-1]]
        forbidden_configurations[",".join(map(lambda x: str(x), sorted_chart))] = True

def check_forbidden(current_chart, forbidden_configurations):
    """
    Checks if a key is forbidden. If it is, we don't have to proceed any further. Note that we sort the middle 
    entries, as they can occur in any order and it won't make a difference in terms of how future neighbors 
    act.
    """
    if len(current_chart) < 2:
        if forbidden_configurations.has_key(",".join(map(lambda x: str(x), current_chart))):
            return True
        else:
            return False
    else:
        sorted_chart = [current_chart[0]] + sorted(current_chart[1:(len(current_chart)-2)]) + [current_chart[-1]]
        if forbidden_configurations.has_key(",".join(map(lambda x: str(x), sorted_chart))):
            return True
        else:
            return False

