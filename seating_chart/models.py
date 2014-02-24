from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.ForeignKey(User)

    def upcoming_dinners(self):
        return Dinner.objects.filter(account=self, is_saved=False).order_by('date')

class Person(models.Model):
    account = models.ForeignKey(Account)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __unicode__(self):
        return str(self.first_name) + " " + str(self.last_name)

    def get_name(self):
        return str(self.first_name) + " " + str(self.last_name)

class Dinner(models.Model):
    account = models.ForeignKey(Account)

    date = models.DateField(null=True, blank=True)
    is_saved = models.BooleanField(default=False)

    def __unicode__(self):
            return str(self.date) + ": " + str(self.attendees()) + " attendees"

    def get_seat_numbers(self):
        return range(0, self.attendees())

    def get_person_to_dinners(self):
        return PersonToDinner.objects.filter(dinner=self).order_by('person__last_name')

    def attendees(self):
        return self.get_person_to_dinners().count()

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

    def get_left_side(self):
        if dinner.is_saved():
            head = PersonToDinner.objects.get(dinner=dinner, is_head=True)
            left_side = []
            head_left_neighbor = head.left_neighbor
            while head_left_neighbor.is_foot == False:
                left_side.append(head_left_neighbor)
                head_left_neighbor = head_left_neighbor.left_neighbor
            return left_side
        return None

    def get_right_side(self):
        if dinner.is_saved():
            head = PersonToDinner.objects.get(dinner=dinner, is_head=True)
            left_side = []
            head_right_neighbor = head.right_neighbor
            while head_right_neighbor.is_foot == False:
                right_side.append(head_right_neighbor)
                head_right_neighbor = head_right_neighbor.right_neighbor
            return right_side
        return None


class PersonToDinner(models.Model):
    dinner = models.ForeignKey(Dinner)
    person = models.ForeignKey(Person)

    left_neighbor = models.ForeignKey('self', null=True, related_name='left_neighbor_at_dinner')
    right_neighbor = models.ForeignKey('self', null=True, related_name='right_neighbor_at_dinner')

    is_head = models.BooleanField(default=False)
    is_foot = models.BooleanField(default=False)

    def __unicode__(self):
            return str(self.person.get_name()) + ": " + str(self.dinner)

