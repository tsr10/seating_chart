from random import shuffle

NUMBER_OF_RANDOM_ARRANGEMENTS_TO_TRY = 10000


def create_possible_neighbor_dict(diners, past_seatings):
    """Create the dictionary that lists the possible neighbors for each diner. Possible neighbors should be
    excluded when one of the past dinners we're looking up has that diner sitting next to that person.
    """
    possible_neighbors = {}
    for diner in diners:
        diner_seatings = past_seatings.filter(person=diner)
        past_neighbors = [diner]
        for seating in diner_seatings:
            past_neighbors += seating.get_neighbors()
        cannot_sit_next_to_list = list(set(past_neighbors))
        possible_neighbors[str(diner.pk)] = [str(potential_neighbor.pk) for potential_neighbor in diners if (potential_neighbor not in cannot_sit_next_to_list)]
    return possible_neighbors


def make_new_seating_chart(diners, manually_placed_diners, randomly_placed_diners, past_seatings, past_dinners=[]):
    """Generate a new seating chart for a dinner.

    Create a dictionary that contains the possible diners for each neighbor based on the old Seating objects fetched by the
    past_dinners value. If a valid dinner isn't possible given these constraints, drop the oldest dinner in the list and
    try again.
    """
    possible_neighbors = create_possible_neighbor_dict(diners=diners, past_seatings=past_seatings)
    i = 0
    while i < NUMBER_OF_RANDOM_ARRANGEMENTS_TO_TRY:
        diner_list = randomly_arrange_diners(diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=randomly_placed_diners)
        return_value, chart = add_one_more_diner(current_chart=[], possible_neighbors=possible_neighbors, diner_list=diner_list, manually_placed_diners=manually_placed_diners)
        if return_value is True:
            break
        i += 1
    if return_value is False:
        del past_dinners[-1]
        chart = make_new_seating_chart(diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=randomly_placed_diners, past_dinners=past_dinners, past_seatings=past_seatings.filter(dinner__in=past_dinners))
    return chart


def add_one_more_diner(current_chart, possible_neighbors, diner_list, manually_placed_diners):
    """Try adding one more diner to the table. If one more successfully added, keep calling this function until
    either the table is full or the function fails.
    """
    seat_number_to_fill = len(current_chart)
    if seat_number_to_fill == len(diner_list):
        if (seat_number_to_fill in manually_placed_diners and 0 in manually_placed_diners) or (diner_list[seat_number_to_fill - 1] in possible_neighbors[diner_list[0]]):
            return True, current_chart
        else:
            return False, current_chart
    next_choice = fill_seat_if_possible(seat_number_to_fill=seat_number_to_fill, possible_neighbors=possible_neighbors, manually_placed_diners=manually_placed_diners, diner_list=diner_list)
    if next_choice:
        current_chart.append(next_choice)
        return_value, chart = add_one_more_diner(current_chart=current_chart, possible_neighbors=possible_neighbors, manually_placed_diners=manually_placed_diners, diner_list=diner_list)
        if return_value is True:
            return True, chart
    return False, current_chart


def fill_seat_if_possible(seat_number_to_fill, possible_neighbors, manually_placed_diners, diner_list):
    """Returns the diner who should sit in the seat number specified by seat_number_to_fill.

    Check to see if the user chose to place a diner manually in this seat. If two consecutive diners are manually placed, omit the check
    to possible_neighbors. If the next diner is randomly placed, check the possible_neighbor dictionary to make sure that they can sit there.
    If no randomly placed diners qualify, or if the manually placed diner cannot sit to its already-placed neighbor, return None.
    """
    if seat_number_to_fill in manually_placed_diners:
        if (manually_placed_diners[seat_number_to_fill] in possible_neighbors[diner_list[seat_number_to_fill - 1]]) or (seat_number_to_fill - 1) in manually_placed_diners:
            next_choice = manually_placed_diners[seat_number_to_fill]
    elif diner_list[seat_number_to_fill] in possible_neighbors[diner_list[seat_number_to_fill - 1]]:
        next_choice = diner_list[seat_number_to_fill]
    else:
        next_choice = None
    return next_choice


def configure_seating_flags(seating_list):
    """Loads each diner's neighbors and sets the is_head and is_foot flags.

    :param seating_list: The list of seatings we want to set the variables for
    :type seating_list: [Seating]
    """
    for i, seating in enumerate(seating_list):
        seating_list[i].left_neighbor = seating_list[i-1]
        seating_list[i].right_neighbor = seating_list[(i+1) % (len(seating_list))]
        seating_list[i].seat_number = i
        if i == 0:
            seating_list[i].is_head = True
        if len(seating_list)/2 == i:
            seating_list[i].is_foot = True
    return seating_list


def randomly_arrange_diners(randomly_placed_diners, manually_placed_diners, diners):
    """Creates a new diner list with manually placed diners in their proper location and the other diners placed
    in a random order.
    """
    new_diner_list = []
    shuffle(randomly_placed_diners)
    for i in xrange(0, len(diners)):
        if i in manually_placed_diners:
            new_diner_list.append(manually_placed_diners[i])
        else:
            new_diner_list.append(randomly_placed_diners[0])
            randomly_placed_diners.pop(0)
    return new_diner_list
