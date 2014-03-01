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

    def get_available_seats(self):
        available_seats = []
        if not PersonToDinner.objects.filter(dinner=self, is_head=True).exists():
            available_seats.append('head')
        if not PersonToDinner.objects.filter(dinner=self, is_foot=True).exists():
            available_seats.append('foot')
        for i in range(0, self.number_of_pairs()):
            if not PersonToDinner.objects.filter(dinner=self, seat_number=str(i) + '__left').exists():
                available_seats.append(str(i) + '__left')
            if not PersonToDinner.objects.filter(dinner=self, seat_number=str(i) + '__right').exists():
                available_seats.append(str(i) + '__right')
        return available_seats

    def get_arranged_dinner(self):
        pairs_list = []
        head = PersonToDinner.objects.get(dinner=self, is_head=True)
        for i in range(0, self.number_of_pairs()):
            try:
                left = PersonToDinner.objects.get(dinner=self, seat_number=str(i) + '__left')
            except:
                left = None
            try:
                right = PersonToDinner.objects.get(dinner=self, seat_number=str(i) + '__right')
            except:
                right = None
            pairs_list.append((left, right))
        foot = PersonToDinner.objects.get(dinner=self, is_foot=True)
        return head, pairs_list, foot

    def display_arranged_dinner(self):
        display = ""
        head = PersonToDinner.objects.get(dinner=self, is_head=True).person.get_name()
        display += head + "<br>"
        for i in range(0, self.number_of_pairs()):
            try:
                left = PersonToDinner.objects.get(dinner=self, seat_number=str(i) + '__left').person.get_name()
            except:
                left = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
            try:
                right = PersonToDinner.objects.get(dinner=self, seat_number=str(i) + '__right').person.get_name()
            except:
                right = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
            display += str(left) + '&nbsp;&nbsp;&nbsp;' + str(right) + "<br>"
        foot = PersonToDinner.objects.get(dinner=self, is_foot=True).person.get_name()
        display += foot + '<br>'
        return display

    def save_neighbors(self):
        head, pairs_list, foot = self.get_arranged_dinner()
        left_side_left_neighbor = head
        right_side_right_neighbor = head
        for left, right in pairs_list:
            if left:
                left_side_left_neighbor.right_neighbor = left
                left.left_neighbor = left_side_left_neighbor
                left.save()
                left_side_left_neighbor.save()
                left_side_left_neighbor = left
            if right:
                right_side_right_neighbor.left_neighbor = right
                right.right_neighbor = right_side_right_neighbor
                right.save()
                right_side_right_neighbor.save()
                right_side_right_neighbor = right
        foot.left_neighbor = left_side_left_neighbor
        left_side_left_neighbor.right_neighbor = foot
        foot.right_neighbor = right_side_right_neighbor
        right_side_right_neighbor.left_neighbor = foot
        foot.save()
        right_side_right_neighbor.save()
        left_side_left_neighbor.save()
        return self

    def reset_dinner(self):
        self.is_saved = False
        for person_to_dinner in PersonToDinner.objects.filter(dinner=self):
            person_to_dinner.left_neighbor = None
            person_to_dinner.right_neighbor = None
            person_to_dinner.seat_number = ''
            person_to_dinner.is_head = False
            person_to_dinner.is_foot = False
            person_to_dinner.save()
        self.save()
        return self

class PersonToDinner(models.Model):
    dinner = models.ForeignKey(Dinner)
    person = models.ForeignKey(Person)

    left_neighbor = models.ForeignKey('self', null=True, related_name='left_neighbor_at_dinner')
    right_neighbor = models.ForeignKey('self', null=True, related_name='right_neighbor_at_dinner')

    seat_number = models.CharField(max_length=100, default='')

    is_head = models.BooleanField(default=False)
    is_foot = models.BooleanField(default=False)

    manually_placed_diner = models.BooleanField(default=False)

    def __unicode__(self):
            return str(self.person.get_name()) + ": " + str(self.dinner)

