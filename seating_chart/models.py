from django.db import models

class Person(models.Model):
	name = models.CharField(max_length=100)

	def __unicode__(self):
	        return str(self.name)

class Dinner(models.Model):
	date = models.DateField(null=True, blank=True)
	attendees = models.IntegerField(null=True, blank=True)
	is_saved = models.BooleanField(default=False)

	def __unicode__(self):
	        return str(self.date) + ": " + str(self.attendees) + " attendees"

	def get_seat_numbers(self):
		return range(0, self.attendees)

	def get_person_to_dinners(self):
		return PersonToDinner.objects.filter(dinner=self)

class PersonToDinner(models.Model):
	dinner = models.ForeignKey(Dinner)
	person = models.ForeignKey(Person)
	seat_number = models.IntegerField(null=True, blank=True)

	def __unicode__(self):
	        return str(self.person.name) + ": " + str(self.dinner) + ", seat number: " + str(self.seat_number)