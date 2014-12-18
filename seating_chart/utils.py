from random import shuffle


def create_possible_neighbor_dict(diners, past_seatings):
    """
    This function creates the dictionary that lists the possible neighbors for each diner. Possible neighbors are
    excluded when one of the past dinners we're looking up has the diner sitting next to that person.
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
    """
    This is the function we call when we want to generate a seating chart for a dinner. It doesn't do any saving.
    It first creates a dictionary that contains the possible diners for each neighbor based on the old Seating
    objects fetched by the past_dinners value. If a valid dinner isn't possible given these constraints, we drop
    the oldest dinner in the list and try again.
    """
    possible_neighbors = create_possible_neighbor_dict(diners=diners, past_seatings=past_seatings)
    i = 0
    while i < 100000:
        diner_list = randomly_arrange_diners(diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=list(randomly_placed_diners))
        return_value, chart = add_one_more_diner(current_chart=[], possible_neighbors=possible_neighbors, diner_list=diner_list, manually_placed_diners=manually_placed_diners)
        if return_value is True:
            break
        i += 1
    if return_value is False:
        del past_dinners[-1]
        chart = make_new_seating_chart(diners=diners, manually_placed_diners=manually_placed_diners, randomly_placed_diners=randomly_placed_diners, past_dinners=past_dinners, past_seatings=past_seatings.filter(dinner__in=past_dinners))
    return chart


def add_one_more_diner(current_chart, possible_neighbors, diner_list, manually_placed_diners):
    """
    We try adding one more diner to the table here. This is a recursive function. I tried out a 'smarter' solution,
    one that didn't just randomly arrange, but it ended up running in n! time, which was far too slow. This implementation
    will miss out on possible solutions, but that's okay - there isn't a huge dollar cost associated with
    dropping an extra dinner or two.
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
    """
    First checks to see if the user chose to place a diner manually in this seat - if not, we see if any of the diners to randomly place
    qualify for this seat number. If no diners qualify, we return None.
    """
    if seat_number_to_fill in manually_placed_diners:
        if (manually_placed_diners[seat_number_to_fill] in possible_neighbors[diner_list[seat_number_to_fill - 1]]) or (seat_number_to_fill - 1) in manually_placed_diners:
            next_choice = manually_placed_diners[seat_number_to_fill]
    elif diner_list[seat_number_to_fill] in possible_neighbors[diner_list[seat_number_to_fill - 1]]:
        next_choice = diner_list[seat_number_to_fill]
    else:
        next_choice = None
    return next_choice


def configure_seating_flags(seating_list, dinner):
    """
    Loads each diner's neighbors and sets the is_head and is_foot flags.
    """
    for i, seating in enumerate(seating_list):
        seating_list[i].left_neighbor = seating_list[i-1]
        seating_list[i].right_neighbor = seating_list[(i+1) % (len(seating_list))]
        seating_list[i].seat_number = i
        if i == 0:
            seating_list[i].is_head = True
        if dinner.attendees()/2 == i:
            seating_list[i].is_foot = True
    return seating_list


def randomly_arrange_diners(randomly_placed_diners, manually_placed_diners, diners):
    """
    Creates a new diner list with manually placed diners in their proper location and the other diners placed
    in a random order. Used to create the new list we're testing against.
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
