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

class PersonToDinner(models.Model):
    dinner = models.ForeignKey(Dinner)
    person = models.ForeignKey(Person)

    left_neighbor = models.ForeignKey('self', null=True, related_name='left_neighbor_at_dinner')
    right_neighbor = models.ForeignKey('self', null=True, related_name='right_neighbor_at_dinner')

    head = models.BooleanField(default=False)
    foot = models.BooleanField(default=False)
    seat_number = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
            return str(self.person.get_name()) + ": " + str(self.dinner) + ", seat number: " + str(self.seat_number)