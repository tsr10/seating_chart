from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    """
    An account variable for assigning flags to logged in users. One per user.
    """
    user = models.ForeignKey(User)

    def upcoming_dinners(self):
        return Dinner.objects.filter(account=self, is_saved=False, is_processing=False).order_by('date')


class Person(models.Model):
    """
    Holds the information for a specific person. You can't have two people with the same name in the same account.
    """
    account = models.ForeignKey(Account)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.first_name) + " " + str(self.last_name)

    def get_name(self):
        return str(self.first_name) + " " + str(self.last_name)

    class Meta:
        unique_together = ("account", "first_name", "last_name")


class Dinner(models.Model):
    """
    The dinner variable. All information about the dinner is foreign keyed to this model. One per dinner.
    """
    account = models.ForeignKey(Account)

    date = models.DateField(null=True, blank=True)
    is_saved = models.BooleanField(default=False)
    is_processing = models.BooleanField(default=False)

    def __unicode__(self):
            return str(self.date) + ": " + str(self.attendees()) + " attendees"

    def get_seat_numbers(self):
        return range(0, self.attendees())

    def get_seating_order(self):
        attendees = self.attendees()
        if attendees % 2 == 1:
            pad = ["None"]
        else:
            pad = []
        first_half = range(1, self.attendees()/2) + pad
        second_half = range(self.attendees(), self.attendees()/2, -1)
        return [0] + [i for sub in zip(second_half, first_half) for i in sub] + [self.attendees()/2]

    def get_seatings(self):
        return Seating.objects.filter(dinner=self).order_by('person__last_name')

    def attendees(self):
        return self.get_seatings().count()

    def get_foot_number(self):
        return self.attendees()/2

    def number_of_pairs(self):
        attendees = self.attendees()
        if attendees <= 2:
            return 0
        elif attendees % 2 == 0:
            return attendees/2 - 1
        else:
            return attendees/2

    def pairs_list(self):
        return range(0, self.number_of_pairs())

    def reset_dinner(self):
        self.is_saved = False
        for seating in Seating.objects.filter(dinner=self):
            seating.manually_placed_diner = False
            seating.left_neighbor = None
            seating.right_neighbor = None
            seating.seat_number = None
            seating.is_head = False
            seating.is_foot = False
            seating.save()
        self.save()
        return self

    def render_chart(self):
        """
        Prepares the seating chart for showing on the page.
        """
        seatings = Seating.objects.filter(dinner=self).order_by('seat_number')
        head = seatings[0]
        foot = seatings[len(seatings)/2]
        second_half = seatings[len(seatings):len(seatings)/2:-1]
        first_half = seatings[1:(len(seatings)/2)]
        if len(first_half) < len(second_half):
            first_half += [{"person": "Empty seat"}]
        sides = zip(second_half, first_half)
        return {"head": head, "sides": sides, "foot": foot}


class Seating(models.Model):
    """
    The model that links people to dinners.
    """
    dinner = models.ForeignKey(Dinner)
    person = models.ForeignKey(Person)

    left_neighbor = models.ForeignKey('self', null=True, related_name='left_neighbor_at_dinner')
    right_neighbor = models.ForeignKey('self', null=True, related_name='right_neighbor_at_dinner')

    seat_number = models.IntegerField(null=True, blank=True)

    is_head = models.BooleanField(default=False)
    is_foot = models.BooleanField(default=False)

    manually_placed_diner = models.BooleanField(default=False)

    def __unicode__(self):
            return str(self.person.get_name()) + ": " + str(self.dinner)

    def get_neighbors(self):
        return [self.left_neighbor.person, self.right_neighbor.person]
